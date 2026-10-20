"""Formulários com validação local e salvamento HTTP assíncrono."""

from datetime import datetime
from urllib.parse import urlparse

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtGui import QImageReader
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QHBoxLayout,
    QFileDialog, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget,
)

from cliente.telas.estrelas import Estrelas


class Formulario(QDialog):
    salvo = Signal(object)

    def __init__(self, titulo, executor, salvar, parent=None):
        super().__init__(parent)
        self.executor = executor
        self.salvar = salvar
        self._salvando = False
        self.setWindowTitle(titulo)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumWidth(480)
        self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(24, 24, 24, 24)
        self.layout_principal.setSpacing(16)
        cabecalho = QLabel(titulo)
        cabecalho.setObjectName("secao")
        self.layout_principal.addWidget(cabecalho)
        self.campos = QWidget()
        self.form = QFormLayout(self.campos)
        self.form.setContentsMargins(0, 0, 0, 0)
        self.form.setSpacing(12)
        self.form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.layout_principal.addWidget(self.campos)
        self.erro = QLabel()
        self.erro.setObjectName("erro")
        self.erro.setTextFormat(Qt.TextFormat.PlainText)
        self.erro.setWordWrap(True)
        self.erro.hide()
        self.layout_principal.addWidget(self.erro)
        self.botoes = QDialogButtonBox()
        self.botao_salvar = self.botoes.addButton(
            "Salvar", QDialogButtonBox.ButtonRole.AcceptRole)
        self.botao_salvar.setObjectName("primario")
        self.botao_salvar.setDefault(True)
        self.botoes.addButton(
            "Cancelar", QDialogButtonBox.ButtonRole.RejectRole)
        self.botoes.accepted.connect(self.enviar)
        self.botoes.rejected.connect(self.reject)
        self.layout_principal.addWidget(self.botoes)

    def dados(self):
        raise NotImplementedError

    def enviar(self):
        if self._salvando:
            return
        try:
            dados = self.dados()
        except ValueError as erro:
            self.mostrar_erro(str(erro))
            return
        self.erro.hide()
        self._salvando = True
        self.campos.setEnabled(False)
        self.botoes.setEnabled(False)
        self.botao_salvar.setText("Salvando…")
        self.executor.executar(lambda: self.salvar(
            dados), self._sucesso, self._falha)

    def _sucesso(self, resultado):
        self._salvando = False
        self.accept()
        self.salvo.emit(resultado)

    def _falha(self, mensagem):
        self._salvando = False
        self.campos.setEnabled(True)
        self.botoes.setEnabled(True)
        self.botao_salvar.setText("Salvar")
        self.mostrar_erro(mensagem)

    def mostrar_erro(self, mensagem):
        self.erro.setText(mensagem)
        self.erro.show()

    def reject(self):
        if not self._salvando:
            super().reject()

    def closeEvent(self, evento):
        if self._salvando:
            evento.ignore()
        else:
            super().closeEvent(evento)


