# Servidor Flask responsável pela API do TechGames
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "aplicacao": "TechGames"
    })


# Rota para listar os jogos cadastrados
@app.get("/jogos")
def listar_jogos():
    return jsonify([])


# Rota para cadastrar um novo jogo
@app.post("/jogos")
def cadastrar_jogo():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados do jogo em JSON."}), 400

    # Verifica se os campos obrigatórios foram preenchidos
    campos_obrigatorios = ["nome", "genero", "plataforma", "ano_lancamento"]

    for campo in campos_obrigatorios:
        if campo not in dados or dados[campo] is None or dados[campo] == "":
            return jsonify({
                "erro": f"O campo '{campo}' é obrigatório."
            }), 400

    # Verifica se o ano de lançamento é válido
    ano = dados["ano_lancamento"]

    if type(ano) is not int or ano < 1950 or ano > 2100:
        return jsonify({
            "erro": "O ano de lançamento deve ser um número inteiro válido."
        }), 400

    # Verifica se o nome do jogo é válido
    nome = dados["nome"]

    if not isinstance(nome, str) or not nome.strip():
        return jsonify({
            "erro": "O nome do jogo deve ser um texto válido."
        }), 400

    # Verifica se gênero e plataforma são textos válidos
    for campo in ["genero", "plataforma"]:
        valor = dados[campo]

        if not isinstance(valor, str) or not valor.strip():
            return jsonify({
                "erro": f"O campo '{campo}' deve ser um texto válido."
            }), 400

    return jsonify({
        "mensagem": "Dados do jogo recebidos",
        "jogo": dados
    }), 200


if __name__ == "__main__":
    app.run(debug=True)