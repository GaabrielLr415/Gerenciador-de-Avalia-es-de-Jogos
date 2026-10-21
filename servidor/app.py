# Servidor Flask responsável pela API do TechGames
from datetime import datetime
from pathlib import Path
import sys
from urllib.parse import urlparse

from flask import Flask, jsonify, request

# Garante que o pacote 'servidor' possa ser importado independentemente do diretório de execução
DIRETORIO_RAIZ = Path(__file__).resolve().parents[1]
if str(DIRETORIO_RAIZ) not in sys.path:
    sys.path.insert(0, str(DIRETORIO_RAIZ))

from servidor.storage.repositorio_json import (
    AvaliacaoSemAutorError,
    RepositorioJSON,
    validar_metadados,
)

from servidor.patterns import ServicoAvaliacoes, AvaliacoesProxy

app = Flask(__name__)
# IDs fictícios para demonstrar o Proxy, sem autenticação.
app.config["MODERADORES_IDS"] = (99,)

# Repositório padrão persistente em arquivos JSON (dados/jogos.json e dados/avaliacoes.json)
repositorio_padrao = RepositorioJSON()


def obter_repositorio() -> RepositorioJSON:
    """Retorna o repositório configurado na aplicação ou o repositório JSON padrão."""
    return app.config.get("REPOSITORIO", repositorio_padrao)


def obter_servico():
    repo = obter_repositorio()
    servico = app.extensions.get("avaliacoes")
    if servico is None or servico.repositorio is not repo:
        servico = ServicoAvaliacoes(repo)
        app.extensions["avaliacoes"] = servico
    return servico


def obter_proxy():
    identificacao = request.headers.get("X-Ator-Id", "")
    if not identificacao.isascii() or not identificacao.isdecimal():
        raise PermissionError("Informe X-Ator-Id com um inteiro positivo.")
    # Limita a conversão de valores arbitrariamente longos.
    if len(identificacao) > 10 or int(identificacao) > 2147483647:
        raise PermissionError("Identificação local fora do intervalo permitido.")
    return AvaliacoesProxy(obter_servico(), int(identificacao),
                           app.config["MODERADORES_IDS"])


@app.errorhandler(PermissionError)
def tratar_permissao(excecao):
    return erro(str(excecao), 403)


# Função para retornar mensagens de erro
def erro(mensagem, status=400):
    tipos_erros = {
        400: "Dados inválidos",
        403: "Acesso negado",
        404: "Não encontrado",
        500: "Erro interno do servidor"
    }

    return jsonify({
        "erro": tipos_erros.get(status, "Erro na requisição"),
        "detalhes": mensagem
    }), status


# Trata erros internos do servidor
@app.errorhandler(500)
def tratar_erro_interno(excecao):
    app.logger.error("Erro interno no servidor: %s", excecao)

    return erro(
        "Não foi possível concluir a operação.",
        500
    )


@app.errorhandler(AvaliacaoSemAutorError)
def tratar_avaliacao_sem_autor(excecao):
    return erro(str(excecao), 403)


# Valida os dados de um jogo
def validar_jogo(dados):
    if not isinstance(dados, dict):
        return None, "Envie os dados do jogo em JSON."

    campos = ["nome", "genero", "plataforma", "ano_lancamento"]

    for campo in campos:
        if campo not in dados or dados[campo] is None:
            return None, f"O campo '{campo}' é obrigatório."

    for campo in ["nome", "genero", "plataforma"]:
        valor = dados[campo]

        if not isinstance(valor, str) or not valor.strip():
            return None, f"O campo '{campo}' deve ser um texto válido."

    ano = dados["ano_lancamento"]
    ano_atual = datetime.now().year

    if type(ano) is not int or not 1950 <= ano <= ano_atual:
        return None, "O ano de lançamento é inválido."

    descricao = dados.get("descricao", "")

    if not isinstance(descricao, str):
        return None, "A descrição deve ser um texto válido."

    jogo_validado = {
        "nome": dados["nome"].strip(),
        "genero": dados["genero"].strip(),
        "plataforma": dados["plataforma"].strip(),
        "ano_lancamento": ano,
        "descricao": descricao.strip()
    }

    if "capa_url" in dados:
        capa_url = dados["capa_url"]
        if not isinstance(capa_url, str):
            return None, "O link da capa deve ser um texto válido."
        capa_url = capa_url.strip()
        try:
            endereco = urlparse(capa_url)
            valido = endereco.scheme in ("http", "https") and bool(endereco.hostname)
        except ValueError:
            valido = False
        if capa_url and not valido:
            return None, "Informe um link de capa HTTP ou HTTPS válido."
        jogo_validado["capa_url"] = capa_url

    return jogo_validado, None


