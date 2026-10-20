"""Tema compartilhado pelas janelas e formulários."""

TEMA = """
QWidget { color: #e8edf5; font-family: 'Segoe UI'; font-size: 10pt; }
QMainWindow, QDialog { background: #101722; }
QWidget#biblioteca, QFrame#painel { background: #182231; border-radius: 12px; }
QLabel { background: transparent; }
QLabel#marca { font-size: 23pt; font-weight: 700; color: #7de2c4; }
QLabel#titulo { font-size: 22pt; font-weight: 700; }
QLabel#subtitulo { color: #a7b6cb; }
QLabel#secao { font-size: 13pt; font-weight: 600; }
QLabel#media { font-size: 18pt; font-weight: 600; color: #f5c86a; }
QLabel#erro { color: #ffb2ad; background: #3a242b; border-radius: 6px; padding: 10px; }
QLabel#aviso { color: #e1c489; }
QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #0e1622; border: 1px solid #3b4c63; border-radius: 6px;
    padding: 8px; selection-background-color: #286553;
}
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #7de2c4;
}
QPushButton {
    background: #26374b; border: 1px solid #3b4c63; border-radius: 6px;
    padding: 9px 14px; font-weight: 600;
}
QPushButton:hover { background: #344b65; border-color: #8da2ba; }
QPushButton:focus { border: 1px solid #7de2c4; }
QPushButton#primario { background: #7de2c4; color: #10271f; border-color: #7de2c4; }
QPushButton#primario:hover { background: #a1efd8; }
QPushButton#perigo { color: #ffb2ad; }
QPushButton:disabled { background: #202c3c; color: #77869a; border-color: #2b3a4e; }
QListWidget, QTableWidget {
    background: #182231; alternate-background-color: #1c293b;
    border: none; border-radius: 8px; outline: none;
}
QListWidget::item { padding: 15px 10px; border-bottom: 1px solid #27364a; }
QListWidget::item:selected { background: #285147; color: #ffffff; border-radius: 6px; }
QListWidget::item:hover { background: #263b4f; }
QTableWidget::item { padding: 9px; border: none; }
QTableWidget::item:selected { background: #285147; color: #ffffff; }
QHeaderView::section { background: #203045; color: #a7b6cb; padding: 10px; border: none; }
QTableCornerButton::section { background: #203045; border: none; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #131d2b; width: 10px; }
QScrollBar::handle:vertical { background: #4c5f75; border-radius: 4px; min-height: 24px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QStatusBar { color: #b6c4d6; background: #0d141e; padding: 6px; }
QProgressBar { border: none; background: #26374b; max-height: 4px; }
QProgressBar::chunk { background: #7de2c4; }
QSplitter::handle { background: #101722; width: 14px; }
QToolTip { background: #26374b; color: #ffffff; border: 1px solid #7de2c4; padding: 5px; }
"""

TEMA += """
QMainWindow, QDialog { background: #1c1e24; }
QWidget#biblioteca, QListWidget { background: #1c1e24; }
QFrame#painel { background: #242830; }
QLabel#marca { color: #ffffff; font-size: 20pt; }
QLabel#subtitulo { color: #a5afbd; }
QLineEdit { background: #2b3038; min-height: 26px; border-color: #343a44; }
QPushButton { background: #2b3038; border-color: #434952; }
QPushButton#primario { background: #ff4248; color: white; border-color: #ff4248; border-radius: 18px; padding: 10px 20px; }
QPushButton#primario:hover { background: #ff6268; }
QListWidget::item { padding: 0; border: none; background: transparent; }
QListWidget::item:selected, QListWidget::item:hover { background: transparent; }
QSplitter::handle { background: #1c1e24; }
QStatusBar { background: #191b20; }
QComboBox { color: #ffffff; background: #2b3038; }
QComboBox QAbstractItemView {
    color: #ffffff; background: #2b3038;
    selection-color: #ffffff; selection-background-color: #bd3038;
    border: 1px solid #59616e; outline: none;
}
QComboBox QAbstractItemView::item { min-height: 30px; padding: 4px 10px; }
QComboBox QAbstractItemView::item:selected { color: #ffffff; background: #bd3038; }
"""
