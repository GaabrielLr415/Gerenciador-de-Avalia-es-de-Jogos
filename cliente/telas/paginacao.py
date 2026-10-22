"""Navegação por páginas sem alterar os endpoints existentes."""

from math import ceil

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class Paginacao(QWidget):
    alterada = Signal(int)

    def __init__(self, por_pagina=12, parent=None):
        super().__init__(parent)
        self.por_pagina = por_pagina
        self.pagina = 1
        self.total = 0
        self.layout_paginas = QHBoxLayout(self)
        self.layout_paginas.setContentsMargins(0, 8, 0, 0)
        self.layout_paginas.setSpacing(6)

    @property
    def quantidade(self):
        return max(1, ceil(self.total / self.por_pagina))

    def atualizar(self, total, pagina=None):
        self.total = total
        self.pagina = max(1, min(pagina or self.pagina, self.quantidade))
        while self.layout_paginas.count():
            item = self.layout_paginas.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
        self.layout_paginas.addStretch()
        self._botao("Anterior", self.pagina - 1, self.pagina > 1)
        indices = sorted({1, self.quantidade} | set(range(
            max(1, self.pagina - 2), min(self.quantidade, self.pagina + 2) + 1)))
        anterior = 0
        for indice in indices:
            if anterior and indice > anterior + 1:
                self.layout_paginas.addWidget(QLabel("…"))
            self._botao(str(indice), indice, True, indice == self.pagina)
            anterior = indice
        self._botao("Próxima", self.pagina + 1, self.pagina < self.quantidade)
        self.layout_paginas.addStretch()
        self.setVisible(total > self.por_pagina)

    def _botao(self, texto, pagina, habilitado, marcado=False):
        botao = QPushButton(texto)
        botao.setObjectName("pagina")
        botao.setCheckable(marcado)
        botao.setChecked(marcado)
        botao.setEnabled(habilitado)
        botao.setAccessibleName(f"Página {pagina}" if texto.isdecimal() else texto + " página")
        botao.clicked.connect(lambda _=False, numero=pagina: self.ir_para(numero))
        self.layout_paginas.addWidget(botao)

    def ir_para(self, pagina):
        pagina = max(1, min(pagina, self.quantidade))
        if pagina != self.pagina:
            self.pagina = pagina
            self.alterada.emit(pagina)

    def recortar(self, itens):
        inicio = (self.pagina - 1) * self.por_pagina
        return itens[inicio:inicio + self.por_pagina]
