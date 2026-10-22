"""Tema compartilhado pela biblioteca, detalhes e formulários."""

TEMA = """
QWidget { color: #f0f1f4; font-family: 'Segoe UI'; font-size: 10pt; }
QMainWindow, QDialog, QWidget#aplicacao, QWidget#conteudo { background: #282b33; }
QFrame#barra_superior {
    background: #242730; border: none; border-bottom: 1px solid #464c59;
}
QLabel { background: transparent; }
QLabel#marca { color: #f7f7f9; font-size: 14pt; font-weight: 800; }
QLabel#simbolo_marca {
    color: #ffffff; background: #c83a2e; border-radius: 11px;
    font-size: 13pt; font-weight: 800;
}
QLabel#titulo { color: #f7f7f9; font-size: 22pt; font-weight: 700; }
QLabel#subtitulo { color: #b4bbc8; }
QLabel#secao { color: #f0f1f4; font-size: 13pt; font-weight: 600; }
QLabel#estado_vazio {
    color: #c1c6d0; background: #303540; padding: 22px; border-radius: 12px;
}
QFrame#painel { background: #303540; border-radius: 12px; }
QFrame#painel_filtros { background: #303540; border: 1px solid #697383; border-radius: 12px; }
QPushButton#botao_filtros { padding: 8px 12px; }
QPushButton#botao_filtros[ativo="true"] { color: #ffe7e2; background: #503735; border-color: #9e5148; }
QFrame#cartao_avaliacao { background: #343a46; border: 1px solid #535b69; border-radius: 12px; }
QLabel#autor_avaliacao { color: #faf7f6; font-weight: 700; font-size: 11pt; }
QLabel#capa_detalhes { background: #453841; color: #ffb3a7; border-radius: 10px; font-size: 40pt; font-weight: 800; }
QLabel#nota_detalhes { color: #f5c86a; font-size: 17pt; font-weight: 700; }
QPushButton#menu_jogo { padding: 0; font-size: 20pt; background: #3b424e; }
QPushButton#menu_jogo::menu-indicator { image: none; }
QMenu { background: #353b46; border: 1px solid #697383; padding: 6px; }
QMenu::item { padding: 9px 16px; border-radius: 6px; }
QMenu::item:selected { background: #75473f; color: #ffffff; }
QMenu::item:disabled { color: #cbd0da; }
QMenu::separator { height: 1px; background: #596271; margin: 5px; }
QFrame#estado_colecao {
    background: #2c313b; border: 1px solid #424a58; border-radius: 16px;
}
QFrame#estado_colecao QLabel { background: transparent; color: #b8c0ce; }
QFrame#estado_colecao QLabel#titulo_estado { color: #f5f6f8; font-size: 17pt; font-weight: 600; }
QWidget#biblioteca { background: transparent; }
QLabel#media { color: #c6ef85; font-size: 18pt; font-weight: 600; }
QLabel#erro {
    color: #ffd0ce; background: #382529; border: 1px solid #654049;
    border-radius: 9px; padding: 12px;
}
QFrame#erro {
    background: #382529; border: 1px solid #654049; border-radius: 10px;
}
QFrame#erro QLabel { color: #ffd0ce; }
QLabel#titulo_erro { color: #fff0ed; font-weight: 700; }
QLabel#aviso { color: #ebce9e; }
QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #353a46; border: 1px solid #515867; border-radius: 8px;
    padding: 8px; color: #f0f1f4; selection-background-color: #97483e;
}
QLineEdit { min-height: 24px; }
QLineEdit#busca_jogos {
    background: #2c313a; border: 1px solid transparent; border-radius: 13px;
    padding: 8px 12px; font-family: 'Segoe UI';
    font-size: 11pt; font-weight: 400; placeholder-text-color: #aeb6c3;
}
QLineEdit#busca_jogos:focus { border-color: #ff8577; }
QLineEdit#busca_jogos QToolButton {
    background: transparent; border: none; padding: 0;
}
QSpinBox, QDoubleSpinBox, QComboBox { min-height: 24px; }
QSpinBox#id_status { min-height: 18px; padding: 3px 8px; }
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #ff8577;
}
QPushButton {
    background: #373d49; color: #f1f2f5; border: 1px solid #525a69;
    border-radius: 8px; padding: 10px 14px; font-weight: 600;
}
QPushButton:hover { background: #454c59; border-color: #aa746c; }
QPushButton:focus { border-color: #ff8577; }
QPushButton#primario {
    background: #c83a2e; color: #ffffff; border-color: #c83a2e;
    border-radius: 9px; padding: 10px 18px;
}
QPushButton#primario:hover { background: #d34335; border-color: #d34335; }
QPushButton#avatar_perfil[conectado="true"] {
    color: #ffffff; background: #bd3c31; border: 1px solid #e27768;
    border-radius: 20px; padding: 0; font-size: 13pt; font-weight: 700;
}
QPushButton#avatar_perfil[conectado="true"]:hover { background: #d04b3e; }
QPushButton#avatar_perfil::menu-indicator { image: none; width: 0; }
QPushButton#navegacao {
    padding: 9px 10px; color: #c2c7d0; font-size: 9pt;
    background: transparent; border: 1px solid transparent;
}
QPushButton#navegacao:checked {
    color: #ffe7e2; background: #503735; border-color: #9e5148;
}
QPushButton#navegacao:hover { background: #433634; }
QPushButton#logo_inicio {
    background: transparent; border: 1px solid transparent; padding: 0;
}
QPushButton#logo_inicio:hover { border-color: #9e5148; }
QPushButton#logo_inicio:focus { border-color: #ff8577; }
QPushButton#pagina { padding: 7px 11px; }
QPushButton#pagina:checked { color: #ffffff; background: #c83a2e; border-color: #c83a2e; }
QPushButton#perigo { color: #ffb0b0; }
QPushButton:disabled { background: #30343d; color: #88909f; border-color: #454b57; }
QPushButton#primario:disabled { background: #75453f; color: #c6aaa7; border-color: #75453f; }
QListWidget {
    background: transparent; border: none; outline: none;
}
QListWidget::item, QListWidget::item:selected, QListWidget::item:hover {
    padding: 0; border: none; background: transparent;
}
QTableWidget {
    background: #2a2f39; alternate-background-color: #333a47;
    border: none; border-radius: 8px; outline: none;
}
QTableWidget::item { padding: 9px; border: none; }
QTableWidget::item:selected { background: #75473f; color: #ffffff; }
QHeaderView::section { background: #404755; color: #c7ccd5; padding: 10px; border: none; }
QTableCornerButton::section { background: #404755; border: none; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #282b33; width: 9px; margin: 0; }
QScrollBar::handle:vertical { background: #646d7c; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QStatusBar { color: #b1b9c7; background: #23262e; padding: 5px; border-top: 1px solid #464c59; }
QProgressBar { border: none; background: #3b424e; max-height: 3px; }
QProgressBar::chunk { background: #c83a2e; }
QSplitter::handle { background: #282b33; }
QToolTip { background: #353b46; color: #ffffff; border: 1px solid #d77c70; padding: 6px; }
QComboBox QAbstractItemView {
    color: #f0f1f4; background: #373d49;
    selection-color: #ffffff; selection-background-color: #97483e;
    border: 1px solid #737d8e; outline: none;
}
QComboBox QAbstractItemView::item { min-height: 30px; padding: 4px 10px; }
QComboBox QAbstractItemView::item:selected { color: #ffffff; background: #97483e; }
QDialog#dialogo_formulario { background: transparent; }
QWidget#campos_formulario, QScrollArea#rolagem_formulario {
    background: #2d323c;
}
QFrame#popup_formulario {
    background: #2d323c; border: 1px solid #535b69; border-radius: 18px;
}
QLabel#popup_legenda { color: #ffb3a7; font-size: 9pt; font-weight: 600; }
QLabel#popup_titulo { color: #faf7f6; font-size: 21pt; font-weight: 700; }
QFrame#painel_nota {
    background: #3c3438; border: 1px solid #80534e; border-radius: 12px;
}
QFrame#painel_capa {
    background: #343a46; border: 1px solid #555f70; border-radius: 12px;
}
QDoubleSpinBox#nota_popup {
    background: transparent; border: none; color: #fff0ec;
    font-size: 18pt; font-weight: 700; padding: 0; min-height: 48px;
}
QDoubleSpinBox#nota_popup::up-button, QDoubleSpinBox#nota_popup::down-button {
    width: 0; height: 0;
}
QPushButton#fechar_popup {
    color: #c2c7d1; background: #404754; border: none;
    border-radius: 10px; padding: 0; font-size: 18pt; font-weight: 400;
}
QPushButton#fechar_popup:hover { color: #ffffff; background: #69453f; }
QPushButton#fechar_popup:disabled { color: #969eac; background: #3b414c; }
QPushButton#acao_discreta {
    color: #ffc2b7; background: transparent; border: none; padding: 3px 6px;
}
QPushButton#acao_discreta:hover { color: #fff0ec; background: #60443f; }
QPushButton#opcoes_avaliacao {
    text-align: left; color: #c1c7d2; border: none;
    background: transparent; padding: 8px 0;
}
QPushButton#opcoes_avaliacao:hover { color: #ffd1c7; }

QLabel#titulo_detalhes { color: #ffffff; font-size: 25pt; font-weight: 800; }
QLabel#nota_principal { color: #f5cf80; font-size: 29pt; font-weight: 800; }
QLabel#legenda_detalhes { color: #c4bdbe; font-size: 8pt; font-weight: 600; }
QLabel#avatar_avaliacao { background: #57403f; color: #ffd1c4; border-radius: 19px; font-size: 14pt; font-weight: 700; }
QLabel#nota_cartao { background: #41483d; color: #c8eb96; border-radius: 8px; padding: 7px 11px; font-size: 12pt; font-weight: 700; }
QFrame#sobre_detalhes { background: #303540; border-radius: 14px; }
QPushButton#acao_discreta { color: #e7ada3; background: transparent; border: none; padding: 5px; }
QPushButton#acao_discreta:hover { color: #ffffff; background: #48404a; }
"""
