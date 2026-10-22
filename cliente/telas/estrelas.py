"""Controle de estrelas com seleção em quartos de estrela."""

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget


class Estrelas(QWidget):
    nota_alterada = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._nota = 0.0
        self.setFixedSize(240, 48)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName("Nota em estrelas")
        self.setToolTip("Cada estrela tem quatro partes. Use ← / → para ajustar ¼ de estrela ou Home para zerar.")
        self._atualizar_acessibilidade()

    def sizeHint(self):
        return QSize(240, 48)

    @property
    def nota(self):
        return self._nota

    def definir_nota(self, nota):
        nota = max(0.0, min(10.0, float(nota)))
        if nota != self._nota:
            self._nota = nota
            self._atualizar_acessibilidade()
            self.update()
            self.nota_alterada.emit(nota)

    def _atualizar_acessibilidade(self):
        self.setAccessibleDescription(f"{self._nota / 2:g} de 5 estrelas. Nota {self._nota:g} de 10.")

    def mousePressEvent(self, evento):
        if evento.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            self.definir_nota(max(0.5, math.ceil(evento.position().x() / 12) * 0.5))
            evento.accept()

    def keyPressEvent(self, evento):
        if evento.key() in (Qt.Key.Key_Right, Qt.Key.Key_Up):
            self.definir_nota(self._nota + 0.5)
        elif evento.key() in (Qt.Key.Key_Left, Qt.Key.Key_Down):
            self.definir_nota(self._nota - 0.5)
        elif evento.key() == Qt.Key.Key_Home:
            self.definir_nota(0)
        elif evento.key() == Qt.Key.Key_End:
            self.definir_nota(10)
        else:
            super().keyPressEvent(evento)

    def paintEvent(self, evento):
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.RenderHint.Antialiasing)
        for indice in range(5):
            centro = QPointF(indice * 48 + 24, 24)
            estrela = QPainterPath()
            for ponto in range(10):
                angulo = -math.pi / 2 + ponto * math.pi / 5
                raio = 19 if ponto % 2 == 0 else 8.5
                posicao = centro + QPointF(math.cos(angulo) * raio, math.sin(angulo) * raio)
                if ponto == 0:
                    estrela.moveTo(posicao)
                else:
                    estrela.lineTo(posicao)
            estrela.closeSubpath()
            pintor.fillPath(estrela, QColor("#535c6c"))
            fracao = max(0.0, min(1.0, self._nota / 2 - indice))
            pintor.save()
            pintor.setClipRect(QRectF(indice * 48 + 5, 0, 38 * fracao, 48))
            pintor.fillPath(estrela, QColor("#f5c86a"))
            pintor.restore()
        if self.hasFocus():
            pintor.setPen(QPen(QColor("#ff8577"), 1, Qt.PenStyle.DashLine))
            pintor.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)
