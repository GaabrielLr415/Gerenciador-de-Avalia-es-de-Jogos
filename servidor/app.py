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

    return jsonify({
        "mensagem": "Dados do jogo recebidos",
        "jogo": dados
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
