"""Perfis locais sem senha, vinculados aos IDs já usados nas avaliações."""

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QLabel, QSpinBox,
    QVBoxLayout,
)

from cliente.telas.avisos import AvisoErro


class PerfisLocais:
    def __init__(self, preferencias):
        self.preferencias = preferencias

    def listar(self):
        try:
            dados = json.loads(self.preferencias.value("perfis/usuarios", "[]"))
        except (TypeError, ValueError):
            return []
        if not isinstance(dados, list):
            return []
        return [p for p in dados if isinstance(p, dict)
                and isinstance(p.get("nome"), str) and p["nome"].strip()
                and type(p.get("id")) is int and 1 <= p["id"] <= 2147483647]

    def ativo(self):
        identificador = self.preferencias.value("perfis/ativo", "")
        return next((p for p in self.listar() if str(p["id"]) == str(identificador)), None)

    def proximo_id(self):
        usados = {p["id"] for p in self.listar()} | {99}
        candidato = 1
        while candidato in usados:
            candidato += 1
        return candidato

    def entrar(self, nome, identificador):
        nome = nome.strip()
        if not nome or len(nome) > 60:
            raise ValueError("Informe um nome de 1 a 60 caracteres.")
        if type(identificador) is not int or not 1 <= identificador <= 2147483647:
            raise ValueError("Informe um ID local positivo válido.")
        perfis = self.listar()
        existente = next((p for p in perfis if p["nome"].casefold() == nome.casefold()), None)
        if existente and existente["id"] != identificador:
            raise ValueError("Esse nome já está vinculado a outro ID local.")
        if any(p["id"] == identificador and p != existente for p in perfis):
            raise ValueError("Esse ID já pertence a outro perfil neste computador.")
        perfil = existente or {"nome": nome, "id": identificador}
        if not existente:
            perfis.append(perfil)
        self.preferencias.setValue("perfis/usuarios", json.dumps(perfis, ensure_ascii=False))
        self.preferencias.setValue("perfis/ativo", perfil["id"])
        self.preferencias.sync()
        return dict(perfil)

    def sair(self):
        self.preferencias.remove("perfis/ativo")
        self.preferencias.sync()


class DialogoPerfil(QDialog):
    def __init__(self, perfis, parent=None):
        super().__init__(parent)
        self.perfis = perfis
        self.perfil = None
        self.setWindowTitle("Seu perfil local")
        self.setMinimumWidth(420)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 26, 26, 26)
        layout.setSpacing(16)
        titulo = QLabel("Quem está jogando?")
        titulo.setObjectName("popup_titulo")
        layout.addWidget(titulo)
        ajuda = QLabel("Escolha um perfil ou digite seu nome. Sem senha.")
        ajuda.setWordWrap(True)
        layout.addWidget(ajuda)
        form = QFormLayout()
        self.nome = QComboBox()
        self.nome.setEditable(True)
        self.nome.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.nome.lineEdit().setMaxLength(60)
        self.nome.setAccessibleName("Nome do perfil local")
        for perfil in perfis.listar():
            self.nome.addItem(perfil["nome"], perfil["id"])
        self.nome.setCurrentIndex(-1)
        self.nome.lineEdit().setPlaceholderText("Seu nome")
        self.identificador = QSpinBox()
        self.identificador.setRange(1, 2147483647)
        self.identificador.setValue(perfis.proximo_id())
        self.nome.currentIndexChanged.connect(self._selecionar)
        self.nome.editTextChanged.connect(self._identificar_nome)
        form.addRow("Nome", self.nome)
        form.addRow("ID local", self.identificador)
        layout.addLayout(form)
        explicacao = QLabel("Para recuperar suas avaliações, use o mesmo ID de autor que já utilizava.")
        explicacao.setObjectName("subtitulo")
        explicacao.setWordWrap(True)
        layout.addWidget(explicacao)
        self.erro = AvisoErro(compacto=True)
        self.erro.hide()
        layout.addWidget(self.erro)
        botoes = QDialogButtonBox()
        self.entrar = botoes.addButton("Entrar", QDialogButtonBox.ButtonRole.AcceptRole)
        self.entrar.setObjectName("primario")
        botoes.addButton("Cancelar", QDialogButtonBox.ButtonRole.RejectRole)
        botoes.accepted.connect(self._entrar)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)
        ativo = perfis.ativo()
        if ativo:
            self.nome.setCurrentIndex(self.nome.findData(ativo["id"]))

    def _selecionar(self, indice):
        identificador = self.nome.itemData(indice)
        self.identificador.setValue(identificador if identificador else self.perfis.proximo_id())

    def _identificar_nome(self, nome):
        existente = next((p for p in self.perfis.listar()
                          if p["nome"].casefold() == nome.strip().casefold()), None)
        self.identificador.setValue(existente["id"] if existente else self.perfis.proximo_id())

    def _entrar(self):
        try:
            self.perfil = self.perfis.entrar(self.nome.currentText(), self.identificador.value())
        except ValueError as erro:
            self.erro.setText(str(erro))
            self.erro.show()
            return
        self.accept()
