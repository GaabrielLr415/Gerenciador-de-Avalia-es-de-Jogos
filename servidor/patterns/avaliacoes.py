"""Padrões da issue #2. A integração às rotas é responsabilidade do backend."""
from copy import deepcopy
from statistics import mean

from servidor.storage.repositorio_json import validar_metadados


class AvaliacaoBuilder:
    """Constrói uma avaliação válida sem gerar IDs ou gravar arquivos."""

    def __init__(self):
        self._dados = {"comentario": "", "metadados": {}}

    def com_autor(self, autor_id):
        if type(autor_id) is not int or autor_id <= 0:
            raise ValueError("O autor_id deve ser um inteiro positivo.")
        self._dados["autor_id"] = autor_id
        return self

    def com_nota(self, nota):
        if type(nota) not in (int, float) or not 0 <= nota <= 10:
            raise ValueError("A nota deve ser um número entre 0 e 10.")
        self._dados["nota"] = nota
        return self

    def com_comentario(self, comentario):
        if not isinstance(comentario, str):
            raise ValueError("O comentário deve ser um texto válido.")
        self._dados["comentario"] = comentario.strip()
        return self

    def com_metadados(self, metadados):
        validar_metadados(metadados)
        self._dados["metadados"] = deepcopy(metadados)
        return self

    def construir(self):
        if "nota" not in self._dados or "autor_id" not in self._dados:
            raise ValueError("Nota e autor_id são obrigatórios.")
        return deepcopy(self._dados)

    @classmethod
    def de_dados(cls, dados):
        if not isinstance(dados, dict):
            raise ValueError("Envie os dados da avaliação em JSON.")
        return (cls().com_autor(dados.get("autor_id"))
                .com_nota(dados.get("nota"))
                .com_comentario(dados.get("comentario", ""))
                .com_metadados(dados.get("metadados", {})))


class EventosAvaliacoes:
    """Subject: notifica observadores após uma gravação bem-sucedida."""

    def __init__(self):
        self._observadores = []

    def inscrever(self, observador):
        if observador not in self._observadores:
            self._observadores.append(observador)

    def remover(self, observador):
        if observador in self._observadores:
            self._observadores.remove(observador)

    def notificar(self, jogo_id):
        for observador in tuple(self._observadores):
            observador.atualizar(jogo_id)


class NotaMediaObserver:
    """Recalcula a média aritmética das notas persistidas, na escala 0–10."""

    def __init__(self, repositorio):
        self.repositorio = repositorio
        self._resultados = {}

    def atualizar(self, jogo_id):
        notas = [a["nota"] for a in self.repositorio.listar_avaliacoes(jogo_id)]
        if any(type(n) not in (int, float) or not 0 <= n <= 10 for n in notas):
            raise ValueError("Avaliação persistida contém nota inválida.")
        self._resultados[jogo_id] = {
            "jogo_id": jogo_id,
            "quantidade": len(notas),
            "media": mean(notas) if notas else None,
        }
        return dict(self._resultados[jogo_id])

    def consultar(self, jogo_id):
        # Reconstrói após reinício e reconhece gravações de outros serviços.
        return self.atualizar(jogo_id)


class ServicoAvaliacoes:
    """Subject real do Proxy: combina Builder, persistência e notificações."""

    def __init__(self, repositorio, eventos=None):
        self.repositorio = repositorio
        self.eventos = eventos if eventos is not None else EventosAvaliacoes()
        self.media = NotaMediaObserver(repositorio)
        self.eventos.inscrever(self.media)

    def _buscar(self, avaliacao_id):
        avaliacao = self.repositorio.buscar_avaliacao(avaliacao_id)
        if avaliacao is None:
            raise LookupError("Avaliação não encontrada.")
        return avaliacao

    def publicar(self, jogo_id, dados):
        if self.repositorio.buscar_jogo(jogo_id) is None:
            raise LookupError("Jogo não encontrado.")
        dados = AvaliacaoBuilder.de_dados(dados).construir()
        resultado = self.repositorio.criar_avaliacao(jogo_id, dados)
        self.eventos.notificar(jogo_id)
        return resultado

    def editar(self, avaliacao_id, dados):
        atual = self._buscar(avaliacao_id)
        if not isinstance(dados, dict) or "nota" not in dados:
            raise ValueError("O campo 'nota' é obrigatório.")
        # Preserva autoria e vínculos; segue o PUT existente para comentário.
        novos = {"nota": dados["nota"], "autor_id": atual.get("autor_id"),
                 "comentario": dados.get("comentario", ""),
                 "metadados": dados.get("metadados", atual.get("metadados", {}))}
        novos = AvaliacaoBuilder.de_dados(novos).construir()
        resultado = self.repositorio.atualizar_avaliacao(avaliacao_id, novos)
        if resultado is None:
            raise LookupError("Avaliação não encontrada.")
        self.eventos.notificar(atual["jogo_id"])
        return resultado

    def excluir(self, avaliacao_id):
        atual = self._buscar(avaliacao_id)
        if not self.repositorio.excluir_avaliacao(avaliacao_id):
            raise LookupError("Avaliação não encontrada.")
        self.eventos.notificar(atual["jogo_id"])
        return True


class AvaliacoesProxy:
    """Controla acesso ao serviço com IDs fictícios, sem autenticação ou login."""

    def __init__(self, servico, ator_id, moderadores=()):
        if type(ator_id) is not int or ator_id <= 0:
            raise PermissionError("Informe uma identificação local válida.")
        moderadores = tuple(moderadores)
        if any(type(i) is not int or i <= 0 for i in moderadores):
            raise ValueError("IDs de moderadores devem ser inteiros positivos.")
        self.servico = servico
        self.ator_id = ator_id
        # A configuração pertence ao servidor, nunca ao corpo da requisição.
        self.moderadores = frozenset(moderadores)

    def _autorizar(self, avaliacao_id):
        atual = self.servico._buscar(avaliacao_id)
        autor = atual.get("autor_id")
        # Mantém a regra existente para avaliações legadas sem autor.
        if type(autor) is not int or autor <= 0:
            raise PermissionError("Avaliação sem autor identificado não pode ser alterada.")
        if self.ator_id != autor and self.ator_id not in self.moderadores:
            raise PermissionError("Somente o autor ou moderador pode alterar a avaliação.")

    def publicar(self, jogo_id, dados):
        if not isinstance(dados, dict):
            raise ValueError("Envie os dados da avaliação em JSON.")
        if "autor_id" in dados and dados["autor_id"] != self.ator_id:
            raise PermissionError("O autor deve corresponder à identificação local.")
        return self.servico.publicar(jogo_id, {**dados, "autor_id": self.ator_id})

    def editar(self, avaliacao_id, dados):
        self._autorizar(avaliacao_id)
        return self.servico.editar(avaliacao_id, dados)

    def excluir(self, avaliacao_id):
        self._autorizar(avaliacao_id)
        return self.servico.excluir(avaliacao_id)
