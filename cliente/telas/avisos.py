"""Avisos de erro com ilustração local e mensagem legível."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout


class AvisoErro(QFrame):
    def __init__(self, parent=None, *, compacto=False):
        super().__init__(parent)
        self.setObjectName("erro")
        self.setAccessibleName("Aviso de erro")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(14)
        self.imagem = QLabel()
        self.imagem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lado = 64 if compacto else 96
        self.imagem.setFixedSize(lado, lado)
        caminho = Path(__file__).resolve().parents[2] / "imagem" / "500.png"
        imagem = QPixmap(str(caminho))
        if imagem.isNull():
            self.imagem.hide()
        else:
            self.imagem.setPixmap(imagem.scaled(
                lado, lado, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.imagem)
        textos = QVBoxLayout()
        textos.setSpacing(5)
        textos.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        titulo = QLabel("Oops! Aconteceu algum erro")
        titulo.setObjectName("titulo_erro")
        titulo.setWordWrap(True)
        textos.addWidget(titulo)
        self.mensagem = QLabel()
        self.mensagem.setTextFormat(Qt.TextFormat.PlainText)
        self.mensagem.setWordWrap(True)
        self.mensagem.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.mensagem.setMinimumWidth(0)
        self.mensagem.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        textos.addWidget(self.mensagem)
        layout.addLayout(textos, 1)

    def setText(self, mensagem):
        self.mensagem.setText(mensagem)
        self.setAccessibleDescription(mensagem)

    def text(self):
        return self.mensagem.text()

