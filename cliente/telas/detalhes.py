"""Detalhes do jogo e avaliações com ações junto de cada registro."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog, QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QMenu,
    QPushButton, QScrollArea, QStackedWidget, QVBoxLayout, QWidget,
)

from cliente.telas.estrelas import Estrelas


def texto(conteudo="", estilo=None):
    label = QLabel(conteudo)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    if estilo:
        label.setObjectName(estilo)
    return label


def estrelas_leitura(nota, parent=None):
    estrelas = Estrelas(parent)
    estrelas.definir_nota(nota)
    estrelas.setEnabled(False)
    estrelas.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    estrelas.setCursor(Qt.CursorShape.ArrowCursor)
    estrelas.setToolTip(f"Nota {nota:g} de 10".replace(".", ","))
    return estrelas


class CartaoAvaliacao(QFrame):
    editar = Signal(int)
    excluir = Signal(int)

    def __init__(self, avaliacao, autor, parent=None):
        super().__init__(parent)
        self.avaliacao_id = avaliacao["id"]
        self.setObjectName("cartao_avaliacao")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)
        self.autor = texto(autor, "autor_avaliacao")
        layout.addWidget(self.autor)
        linha_nota = QHBoxLayout()
        linha_nota.setSpacing(14)
        self.estrelas = estrelas_leitura(avaliacao["nota"], self)
        linha_nota.addWidget(self.estrelas)
        linha_nota.addWidget(texto(f"{avaliacao['nota']:g} / 10".replace(".", ","), "subtitulo"))
        linha_nota.addStretch()
        layout.addLayout(linha_nota)
        self.comentario = texto(avaliacao.get("comentario") or "Sem comentário.")
        self.comentario.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.comentario.setAccessibleName("Comentário da avaliação")
        layout.addWidget(self.comentario)
        autor_id = avaliacao.get("autor_id")
        identificado = type(autor_id) is int and autor_id > 0
        self.aviso = texto("Avaliação antiga sem autor identificado. Edição e exclusão indisponíveis.", "subtitulo")
        self.aviso.setVisible(not identificado)
        layout.addWidget(self.aviso)
        acoes = QHBoxLayout()
        acoes.addStretch()
        self.botao_editar = QPushButton("Editar")
        self.botao_editar.setAccessibleName(f"Editar avaliação de {autor}")
        self.botao_editar.setEnabled(identificado)
        self.botao_editar.clicked.connect(lambda: self.editar.emit(self.avaliacao_id))
        self.botao_excluir = QPushButton("Excluir")
        self.botao_excluir.setObjectName("perigo")
        self.botao_excluir.setAccessibleName(f"Excluir avaliação de {autor}")
        self.botao_excluir.setEnabled(identificado)
        self.botao_excluir.clicked.connect(lambda: self.excluir.emit(self.avaliacao_id))
        for botao in (self.botao_editar, self.botao_excluir):
            botao.setToolTip("Apenas o autor ou um moderador pode alterar a avaliação.")
            acoes.addWidget(botao)
        layout.addLayout(acoes)


class DialogoDetalhes(QDialog):
    editar_avaliacao = Signal(int)
    excluir_avaliacao = Signal(int)

    def __init__(self, ocupado, parent=None):
        super().__init__(parent)
        self._ocupado = ocupado
        self.cartoes = {}
        self.setWindowTitle("Detalhes do jogo")
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("dialogo_formulario")
        self.setMinimumSize(560, 440)
        self.setMaximumHeight(max(440, self.screen().availableGeometry().height() - 40))
        self.resize(900, min(800, self.maximumHeight()))
        externo = QVBoxLayout(self)
        externo.setContentsMargins(14, 14, 14, 14)
        painel = QFrame()
        painel.setObjectName("popup_formulario")
        sombra = QGraphicsDropShadowEffect(painel)
        sombra.setBlurRadius(24)
        sombra.setOffset(0, 5)
        sombra.setColor(QColor(0, 0, 0, 110))
        painel.setGraphicsEffect(sombra)
        externo.addWidget(painel)
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(14)
        topo = QHBoxLayout()
        topo.addWidget(texto("DETALHES DO JOGO", "popup_legenda"))
        topo.addStretch()
        self.fechar = QPushButton("×")
        self.fechar.setObjectName("fechar_popup")
        self.fechar.setFixedSize(32, 32)
        self.fechar.setAccessibleName("Fechar detalhes do jogo")
        self.fechar.setToolTip("Fechar (Esc)")
        self.fechar.clicked.connect(self.reject)
        topo.addWidget(self.fechar)
        layout.addLayout(topo)
        self.paginas = QStackedWidget()
        vazio = QWidget()
        vazio_layout = QVBoxLayout(vazio)
        self.mensagem_vazia = texto("Escolha um jogo.", "secao")
        self.mensagem_vazia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vazio_layout.addWidget(self.mensagem_vazia)
        self.paginas.addWidget(vazio)
        self.scroll = QScrollArea()
        self.scroll.setObjectName("rolagem_formulario")
        self.scroll.setWidgetResizable(True)
        conteudo = QWidget()
        conteudo.setObjectName("campos_formulario")
        corpo = QVBoxLayout(conteudo)
        corpo.setContentsMargins(0, 0, 8, 0)
        corpo.setSpacing(18)
        cabecalho = QHBoxLayout()
        cabecalho.setSpacing(22)
        self.capa = QLabel()
        self.capa.setObjectName("capa_detalhes")
        self.capa.setFixedSize(140, 196)
        self.capa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capa.setAccessibleName("Capa do jogo")
        cabecalho.addWidget(self.capa, 0, Qt.AlignmentFlag.AlignTop)
        resumo = QVBoxLayout()
        resumo.setSpacing(8)
        resumo.setAlignment(Qt.AlignmentFlag.AlignTop)
        linha_titulo = QHBoxLayout()
        self.titulo = texto(estilo="popup_titulo")
        linha_titulo.addWidget(self.titulo, 1)
        self.botao_menu = QPushButton("⋯")
        self.botao_menu.setObjectName("menu_jogo")
        self.botao_menu.setFixedSize(38, 34)
        self.botao_menu.setAccessibleName("Mais ações do jogo")
        self.botao_menu.setToolTip("Editar, trocar capa ou excluir jogo")
        menu = QMenu(self.botao_menu)
        self.acao_editar = menu.addAction("Editar jogo")
        self.acao_capa = menu.addAction("Trocar capa")
        menu.addSeparator()
        self.acao_excluir = menu.addAction("Excluir jogo e avaliações…")
        self.botao_menu.setMenu(menu)
        linha_titulo.addWidget(self.botao_menu, 0, Qt.AlignmentFlag.AlignTop)
        resumo.addLayout(linha_titulo)
        self.informacoes = texto(estilo="subtitulo")
        resumo.addWidget(self.informacoes)
        self.estrelas = estrelas_leitura(0, self)
        resumo.addWidget(self.estrelas)
        self.nota_estrelas = texto(estilo="nota_detalhes")
        resumo.addWidget(self.nota_estrelas)
        linha_media = QHBoxLayout()
        linha_media.setSpacing(16)
        self.media = texto(estilo="subtitulo")
        self.quantidade = texto(estilo="subtitulo")
        linha_media.addWidget(self.media)
        linha_media.addWidget(self.quantidade)
        linha_media.addStretch()
        resumo.addLayout(linha_media)
        self.nova_avaliacao = QPushButton("Avaliar jogo")
        self.nova_avaliacao.setObjectName("primario")
        resumo.addWidget(self.nova_avaliacao, 0, Qt.AlignmentFlag.AlignLeft)
        cabecalho.addLayout(resumo, 1)
        corpo.addLayout(cabecalho)
        self.sucesso = texto(estilo="sucesso")
        self.sucesso.hide()
        corpo.addWidget(self.sucesso)
        corpo.addWidget(texto("Sobre o jogo", "secao"))
        self.descricao = texto()
        self.descricao.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        corpo.addWidget(self.descricao)
        corpo.addWidget(texto("Avaliações", "secao"))
        self.sem_avaliacoes = texto("Este jogo ainda não tem avaliações. Compartilhe sua opinião!", "estado_vazio")
        corpo.addWidget(self.sem_avaliacoes)
        self.avaliacoes_layout = QVBoxLayout()
        self.avaliacoes_layout.setSpacing(12)
        corpo.addLayout(self.avaliacoes_layout)
        corpo.addStretch()
        self.scroll.setWidget(conteudo)
        self.paginas.addWidget(self.scroll)
        layout.addWidget(self.paginas, 1)
        for botao in self.findChildren(QPushButton):
            botao.setAutoDefault(False)

    def definir_capa(self, imagem, nome):
        if imagem.isNull():
            self.capa.setPixmap(imagem)
            self.capa.setText(nome[:1].upper())
        else:
            self.capa.setText("")
            redimensionada = imagem.scaled(self.capa.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                          Qt.TransformationMode.SmoothTransformation)
            self.capa.setPixmap(redimensionada.copy(
                (redimensionada.width() - self.capa.width()) // 2,
                (redimensionada.height() - self.capa.height()) // 2,
                self.capa.width(), self.capa.height()))

    def preencher_avaliacoes(self, avaliacoes, nome_autor):
        while self.avaliacoes_layout.count():
            widget = self.avaliacoes_layout.takeAt(0).widget()
            if widget:
                widget.hide()
                widget.deleteLater()
        self.cartoes = {}
        self.sem_avaliacoes.setVisible(not avaliacoes)
        for avaliacao in avaliacoes:
            cartao = CartaoAvaliacao(avaliacao, nome_autor(avaliacao.get("autor_id")), self)
            cartao.editar.connect(self.editar_avaliacao)
            cartao.excluir.connect(self.excluir_avaliacao)
            self.cartoes[avaliacao["id"]] = cartao
            self.avaliacoes_layout.addWidget(cartao)

    def ocupar(self, ocupado):
        self.paginas.setEnabled(not ocupado)
        self.fechar.setEnabled(not ocupado)

    def reject(self):
        if not self._ocupado():
            super().reject()

    def closeEvent(self, evento):
        if self._ocupado():
            evento.ignore()
        else:
            super().closeEvent(evento)
