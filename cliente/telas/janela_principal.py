"""Biblioteca, detalhes e avaliações; toda persistência passa pelo APIClient."""

from pathlib import Path

from PySide6.QtCore import QPoint, QSettings, QSize, QSignalBlocker, QTimer, Qt
from PySide6.QtGui import QIcon, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QFileDialog, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu, QMessageBox,
    QProgressBar, QPushButton, QSplitter, QStackedWidget, QToolButton, QVBoxLayout, QWidget, QSpinBox,
)

from cliente.services.tarefas import ExecutorHTTP
from cliente.telas.avisos import AvisoErro
from cliente.telas.cards import AvaliacoesDelegate, CardsDelegate, GradeJogos
from cliente.telas.detalhes import DialogoDetalhes
from cliente.telas.formularios import FormularioAvaliacao, FormularioJogo
from cliente.telas.paginacao import Paginacao
from cliente.telas.perfis import DialogoPerfil, PerfisLocais


def rotulo(texto="", estilo=None):
    label = QLabel(texto)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    if estilo:
        label.setObjectName(estilo)
    return label


class JanelaPrincipal(QMainWindow):
    def __init__(self, api, parent=None, *, carregar=True):
        super().__init__(parent)
        self.api = api
        self.executor = ExecutorHTTP(self)
        self._jogos = []
        self._avaliacoes = []
        self._minhas = []
        self._aba_minhas = False
        self.jogo = None
        self.dialogo = None
        self._avaliar_pendente = None
        self._avaliacao_id_selecionada = None
        self.setWindowTitle("TechGames")
        self.resize(1440, 900)
        self.preferencias = QSettings("TechForce", "TechGames")
        self.perfis = PerfisLocais(self.preferencias)
        self.perfil = self.perfis.ativo()
        if self.perfil:
            self.api.ator_id = self.perfil["id"]
        self.setMinimumSize(900, 650)
        self._montar_tela()
        self.executor.ocupado_alterado.connect(self._ocupacao)
        self.statusBar().showMessage(f"Servidor: {self.api.base_url}")
        if carregar:
            QTimer.singleShot(0, self.atualizar)
            if not self.perfil:
                QTimer.singleShot(0, self.abrir_perfil)

    def _montar_tela(self):
        central = QWidget()
        central.setObjectName("aplicacao")
        estrutura = QVBoxLayout(central)
        estrutura.setContentsMargins(0, 0, 0, 0)
        estrutura.setSpacing(0)

        self.barra_superior = QFrame()
        self.barra_superior.setObjectName("barra_superior")
        cabecalho = QGridLayout(self.barra_superior)
        cabecalho.setContentsMargins(20, 14, 20, 14)
        cabecalho.setSpacing(10)
        cabecalho.setColumnStretch(0, 1)
        cabecalho.setColumnStretch(2, 1)
        identidade_widget = QWidget()
        identidade = QHBoxLayout(identidade_widget)
        identidade.setContentsMargins(0, 0, 0, 0)
        identidade.setSpacing(9)
        cabecalho.addWidget(identidade_widget, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.navegacao = QWidget()
        navegacao = QHBoxLayout(self.navegacao)
        navegacao.setContentsMargins(0, 0, 0, 0)
        navegacao.setSpacing(8)
        cabecalho.addWidget(self.navegacao, 0, 1, Qt.AlignmentFlag.AlignCenter)
        acoes_cabecalho = QWidget()
        acoes = QHBoxLayout(acoes_cabecalho)
        acoes.setContentsMargins(0, 0, 0, 0)
        acoes.setSpacing(10)
        cabecalho.addWidget(acoes_cabecalho, 0, 2)
        pasta_imagens = Path(__file__).resolve().parents[2] / "imagem"
        caminho_logo = next((pasta_imagens / nome for nome in
                             ("logo.svg", "logo techgamer.svg.svg", "logo.png",
                              "logo.webp", "logo.jpg", "logo.jpeg")
                             if (pasta_imagens / nome).is_file()), None)
        imagem_logo = QPixmap(str(caminho_logo)) if caminho_logo else QPixmap()
        self.botao_inicio_logo = QPushButton()
        self.botao_inicio_logo.setObjectName("logo_inicio")
        self.botao_inicio_logo.setFixedSize(214, 56)
        self.botao_inicio_logo.setToolTip("Voltar ao início")
        self.botao_inicio_logo.setAccessibleName("TechGamer — voltar ao início")
        self.botao_inicio_logo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.botao_inicio_logo.clicked.connect(self._abrir_biblioteca)
        identidade.addWidget(self.botao_inicio_logo)
        marca_layout = QHBoxLayout(self.botao_inicio_logo)
        marca_layout.setContentsMargins(0, 0, 0, 0)
        marca_layout.setSpacing(9)
        if not imagem_logo.isNull():
            self.logo = QLabel()
            self.logo.setAccessibleName("Logo TechGamer")
            self.logo.setFixedSize(210, 54)
            self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo.setPixmap(imagem_logo.scaled(
                self.logo.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
            self.logo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            marca_layout.addWidget(self.logo)
        else:
            simbolo = rotulo("TG", "simbolo_marca")
            simbolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            simbolo.setFixedSize(36, 36)
            simbolo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            marca_layout.addWidget(simbolo)
            marca = rotulo("TECHGAMES", "marca")
            marca.setWordWrap(False)
            marca.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            marca_layout.addWidget(marca)
        self.botao_biblioteca = QPushButton("INÍCIO")
        self.botao_biblioteca.setObjectName("navegacao")
        self.botao_biblioteca.setCheckable(True)
        self.botao_biblioteca.setChecked(True)
        self.botao_biblioteca.setToolTip("Mostrar todos os jogos")
        self.botao_biblioteca.clicked.connect(self._abrir_biblioteca)
        navegacao.addWidget(self.botao_biblioteca)
        self.botao_minhas = QPushButton("MINHAS AVALIAÇÕES")
        self.botao_minhas.setObjectName("navegacao")
        self.botao_minhas.setCheckable(True)
        self.botao_minhas.clicked.connect(self.abrir_minhas_avaliacoes)
        navegacao.addWidget(self.botao_minhas)
        self.botao_atualizar = QPushButton("ATUALIZAR")
        self.botao_atualizar.setObjectName("navegacao")
        self.botao_atualizar.setToolTip("Consultar novamente os dados no servidor (F5)")
        self.botao_atualizar.setShortcut("F5")
        self.botao_atualizar.clicked.connect(self.atualizar)
        navegacao.addWidget(self.botao_atualizar)
        estrutura.addWidget(self.barra_superior)

        self.conexao = rotulo("Conectando…", "subtitulo")
        self.statusBar().addPermanentWidget(self.conexao)
        identificacao = QWidget()
        identificacao_layout = QHBoxLayout(identificacao)
        identificacao_layout.setContentsMargins(12, 0, 0, 0)
        identificacao_layout.setSpacing(8)
        identificacao_layout.addWidget(rotulo("ID local", "subtitulo"))
        self.ator_local = QSpinBox()
        self.ator_local.setObjectName("id_status")
        self.ator_local.setFixedHeight(28)
        self.ator_local.setFixedWidth(88)
        self.ator_local.setRange(1, 2147483647)
        self.ator_local.setValue(self.api.ator_id or 1)
        self.ator_local.setToolTip("Identificação fictícia para avaliações. Moderador de demonstração: 99.")
        self.ator_local.setAccessibleName("Identificação local para editar e excluir avaliações")
        self.ator_local.valueChanged.connect(lambda valor: setattr(self.api, "ator_id", valor))
        self.ator_local.valueChanged.connect(self._identificacao_alterada)
        identificacao_layout.addWidget(self.ator_local)
        self.statusBar().addPermanentWidget(identificacao)
        self.nome_perfil = rotulo(estilo="subtitulo")
        self.statusBar().addPermanentWidget(self.nome_perfil)

        conteudo = QWidget()
        conteudo.setObjectName("conteudo")
        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(20, 24, 20, 16)
        layout.setSpacing(12)
        self.sucesso = rotulo()
        self.sucesso.hide()
        layout.addWidget(self.sucesso)
        self.erro = AvisoErro()
        self.erro.hide()
        layout.addWidget(self.erro)
        self.progresso = QProgressBar()
        self.progresso.setRange(0, 0)
        self.progresso.setTextVisible(False)
        self.progresso.hide()
        layout.addWidget(self.progresso)

        self.divisao = QSplitter(Qt.Orientation.Vertical)
        self.conteudo_paginas = QStackedWidget()
        biblioteca = QWidget()
        biblioteca.setObjectName("biblioteca")
        esquerda = QVBoxLayout(biblioteca)
        esquerda.setContentsMargins(0, 8, 0, 0)
        esquerda.setSpacing(14)
        titulo_colecao = QHBoxLayout()
        titulo_colecao.setSpacing(12)
        titulo_colecao.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        titulo_colecao.addWidget(rotulo("Jogos", "secao"))
        titulo_colecao.addStretch()
        self.busca = QLineEdit()
        self.busca.setObjectName("busca_jogos")
        self.busca.setPlaceholderText("PROCURAR JOGO")
        self.busca.setToolTip("Buscar por nome, gênero ou plataforma")
        self.busca.setMinimumWidth(220)
        self.busca.setMaximumWidth(520)
        self.busca.setFixedHeight(46)
        svg_lupa = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#d4d7de" stroke-width="2"><circle cx="10" cy="10" r="6"/><path d="m14.5 14.5 6 6"/></svg>'
        try:
            svg_lupa = (pasta_imagens / "LUPA.svg").read_bytes().replace(
                b"<path ", b'<path fill="#d4d7de" ', 1)
        except OSError:
            pass
        imagem_lupa = QPixmap()
        imagem_lupa.loadFromData(svg_lupa, "SVG")
        self.acao_buscar = self.busca.addAction(
            QIcon(imagem_lupa), QLineEdit.ActionPosition.TrailingPosition)
        self.acao_buscar.setText("Procurar jogo")
        self.acao_buscar.setToolTip("Procurar jogo")
        self.acao_buscar.triggered.connect(lambda: (self.busca.setFocus(), self._filtrar()))
        for botao_lupa in self.busca.findChildren(QToolButton):
            botao_lupa.setIconSize(QSize(24, 24))
            botao_lupa.setAccessibleName("Procurar jogo")
        for botao in (self.botao_biblioteca, self.botao_minhas, self.botao_atualizar):
            botao.setFixedHeight(40)
        acoes.addWidget(self.busca, 1)
        self.botao_perfil = QPushButton()
        self.botao_perfil.setObjectName("avatar_perfil")
        self.botao_perfil.setCursor(Qt.CursorShape.PointingHandCursor)
        self.botao_perfil.clicked.connect(lambda: self.abrir_perfil() if not self.perfil else None)
        self.menu_perfil = QMenu(self.botao_perfil)
        self.menu_perfil.setMinimumWidth(190)
        self.acao_nome_perfil = self.menu_perfil.addAction("")
        self.acao_nome_perfil.setEnabled(False)
        self.menu_perfil.addSeparator()
        self.menu_perfil.addAction("Trocar perfil", self.abrir_perfil)
        self.acao_sair_perfil = self.menu_perfil.addAction("Sair", self.sair_perfil)
        acoes.addWidget(self.botao_perfil)
        self.busca.setClearButtonEnabled(True)
        self.busca.setAccessibleName("Buscar jogos")
        self._busca_timer = QTimer(self)
        self._busca_timer.setSingleShot(True)
        self._busca_timer.setInterval(300)
        self._busca_timer.timeout.connect(self._filtrar)
        self.busca.textChanged.connect(lambda: self._busca_timer.start())
        self.total_jogos = rotulo("Nenhum jogo carregado", "subtitulo")
        titulo_colecao.addWidget(self.total_jogos)
        self.botao_filtros = QPushButton("Filtros")
        self.botao_filtros.setObjectName("botao_filtros")
        self.botao_filtros.setFixedHeight(40)
        self.botao_filtros.setAccessibleName("Abrir filtros de jogos")
        self.botao_filtros.clicked.connect(self._abrir_filtros)
        titulo_colecao.addWidget(self.botao_filtros)
        esquerda.addLayout(titulo_colecao)
        self.painel_filtros = QFrame(self, Qt.WindowType.Popup)
        self.painel_filtros.setObjectName("painel_filtros")
        self.painel_filtros.setFixedWidth(340)
        painel_layout = QVBoxLayout(self.painel_filtros)
        painel_layout.setContentsMargins(18, 16, 18, 16)
        painel_layout.setSpacing(14)
        cabecalho_filtros = QHBoxLayout()
        cabecalho_filtros.addWidget(rotulo("Filtrar jogos", "secao"), 1)
        fechar_filtros = QPushButton("×")
        fechar_filtros.setObjectName("fechar_popup")
        fechar_filtros.setFixedSize(28, 28)
        fechar_filtros.setAccessibleName("Fechar filtros")
        fechar_filtros.clicked.connect(self.painel_filtros.hide)
        cabecalho_filtros.addWidget(fechar_filtros)
        painel_layout.addLayout(cabecalho_filtros)
        self._atalho_fechar_filtros = QShortcut("Esc", self.painel_filtros)
        self._atalho_fechar_filtros.activated.connect(self.painel_filtros.hide)
        filtros = QFormLayout()
        filtros.setSpacing(12)
        filtros.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.filtro_genero = QComboBox()
        self.filtro_plataforma = QComboBox()
        self.filtro_ano = QComboBox()
        for combo, nome in ((self.filtro_genero, "Gênero"),
                            (self.filtro_plataforma, "Plataforma"), (self.filtro_ano, "Ano")):
            combo.setAccessibleName("Filtrar por " + nome.lower())
            combo.addItem("Todos", "")
            combo.currentIndexChanged.connect(self._filtrar)
            filtros.addRow(nome, combo)
        self.ordenacao = QComboBox()
        self.ordenacao.setAccessibleName("Ordenar jogos")
        self.ordenacao.addItem("Ordem de cadastro", "cadastro")
        self.ordenacao.addItem("Nome: A–Z", "nome")
        self.ordenacao.addItem("Maior nota", "nota")
        self.ordenacao.addItem("Mais recentes", "ano")
        self.ordenacao.currentIndexChanged.connect(self._filtrar)
        filtros.addRow("Ordenar", self.ordenacao)
        painel_layout.addLayout(filtros)
        rodape_filtros = QHBoxLayout()
        self.limpar_filtros = QPushButton("Limpar filtros")
        self.limpar_filtros.clicked.connect(self._limpar_filtros)
        rodape_filtros.addWidget(self.limpar_filtros)
        rodape_filtros.addStretch()
        self.concluir_filtros = QPushButton("Pronto")
        self.concluir_filtros.setObjectName("primario")
        self.concluir_filtros.clicked.connect(self.painel_filtros.hide)
        rodape_filtros.addWidget(self.concluir_filtros)
        painel_layout.addLayout(rodape_filtros)
        self.lista = GradeJogos()
        self.lista.setViewMode(QListWidget.ViewMode.IconMode)
        self.lista.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.lista.setMovement(QListWidget.Movement.Static)
        self.lista.setSpacing(10)
        self.lista.setGridSize(QSize(188, 316))
        self.cards = CardsDelegate(self.lista)
        self.lista.setItemDelegate(self.cards)
        self.cards.falha_capa.connect(self._falha_capa)
        self.lista.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.lista.itemClicked.connect(self.abrir_avaliacoes_card)
        self.lista.itemActivated.connect(self.abrir_avaliacoes_card)
        self.lista.setAccessibleName("Jogos")
        esquerda.addWidget(self.lista, 1)
        self.sem_resultados = rotulo(
            "Sua coleção começa aqui. Adicione seu primeiro jogo.", "estado_vazio")
        self.sem_resultados.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sem_resultados.setMinimumHeight(90)
        esquerda.addWidget(self.sem_resultados, 1)
        self.paginacao = Paginacao(12)
        self.paginacao.alterada.connect(lambda _: self._preencher_biblioteca())
        esquerda.addWidget(self.paginacao)
        self.novo_jogo = QPushButton("+ Adicionar jogo")
        self.novo_jogo.setObjectName("primario")
        self.novo_jogo.setFixedHeight(40)
        self.novo_jogo.clicked.connect(self.adicionar_jogo)
        titulo_colecao.addWidget(self.novo_jogo)
        self.divisao.addWidget(biblioteca)

        self.janela_detalhes = DialogoDetalhes(lambda: self.executor.ocupado, self)
        self.paginas = self.janela_detalhes.paginas
        self.mensagem_vazia = self.janela_detalhes.mensagem_vazia
        self.titulo = self.janela_detalhes.titulo
        self.informacoes = self.janela_detalhes.informacoes
        self.descricao = self.janela_detalhes.descricao
        self.media = self.janela_detalhes.media
        self.quantidade = self.janela_detalhes.quantidade
        self.sucesso_detalhes = self.janela_detalhes.sucesso
        self.nova_avaliacao = self.janela_detalhes.nova_avaliacao
        self.nova_avaliacao.clicked.connect(self.adicionar_avaliacao)
        self.janela_detalhes.acao_capa.triggered.connect(self.escolher_capa)
        self.janela_detalhes.acao_editar.triggered.connect(self.abrir_edicao_jogo)
        self.janela_detalhes.acao_excluir.triggered.connect(self.remover_jogo)
        self.janela_detalhes.editar_avaliacao.connect(self.abrir_edicao_avaliacao)
        self.janela_detalhes.excluir_avaliacao.connect(self.remover_avaliacao)
        self.cards.capa_carregada.connect(lambda _: self._atualizar_capa_detalhes())
        self.divisao.setStretchFactor(0, 3)
        self.divisao.setStretchFactor(1, 1)
        self.divisao.setSizes([510, 310])
        self.conteudo_paginas.addWidget(self.divisao)
        self._montar_minhas_avaliacoes()
        layout.addWidget(self.conteudo_paginas, 1)
        estrutura.addWidget(conteudo, 1)
        self.setCentralWidget(central)
        self._atualizar_perfil_visual()

    def _montar_minhas_avaliacoes(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(12)
        titulo = QHBoxLayout()
        titulo.setSpacing(12)
        titulo.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        titulo.addWidget(rotulo("Minhas avaliações", "secao"))
        titulo.addStrut(40)
        titulo.addStretch()
        self.total_minhas = rotulo(estilo="subtitulo")
        titulo.addWidget(self.total_minhas)
        layout.addLayout(titulo)
        self.lista_minhas = QListWidget()
        self.lista_minhas.setAccessibleName("Avaliações do perfil local")
        self.lista_minhas.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.lista_minhas.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.delegate_minhas = AvaliacoesDelegate(self.lista_minhas)
        self.lista_minhas.setItemDelegate(self.delegate_minhas)
        self.delegate_minhas.falha_capa.connect(lambda _, erro: self.statusBar().showMessage(erro))
        self.lista_minhas.currentItemChanged.connect(self._selecionar_minha)
        self.lista_minhas.itemDoubleClicked.connect(lambda _: self.editar_minha_avaliacao())
        layout.addWidget(self.lista_minhas, 1)
        self.vazio_minhas = rotulo(estilo="estado_vazio")
        self.vazio_minhas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.vazio_minhas, 1)
        self.paginacao_minhas = Paginacao(6)
        self.paginacao_minhas.alterada.connect(lambda _: self._preencher_minhas())
        layout.addWidget(self.paginacao_minhas)
        botoes = QHBoxLayout()
        self.editar_minha = QPushButton("Editar avaliação")
        self.editar_minha.clicked.connect(self.editar_minha_avaliacao)
        self.excluir_minha = QPushButton("Excluir avaliação")
        self.excluir_minha.setObjectName("perigo")
        self.excluir_minha.clicked.connect(self.excluir_minha_avaliacao)
        botoes.addWidget(self.editar_minha)
        botoes.addWidget(self.excluir_minha)
        botoes.addStretch()
        layout.addLayout(botoes)
        self.conteudo_paginas.addWidget(pagina)
        self._preencher_minhas()

    def _atualizar_perfil_visual(self):
        conectado = self.perfil is not None
        self.botao_perfil.setText(self.perfil["nome"][:1].upper() if conectado else "Entrar")
        self.botao_perfil.setFixedSize(40 if conectado else 76, 40)
        self.botao_perfil.setProperty("conectado", conectado)
        self.botao_perfil.setMenu(self.menu_perfil if conectado else None)
        self.botao_perfil.setToolTip("Perfil de " + self.perfil["nome"] if conectado else "Entrar sem senha")
        self.botao_perfil.setAccessibleName("Abrir menu do perfil de " + self.perfil["nome"] if conectado else "Entrar com perfil local")
        self.acao_nome_perfil.setText(self.perfil["nome"].replace("&", "&&") if conectado else "")
        self.botao_perfil.style().unpolish(self.botao_perfil)
        self.botao_perfil.style().polish(self.botao_perfil)
        self.nome_perfil.setText("Perfil: " + self.perfil["nome"] if self.perfil else "Sem perfil")
        self.ator_local.setReadOnly(conectado or self.api.ator_id is None)
        self.ator_local.setSpecialValueText("—" if self.api.ator_id is None else "")
        if self.jogo is not None:
            self.janela_detalhes.preencher_avaliacoes(self._avaliacoes, self._nome_autor)

    def sair_perfil(self):
        if self.executor.ocupado or not self.perfil:
            return
        self.menu_perfil.hide()
        if self.dialogo is not None:
            try:
                if self.dialogo.isVisible():
                    self.dialogo.reject()
            except RuntimeError:
                pass
        self.perfis.sair()
        self.perfil = None
        self.api.ator_id = None
        with QSignalBlocker(self.ator_local):
            self.ator_local.setValue(1)
        self._minhas = []
        self._avaliacao_id_selecionada = None
        self._limpar_sucesso()
        self._atualizar_perfil_visual()
        self._preencher_minhas()
        self._abrir_biblioteca()

    def abrir_perfil(self):
        if self.executor.ocupado:
            QTimer.singleShot(100, self.abrir_perfil)
            return
        self.janela_detalhes.hide()
        dialogo = DialogoPerfil(self.perfis, self)
        self.dialogo_perfil = dialogo
        dialogo.accepted.connect(lambda: self._usar_perfil(dialogo.perfil))
        dialogo.finished.connect(lambda _: dialogo.deleteLater())
        dialogo.open()

    def _usar_perfil(self, perfil):
        self.perfil = dict(perfil)
        with QSignalBlocker(self.ator_local):
            self.ator_local.setValue(perfil["id"])
        self.api.ator_id = perfil["id"]
        self._minhas = []
        self.paginacao_minhas.pagina = 1
        self._atualizar_perfil_visual()
        self._preencher_minhas()
        if self._aba_minhas:
            self._carregar_minhas()

    def _identificacao_alterada(self, valor):
        # Mantém o seletor de demonstração compatível, sem misturar perfis.
        if self.perfil and self.perfil["id"] != valor:
            self.perfis.sair()
            self.perfil = None
        self._minhas = []
        self._atualizar_perfil_visual()
        self._preencher_minhas()

    def abrir_minhas_avaliacoes(self):
        if self.executor.ocupado:
            return
        self._aba_minhas = True
        self.botao_biblioteca.setChecked(False)
        self.botao_minhas.setChecked(True)
        self.conteudo_paginas.setCurrentIndex(1)
        self.janela_detalhes.hide()
        self._busca_timer.stop()
        with QSignalBlocker(self.busca):
            self.busca.clear()
        self.paginacao_minhas.pagina = 1
        self._minhas = []
        self._preencher_minhas()
        if not self.perfil:
            self.abrir_perfil()
        else:
            self._carregar_minhas()

    def _carregar_minhas(self):
        if not self.perfil or self.executor.ocupado:
            return
        autor_id = self.perfil["id"]
        selecionada = self._minha_selecionada()
        selecionar_id = selecionada["avaliacao"]["id"] if selecionada else None
        self.erro.hide()
        self.vazio_minhas.setText("Carregando suas avaliações…")

        def consultar():
            jogos = self.api.listar_jogos()
            resultado = []
            for jogo in jogos:
                for avaliacao in self.api.listar_avaliacoes(jogo["id"]):
                    if type(avaliacao.get("autor_id")) is int and avaliacao["autor_id"] == autor_id:
                        resultado.append({"jogo": jogo, "avaliacao": avaliacao})
            return sorted(resultado, key=lambda item: item["avaliacao"]["id"], reverse=True)

        def receber(itens):
            if self.perfil and self.perfil["id"] == autor_id:
                self._minhas = itens
                self._preencher_minhas(selecionar_id)
                self.conexao.setText("Servidor conectado")
                self.statusBar().showMessage("Suas avaliações foram atualizadas.")

        def falha(mensagem):
            self.vazio_minhas.setText("Não foi possível consultar suas avaliações. Use Atualizar para tentar novamente.")
            self._falha(mensagem)

        self.executor.executar(consultar, receber, falha)

    def _preencher_minhas(self, selecionar_id=None):
        termo = self.busca.text().strip().casefold()
        itens = [item for item in self._minhas if termo in (
            item["jogo"]["nome"] + " " + item["avaliacao"].get("comentario", "")).casefold()]
        if selecionar_id is not None:
            indice = next((i for i, item in enumerate(itens) if item["avaliacao"]["id"] == selecionar_id), None)
            if indice is not None:
                self.paginacao_minhas.pagina = indice // self.paginacao_minhas.por_pagina + 1
        self.paginacao_minhas.atualizar(len(itens))
        with QSignalBlocker(self.lista_minhas):
            self.lista_minhas.clear()
            selecionado = None
            for dados in self.paginacao_minhas.recortar(itens):
                visual = dict(dados)
                visual["capa_local"] = self.preferencias.value(f"capas/{dados['jogo']['id']}", "")
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole + 1, visual)
                item.setText(f"{dados['jogo']['nome']}: nota {dados['avaliacao']['nota']:g}. "
                             + (dados['avaliacao'].get('comentario') or 'Sem comentário.'))
                item.setToolTip(item.text())
                item.setSizeHint(QSize(480, 182))
                self.lista_minhas.addItem(item)
                if dados["avaliacao"]["id"] == selecionar_id:
                    selecionado = item
            if self.lista_minhas.count():
                self.lista_minhas.setCurrentItem(selecionado or self.lista_minhas.item(0))
        self.lista_minhas.setVisible(bool(itens))
        self.vazio_minhas.setVisible(not itens)
        self.vazio_minhas.setText("Entre com seu perfil para consultar suas avaliações." if not self.perfil else
                                 "Nenhuma avaliação encontrada para este perfil." if not termo else
                                 "Nenhuma avaliação corresponde à pesquisa.")
        self.total_minhas.setText(f"{len(itens)} avaliação(ões)")
        self._selecionar_minha()

    def _minha_selecionada(self):
        item = self.lista_minhas.currentItem()
        return item.data(Qt.ItemDataRole.UserRole + 1) if item else None

    def _selecionar_minha(self, *_):
        dados = self._minha_selecionada()
        habilitar = bool(dados and self.perfil and
                         dados["avaliacao"].get("autor_id") == self.perfil["id"]
                         and not self.executor.ocupado)
        self.editar_minha.setEnabled(habilitar)
        self.excluir_minha.setEnabled(habilitar)

    def editar_minha_avaliacao(self):
        dados = self._minha_selecionada()
        if not dados or not self.editar_minha.isEnabled():
            return
        avaliacao = dados["avaliacao"]
        self._abrir_formulario(FormularioAvaliacao(
            self.executor, lambda novos: self.api.editar_avaliacao(avaliacao["id"], novos),
            avaliacao, self, nome_jogo=dados["jogo"]["nome"],
        ), lambda _: self._operacao_concluida("Avaliação atualizada com sucesso."))

    def excluir_minha_avaliacao(self):
        dados = self._minha_selecionada()
        if not dados or not self.excluir_minha.isEnabled():
            return
        if self._confirmar("Excluir avaliação", "Excluir sua avaliação deste jogo?"):
            self._limpar_sucesso()
            self.executor.executar(lambda: self.api.excluir_avaliacao(dados["avaliacao"]["id"]),
                                  lambda _: self._operacao_concluida("Avaliação excluída com sucesso."),
                                  self._falha)

    def _abrir_biblioteca(self):
        self.painel_filtros.hide()
        estava_minhas = self._aba_minhas
        self._aba_minhas = False
        self.conteudo_paginas.setCurrentIndex(0)
        self.janela_detalhes.hide()
        self.botao_biblioteca.setChecked(True)
        self.botao_minhas.setChecked(False)
        self._busca_timer.stop()
        for combo in (self.filtro_genero, self.filtro_plataforma, self.filtro_ano, self.ordenacao):
            with QSignalBlocker(combo):
                combo.setCurrentIndex(0)
        with QSignalBlocker(self.busca):
            self.busca.clear()
        self._atualizar_indicador_filtros()
        self.paginacao.pagina = 1
        self.paginacao_minhas.pagina = 1
        if not self.executor.ocupado:
            if estava_minhas:
                self.atualizar()
            else:
                self._preencher_biblioteca()
        self.busca.setFocus()

    def _abrir_filtros(self):
        if self.executor.ocupado:
            return
        self.painel_filtros.adjustSize()
        ponto = self.botao_filtros.mapToGlobal(QPoint(self.botao_filtros.width(), self.botao_filtros.height() + 6))
        tela = self.botao_filtros.screen().availableGeometry()
        largura = self.painel_filtros.width()
        altura = self.painel_filtros.height()
        x = max(tela.left(), min(ponto.x() - largura, tela.right() - largura + 1))
        y = ponto.y()
        if y + altura > tela.bottom() + 1:
            y = self.botao_filtros.mapToGlobal(QPoint(0, -altura - 6)).y()
        y = max(tela.top(), min(y, tela.bottom() - altura + 1))
        self.painel_filtros.move(x, y)
        self.painel_filtros.show()
        self.filtro_genero.setFocus()

    def _atualizar_indicador_filtros(self):
        total = sum(bool(combo.currentData()) for combo in (
            self.filtro_genero, self.filtro_plataforma, self.filtro_ano))
        total += self.ordenacao.currentData() != "cadastro"
        self.botao_filtros.setText(f"Filtros · {total}" if total else "Filtros")
        self.botao_filtros.setProperty("ativo", bool(total))
        self.botao_filtros.style().unpolish(self.botao_filtros)
        self.botao_filtros.style().polish(self.botao_filtros)
        self.botao_filtros.setToolTip("Filtrar por gênero, plataforma, ano e ordenar jogos")

    def _limpar_filtros(self):
        for combo in (self.filtro_genero, self.filtro_plataforma, self.filtro_ano, self.ordenacao):
            with QSignalBlocker(combo):
                combo.setCurrentIndex(0)
        self._filtrar()

    def abrir_detalhes(self):
        item = self.lista.currentItem()
        if item is not None:
            if not self.executor.ocupado and (
                self.jogo is None or self.jogo["id"] != item.data(Qt.ItemDataRole.UserRole)
            ):
                self._selecionar_jogo()
            self.paginas.show()
            self.janela_detalhes.show()
            self.janela_detalhes.raise_()

    def abrir_avaliacao_card(self, item):
        jogo_id = item.data(Qt.ItemDataRole.UserRole)
        if self.jogo and self.jogo["id"] == jogo_id and not self.executor.ocupado:
            self.adicionar_avaliacao()
        else:
            self._avaliar_pendente = jogo_id
            if not self.executor.ocupado:
                self._selecionar_jogo()

    def abrir_avaliacoes_card(self, item):
        self._avaliar_pendente = None
        self.lista.setCurrentItem(item)
        self.abrir_detalhes()

    def _falha_capa(self, url, mensagem):
        for indice in range(self.lista.count()):
            item = self.lista.item(indice)
            dados = item.data(Qt.ItemDataRole.UserRole + 1) or {}
            if dados.get("capa_url") == url:
                item.setToolTip(f"{dados.get('nome', '')}\nCapa: {mensagem}")
        self.statusBar().showMessage(f"Capa não carregada: {mensagem}")

    def escolher_capa(self):
        if not self.jogo:
            return
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolher capa", "", "Imagens (*.png *.jpg *.jpeg *.webp)")
        if caminho:
            self.preferencias.setValue(f"capas/{self.jogo['id']}", caminho)
            item = self.lista.currentItem()
            if item:
                visual = item.data(Qt.ItemDataRole.UserRole + 1) or {}
                visual["capa_local"] = caminho
                item.setData(Qt.ItemDataRole.UserRole + 1, visual)
            self._atualizar_capa_detalhes()

    def _ocupacao(self, ocupado):
        self.progresso.setVisible(ocupado)
        self.ator_local.setEnabled(not ocupado)
        self.divisao.setEnabled(not ocupado)
        self.botao_atualizar.setEnabled(not ocupado)
        self.botao_biblioteca.setEnabled(not ocupado)
        self.botao_inicio_logo.setEnabled(not ocupado)
        self.botao_minhas.setEnabled(not ocupado)
        self.botao_perfil.setEnabled(not ocupado)
        self.lista_minhas.setEnabled(not ocupado)
        self.paginacao_minhas.setEnabled(not ocupado)
        self.novo_jogo.setEnabled(not ocupado)
        self.botao_filtros.setEnabled(not ocupado)
        self._selecionar_minha()
        self.janela_detalhes.ocupar(ocupado)
        if ocupado:
            self.statusBar().showMessage("Aguarde, consultando o servidor…")

    def _falha(self, mensagem):
        self.erro.setText(mensagem)
        self.erro.show()
        self.conexao.setText("Falha na operação")
        self.statusBar().showMessage(
            "Confira o servidor e use Atualizar para tentar novamente.")

    def atualizar(self, *_args, selecionar_id=None):
        if self.executor.ocupado:
            return
        if self._aba_minhas:
            self.delegate_minhas.tentar_novamente()
            self._carregar_minhas()
            return
        self.cards.tentar_novamente()
        if selecionar_id is None and self.jogo:
            selecionar_id = self.jogo["id"]
        self.erro.hide()

        def consultar_catalogo():
            jogos = self.api.listar_jogos()
            for jogo in jogos:
                jogo["media"] = self.api.consultar_media(jogo["id"])["media"]
            return jogos

        self.executor.executar(
            consultar_catalogo,
            lambda jogos: self._receber_jogos(
                jogos, selecionar_id), self._falha,
        )

    def _receber_jogos(self, jogos, selecionar_id):
        self._jogos = jogos
        for combo, campo, titulo in ((self.filtro_genero, "genero", "Gênero"),
                                     (self.filtro_plataforma, "plataforma", "Plataforma"),
                                     (self.filtro_ano, "ano_lancamento", "Ano")):
            atual = combo.currentData()
            valores = set()
            for jogo in jogos:
                texto = str(jogo.get(campo, ""))
                valores.update(v.strip() for v in (texto.split(",") if campo == "genero" else [texto]) if v.strip())
            with QSignalBlocker(combo):
                combo.clear()
                combo.addItem("Todos", "")
                for valor in sorted(valores, key=str.casefold):
                    combo.addItem(valor, valor)
                indice = combo.findData(atual)
                combo.setCurrentIndex(max(0, indice))
        self.conexao.setText("Servidor conectado")
        self._atualizar_indicador_filtros()
        self._preencher_biblioteca(selecionar_id)

    def _filtrar(self):
        self._atualizar_indicador_filtros()
        if self.executor.ocupado:
            self._busca_timer.start()
            return
        if self._aba_minhas:
            self.paginacao_minhas.pagina = 1
            self._preencher_minhas()
        else:
            self.paginacao.pagina = 1
            self._preencher_biblioteca()

    def _preencher_biblioteca(self, selecionar_id=None):
        termo = self.busca.text().strip().casefold()
        jogos = [j for j in self._jogos if termo in " ".join(
            str(j.get(campo, "")) for campo in ("nome", "genero", "plataforma")
        ).casefold()]
        genero = self.filtro_genero.currentData()
        plataforma = self.filtro_plataforma.currentData()
        ano = self.filtro_ano.currentData()
        jogos = [j for j in jogos if
                 (not genero or genero in [v.strip() for v in j["genero"].split(",")]) and
                 (not plataforma or j["plataforma"] == plataforma) and
                 (not ano or str(j["ano_lancamento"]) == ano)]
        ordem = self.ordenacao.currentData()
        if ordem == "nome":
            jogos.sort(key=lambda j: j["nome"].casefold())
        elif ordem == "nota":
            jogos.sort(key=lambda j: (-(j.get("media") if j.get("media") is not None else -1), j["nome"].casefold()))
        elif ordem == "ano":
            jogos.sort(key=lambda j: (-j["ano_lancamento"], j["nome"].casefold()))
        if selecionar_id is not None:
            indice = next((i for i, j in enumerate(jogos) if j["id"] == selecionar_id), None)
            if indice is not None:
                self.paginacao.pagina = indice // self.paginacao.por_pagina + 1
        self.paginacao.atualizar(len(jogos))
        with QSignalBlocker(self.lista):
            self.lista.clear()
            selecionado = None
            for jogo in self.paginacao.recortar(jogos):
                item = QListWidgetItem(
                    f"{jogo['nome']}\n{jogo['plataforma']} · {jogo['ano_lancamento']}")
                item.setData(Qt.ItemDataRole.UserRole, jogo["id"])
                item.setToolTip(jogo["nome"])
                self.lista.addItem(item)
                visual = dict(jogo)
                visual["capa_local"] = self.preferencias.value(
                    f"capas/{jogo['id']}", "")
                item.setData(Qt.ItemDataRole.UserRole + 1, visual)
                item.setSizeHint(QSize(max(1, self.lista.gridSize().width() - 10), 306))
                if jogo["id"] == selecionar_id:
                    selecionado = item
            if jogos:
                self.lista.setCurrentItem(selecionado or self.lista.item(0))
        self.total_jogos.setText(f"{len(jogos)} de {len(self._jogos)} jogos")
        self.lista.setVisible(bool(jogos))
        self.sem_resultados.setVisible(not jogos)
        self.sem_resultados.setText(
            "Nenhum jogo encontrado. Tente outro nome, gênero ou plataforma."
            if termo or genero or plataforma or ano else "Sua coleção começa aqui. Adicione seu primeiro jogo.")
        self._selecionar_jogo()

    def _selecionar_jogo(self, *_args):
        item = self.lista.currentItem()
        self.jogo = None
        self._avaliacoes = []
        self._avaliacao_id_selecionada = None
        self.paginas.setCurrentIndex(0)
        if item is None:
            self.janela_detalhes.hide()
            self._avaliar_pendente = None
            self.mensagem_vazia.setText(
                "Escolha um jogo ou adicione um novo.")
            self.statusBar().showMessage("Jogos atualizados.")
            return
        jogo_id = item.data(Qt.ItemDataRole.UserRole)
        self.mensagem_vazia.setText("Carregando detalhes e avaliações…")
        self.erro.hide()

        def consultar():
            return (self.api.buscar_jogo(jogo_id), self.api.listar_avaliacoes(jogo_id),
                    self.api.consultar_media(jogo_id))

        def falha(mensagem):
            self._avaliar_pendente = None
            self.mensagem_vazia.setText(
                "Não foi possível carregar este jogo. Clique em Atualizar para tentar novamente.")
            self._falha(mensagem)

        self.executor.executar(consultar, self._receber_detalhes, falha)

    def _receber_detalhes(self, dados):
        self.jogo, self._avaliacoes, agregado = dados
        jogo = self.jogo
        self.titulo.setText(jogo["nome"])
        self.informacoes.setText(
            f"{jogo['genero']}  ·  {jogo['plataforma']}  ·  {jogo['ano_lancamento']}")
        self.descricao.setText(jogo.get("descricao") or "Sem descrição.")
        media = agregado["media"]
        item = self.lista.currentItem()
        if item is not None:
            visual = item.data(Qt.ItemDataRole.UserRole + 1) or {}
            visual["media"] = media
            item.setData(Qt.ItemDataRole.UserRole + 1, visual)
        if media is not None:
            self.media.setText(
                f"Nota média {media:.2f} / 10".replace(".", ","))
        else:
            self.media.setText("Ainda sem avaliações")
        self.quantidade.setText(
            f"{agregado['quantidade']} " + ("avaliação" if agregado['quantidade'] == 1 else "avaliações"))
        self._avaliacao_id_selecionada = None
        self.janela_detalhes.estrelas.definir_nota(media or 0)
        self.janela_detalhes.nota_estrelas.setText(
            f"{media / 2:.2f} de 5".replace(".", ",") if media is not None else "Seja o primeiro a avaliar")
        self.janela_detalhes.preencher_avaliacoes(self._avaliacoes, self._nome_autor)
        self._atualizar_capa_detalhes()
        self.paginas.setCurrentIndex(1)
        self.conexao.setText("Servidor conectado")
        self.statusBar().showMessage(
            "Clique em um card para ver avaliações e comentários. Use Avaliar jogo para criar uma avaliação.")
        if self._avaliar_pendente == jogo["id"]:
            self._avaliar_pendente = None
            QTimer.singleShot(0, self.adicionar_avaliacao)

    def _nome_autor(self, autor_id):
        if type(autor_id) is not int or autor_id <= 0:
            return "Sem autor identificado"
        if self.perfil and self.perfil["id"] == autor_id:
            return self.perfil["nome"] + " \u00b7 Voc\u00ea"
        perfil = next((p for p in self.perfis.listar() if p["id"] == autor_id), None)
        return perfil["nome"] if perfil else f"Autor {autor_id}"

    def _atualizar_capa_detalhes(self):
        if self.jogo:
            caminho = self.preferencias.value(f"capas/{self.jogo['id']}", "")
            imagem = self.cards.obter_capa(self.jogo, caminho)
            self.janela_detalhes.definir_capa(imagem, self.jogo["nome"])

    def avaliacao_selecionada(self):
        return next((a for a in self._avaliacoes if a["id"] == self._avaliacao_id_selecionada), None)

    def _selecionar_avaliacao(self, avaliacao_id):
        self._avaliacao_id_selecionada = avaliacao_id

    def _limpar_sucesso(self):
        self.sucesso.clear()
        self.sucesso.hide()
        self.sucesso_detalhes.clear()
        self.sucesso_detalhes.hide()

    def _operacao_concluida(self, mensagem, selecionar_id=None):
        # Confirma somente após resposta de sucesso. O recarregamento e suas
        # mensagens de status não apagam a confirmação da gravação realizada.
        for aviso in (self.sucesso, self.sucesso_detalhes):
            aviso.setText(mensagem)
            aviso.show()
        self.atualizar(selecionar_id=selecionar_id)

    def _abrir_formulario(self, formulario, ao_salvar):
        self._limpar_sucesso()
        if self.janela_detalhes.isVisible() and formulario.parent() is self:
            formulario.setParent(self.janela_detalhes, formulario.windowFlags())
        self.dialogo = formulario
        formulario.salvo.connect(ao_salvar)
        formulario.finished.connect(lambda _: formulario.deleteLater())
        formulario.open()

    def _jogo_salvo(self, jogo, mensagem):
        if jogo.get("capa_url"):
            self.preferencias.remove(f"capas/{jogo['id']}")
        self._busca_timer.stop()
        with QSignalBlocker(self.busca):
            self.busca.clear()
        for combo in (self.filtro_genero, self.filtro_plataforma, self.filtro_ano):
            with QSignalBlocker(combo):
                combo.setCurrentIndex(0)
        self._operacao_concluida(mensagem, selecionar_id=jogo["id"])

    def adicionar_jogo(self):
        if not self.executor.ocupado:
            self._abrir_formulario(FormularioJogo(
                self.executor, self.api.cadastrar_jogo, parent=self),
                lambda jogo: self._jogo_salvo(jogo, "Jogo cadastrado com sucesso."))

    def abrir_edicao_jogo(self):
        if self.jogo and not self.executor.ocupado:
            jogo = self.jogo.copy()
            self._abrir_formulario(FormularioJogo(
                self.executor, lambda dados: self.api.editar_jogo(
                    jogo["id"], dados), jogo, self,
            ), lambda jogo: self._jogo_salvo(jogo, "Jogo atualizado com sucesso."))

    def _confirmar(self, titulo, texto):
        caixa = QMessageBox(self)
        caixa.setWindowTitle(titulo)
        caixa.setIcon(QMessageBox.Icon.Warning)
        caixa.setTextFormat(Qt.TextFormat.PlainText)
        caixa.setText(texto)
        excluir = caixa.addButton(
            "Excluir", QMessageBox.ButtonRole.DestructiveRole)
        cancelar = caixa.addButton(
            "Cancelar", QMessageBox.ButtonRole.RejectRole)
        caixa.setDefaultButton(cancelar)
        caixa.setEscapeButton(cancelar)
        caixa.exec()
        return caixa.clickedButton() == excluir

    def remover_jogo(self):
        if not self.jogo or self.executor.ocupado:
            return
        jogo = self.jogo.copy()
        if self._confirmar("Excluir jogo", f"Excluir “{jogo['nome']}” e todas as suas avaliações? Esta ação não pode ser desfeita."):
            self._limpar_sucesso()
            self.executor.executar(lambda: self.api.excluir_jogo(
                jogo["id"]), lambda _: self._operacao_concluida(
                    "Jogo excluído com sucesso."), self._falha)

    def adicionar_avaliacao(self):
        if self.api.ator_id is None and not self.executor.ocupado:
            self.abrir_perfil()
            return
        if self.dialogo is not None:
            try:
                if self.dialogo.isVisible():
                    self.dialogo.raise_()
                    return
            except RuntimeError:
                pass
        if self.jogo and not self.executor.ocupado:
            jogo_id = self.jogo["id"]
            formulario = FormularioAvaliacao(
                self.executor, lambda dados: self.api.cadastrar_avaliacao(jogo_id, dados),
                parent=self.janela_detalhes if self.janela_detalhes.isVisible() else self,
                nome_jogo=self.jogo["nome"],
            )
            formulario.autor.setValue(self.ator_local.value())
            if self.perfil:
                formulario.autor.setReadOnly(True)
            else:
                formulario.autor.valueChanged.connect(self.ator_local.setValue)
            formulario.setWindowTitle(f"Avaliar — {self.jogo['nome']}")
            self._abrir_formulario(formulario, lambda _: self._operacao_concluida(
                "Avaliação publicada com sucesso.", selecionar_id=jogo_id))

    def abrir_edicao_avaliacao(self, avaliacao_id=None):
        if self.api.ator_id is None and not self.executor.ocupado:
            self.abrir_perfil()
            return
        if avaliacao_id is not None:
            self._selecionar_avaliacao(avaliacao_id)
        avaliacao = self.avaliacao_selecionada()
        if avaliacao and type(avaliacao.get("autor_id")) is int and avaliacao["autor_id"] > 0 and not self.executor.ocupado:
            self._abrir_formulario(FormularioAvaliacao(
                self.executor, lambda dados: self.api.editar_avaliacao(
                    avaliacao["id"], dados), avaliacao, self, nome_jogo=self.jogo["nome"],
            ), lambda _: self._operacao_concluida("Avaliação atualizada com sucesso."))

    def remover_avaliacao(self, avaliacao_id=None):
        if self.api.ator_id is None and not self.executor.ocupado:
            self.abrir_perfil()
            return
        if avaliacao_id is not None:
            self._selecionar_avaliacao(avaliacao_id)
        avaliacao = self.avaliacao_selecionada()
        if not avaliacao or type(avaliacao.get("autor_id")) is not int or avaliacao["autor_id"] <= 0 or self.executor.ocupado:
            return
        if self._confirmar("Excluir avaliação", "Excluir a avaliação selecionada? Esta ação não pode ser desfeita."):
            self._limpar_sucesso()
            self.executor.executar(lambda: self.api.excluir_avaliacao(
                avaliacao["id"]), lambda _: self._operacao_concluida(
                    "Avaliação excluída com sucesso."), self._falha)

    def closeEvent(self, evento):
        if self.executor.ocupado:
            self.statusBar().showMessage(
                "Aguarde a operação em andamento terminar antes de fechar.")
            evento.ignore()
        else:
            super().closeEvent(evento)
