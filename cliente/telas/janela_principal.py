"""Biblioteca, detalhes e avaliações; toda persistência passa pelo APIClient."""

from pathlib import Path

from PySide6.QtCore import QSettings, QSize, QSignalBlocker, QTimer, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPlainTextEdit,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy, QSplitter, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QSpinBox,
)

from cliente.services.tarefas import ExecutorHTTP
from cliente.telas.cards import CardsDelegate
from cliente.telas.formularios import FormularioAvaliacao, FormularioJogo


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
        self.jogo = None
        self.dialogo = None
        self._avaliar_pendente = None
        self.setWindowTitle("TechGames")
        self.resize(1440, 900)
        self.preferencias = QSettings("TechForce", "TechGames")
        self.setMinimumSize(900, 650)
        self._montar_tela()
        self.executor.ocupado_alterado.connect(self._ocupacao)
        self.statusBar().showMessage(f"Servidor: {self.api.base_url}")
        if carregar:
            QTimer.singleShot(0, self.atualizar)

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
        if not imagem_logo.isNull():
            self.logo = QLabel()
            self.logo.setAccessibleName("Logo TechGamer")
            self.logo.setFixedSize(210, 54)
            self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo.setPixmap(imagem_logo.scaled(
                self.logo.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
            identidade.addWidget(self.logo)
        else:
            simbolo = rotulo("TG", "simbolo_marca")
            simbolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            simbolo.setFixedSize(36, 36)
            identidade.addWidget(simbolo)
            marca = rotulo("TECHGAMES", "marca")
            marca.setWordWrap(False)
            identidade.addWidget(marca)
        self.botao_biblioteca = QPushButton("INÍCIO")
        self.botao_biblioteca.setObjectName("navegacao")
        self.botao_biblioteca.setCheckable(True)
        self.botao_biblioteca.setChecked(True)
        self.botao_biblioteca.setToolTip("Mostrar todos os jogos")
        self.botao_biblioteca.clicked.connect(self._abrir_biblioteca)
        navegacao.addWidget(self.botao_biblioteca)
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
        self.ator_local.setFixedWidth(88)
        self.ator_local.setRange(1, 2147483647)
        self.ator_local.setValue(self.api.ator_id)
        self.ator_local.setToolTip("Identificação fictícia para avaliações. Moderador de demonstração: 99.")
        self.ator_local.setAccessibleName("Identificação local para editar e excluir avaliações")
        self.ator_local.valueChanged.connect(lambda valor: setattr(self.api, "ator_id", valor))
        identificacao_layout.addWidget(self.ator_local)
        self.statusBar().addPermanentWidget(identificacao)

        conteudo = QWidget()
        conteudo.setObjectName("conteudo")
        layout = QVBoxLayout(conteudo)
        layout.setContentsMargins(20, 24, 20, 16)
        layout.setSpacing(12)
        self.sucesso = rotulo()
        self.sucesso.hide()
        layout.addWidget(self.sucesso)
        self.erro = rotulo(estilo="erro")
        self.erro.hide()
        layout.addWidget(self.erro)
        self.progresso = QProgressBar()
        self.progresso.setRange(0, 0)
        self.progresso.setTextVisible(False)
        self.progresso.hide()
        layout.addWidget(self.progresso)

        self.divisao = QSplitter(Qt.Orientation.Vertical)
        biblioteca = QWidget()
        biblioteca.setObjectName("biblioteca")
        esquerda = QVBoxLayout(biblioteca)
        esquerda.setContentsMargins(0, 8, 0, 0)
        esquerda.setSpacing(14)
        titulo_colecao = QHBoxLayout()
        titulo_colecao.addWidget(rotulo("Jogos", "secao"))
        titulo_colecao.addStretch()
        self.busca = QLineEdit()
        self.busca.setPlaceholderText(
            "Buscar por nome, gênero ou plataforma…")
        self.busca.setMinimumWidth(140)
        self.busca.setMaximumWidth(520)
        acoes.addWidget(self.busca, 1)
        self.busca.setClearButtonEnabled(True)
        self.busca.setAccessibleName("Buscar jogos")
        self._busca_timer = QTimer(self)
        self._busca_timer.setSingleShot(True)
        self._busca_timer.setInterval(300)
        self._busca_timer.timeout.connect(self._filtrar)
        self.busca.textChanged.connect(lambda: self._busca_timer.start())
        self.total_jogos = rotulo("Nenhum jogo carregado", "subtitulo")
        titulo_colecao.addWidget(self.total_jogos)
        esquerda.addLayout(titulo_colecao)
        self.lista = QListWidget()
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
        self.lista.itemClicked.connect(self.abrir_avaliacao_card)
        self.lista.itemActivated.connect(self.abrir_avaliacao_card)
        self.lista.setAccessibleName("Jogos")
        esquerda.addWidget(self.lista, 1)
        self.sem_resultados = rotulo(
            "Sua coleção começa aqui. Adicione seu primeiro jogo.", "estado_vazio")
        self.sem_resultados.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sem_resultados.setMinimumHeight(90)
        esquerda.addWidget(self.sem_resultados, 1)
        self.novo_jogo = QPushButton("+ Adicionar jogo")
        self.novo_jogo.setObjectName("primario")
        self.novo_jogo.clicked.connect(self.adicionar_jogo)
        acoes.addWidget(self.novo_jogo)
        self.botao_detalhes = QPushButton("DETALHES")
        self.botao_detalhes.setObjectName("navegacao")
        self.botao_detalhes.setEnabled(False)
        self.botao_detalhes.clicked.connect(self.abrir_detalhes)
        navegacao.addWidget(self.botao_detalhes)
        self.divisao.addWidget(biblioteca)

        self.paginas = QStackedWidget()
        vazio = QFrame()
        vazio.setObjectName("painel")
        vazio_layout = QVBoxLayout(vazio)
        vazio_layout.addStretch()
        self.mensagem_vazia = rotulo(
            "Escolha um jogo para ver os detalhes e as avaliações.", "secao")
        self.mensagem_vazia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vazio_layout.addWidget(self.mensagem_vazia)
        vazio_layout.addStretch()
        self.paginas.addWidget(vazio)

        painel = QFrame()
        painel.setObjectName("painel")
        direita = QVBoxLayout(painel)
        direita.setContentsMargins(20, 18, 20, 18)
        direita.setSpacing(10)
        self.titulo = rotulo(estilo="titulo")
        direita.addWidget(self.titulo)
        self.sucesso_detalhes = rotulo()
        self.sucesso_detalhes.hide()
        direita.addWidget(self.sucesso_detalhes)
        self.informacoes = rotulo(estilo="subtitulo")
        direita.addWidget(self.informacoes)
        self.descricao = QPlainTextEdit()
        self.descricao.setReadOnly(True)
        self.descricao.setAccessibleName("Descrição do jogo")
        self.descricao.setFixedHeight(60)
        direita.addWidget(self.descricao)
        acoes_jogo = QHBoxLayout()
        self.botao_capa = QPushButton("Escolher capa")
        self.botao_capa.clicked.connect(self.escolher_capa)
        acoes_jogo.addWidget(self.botao_capa)
        self.editar_jogo = QPushButton("Editar jogo")
        self.editar_jogo.clicked.connect(self.abrir_edicao_jogo)
        self.excluir_jogo = QPushButton("Excluir jogo")
        self.excluir_jogo.setObjectName("perigo")
        self.excluir_jogo.clicked.connect(self.remover_jogo)
        acoes_jogo.addWidget(self.editar_jogo)
        acoes_jogo.addWidget(self.excluir_jogo)
        acoes_jogo.addStretch()
        direita.addLayout(acoes_jogo)
        self.media = rotulo("Sem avaliações", "media")
        direita.addWidget(self.media)
        self.quantidade = rotulo(estilo="subtitulo")
        direita.addWidget(self.quantidade)

        acoes = QHBoxLayout()
        acoes.addWidget(rotulo("Avaliações", "secao"))
        acoes.addStretch()
        self.nova_avaliacao = QPushButton("+ Avaliar jogo")
        self.nova_avaliacao.setObjectName("primario")
        self.nova_avaliacao.clicked.connect(self.adicionar_avaliacao)
        acoes.addWidget(self.nova_avaliacao)
        direita.addLayout(acoes)
        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Autor", "Nota", "Comentário"])
        self.tabela.setAccessibleName("Avaliações do jogo selecionado")
        self.tabela.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.tabela.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.setShowGrid(False)
        self.tabela.setWordWrap(False)
        self.tabela.verticalHeader().hide()
        self.tabela.verticalHeader().setDefaultSectionSize(46)
        self.tabela.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch)
        self.tabela.setMinimumHeight(120)
        self.tabela.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        self.tabela.itemSelectionChanged.connect(self._selecionar_avaliacao)
        self.tabela.cellDoubleClicked.connect(
            lambda *_: self.abrir_edicao_avaliacao())
        direita.addWidget(self.tabela, 1)
        self.comentario = QPlainTextEdit()
        self.comentario.setReadOnly(True)
        self.comentario.setAccessibleName("Comentário completo da avaliação")
        self.comentario.setPlaceholderText(
            "Selecione uma avaliação para ler o comentário completo.")
        self.comentario.setFixedHeight(56)
        direita.addWidget(self.comentario)
        self.aviso_autor = rotulo(estilo="aviso")
        self.aviso_autor.hide()
        direita.addWidget(self.aviso_autor)
        botoes_avaliacao = QHBoxLayout()
        self.editar_avaliacao = QPushButton("Editar avaliação")
        self.editar_avaliacao.clicked.connect(self.abrir_edicao_avaliacao)
        self.excluir_avaliacao = QPushButton("Excluir avaliação")
        self.excluir_avaliacao.setObjectName("perigo")
        self.excluir_avaliacao.clicked.connect(self.remover_avaliacao)
        botoes_avaliacao.addWidget(self.editar_avaliacao)
        botoes_avaliacao.addWidget(self.excluir_avaliacao)
        botoes_avaliacao.addStretch()
        direita.addLayout(botoes_avaliacao)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(painel)
        self.paginas.addWidget(scroll)
        self.janela_detalhes = QDialog(self)
        self.janela_detalhes.setWindowTitle("Detalhes do jogo")
        self.janela_detalhes.resize(900, 760)
        self.janela_detalhes.setWindowModality(Qt.WindowModality.WindowModal)
        QVBoxLayout(self.janela_detalhes).addWidget(self.paginas)
        self.divisao.setStretchFactor(0, 3)
        self.divisao.setStretchFactor(1, 1)
        self.divisao.setSizes([510, 310])
        layout.addWidget(self.divisao, 1)
        estrutura.addWidget(conteudo, 1)
        self.setCentralWidget(central)
        self._selecionar_avaliacao()

    def _abrir_biblioteca(self):
        self.botao_biblioteca.setChecked(True)
        self.busca.clear()
        self.busca.setFocus()

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

    def _ocupacao(self, ocupado):
        self.progresso.setVisible(ocupado)
        self.ator_local.setEnabled(not ocupado)
        self.divisao.setEnabled(not ocupado)
        self.botao_atualizar.setEnabled(not ocupado)
        self.botao_biblioteca.setEnabled(not ocupado)
        self.novo_jogo.setEnabled(not ocupado)
        self.botao_detalhes.setEnabled(not ocupado and self.jogo is not None)
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
        self.conexao.setText("Servidor conectado")
        self._preencher_biblioteca(selecionar_id)

    def _filtrar(self):
        if self.executor.ocupado:
            self._busca_timer.start()
            return
        self._preencher_biblioteca(self.jogo["id"] if self.jogo else None)

    def _preencher_biblioteca(self, selecionar_id=None):
        termo = self.busca.text().strip().casefold()
        jogos = [j for j in self._jogos if termo in " ".join(
            str(j.get(campo, "")) for campo in ("nome", "genero", "plataforma")
        ).casefold()]
        with QSignalBlocker(self.lista):
            self.lista.clear()
            selecionado = None
            for jogo in jogos:
                item = QListWidgetItem(
                    f"{jogo['nome']}\n{jogo['plataforma']} · {jogo['ano_lancamento']}")
                item.setData(Qt.ItemDataRole.UserRole, jogo["id"])
                item.setToolTip(jogo["nome"])
                self.lista.addItem(item)
                visual = dict(jogo)
                visual["capa_local"] = self.preferencias.value(
                    f"capas/{jogo['id']}", "")
                item.setData(Qt.ItemDataRole.UserRole + 1, visual)
                item.setSizeHint(QSize(178, 306))
                if jogo["id"] == selecionar_id:
                    selecionado = item
            if jogos:
                self.lista.setCurrentItem(selecionado or self.lista.item(0))
        self.total_jogos.setText(f"{len(jogos)} de {len(self._jogos)} jogos")
        self.lista.setVisible(bool(jogos))
        self.sem_resultados.setVisible(not jogos)
        self.sem_resultados.setText(
            "Nenhum jogo encontrado. Tente outro nome, gênero ou plataforma."
            if termo else "Sua coleção começa aqui. Adicione seu primeiro jogo.")
        self._selecionar_jogo()

    def _selecionar_jogo(self, *_args):
        item = self.lista.currentItem()
        self.jogo = None
        self._avaliacoes = []
        self.paginas.setCurrentIndex(0)
        self.botao_detalhes.setEnabled(False)
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
        self.descricao.setPlainText(
            jogo.get("descricao") or "Nenhuma descrição adicionada.")
        media = agregado["media"]
        item = self.lista.currentItem()
        if item is not None:
            visual = item.data(Qt.ItemDataRole.UserRole + 1) or {}
            visual["media"] = media
            item.setData(Qt.ItemDataRole.UserRole + 1, visual)
        if media is not None:
            self.media.setText(
                f"★ {media / 2:.2f} / 5   ·   Nota média {media:.2f} / 10".replace(".", ","))
        else:
            self.media.setText("Ainda sem avaliações")
        self.quantidade.setText(
            f"{agregado['quantidade']} avaliação(ões) · Média calculada pelo servidor")
        with QSignalBlocker(self.tabela):
            self.tabela.setRowCount(len(self._avaliacoes))
            for linha, avaliacao in enumerate(self._avaliacoes):
                autor = avaliacao.get("autor_id")
                valores = (
                    f"Autor {autor}" if autor else "Sem autor",
                    f"★ {avaliacao['nota'] / 2:g}/5 · {avaliacao['nota']:g}/10".replace(
                        ".", ","),
                    avaliacao.get("comentario") or "Sem comentário",
                )
                for coluna, valor in enumerate(valores):
                    item = QTableWidgetItem(valor)
                    item.setToolTip(valor)
                    self.tabela.setItem(linha, coluna, item)
            self.tabela.clearSelection()
            self.tabela.setCurrentCell(-1, -1)
        self._selecionar_avaliacao()
        self.paginas.setCurrentIndex(1)
        self.botao_detalhes.setEnabled(True)
        self.conexao.setText("Servidor conectado")
        self.statusBar().showMessage(
            "Clique em um card para avaliar. Use Detalhes do jogo para consultar as avaliações.")
        if self._avaliar_pendente == jogo["id"]:
            self._avaliar_pendente = None
            QTimer.singleShot(0, self.adicionar_avaliacao)

    def avaliacao_selecionada(self):
        linha = self.tabela.currentRow()
        return self._avaliacoes[linha] if 0 <= linha < len(self._avaliacoes) else None

    def _selecionar_avaliacao(self):
        avaliacao = self.avaliacao_selecionada()
        autor = avaliacao.get("autor_id") if avaliacao else None
        pode_alterar = type(autor) is int and autor > 0
        self.editar_avaliacao.setEnabled(pode_alterar)
        self.excluir_avaliacao.setEnabled(pode_alterar)
        self.comentario.setPlainText(
            (avaliacao.get("comentario") or "Sem comentário.") if avaliacao else "")
        self.aviso_autor.setVisible(avaliacao is not None and not pode_alterar)
        self.aviso_autor.setText(
            "Esta avaliação antiga não tem autor identificado. O servidor bloqueia sua edição e exclusão individual.")

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
            formulario.autor.valueChanged.connect(self.ator_local.setValue)
            formulario.setWindowTitle(f"Avaliar — {self.jogo['nome']}")
            self._abrir_formulario(formulario, lambda _: self._operacao_concluida(
                "Avaliação publicada com sucesso.", selecionar_id=jogo_id))

    def abrir_edicao_avaliacao(self):
        avaliacao = self.avaliacao_selecionada()
        if avaliacao and self.editar_avaliacao.isEnabled() and not self.executor.ocupado:
            self._abrir_formulario(FormularioAvaliacao(
                self.executor, lambda dados: self.api.editar_avaliacao(
                    avaliacao["id"], dados), avaliacao, self, nome_jogo=self.jogo["nome"],
            ), lambda _: self._operacao_concluida("Avaliação atualizada com sucesso."))

    def remover_avaliacao(self):
        avaliacao = self.avaliacao_selecionada()
        if not avaliacao or not self.excluir_avaliacao.isEnabled() or self.executor.ocupado:
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
