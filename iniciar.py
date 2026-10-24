"""Entrada única do pacote portátil: servidor HTTP local e cliente Qt."""

import argparse
import json
import logging
from pathlib import Path
import sys
import tempfile
import threading

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtWidgets import QMessageBox
from werkzeug.serving import make_server

from cliente.main import criar_aplicacao
from cliente.services.api_client import APIClient
from cliente.telas.janela_principal import JanelaPrincipal
from servidor.storage.repositorio_json import RepositorioJSON


def pasta_aplicacao():
    """Dados editáveis ficam junto ao executável, fora das bibliotecas incluídas."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def configurar_preferencias(pasta):
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(pasta))


def iniciar_servidor(repositorio):
    from servidor.app import app

    app.config["REPOSITORIO"] = repositorio
    # Porta livre escolhida pelo sistema; não interfere em outro Flask na 5000.
    servidor = make_server("127.0.0.1", 0, app)
    thread = threading.Thread(
        target=servidor.serve_forever,
        kwargs={"poll_interval": 0.05},
        name="TechGamer-Servidor",
        daemon=True,
    )
    thread.start()
    return servidor, thread


def verificar_portatil(qt, api, relatorio, pasta_temporaria):
    """Confere o pacote com dados e preferências descartáveis, sem alterar a biblioteca."""
    configurar_preferencias(pasta_temporaria / "preferencias")
    assert api.verificar_servidor()["status"] == "ok"
    jogo = api.cadastrar_jogo({
        "nome": "Verificação portátil", "genero": "Aventura", "plataforma": "PC",
        "ano_lancamento": 2020, "descricao": "Dados temporários de verificação.",
    })
    avaliacao = api.cadastrar_avaliacao(jogo["id"], {"autor_id": 7, "nota": 8})
    api.ator_id = 7
    api.editar_avaliacao(avaliacao["id"], {"nota": 10, "comentario": "Edição conferida"})
    assert api.consultar_media(jogo["id"])["media"] == 10
    assert len(api.listar_avaliacoes_por_autor(7)) == 1

    janela = JanelaPrincipal(api, carregar=False)
    janela.show()
    janela.atualizar()
    resultado = {"ok": False, "erro": "A interface não concluiu a consulta no prazo."}
    temporizador = QTimer()
    temporizador.setInterval(25)

    def conferir_interface():
        if janela.executor.ocupado or not janela._jogos:
            return
        try:
            assert janela.jogo["id"] == jogo["id"]
            assert janela.janela_detalhes.nota_principal.text() == "10 / 10"
            assert hasattr(janela, "logo") and not janela.logo.pixmap().isNull()
            api.excluir_jogo(jogo["id"])
            assert api.listar_avaliacoes_por_autor(7) == []
            resultado.clear()
            resultado.update({
                "ok": True,
                "executavel_autonomo": bool(getattr(sys, "frozen", False)),
                "http_local": True,
                "interface_qt": True,
                "logo": True,
                "crud_e_media": True,
            })
        except Exception as erro:
            resultado["erro"] = str(erro)
        temporizador.stop()
        qt.quit()

    temporizador.timeout.connect(conferir_interface)
    temporizador.start()
    limite = QTimer()
    limite.setSingleShot(True)
    limite.timeout.connect(qt.quit)
    limite.start(15000)
    qt.exec()
    janela.executor.pool.waitForDone(10000)
    janela.close()
    relatorio.parent.mkdir(parents=True, exist_ok=True)
    relatorio.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if resultado["ok"] else 1


def main():
    parser = argparse.ArgumentParser(description="Abrir o TechGamer com servidor local automático")
    parser.add_argument("--verificar", type=Path, help=argparse.SUPPRESS)
    argumentos = parser.parse_args()
    qt = criar_aplicacao()
    servidor = thread = None
    try:
        with tempfile.TemporaryDirectory(prefix="techgamer-portatil-") as temporaria:
            teste = Path(temporaria)
            raiz = pasta_aplicacao()
            dados = teste / "dados" if argumentos.verificar else raiz / "dados"
            preferencias = raiz / "preferencias" if getattr(sys, "frozen", False) else raiz / ".local" / "preferencias-portatil"
            configurar_preferencias(teste / "preferencias" if argumentos.verificar else preferencias)
            repositorio = RepositorioJSON(dados / "jogos.json", dados / "avaliacoes.json")
            servidor, thread = iniciar_servidor(repositorio)
            api = APIClient(f"http://127.0.0.1:{servidor.server_port}")
            if argumentos.verificar:
                return verificar_portatil(qt, api, argumentos.verificar.resolve(), teste)
            janela = JanelaPrincipal(api)
            janela.show()
            return qt.exec()
    except Exception as erro:
        logging.exception("Falha ao iniciar o TechGamer portátil")
        if argumentos.verificar:
            argumentos.verificar.write_text(json.dumps({"ok": False, "erro": str(erro)}), encoding="utf-8")
        else:
            QMessageBox.critical(None, "Não foi possível abrir o TechGamer", str(erro))
        return 1
    finally:
        if servidor is not None:
            servidor.shutdown()
            thread.join(timeout=5)
            servidor.server_close()


if __name__ == "__main__":
    sys.exit(main())