# Valida os dados de uma avaliação
def validar_avaliacao(dados, *, criacao=True):
    if not isinstance(dados, dict):
        return None, "Envie os dados da avaliação em JSON."

    if "nota" not in dados:
        return None, "O campo 'nota' é obrigatório."

    nota = dados["nota"]

    if type(nota) not in (int, float) or not 0 <= nota <= 10:
        return None, "A nota deve ser um número entre 0 e 10."

    comentario = dados.get("comentario", "")

    if not isinstance(comentario, str):
        return None, "O comentário deve ser um texto válido."

    avaliacao_validada = {
        "nota": nota,
        "comentario": comentario.strip()
    }

    if criacao:
        autor_id = dados.get("autor_id")
        if type(autor_id) is not int or autor_id <= 0:
            return None, "O autor_id deve ser um inteiro positivo."
        avaliacao_validada["autor_id"] = autor_id

    if criacao or "metadados" in dados:
        metadados = dados.get("metadados", {})
        try:
            validar_metadados(metadados)
        except ValueError as exc:
            return None, str(exc)
        avaliacao_validada["metadados"] = metadados

    return avaliacao_validada, None


# Rota para verificar se o servidor está funcionando
@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "aplicacao": "TechGames",
        "recursos": ["capa_url", "design_patterns", "media_servidor"],
    })


# Rota para listar todos os jogos
@app.get("/jogos")
def listar_jogos():
    repo = obter_repositorio()
    return jsonify(repo.listar_jogos()), 200


# Rota para buscar um jogo pelo ID
@app.get("/jogos/<int:jogo_id>")
def buscar_jogo(jogo_id):
    repo = obter_repositorio()
    jogo = repo.buscar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    return jsonify(jogo), 200


# Rota para cadastrar um novo jogo
@app.post("/jogos")
def cadastrar_jogo():
    dados = request.get_json(silent=True)
    jogo_validado, mensagem = validar_jogo(dados)

    if mensagem:
        return erro(mensagem)

    repo = obter_repositorio()
    jogo = repo.criar_jogo(jogo_validado)

    return jsonify(jogo), 201


# Rota para atualizar um jogo
@app.put("/jogos/<int:jogo_id>")
def atualizar_jogo(jogo_id):
    repo = obter_repositorio()
    jogo_existente = repo.buscar_jogo(jogo_id)

    if jogo_existente is None:
        return erro("Jogo não encontrado.", 404)

    dados = request.get_json(silent=True)
    jogo_validado, mensagem = validar_jogo(dados)

    if mensagem:
        return erro(mensagem)

    jogo_atualizado = repo.atualizar_jogo(jogo_id, jogo_validado)

    return jsonify(jogo_atualizado), 200


# Rota para excluir um jogo
@app.delete("/jogos/<int:jogo_id>")
def excluir_jogo(jogo_id):
    repo = obter_repositorio()
    excluido = repo.excluir_jogo(jogo_id)

    if not excluido:
        return erro("Jogo não encontrado.", 404)

    return jsonify({
        "mensagem": "Jogo excluído"
    }), 200


# Rota para listar as avaliações de um jogo
@app.get("/jogos/<int:jogo_id>/avaliacoes")
def listar_avaliacoes(jogo_id):
    repo = obter_repositorio()
    jogo = repo.buscar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    resultado = repo.listar_avaliacoes(jogo_id)

    return jsonify(resultado), 200


@app.get("/jogos/<int:jogo_id>/media")
def consultar_media(jogo_id):
    if obter_repositorio().buscar_jogo(jogo_id) is None:
        return erro("Jogo não encontrado.", 404)
    return jsonify(obter_servico().media.consultar(jogo_id)), 200


# Rota para cadastrar uma avaliação
@app.post("/jogos/<int:jogo_id>/avaliacoes")
def cadastrar_avaliacao(jogo_id):
    repo = obter_repositorio()
    jogo = repo.buscar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    dados = request.get_json(silent=True)
    avaliacao_validada, mensagem = validar_avaliacao(dados)

    if mensagem:
        return erro(mensagem)

    avaliacao = obter_servico().publicar(jogo_id, avaliacao_validada)

    return jsonify(avaliacao), 201


# Rota para atualizar uma avaliação
@app.put("/avaliacoes/<int:avaliacao_id>")
def atualizar_avaliacao(avaliacao_id):
    repo = obter_repositorio()
    avaliacao_existente = repo.buscar_avaliacao(avaliacao_id)

    if avaliacao_existente is None:
        return erro("Avaliação não encontrada.", 404)

    dados = request.get_json(silent=True)
    avaliacao_validada, mensagem = validar_avaliacao(dados, criacao=False)

    if mensagem:
        return erro(mensagem)

    avaliacao_atualizada = obter_proxy().editar(avaliacao_id, avaliacao_validada)

    return jsonify(avaliacao_atualizada), 200


# Rota para excluir uma avaliação
@app.delete("/avaliacoes/<int:avaliacao_id>")
def excluir_avaliacao(avaliacao_id):
    repo = obter_repositorio()
    if repo.buscar_avaliacao(avaliacao_id) is None:
        return erro("Avaliação não encontrada.", 404)
    obter_proxy().excluir(avaliacao_id)

    return jsonify({
        "mensagem": "Avaliação excluída"
    }), 200



# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(debug=False)
