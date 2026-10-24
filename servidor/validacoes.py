"""Validação dos corpos JSON da API, sem depender de Flask ou Qt."""

from datetime import datetime
from urllib.parse import urlparse

from servidor.storage.repositorio_json import validar_metadados


def validar_jogo(dados):
    """Valida o formulário completo de jogo e normaliza os textos."""
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


def validar_avaliacao(dados, *, criacao=True):
    """Valida criação/edição, distinguindo campos omitidos de valores vazios."""
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
