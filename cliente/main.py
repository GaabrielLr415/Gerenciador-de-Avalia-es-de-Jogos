"""Inicie com `python -m cliente.main` ou `python cliente/main.py`."""

import argparse
from pathlib import Path
import sys
from urllib.parse import urlparse

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication

from cliente.services.api_client import APIClient
from cliente.telas.janela_principal import JanelaPrincipal
from cliente.telas.tema import TEMA


def criar_aplicacao():
    """Aplica a mesma identidade visual nos modos pelo código e portátil."""
    app = QApplication(sys.argv[:1])
    app.setApplicationName("TechGamer")
    app.setOrganizationName("TechForce")
    app.setStyle("Fusion")
    app.setStyleSheet(TEMA)
    return app


def main():
    parser = argparse.ArgumentParser(description="TechGamer — biblioteca e avaliações de jogos")
    parser.add_argument("--servidor", default="http://127.0.0.1:5000", help="Endereço HTTP da API Flask")
    args = parser.parse_args()
    url = urlparse(args.servidor)
    if url.scheme not in ("http", "https") or not url.netloc:
        parser.error("Informe um endereço como http://127.0.0.1:5000")
    app = criar_aplicacao()
    janela = JanelaPrincipal(APIClient(args.servidor))
    janela.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