class FormularioJogo(Formulario):
    def __init__(self, executor, salvar, jogo=None, parent=None):
        super().__init__("Editar jogo" if jogo else "Adicionar jogo", executor, salvar, parent)
        jogo = jogo or {}
        self.nome = QLineEdit(jogo.get("nome", ""))
        self.nome.setPlaceholderText("Ex.: Hollow Knight")
        self.genero = QLineEdit(jogo.get("genero", ""))
        self.genero.setPlaceholderText("Ex.: Mundo aberto, Metroidvania, Ação")
        self.plataforma = QComboBox()
        self.plataforma.setPlaceholderText("Selecione a plataforma")
        self.plataforma.addItems(
            ["Xbox", "PlayStation", "PC", "Nintendo Switch"])
        plataforma_atual = jogo.get("plataforma", "")
        if plataforma_atual and self.plataforma.findText(plataforma_atual) < 0:
            self.plataforma.addItem(plataforma_atual)
        self.plataforma.setCurrentIndex(
            self.plataforma.findText(plataforma_atual))
        self.ano = QSpinBox()
        self.ano.setRange(1950, datetime.now().year)
        self.ano.setValue(jogo.get("ano_lancamento", datetime.now().year))
        self.descricao = QPlainTextEdit(jogo.get("descricao", ""))
        self.descricao.setPlaceholderText("Sobre o jogo (opcional)")
        self.descricao.setMinimumHeight(110)
        self.capa_url = QLineEdit(jogo.get("capa_url", ""))
        self.capa_url.setPlaceholderText(
            "https://site.com/capa.jpg (opcional)")
        self.capa_url.setClearButtonEnabled(True)
        self.preferencias = QSettings("TechForce", "TechGames")
        self._capa_alterada = False
        self.capa_local = QLineEdit(
            self.preferencias.value(
                f"capas/{jogo['id']}", "") if jogo.get("id") else ""
        )
        self.capa_local.setReadOnly(True)
        self.capa_local.setPlaceholderText("Nenhuma imagem selecionada")
        self.botao_imagem = QPushButton("Escolher imagem…")
        self.botao_imagem.clicked.connect(self.escolher_imagem)
        self.botao_remover_imagem = QPushButton("Remover")
        self.botao_remover_imagem.clicked.connect(self.remover_imagem)
        arquivo = QHBoxLayout()
        arquivo.addWidget(self.capa_local, 1)
        arquivo.addWidget(self.botao_imagem)
        arquivo.addWidget(self.botao_remover_imagem)
        self.capa_url.textChanged.connect(self._link_alterado)
        self.form.addRow("&Nome *", self.nome)
        self.form.addRow("&Gênero *", self.genero)
        self.form.addRow("&Plataforma *", self.plataforma)
        self.form.addRow("&Ano *", self.ano)
        self.form.addRow("Imagem da capa", arquivo)
        self.form.addRow("Ou link da &capa", self.capa_url)
        self.form.addRow("&Descrição", self.descricao)

    def escolher_imagem(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolher imagem de capa", "", "Imagens (*.png *.jpg *.jpeg *.webp)"
        )
        if not caminho:
            return
        if not QImageReader(caminho).canRead():
            self.mostrar_erro(
                "Não foi possível ler esta imagem. Escolha um arquivo PNG, JPG ou WebP válido.")
            return
        self.capa_url.clear()
        self.capa_local.setText(caminho)
        self._capa_alterada = True
        self.erro.hide()

    def remover_imagem(self):
        self.capa_local.clear()
        self._capa_alterada = True

    def _link_alterado(self, texto):
        if texto.strip():
            self.remover_imagem()

    def _sucesso(self, resultado):
        if self._capa_alterada:
            chave = f"capas/{resultado['id']}"
            if self.capa_local.text():
                self.preferencias.setValue(chave, self.capa_local.text())
            else:
                self.preferencias.remove(chave)
        super()._sucesso(resultado)

    def dados(self):
        for campo, nome in ((self.nome, "nome"), (self.genero, "gênero")):
            if not campo.text().strip():
                campo.setFocus()
                raise ValueError(f"Preencha o campo {nome}.")
        if self.plataforma.currentIndex() < 0:
            self.plataforma.setFocus()
            raise ValueError("Selecione a plataforma.")
        self.ano.interpretText()
        if self.capa_local.text() and not QImageReader(self.capa_local.text()).canRead():
            raise ValueError(
                "A imagem selecionada não está disponível. Escolha a imagem novamente ou use um link.")
        capa_url = self.capa_url.text().strip()
        try:
            endereco = urlparse(capa_url)
            valido = endereco.scheme in (
                "http", "https") and bool(endereco.hostname)
        except ValueError:
            valido = False
        if capa_url and not valido:
            self.capa_url.setFocus()
            raise ValueError(
                "Informe um link de imagem válido começando com http:// ou https://.")
        return {
            "nome": self.nome.text().strip(),
            "genero": self.genero.text().strip(),
            "plataforma": self.plataforma.currentText(),
            "ano_lancamento": self.ano.value(),
            "descricao": self.descricao.toPlainText().strip(),
            "capa_url": capa_url,
        }


class FormularioAvaliacao(Formulario):
    def __init__(self, executor, salvar, avaliacao=None, parent=None):
        super().__init__("Editar avaliação" if avaliacao else "Avaliar jogo",
                         executor, salvar, parent)
        self.avaliacao = avaliacao
        registro = avaliacao or {}
        self.autor = QSpinBox()
        self.autor.setRange(1, 2147483647)
        self.autor.setValue(registro.get("autor_id", 1))
        self.autor.setEnabled(avaliacao is None)
        self.autor.setToolTip(
            "Identificador do autor da avaliação. Não é uma autenticação.")
        self.form.addRow("&Autor (ID) *", self.autor)
        self.estrelas = Estrelas()
        linha_estrelas = QHBoxLayout()
        linha_estrelas.addWidget(self.estrelas)
        self.valor_estrelas = QLabel()
        linha_estrelas.addWidget(self.valor_estrelas)
        linha_estrelas.addStretch()
        self.form.addRow("Estrelas", linha_estrelas)

        def mostrar_estrelas(nota):
            self.valor_estrelas.setText(f"{nota / 2:g} / 5".replace(".", ","))
        self.estrelas.nota_alterada.connect(mostrar_estrelas)
        mostrar_estrelas(registro.get("nota", 0))
        linha_nota = QHBoxLayout()
        self.nota = QDoubleSpinBox()
        self.nota.setRange(0, 10)
        self.nota.setDecimals(2)
        self.nota.setSingleStep(0.5)
        self.nota.setSuffix(" / 10")
        self.nota.setAccessibleName("Nota de zero a dez")
        self.nota.setValue(registro.get("nota", 0))
        self.estrelas.definir_nota(self.nota.value())
        self.estrelas.nota_alterada.connect(self.nota.setValue)
        self.nota.valueChanged.connect(self.estrelas.definir_nota)
        zerar = QPushButton("Zerar")
        zerar.clicked.connect(lambda: self.nota.setValue(0))
        linha_nota.addWidget(self.nota, 1)
        linha_nota.addWidget(zerar)
        rotulo_nota = QLabel("&Nota *")
        rotulo_nota.setBuddy(self.nota)
        self.form.addRow(rotulo_nota, linha_nota)
        self.comentario = QPlainTextEdit(registro.get("comentario", ""))
        self.comentario.setPlaceholderText(
            "O que você achou do jogo? (opcional)")
        self.comentario.setMinimumHeight(140)
        self.form.addRow("&Comentário", self.comentario)

    def dados(self):
        self.nota.interpretText()
        self.autor.interpretText()
        dados = {"nota": self.nota.value(
        ), "comentario": self.comentario.toPlainText().strip()}
        if self.avaliacao is None:
            dados["autor_id"] = self.autor.value()
        # Metadados omitidos: a API preserva os existentes durante a edição.
        return dados
