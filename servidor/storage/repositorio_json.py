"""
Módulo de persistência local em arquivos JSON para o TechGames.
Responsável: Angélica (Issue #5)

Implementa o padrão Repository (RepositorioJSON) sem dependência de Flask ou Qt,
garantindo persistência entre reinicializações, não reutilização de IDs e
tratamento seguro de arquivos inexistentes ou inválidos.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

# Diretório padrão de dados na raiz do projeto: <raiz>/dados
DIRETORIO_RAIZ = Path(__file__).resolve().parents[2]
DIRETORIO_DADOS_PADRAO = DIRETORIO_RAIZ / "dados"
ARQUIVO_JOGOS_PADRAO = DIRETORIO_DADOS_PADRAO / "jogos.json"
ARQUIVO_AVALIACOES_PADRAO = DIRETORIO_DADOS_PADRAO / "avaliacoes.json"


class AvaliacaoSemAutorError(PermissionError):
    """Impede alterações de avaliações sem autoria até a definição da regra pelo Proxy."""


def validar_metadados(metadados: Any) -> None:
    """Exige um objeto serializável em JSON sem números não finitos, mesmo aninhados."""
    if not isinstance(metadados, dict):
        raise ValueError("Os metadados devem ser um objeto JSON.")
    try:
        json.dumps(metadados, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Os metadados devem conter apenas valores compatíveis com JSON estrito."
        ) from exc


class RepositorioJSON:
    """
    Repositório para armazenamento e recuperação de Jogos e Avaliações em arquivos JSON.
    Segue o contrato definido em `documentacao/contrato-api.md`.
    """

    def __init__(
        self,
        caminho_jogos: str | Path | None = None,
        caminho_avaliacoes: str | Path | None = None,
        caminho_meta: str | Path | None = None,
    ) -> None:
        self.caminho_jogos = Path(caminho_jogos) if caminho_jogos else ARQUIVO_JOGOS_PADRAO
        self.caminho_avaliacoes = (
            Path(caminho_avaliacoes) if caminho_avaliacoes else ARQUIVO_AVALIACOES_PADRAO
        )

        # Arquivo auxiliar oculto para preservar contadores de IDs mesmo após exclusões
        if caminho_meta:
            self.caminho_meta = Path(caminho_meta)
        else:
            self.caminho_meta = self.caminho_jogos.parent / ".contadores_id.json"

        self._garantir_arquivos_iniciais()

    # -------------------------------------------------------------------------
    # Métodos internos de leitura, escrita segura e controle de IDs
    # -------------------------------------------------------------------------

    def _garantir_arquivos_iniciais(self) -> None:
        """Garante que os diretórios e arquivos JSON existam e sejam válidos."""
        self.caminho_jogos.parent.mkdir(parents=True, exist_ok=True)
        self.caminho_avaliacoes.parent.mkdir(parents=True, exist_ok=True)
        self.caminho_meta.parent.mkdir(parents=True, exist_ok=True)

        if not self.caminho_jogos.exists():
            self._salvar_lista(self.caminho_jogos, [])
        else:
            self._ler_lista(self.caminho_jogos)

        if not self.caminho_avaliacoes.exists():
            self._salvar_lista(self.caminho_avaliacoes, [])
        else:
            self._ler_lista(self.caminho_avaliacoes)

    def _fazer_backup_corrompido(self, caminho: Path) -> None:
        """Cria uma cópia de segurança caso um arquivo existente esteja corrompido."""
        if caminho.exists() and caminho.stat().st_size > 0:
            backup = caminho.with_suffix(caminho.suffix + ".bak")
            shutil.copy2(caminho, backup)

    def _ler_lista(self, caminho: Path) -> list[dict[str, Any]]:
        """
        Lê uma lista de dicionários a partir de um arquivo JSON.
        Trata arquivos inexistentes, vazios ou com JSON inválido sem quebrar a aplicação.
        """
        if not caminho.exists():
            self._salvar_lista(caminho, [])
            return []

        try:
            conteudo = caminho.read_text(encoding="utf-8").strip()
            if not conteudo:
                self._salvar_lista(caminho, [])
                return []

            dados = json.loads(conteudo)
            if not isinstance(dados, list):
                self._fazer_backup_corrompido(caminho)
                self._salvar_lista(caminho, [])
                return []

            # Filtra apenas itens que sejam dicionários válidos com 'id' inteiro
            lista_valida: list[dict[str, Any]] = [
                item
                for item in dados
                if isinstance(item, dict)
                and type(item.get("id")) is int
                and item["id"] > 0
            ]
            if len(lista_valida) != len(dados):
                self._fazer_backup_corrompido(caminho)
                self._salvar_lista(caminho, lista_valida)

            return lista_valida
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._fazer_backup_corrompido(caminho)
            self._salvar_lista(caminho, [])
            return []

    def _salvar_json(self, caminho: Path, dados: Any) -> None:
        """
        Grava JSON de forma atômica usando arquivo temporário no mesmo diretório.
        """
        caminho.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(
            dir=str(caminho.parent), prefix=f".{caminho.name}.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as arquivo_tmp:
                json.dump(dados, arquivo_tmp, ensure_ascii=False, indent=2)
                arquivo_tmp.write("\n")
            os.replace(temp_path, caminho)
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise

    def _salvar_lista(self, caminho: Path, dados: list[dict[str, Any]]) -> None:
        """Grava uma lista de registros em JSON de forma atômica."""
        self._salvar_json(caminho, dados)

    def _ler_contadores(self) -> dict[str, int]:
        """Lê o histórico do último ID gerado para nunca reutilizar IDs excluídos."""
        padrao = {"ultimo_id_jogo": 0, "ultimo_id_avaliacao": 0}
        if not self.caminho_meta.exists():
            return padrao

        try:
            conteudo = self.caminho_meta.read_text(encoding="utf-8").strip()
            dados = json.loads(conteudo)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._fazer_backup_corrompido(self.caminho_meta)
            raise ValueError(
                f"O arquivo de contadores de ID está corrompido: {self.caminho_meta}"
            ) from exc

        if not isinstance(dados, dict):
            self._fazer_backup_corrompido(self.caminho_meta)
            raise ValueError(
                f"O arquivo de contadores de ID tem formato inválido: {self.caminho_meta}"
            )

        for chave in padrao:
            valor = dados.get(chave, 0)
            if type(valor) is not int or valor < 0:
                self._fazer_backup_corrompido(self.caminho_meta)
                raise ValueError(
                    f"O contador '{chave}' deve ser um inteiro não negativo."
                )

        return {chave: dados.get(chave, 0) for chave in padrao}

    def _salvar_contadores(self, contadores: dict[str, int]) -> None:
        """Salva os contadores de ID atomicamente, propagando falhas de escrita."""
        self._salvar_json(self.caminho_meta, contadores)

    def _gerar_proximo_id_jogo(self, jogos: list[dict[str, Any]]) -> int:
        """Gera um ID inteiro positivo e único para Jogo, sem reutilizar IDs antigos."""
        contadores = self._ler_contadores()
        maior_id_atual = max((jogo.get("id", 0) for jogo in jogos), default=0)
        proximo_id = max(maior_id_atual, contadores["ultimo_id_jogo"]) + 1
        contadores["ultimo_id_jogo"] = proximo_id
        self._salvar_contadores(contadores)
        return proximo_id

    def _gerar_proximo_id_avaliacao(self, avaliacoes: list[dict[str, Any]]) -> int:
        """Gera um ID inteiro positivo e único para Avaliação, sem reutilizar IDs antigos."""
        contadores = self._ler_contadores()
        maior_id_atual = max((av.get("id", 0) for av in avaliacoes), default=0)
        proximo_id = max(maior_id_atual, contadores["ultimo_id_avaliacao"]) + 1
        contadores["ultimo_id_avaliacao"] = proximo_id
        self._salvar_contadores(contadores)
        return proximo_id

    # -------------------------------------------------------------------------
    # Operações de Jogos
    # -------------------------------------------------------------------------

    def listar_jogos(self) -> list[dict[str, Any]]:
        """Retorna a lista de todos os jogos armazenados."""
        return self._ler_lista(self.caminho_jogos)

    def buscar_jogo(self, jogo_id: int) -> dict[str, Any] | None:
        """Busca e retorna um jogo pelo seu ID, ou None caso não exista."""
        jogos = self._ler_lista(self.caminho_jogos)
        for jogo in jogos:
            if jogo.get("id") == jogo_id:
                return jogo
        return None

    def criar_jogo(self, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria um novo jogo com ID único gerado automaticamente e salva no JSON."""
        jogos = self._ler_lista(self.caminho_jogos)
        novo_id = self._gerar_proximo_id_jogo(jogos)

        novo_jogo = {
            "id": novo_id,
            "nome": str(dados["nome"]).strip(),
            "genero": str(dados["genero"]).strip(),
            "plataforma": str(dados["plataforma"]).strip(),
            "ano_lancamento": int(dados["ano_lancamento"]),
            "descricao": str(dados.get("descricao", "")).strip(),
        }

        if "capa_url" in dados:
            novo_jogo["capa_url"] = str(dados["capa_url"]).strip()
        jogos.append(novo_jogo)
        self._salvar_lista(self.caminho_jogos, jogos)
        return novo_jogo

    def atualizar_jogo(self, jogo_id: int, dados: dict[str, Any]) -> dict[str, Any] | None:
        """Atualiza os dados de um jogo existente pelo ID. Retorna None se não existir."""
        jogos = self._ler_lista(self.caminho_jogos)

        for indice, jogo in enumerate(jogos):
            if jogo.get("id") == jogo_id:
                jogo_atualizado = {
                    "id": jogo_id,
                    "nome": str(dados["nome"]).strip(),
                    "genero": str(dados["genero"]).strip(),
                    "plataforma": str(dados["plataforma"]).strip(),
                    "ano_lancamento": int(dados["ano_lancamento"]),
                    "descricao": str(dados.get("descricao", "")).strip(),
                }
                if "capa_url" in dados or "capa_url" in jogo:
                    jogo_atualizado["capa_url"] = str(dados.get("capa_url", jogo.get("capa_url", ""))).strip()
                jogos[indice] = jogo_atualizado
                self._salvar_lista(self.caminho_jogos, jogos)
                return jogo_atualizado

        return None

    def excluir_jogo(self, jogo_id: int) -> bool:
        """
        Exclui um jogo pelo ID e remove em cascata todas as avaliações associadas a ele.
        Retorna True se o jogo existia e foi excluído, ou False caso contrário.

        Se a gravação das avaliações falhar, tenta restaurar os jogos originais.
        A recuperação não é uma transação entre arquivos e também pode falhar.
        """
        jogos = self._ler_lista(self.caminho_jogos)
        jogos_restantes = [jogo for jogo in jogos if jogo.get("id") != jogo_id]

        if len(jogos_restantes) == len(jogos):
            return False

        # Prepara os dados antes de gravar a exclusão e mantém os jogos originais.
        avaliacoes = self._ler_lista(self.caminho_avaliacoes)
        contadores = self._ler_contadores()
        avaliacoes_restantes = [
            av for av in avaliacoes if av.get("jogo_id") != jogo_id
        ]

        # Preserva o histórico de IDs antes de remover qualquer registro.
        contadores_atualizados = {
            "ultimo_id_jogo": max(
                contadores["ultimo_id_jogo"],
                max((jogo.get("id", 0) for jogo in jogos), default=0),
            ),
            "ultimo_id_avaliacao": max(
                contadores["ultimo_id_avaliacao"],
                max((av.get("id", 0) for av in avaliacoes), default=0),
            ),
        }
        if contadores_atualizados != contadores:
            self._salvar_contadores(contadores_atualizados)

        self._salvar_lista(self.caminho_jogos, jogos_restantes)

        if len(avaliacoes_restantes) != len(avaliacoes):
            try:
                self._salvar_lista(self.caminho_avaliacoes, avaliacoes_restantes)
            except OSError as erro_avaliacoes:
                try:
                    self._salvar_lista(self.caminho_jogos, jogos)
                except OSError as erro_restauracao:
                    raise RuntimeError(
                        "Falha ao gravar as avaliações e ao restaurar os jogos; "
                        "os arquivos podem estar inconsistentes. "
                        f"Gravação das avaliações: {erro_avaliacoes}. "
                        f"Restauração dos jogos: {erro_restauracao}."
                    ) from erro_restauracao
                raise

        return True

    # -------------------------------------------------------------------------
    # Operações de Avaliações
    # -------------------------------------------------------------------------

    @staticmethod
    def _exigir_autor_identificado(avaliacao: dict[str, Any]) -> None:
        autor_id = avaliacao.get("autor_id")
        if type(autor_id) is not int or autor_id <= 0:
            raise AvaliacaoSemAutorError(
                "Avaliações sem autor identificado não podem ser alteradas ou excluídas "
                "até a definição da regra de autorização."
            )

    def listar_avaliacoes(self, jogo_id: int) -> list[dict[str, Any]]:
        """Retorna todas as avaliações associadas a um determinado jogo_id."""
        avaliacoes = self._ler_lista(self.caminho_avaliacoes)
        return [av for av in avaliacoes if av.get("jogo_id") == jogo_id]

    def buscar_avaliacao(self, avaliacao_id: int) -> dict[str, Any] | None:
        """Busca e retorna uma avaliação pelo seu ID, ou None caso não exista."""
        avaliacoes = self._ler_lista(self.caminho_avaliacoes)
        for avaliacao in avaliacoes:
            if avaliacao.get("id") == avaliacao_id:
                return avaliacao
        return None

    def criar_avaliacao(self, jogo_id: int, dados: dict[str, Any]) -> dict[str, Any]:
        """Cria uma nova avaliação para um jogo com ID único gerado automaticamente."""
        autor_id = dados.get("autor_id")
        if type(autor_id) is not int or autor_id <= 0:
            raise ValueError("O autor_id deve ser um inteiro positivo.")

        metadados = dados.get("metadados", {})
        validar_metadados(metadados)

        avaliacoes = self._ler_lista(self.caminho_avaliacoes)
        novo_id = self._gerar_proximo_id_avaliacao(avaliacoes)

        nota_bruta = dados["nota"]
        nota = int(nota_bruta) if isinstance(nota_bruta, int) else float(nota_bruta)

        nova_avaliacao = {
            "id": novo_id,
            "jogo_id": int(jogo_id),
            "autor_id": autor_id,
            "nota": nota,
            "comentario": str(dados.get("comentario", "")).strip(),
            "metadados": metadados,
        }

        avaliacoes.append(nova_avaliacao)
        self._salvar_lista(self.caminho_avaliacoes, avaliacoes)
        return nova_avaliacao

    def atualizar_avaliacao(
        self, avaliacao_id: int, dados: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Atualiza nota, comentário e metadados de uma avaliação existente.
        Preserva id, jogo_id, autor_id e os metadados quando estes são omitidos.
        """
        avaliacoes = self._ler_lista(self.caminho_avaliacoes)

        for indice, avaliacao in enumerate(avaliacoes):
            if avaliacao.get("id") == avaliacao_id:
                self._exigir_autor_identificado(avaliacao)
                metadados = dados.get("metadados", avaliacao.get("metadados", {}))
                validar_metadados(metadados)

                nota_bruta = dados["nota"]
                nota = int(nota_bruta) if isinstance(nota_bruta, int) else float(nota_bruta)

                avaliacao_atualizada = {
                    "id": avaliacao_id,
                    "jogo_id": avaliacao["jogo_id"],
                    "autor_id": avaliacao["autor_id"],
                    "nota": nota,
                    "comentario": str(dados.get("comentario", "")).strip(),
                    "metadados": metadados,
                }
                avaliacoes[indice] = avaliacao_atualizada
                self._salvar_lista(self.caminho_avaliacoes, avaliacoes)
                return avaliacao_atualizada

        return None

    def excluir_avaliacao(self, avaliacao_id: int) -> bool:
        """
        Exclui uma avaliação pelo seu ID.
        Retorna True se foi excluída ou False se não foi encontrada.
        """
        avaliacoes = self._ler_lista(self.caminho_avaliacoes)
        for avaliacao in avaliacoes:
            if avaliacao.get("id") == avaliacao_id:
                self._exigir_autor_identificado(avaliacao)
        avaliacoes_restantes = [
            av for av in avaliacoes if av.get("id") != avaliacao_id
        ]

        if len(avaliacoes_restantes) == len(avaliacoes):
            return False

        maior_id_av = max((av.get("id", 0) for av in avaliacoes), default=0)
        contadores = self._ler_contadores()
        if maior_id_av > contadores["ultimo_id_avaliacao"]:
            contadores["ultimo_id_avaliacao"] = maior_id_av
            self._salvar_contadores(contadores)

        self._salvar_lista(self.caminho_avaliacoes, avaliacoes_restantes)
        return True


# -----------------------------------------------------------------------------
# Funções auxiliares de módulo (atalhos diretos sobre o repositório padrão)
# -----------------------------------------------------------------------------

_repositorio_default: RepositorioJSON | None = None


def _obter_repo() -> RepositorioJSON:
    global _repositorio_default
    if _repositorio_default is None:
        _repositorio_default = RepositorioJSON()
    return _repositorio_default


def salvar_jogo(dados: dict[str, Any]) -> dict[str, Any]:
    """Função para salvar um novo jogo."""
    return _obter_repo().criar_jogo(dados)


def consultar_jogos() -> list[dict[str, Any]]:
    """Função para consultar todos os jogos."""
    return _obter_repo().listar_jogos()


def consultar_jogo_por_id(jogo_id: int) -> dict[str, Any] | None:
    """Função para consultar um jogo pelo ID."""
    return _obter_repo().buscar_jogo(jogo_id)


def editar_jogo(jogo_id: int, dados: dict[str, Any]) -> dict[str, Any] | None:
    """Função para editar um jogo existente."""
    return _obter_repo().atualizar_jogo(jogo_id, dados)


def remover_jogo(jogo_id: int) -> bool:
    """Função para excluir um jogo e suas avaliações."""
    return _obter_repo().excluir_jogo(jogo_id)


def salvar_avaliacao(jogo_id: int, dados: dict[str, Any]) -> dict[str, Any]:
    """Função para armazenar uma nova avaliação."""
    return _obter_repo().criar_avaliacao(jogo_id, dados)


def consultar_avaliacoes(jogo_id: int) -> list[dict[str, Any]]:
    """Função para consultar as avaliações de um jogo."""
    return _obter_repo().listar_avaliacoes(jogo_id)


def consultar_avaliacao_por_id(avaliacao_id: int) -> dict[str, Any] | None:
    """Função para consultar uma avaliação pelo ID."""
    return _obter_repo().buscar_avaliacao(avaliacao_id)


def editar_avaliacao(avaliacao_id: int, dados: dict[str, Any]) -> dict[str, Any] | None:
    """Função para editar uma avaliação."""
    return _obter_repo().atualizar_avaliacao(avaliacao_id, dados)


def remover_avaliacao(avaliacao_id: int) -> bool:
    """Função para excluir uma avaliação."""
    return _obter_repo().excluir_avaliacao(avaliacao_id)
