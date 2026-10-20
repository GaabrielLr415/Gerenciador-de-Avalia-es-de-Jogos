"""Cards de jogos com capa local e indicador de nota."""
from hashlib import sha256

from PySide6.QtCore import QRectF, QSize, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QStyledItemDelegate, QStyle
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class CardsDelegate(QStyledItemDelegate):
    falha_capa = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._capas = {}
        self._rede = QNetworkAccessManager(self)
        self._pendentes = set()
        self._falhas = set()

    def tentar_novamente(self):
        for url in self._falhas:
            self._capas.pop(url, None)
        self._falhas.clear()

    def _carregar_link(self, url):
        if url in self._capas or url in self._pendentes:
            return
        endereco = QUrl(url)
        if endereco.scheme() not in ("http", "https") or not endereco.host():
            return
        self._pendentes.add(url)
        pedido = QNetworkRequest(endereco)
        pedido.setRawHeader(b"User-Agent", b"Mozilla/5.0 TechGames/1.0")
        pedido.setRawHeader(b"Accept", b"image/webp,image/png,image/jpeg,image/*;q=0.8")
        pedido.setTransferTimeout(10000)
        resposta = self._rede.get(pedido)
        resposta.downloadProgress.connect(lambda recebidos, total: resposta.abort() if max(recebidos, total) > 10 * 1024 * 1024 else None)

        def concluir():
            imagem = QPixmap()
            mensagem = ""
            if resposta.error() == QNetworkReply.NetworkError.NoError:
                imagem.loadFromData(resposta.readAll())
                if imagem.isNull():
                    mensagem = "O link não retornou uma imagem válida. Use o endereço direto da imagem."
            else:
                mensagem = resposta.errorString()
            if not imagem.isNull():
                imagem = imagem.scaled(360, 440, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            else:
                self._falhas.add(url)
                self.falha_capa.emit(url, mensagem)
            self._capas[url] = imagem
            self._pendentes.discard(url)
            resposta.deleteLater()
            self.parent().viewport().update()

        resposta.finished.connect(concluir)

    def sizeHint(self, option, index):
        return QSize(178, 306)

    def paint(self, painter, option, index):
        jogo = index.data(Qt.ItemDataRole.UserRole + 1) or {}
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(option.rect).adjusted(2, 2, -2, -2)
        path = QPainterPath()
        path.addRoundedRect(r, 10, 10)
        painter.setClipPath(path)
        painter.fillRect(r, QColor("#2b3038"))
        capa = QRectF(r.x(), r.y(), r.width(), 210)
        caminho = jogo.get("capa_local", "")
        if caminho and caminho not in self._capas:
            self._capas[caminho] = QPixmap(caminho).scaled(360, 440, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        chave = caminho
        if (not caminho or self._capas.get(caminho, QPixmap()).isNull()) and jogo.get("capa_url"):
            chave = jogo["capa_url"]
            self._carregar_link(chave)
        imagem = self._capas.get(chave)
        if imagem is not None and not imagem.isNull():
            imagem = imagem.scaled(capa.size().toSize(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            origem = QRectF((imagem.width()-capa.width())/2, (imagem.height()-capa.height())/2, capa.width(), capa.height())
            painter.drawPixmap(capa, imagem, origem)
        else:
            tom = int(sha256(jogo.get("nome", "").encode()).hexdigest()[:4], 16) % 360
            gradiente = QLinearGradient(capa.topLeft(), capa.bottomRight())
            gradiente.setColorAt(0, QColor.fromHsv(tom, 155, 130))
            gradiente.setColorAt(1, QColor("#14171e"))
            painter.fillRect(capa, gradiente)
            painter.setPen(QColor(255, 255, 255, 22))
            painter.setFont(QFont("Segoe UI", 100, QFont.Weight.Bold))
            painter.drawText(capa, Qt.AlignmentFlag.AlignCenter, jogo.get("nome", "?")[:1].upper())
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            painter.drawText(capa.adjusted(14, 20, -14, -28), Qt.AlignmentFlag.AlignBottom | Qt.TextFlag.TextWordWrap, jogo.get("nome", ""))
        painter.setPen(QColor("#f6f7fb"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(r.x()+12, r.y()+224, r.width()-66, 48), Qt.TextFlag.TextWordWrap, jogo.get("nome", ""))
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor("#a5afbd"))
        painter.drawText(QRectF(r.x()+12, r.bottom()-27, 110, 20), str(jogo.get("ano_lancamento", "")))
        circulo = QRectF(r.right()-52, r.y()+230, 40, 40)
        nota = jogo.get("media")
        painter.setPen(QPen(QColor("#4b535f"), 4))
        painter.drawEllipse(circulo)
        if nota is not None:
            painter.setPen(QPen(QColor("#65d323" if nota >= 7 else "#ffbb24"), 4))
            painter.drawArc(circulo, 90*16, -int(float(nota)/10*360*16))
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(circulo, Qt.AlignmentFlag.AlignCenter, f"{nota:.1f}".replace(".", ",") if nota is not None else "—")
        painter.setClipping(False)
        if option.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver):
            painter.setPen(QPen(QColor("#ff4248"), 2))
            painter.drawRoundedRect(r, 10, 10)
        painter.restore()
