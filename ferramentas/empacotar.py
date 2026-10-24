"""Gera uma pasta e um ZIP Windows que incluem Python, Qt e Flask."""

from datetime import datetime
import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys


def main():
    if os.name != "nt" or struct.calcsize("P") != 8:
        raise SystemExit("Gere o pacote em Windows com Python de 64 bits.")
    raiz = Path(__file__).resolve().parents[1]
    identificador = datetime.now().strftime("%Y%m%d-%H%M%S")
    saida = raiz / "dist" / f"TechGamer-Windows-x64-{identificador}"
    trabalho = raiz / ".local" / "empacotamento" / identificador
    bibliotecas_build = raiz / ".local" / "empacotamento" / "lib"
    ambiente = os.environ.copy()
    if bibliotecas_build.is_dir():
        ambiente["PYTHONPATH"] = str(bibliotecas_build)
    comando = [
        sys.executable, "-B", "-m", "PyInstaller", "--onedir", "--windowed",
        "--name", "TechGamer", "--distpath", str(saida),
        "--workpath", str(trabalho / "build"), "--specpath", str(trabalho),
        "--add-data", f"{raiz / 'imagem'}:imagem",
        "--exclude-module", "PySide6.QtWebEngineCore",
        "--exclude-module", "PySide6.QtWebEngineWidgets",
        "--exclude-module", "PySide6.QtWebEngineQuick",
        "--exclude-module", "PySide6.QtPdf",
        "--exclude-module", "PySide6.QtPdfWidgets",
        str(raiz / "iniciar.py"),
    ]
    subprocess.run(comando, cwd=raiz, env=ambiente, check=True)
    pacote = saida / "TechGamer"
    (pacote / "dados").mkdir()
    for nome in ("jogos.json", "avaliacoes.json", ".contadores_id.json"):
        origem = raiz / "dados" / nome
        if origem.is_file():
            shutil.copy2(origem, pacote / "dados" / nome)
    shutil.copy2(raiz / "documentacao" / "uso-portatil.txt", pacote / "LEIA-ME.txt")
    arquivo_zip = Path(shutil.make_archive(str(saida), "zip", root_dir=saida))
    resumo = hashlib.sha256(arquivo_zip.read_bytes()).hexdigest()
    arquivo_zip.with_suffix(".sha256").write_text(f"{resumo}  {arquivo_zip.name}\n", encoding="ascii")
    print(f"Pacote: {pacote}")
    print(f"ZIP: {arquivo_zip}")


if __name__ == "__main__":
    main()
