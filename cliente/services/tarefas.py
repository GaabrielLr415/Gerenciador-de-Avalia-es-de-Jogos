"""Executa o APIClient síncrono sem bloquear o loop de eventos do Qt."""

from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal, Slot


class _Sinais(QObject):
    concluido = Signal(object)


class _Tarefa(QRunnable):
    def __init__(self, numero: int, operacao: Callable, sinais: _Sinais):
        super().__init__()
        self.numero = numero
        self.operacao = operacao
        self.sinais = sinais

    @Slot()
    def run(self):
        try:
            resultado = self.operacao()
        except Exception as erro:
            self.sinais.concluido.emit((self.numero, None, str(erro)))
        else:
            self.sinais.concluido.emit((self.numero, resultado, None))


class ExecutorHTTP(QObject):
    ocupado_alterado = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = QThreadPool(self)
        # Serializa as ações deste cliente, inclusive gravações no servidor JSON.
        self.pool.setMaxThreadCount(1)
        self._pendentes = {}
        self._numero = 0

    @property
    def ocupado(self):
        return bool(self._pendentes)

    def executar(self, operacao, sucesso, falha):
        self._numero += 1
        # Os sinais pertencem ao executor para serem destruídos na thread gráfica.
        sinais = _Sinais(self)
        tarefa = _Tarefa(self._numero, operacao, sinais)
        self._pendentes[self._numero] = (tarefa, sucesso, falha)
        sinais.concluido.connect(self._concluir, Qt.ConnectionType.QueuedConnection)
        self.ocupado_alterado.emit(True)
        self.pool.start(tarefa)

    @Slot(object)
    def _concluir(self, resultado):
        numero, dados, erro = resultado
        tarefa, sucesso, falha = self._pendentes.pop(numero)
        tarefa.sinais.deleteLater()
        self.ocupado_alterado.emit(self.ocupado)
        if erro is None:
            sucesso(dados)
        else:
            falha(erro)
