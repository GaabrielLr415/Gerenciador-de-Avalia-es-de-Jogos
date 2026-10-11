
# Servidor Flask responsável pela API do TechGames
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# Armazenamento temporário para testar o servidor
# Depois será substituído pelo JSON desenvolvido pela Angélica
jogos = []
avaliacoes = []

proximo_id_jogo = 1
proximo_id_avaliacao = 1


# Função para retornar mensagens de erro
def erro(mensagem, status=400):
    return jsonify({
        "erro": "Dados inválidos" if status == 400 else "Não encontrado",
        "detalhes": mensagem
    }), status


# Procura um jogo pelo ID
def encontrar_jogo(jogo_id):
    for jogo in jogos:
        if jogo["id"] == jogo_id:
            return jogo
    return None


# Procura uma avaliação pelo ID
def encontrar_avaliacao(avaliacao_id):
    for avaliacao in avaliacoes:
        if avaliacao["id"] == avaliacao_id:
            return avaliacao
    return None


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

    return jogo_validado, None


# Valida os dados de uma avaliação
def validar_avaliacao(dados):
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

    return avaliacao_validada, None


# Rota para verificar se o servidor está funcionando
@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "aplicacao": "TechGames"
    })


# Rota para listar todos os jogos
@app.get("/jogos")
def listar_jogos():
    return jsonify(jogos), 200


# Rota para buscar um jogo pelo ID
@app.get("/jogos/<int:jogo_id>")
def buscar_jogo(jogo_id):
    jogo = encontrar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    return jsonify(jogo), 200


# Rota para cadastrar um novo jogo
@app.post("/jogos")
def cadastrar_jogo():
    global proximo_id_jogo

    dados = request.get_json(silent=True)
    jogo_validado, mensagem = validar_jogo(dados)

    if mensagem:
        return erro(mensagem)

    jogo = {
        "id": proximo_id_jogo,
        **jogo_validado
    }

    jogos.append(jogo)
    proximo_id_jogo += 1

    return jsonify(jogo), 201


# Rota para atualizar um jogo
@app.put("/jogos/<int:jogo_id>")
def atualizar_jogo(jogo_id):
    jogo = encontrar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    dados = request.get_json(silent=True)
    jogo_validado, mensagem = validar_jogo(dados)

    if mensagem:
        return erro(mensagem)

    jogo.update(jogo_validado)

    return jsonify(jogo), 200


# Rota para excluir um jogo
@app.delete("/jogos/<int:jogo_id>")
def excluir_jogo(jogo_id):
    jogo = encontrar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    jogos.remove(jogo)

    # Exclui também as avaliações relacionadas ao jogo
    avaliacoes[:] = [
        avaliacao for avaliacao in avaliacoes
        if avaliacao["jogo_id"] != jogo_id
    ]

    return jsonify({
        "mensagem": "Jogo excluído"
    }), 200


# Rota para listar as avaliações de um jogo
@app.get("/jogos/<int:jogo_id>/avaliacoes")
def listar_avaliacoes(jogo_id):
    jogo = encontrar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    resultado = [
        avaliacao for avaliacao in avaliacoes
        if avaliacao["jogo_id"] == jogo_id
    ]

    return jsonify(resultado), 200


# Rota para cadastrar uma avaliação
@app.post("/jogos/<int:jogo_id>/avaliacoes")
def cadastrar_avaliacao(jogo_id):
    global proximo_id_avaliacao

    jogo = encontrar_jogo(jogo_id)

    if jogo is None:
        return erro("Jogo não encontrado.", 404)

    dados = request.get_json(silent=True)
    avaliacao_validada, mensagem = validar_avaliacao(dados)

    if mensagem:
        return erro(mensagem)

    avaliacao = {
        "id": proximo_id_avaliacao,
        "jogo_id": jogo_id,
        **avaliacao_validada
    }

    avaliacoes.append(avaliacao)
    proximo_id_avaliacao += 1

    return jsonify(avaliacao), 201


# Rota para atualizar uma avaliação
@app.put("/avaliacoes/<int:avaliacao_id>")
def atualizar_avaliacao(avaliacao_id):
    avaliacao = encontrar_avaliacao(avaliacao_id)

    if avaliacao is None:
        return erro("Avaliação não encontrada.", 404)

    dados = request.get_json(silent=True)
    avaliacao_validada, mensagem = validar_avaliacao(dados)

    if mensagem:
        return erro(mensagem)

    avaliacao.update(avaliacao_validada)

    return jsonify(avaliacao), 200


# Rota para excluir uma avaliação
@app.delete("/avaliacoes/<int:avaliacao_id>")
def excluir_avaliacao(avaliacao_id):
    avaliacao = encontrar_avaliacao(avaliacao_id)

    if avaliacao is None:
        return erro("Avaliação não encontrada.", 404)

    avaliacoes.remove(avaliacao)

    return jsonify({
        "mensagem": "Avaliação excluída"
    }), 200


# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
