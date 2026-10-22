"""Formulários com validação local e salvamento HTTP assíncrono."""

import json
from datetime import datetime
from urllib.parse import urlparse

from PySide6.QtCore import QSettings, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QImageReader
from PySide6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout, QHBoxLayout,
    QFileDialog, QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QScrollArea, QSpinBox, QVBoxLayout, QWidget,
)

from cliente.telas.estrelas import Estrelas, nota_em_meias_estrelas
from cliente.telas.avisos import AvisoErro


class Formulario(QDialog):
    salvo = Signal(object)

    def __init__(self, titulo, executor, salvar, parent=None, *, moderno=False,
                 texto_salvar="Salvar"):
        super().__init__(parent)
        self.executor = executor
        self.salvar = salvar
        self._salvando = False
        self._texto_salvar = texto_salvar
        self.setWindowTitle(titulo)
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumWidth(480)
        self.botao_fechar = None
        if moderno:
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setObjectName("dialogo_formulario")
            externo = QVBoxLayout(self)
            externo.setContentsMargins(16, 16, 16, 16)
            painel = QFrame()
            painel.setObjectName("popup_formulario")
            sombra = QGraphicsDropShadowEffect(painel)
            sombra.setBlurRadius(28)
            sombra.setOffset(0, 6)
            sombra.setColor(QColor(0, 0, 0, 110))
            painel.setGraphicsEffect(sombra)
            externo.addWidget(painel)
            self.layout_principal = QVBoxLayout(painel)
        else:
            self.layout_principal = QVBoxLayout(self)
        self.layout_principal.setContentsMargins(24, 24, 24, 24)
        self.layout_principal.setSpacing(16)
        cabecalho = QLabel(titulo)
        cabecalho.setObjectName("popup_legenda" if moderno else "secao")
        if moderno:
            linha_cabecalho = QHBoxLayout()
            linha_cabecalho.addWidget(cabecalho, 1)
            self.botao_fechar = QPushButton("×")
            self.botao_fechar.setObjectName("fechar_popup")
            self.botao_fechar.setFixedSize(32, 32)
            self.botao_fechar.setAutoDefault(False)
            self.botao_fechar.setAccessibleName("Fechar sem salvar")
            self.botao_fechar.setToolTip("Fechar sem salvar (Esc)")
            self.botao_fechar.clicked.connect(self.reject)
            linha_cabecalho.addWidget(self.botao_fechar)
            self.layout_principal.addLayout(linha_cabecalho)
        else:
            self.layout_principal.addWidget(cabecalho)
        self.campos = QWidget()
        self.form = QFormLayout(self.campos)
        self.form.setContentsMargins(0, 0, 0, 0)
        self.form.setSpacing(12)
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        if moderno:
            self.scroll_campos = QScrollArea()
            self.scroll_campos.setObjectName("rolagem_formulario")
            self.campos.setObjectName("campos_formulario")
            self.scroll_campos.setWidgetResizable(True)
            self.scroll_campos.setFrameShape(QFrame.Shape.NoFrame)
            self.scroll_campos.setMinimumHeight(200)
            self.scroll_campos.setWidget(self.campos)
            self.layout_principal.addWidget(self.scroll_campos, 1)
        else:
            self.layout_principal.addWidget(self.campos)
        self.erro = AvisoErro(compacto=True)
        self.erro.hide()
        self.layout_principal.addWidget(self.erro)
        self.botoes = QDialogButtonBox()
        self.botao_salvar = self.botoes.addButton(
            texto_salvar, QDialogButtonBox.ButtonRole.AcceptRole)
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
        if self.botao_fechar is not None:
            self.botao_fechar.setEnabled(False)
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
        if self.botao_fechar is not None:
            self.botao_fechar.setEnabled(True)
        self.botao_salvar.setText(self._texto_salvar)
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
        super().__init__("EDITAR JOGO" if jogo else "NOVO JOGO", executor, salvar,
                         parent, moderno=True,
                         texto_salvar="Salvar alterações" if jogo else "Adicionar jogo")
        self.setWindowTitle("Editar jogo" if jogo else "Adicionar jogo")
        self.setMinimumWidth(580)
        self.setMaximumHeight(max(420, self.screen().availableGeometry().height() - 40))
        self.resize(640, min(740, self.maximumHeight()))
        titulo = QLabel(jogo["nome"] if jogo else "Adicionar jogo")
        titulo.setTextFormat(Qt.TextFormat.PlainText)
        titulo.setWordWrap(True)
        titulo.setMaximumHeight(86)
        titulo.setObjectName("popup_titulo")
        self.layout_principal.insertWidget(1, titulo)
        self.form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.form.setVerticalSpacing(12)
        self.form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
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
        self.descricao.setFixedHeight(112)
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
        self.capa_local.setMinimumWidth(100)
        self.capa_local.setPlaceholderText("Nenhuma imagem selecionada")
        self.botao_imagem = QPushButton("Escolher imagem…")
        self.botao_imagem.setAutoDefault(False)
        self.botao_imagem.clicked.connect(self.escolher_imagem)
        self.botao_remover_imagem = QPushButton("Remover")
        self.botao_remover_imagem.setAutoDefault(False)
        self.botao_remover_imagem.clicked.connect(self.remover_imagem)
        arquivo = QHBoxLayout()
        arquivo.addWidget(self.capa_local, 1)
        arquivo.addWidget(self.botao_imagem)
        arquivo.addWidget(self.botao_remover_imagem)
        self.capa_url.textChanged.connect(self._link_alterado)
        self.form.addRow("&Nome *", self.nome)
        linha_dados = QHBoxLayout()
        linha_dados.setSpacing(12)
        for texto, campo, proporcao in (("&Gênero *", self.genero, 2),
                                        ("&Plataforma *", self.plataforma, 2),
                                        ("&Ano *", self.ano, 1)):
            grupo = QWidget()
            coluna = QVBoxLayout(grupo)
            coluna.setContentsMargins(0, 0, 0, 0)
            coluna.setSpacing(6)
            legenda = QLabel(texto)
            legenda.setBuddy(campo)
            coluna.addWidget(legenda)
            coluna.addWidget(campo, 0, Qt.AlignmentFlag.AlignBottom)
            linha_dados.addWidget(grupo, proporcao)
        self.form.addRow(linha_dados)

        capa = QFrame()
        capa.setObjectName("painel_capa")
        capa_layout = QVBoxLayout(capa)
        capa_layout.setContentsMargins(14, 14, 14, 14)
        capa_layout.setSpacing(10)
        legenda_capa = QLabel("CAPA DO JOGO (OPCIONAL)")
        legenda_capa.setObjectName("popup_legenda")
        capa_layout.addWidget(legenda_capa)
        capa_layout.addLayout(arquivo)
        legenda_link = QLabel("Ou use um &link de imagem")
        legenda_link.setBuddy(self.capa_url)
        legenda_link.setObjectName("subtitulo")
        capa_layout.addWidget(legenda_link)
        capa_layout.addWidget(self.capa_url)
        self.form.addRow(capa)
        self.form.addRow("&Descrição (opcional)", self.descricao)

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
    def __init__(self, executor, salvar, avaliacao=None, parent=None, *, nome_jogo=""):
        super().__init__("EDITAR AVALIAÇÃO" if avaliacao else "NOVA AVALIAÇÃO",
                         executor, salvar, parent, moderno=True,
                         texto_salvar="Salvar alterações" if avaliacao else "Publicar avaliação")
        self.avaliacao = avaliacao
        self.setWindowTitle("Editar avaliação" if avaliacao else "Avaliar jogo")
        self.setMinimumWidth(540)
        self.setMaximumHeight(max(420, self.screen().availableGeometry().height() - 40))
        self.resize(580, min(660, self.maximumHeight()))
        self.nome_jogo = QLabel(nome_jogo or "Como foi sua experiência?")
        self.nome_jogo.setTextFormat(Qt.TextFormat.PlainText)
        self.nome_jogo.setWordWrap(True)
        self.nome_jogo.setObjectName("popup_titulo")
        self.nome_jogo.setMaximumHeight(86)
        self.nome_jogo.setToolTip(nome_jogo)
        self.layout_principal.insertWidget(1, self.nome_jogo)
        self.form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.form.setVerticalSpacing(10)
        self.form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        registro = avaliacao or {}
        self._nota_original = float(registro.get("nota", 0))

        self.estrelas = Estrelas()
        self.nota = QDoubleSpinBox()
        self.nota.setRange(0, 10)
        self.nota.setDecimals(0 if self._nota_original.is_integer() else 2)
        self.nota.setSingleStep(1)
        self.nota.setSuffix(" / 10")
        self.nota.setFixedWidth(144)
        self.nota.setObjectName("nota_popup")
        self.nota.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.nota.setAccessibleName("Nota de zero a dez")
        self.nota.setValue(registro.get("nota", 0))
        self.estrelas.definir_nota(self.nota.value())
        self.estrelas.nota_alterada.connect(self.nota.setValue)
        self.nota.valueChanged.connect(self._sincronizar_nota)
        self.valor_estrelas = QLabel()
        self.valor_estrelas.setObjectName("subtitulo")

        def mostrar_estrelas(nota):
            self.valor_estrelas.setText(f"{nota_em_meias_estrelas(nota) / 2:g} / 5".replace(".", ","))
        self.estrelas.nota_alterada.connect(mostrar_estrelas)
        mostrar_estrelas(self.nota.value())

        nota_card = QFrame()
        nota_card.setObjectName("painel_nota")
        nota_layout = QVBoxLayout(nota_card)
        nota_layout.setContentsMargins(16, 12, 16, 14)
        nota_layout.setSpacing(6)
        titulo_nota = QHBoxLayout()
        legenda_nota = QLabel("SUA NOTA")
        legenda_nota.setObjectName("popup_legenda")
        titulo_nota.addWidget(legenda_nota)
        titulo_nota.addStretch()
        zerar = QPushButton("Zerar")
        zerar.setObjectName("acao_discreta")
        zerar.setAutoDefault(False)
        zerar.clicked.connect(lambda: self.nota.setValue(0))
        titulo_nota.addWidget(zerar)
        nota_layout.addLayout(titulo_nota)
        linha_nota = QHBoxLayout()
        linha_nota.setSpacing(16)
        linha_nota.addWidget(self.estrelas, 0, Qt.AlignmentFlag.AlignVCenter)
        linha_nota.addStretch()
        linha_nota.addWidget(self.nota, 0, Qt.AlignmentFlag.AlignVCenter)
        nota_layout.addLayout(linha_nota)
        nota_layout.addWidget(self.valor_estrelas)
        self.form.addRow(nota_card)

        self.comentario = QPlainTextEdit(registro.get("comentario", ""))
        self.comentario.setPlaceholderText("O que marcou sua experiência com este jogo?")
        self.comentario.setFixedHeight(112)
        self.comentario.setAccessibleName("Comentário da avaliação, opcional")
        self.form.addRow("&Comentário (opcional)", self.comentario)

        self.autor = QSpinBox()
        self.autor.setRange(1, 2147483647)
        self.autor.setValue(registro.get("autor_id", 1))
        self.autor.setEnabled(avaliacao is None)
        self.autor.setFixedWidth(100)
        self.autor.setToolTip("Identificador local do autor. Não é uma autenticação.")
        self.autor.setAccessibleName("Identificação local do autor")
        linha_autor = QHBoxLayout()
        linha_autor.setSpacing(12)
        linha_autor.addWidget(self.autor)
        explicacao_autor = QLabel("Identificação local da avaliação")
        explicacao_autor.setObjectName("subtitulo")
        explicacao_autor.setWordWrap(True)
        linha_autor.addWidget(explicacao_autor, 1)
        rotulo_autor = QLabel("&Autor")
        rotulo_autor.setBuddy(self.autor)
        self.form.addRow(rotulo_autor, linha_autor)

        self.opcoes_metadados = QPushButton()
        self.opcoes_metadados.setObjectName("opcoes_avaliacao")
        self.opcoes_metadados.setCheckable(True)
        self.opcoes_metadados.setAutoDefault(False)
        self.opcoes_metadados.setAccessibleName("Exibir ou ocultar opções adicionais")
        self.form.addRow(self.opcoes_metadados)
        self.area_metadados = QWidget()
        metadados_layout = QVBoxLayout(self.area_metadados)
        metadados_layout.setContentsMargins(0, 0, 0, 0)
        metadados_layout.setSpacing(8)
        metadados_layout.addWidget(QLabel("Metadados (objeto JSON opcional)"))
        self.metadados = QPlainTextEdit(json.dumps(registro.get("metadados", {}), ensure_ascii=False))
        self.metadados.setPlaceholderText('{"plataforma": "PC"}')
        self.metadados.setFixedHeight(75)
        self.metadados.setAccessibleName("Metadados opcionais em JSON")
        metadados_layout.addWidget(self.metadados)
        self.form.addRow(self.area_metadados)
        self.opcoes_metadados.toggled.connect(self._alternar_metadados)
        self._alternar_metadados(False)
        self.opcoes_metadados.setChecked(bool(registro.get("metadados")))
        self.setTabOrder(self.estrelas, self.nota)
        self.setTabOrder(self.nota, self.comentario)
        self.setTabOrder(self.comentario, self.autor)
        self.setTabOrder(self.autor, self.opcoes_metadados)

    def _alternar_metadados(self, expandido):
        self.area_metadados.setVisible(expandido)
        self.opcoes_metadados.setText(
            "▾ Opções adicionais" if expandido else "▸ Opções adicionais")

    def _sincronizar_nota(self, nota):
        # Uma edição de comentário não deve arredondar uma nota antiga já salva.
        arredondada = nota_em_meias_estrelas(nota)
        if nota != self._nota_original and nota != arredondada:
            self.nota.setValue(arredondada)
            return
        self.estrelas.definir_nota(nota)

    def dados(self):
        self.nota.interpretText()
        self.autor.interpretText()
        dados = {"nota": self.nota.value(
        ), "comentario": self.comentario.toPlainText().strip()}
        if self.avaliacao is None:
            dados["autor_id"] = self.autor.value()
        try:
            metadados = json.loads(self.metadados.toPlainText().strip() or "{}")
            if not isinstance(metadados, dict):
                raise ValueError()
            json.dumps(metadados, allow_nan=False)
        except (ValueError, TypeError):
            self.opcoes_metadados.setChecked(True)
            self.metadados.setFocus()
            QTimer.singleShot(0, self, lambda: self.scroll_campos.ensureWidgetVisible(self.metadados))
            raise ValueError("Os metadados devem ser um objeto JSON válido, sem números não finitos.")
        dados["metadados"] = metadados
        return dados
