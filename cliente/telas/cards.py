"""Cards de jogos com capa local e indicador de nota."""
from hashlib import sha256
import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QListWidget, QStyledItemDelegate, QStyle
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from cliente.telas.estrelas import nota_em_meias_estrelas


def desenhar_capa_preenchida(painter, imagem, area):
    """Mostra a capa inteira sobre um fundo suave da própria imagem."""
    if imagem.isNull() or area.isEmpty():
        return area
    painter.save()
    painter.setClipRect(area, Qt.ClipOperation.IntersectClip)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    fundo = imagem.scaled(12, 12, Qt.AspectRatioMode.IgnoreAspectRatio,
                          Qt.TransformationMode.SmoothTransformation)
    painter.drawPixmap(area, fundo, QRectF(fundo.rect()))
    painter.fillRect(area, QColor(0, 0, 0, 65))
    fator = min(area.width() / imagem.width(), area.height() / imagem.height())
    destino = QRectF(0, 0, imagem.width() * fator, imagem.height() * fator)
    destino.moveCenter(area.center())
    painter.drawPixmap(destino, imagem, QRectF(imagem.rect()))
    painter.restore()
    return destino


class GradeJogos(QListWidget):
    """Ajusta as células e a capacidade da página ao espaço disponível."""

    capacidade_alterada = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.capacidade = 12
        self._ajuste = QTimer(self)
        self._ajuste.setSingleShot(True)
        self._ajuste.timeout.connect(self._ajustar_grade)

    def resizeEvent(self, evento):
        super().resizeEvent(evento)
        self._ajuste.start(0)

    def _ajustar_grade(self):
        margem = 2 * self.spacing()
        largura = max(1, self.viewport().width() - margem)
        altura = max(1, self.viewport().height() - margem)
        colunas = max(1, largura // 188)
        linhas = max(1, altura // 280)
        celula = QSize(largura // colunas, max(280, altura // linhas))
        self.setGridSize(celula)
        for indice in range(self.count()):
            self.item(indice).setSizeHint(self.tamanho_card())
        capacidade = colunas * linhas
        if capacidade != self.capacidade:
            self.capacidade = capacidade
            self.capacidade_alterada.emit(capacidade)

    def tamanho_card(self):
        return QSize(max(1, self.gridSize().width() - 10),
                     max(270, self.gridSize().height() - 10))


class CardsDelegate(QStyledItemDelegate):
    falha_capa = Signal(str, str)
    capa_carregada = Signal(str)

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
                imagem = imagem.scaled(360, 440, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            else:
                self._falhas.add(url)
                self.falha_capa.emit(url, mensagem)
            self._capas[url] = imagem
            self._pendentes.discard(url)
            self.capa_carregada.emit(url)
            resposta.deleteLater()
            self.parent().viewport().update()

        resposta.finished.connect(concluir)

    def sizeHint(self, option, index):
        return index.data(Qt.ItemDataRole.SizeHintRole) or QSize(178, 306)

    def obter_capa(self, jogo, caminho=""):
        if caminho and caminho not in self._capas:
            self._capas[caminho] = QPixmap(caminho).scaled(
                360, 440, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
        imagem = self._capas.get(caminho)
        if (imagem is None or imagem.isNull()) and jogo.get("capa_url"):
            self._carregar_link(jogo["capa_url"])
            imagem = self._capas.get(jogo["capa_url"])
        return imagem if imagem is not None else QPixmap()

    def paint(self, painter, option, index):
        jogo = index.data(Qt.ItemDataRole.UserRole + 1) or {}
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(option.rect).adjusted(2, 2, -2, -2)
        path = QPainterPath()
        path.addRoundedRect(r, 10, 10)
        painter.setClipPath(path)
        painter.fillRect(r, QColor("#373d48"))
        altura_capa = max(1, r.height() - 92)
        capa = QRectF(r.x(), r.y(), r.width(), altura_capa)
        caminho = jogo.get("capa_local", "")
        imagem = self.obter_capa(jogo, caminho)
        if imagem is not None and not imagem.isNull():
            desenhar_capa_preenchida(painter, imagem, capa)
        else:
            tom = int(sha256(jogo.get("nome", "").encode()).hexdigest()[:4], 16) % 360
            gradiente = QLinearGradient(capa.topLeft(), capa.bottomRight())
            gradiente.setColorAt(0, QColor.fromHsv(tom, 155, 130))
            gradiente.setColorAt(1, QColor("#282d37"))
            painter.fillRect(capa, gradiente)
            painter.setPen(QColor(255, 255, 255, 22))
            painter.setFont(QFont("Segoe UI", 100, QFont.Weight.Bold))
            painter.drawText(capa, Qt.AlignmentFlag.AlignCenter, jogo.get("nome", "?")[:1].upper())
            painter.setPen(QColor("white"))
            painter.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            painter.drawText(capa.adjusted(14, 20, -14, -28), Qt.AlignmentFlag.AlignBottom | Qt.TextFlag.TextWordWrap, jogo.get("nome", ""))
        painter.setPen(QColor("#f6f7fb"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(QRectF(r.x()+12, r.y()+altura_capa+14, r.width()-66, 48), Qt.TextFlag.TextWordWrap, jogo.get("nome", ""))
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor("#c0c6d0"))
        painter.drawText(QRectF(r.x()+12, r.bottom()-27, 110, 20), str(jogo.get("ano_lancamento", "")))
        circulo = QRectF(r.right()-52, r.y()+altura_capa+20, 40, 40)
        nota = jogo.get("media")
        painter.setPen(QPen(QColor("#4b535f"), 4))
        painter.drawEllipse(circulo)
        if nota is not None:
            painter.setPen(QPen(QColor("#b5e87a" if nota >= 7 else "#f2c96d"), 4))
            painter.drawArc(circulo, 90*16, -int(float(nota)/10*360*16))
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.drawText(circulo, Qt.AlignmentFlag.AlignCenter, f"{nota:.1f}".replace(".", ",") if nota is not None else "—")
        painter.setClipping(False)
        if option.state & (QStyle.StateFlag.State_Selected | QStyle.StateFlag.State_MouseOver):
            painter.setPen(QPen(QColor("#f27a69"), 2))
            painter.drawRoundedRect(r, 10, 10)
        painter.restore()


class AvaliacoesDelegate(CardsDelegate):
    """Linhas com capa à esquerda, estrelas e comentário à direita."""

    def sizeHint(self, option, index):
        return QSize(480, 182)

    def paint(self, painter, option, index):
        dados = index.data(Qt.ItemDataRole.UserRole + 1) or {}
        jogo = dados.get("jogo", {})
        avaliacao = dados.get("avaliacao", {})
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(option.rect).adjusted(2, 4, -2, -4)
        painter.setPen(QPen(QColor("#f27a69" if option.state & QStyle.StateFlag.State_Selected else "#464c59")))
        painter.setBrush(QColor("#303540"))
        painter.drawRoundedRect(r, 12, 12)
        capa = QRectF(r.x() + 14, r.y() + 14, 100, r.height() - 28)
        caminho = dados.get("capa_local", "")
        if caminho and caminho not in self._capas:
            self._capas[caminho] = QPixmap(caminho)
        imagem = self._capas.get(caminho)
        if (imagem is None or imagem.isNull()) and jogo.get("capa_url"):
            self._carregar_link(jogo["capa_url"])
            imagem = self._capas.get(jogo["capa_url"])
        if imagem is not None and not imagem.isNull():
            desenhar_capa_preenchida(painter, imagem, capa)
        else:
            painter.fillRect(capa, QColor("#45404c"))
            painter.setPen(QColor("#ffb3a7"))
            painter.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
            painter.drawText(capa, Qt.AlignmentFlag.AlignCenter, jogo.get("nome", "?")[:1])
        x = capa.right() + 22
        largura = max(1, r.right() - x - 20)
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor("#f7f7f9"))
        titulo = painter.fontMetrics().elidedText(jogo.get("nome", "Jogo"), Qt.TextElideMode.ElideRight, int(largura))
        painter.drawText(QRectF(x, r.y() + 15, largura, 26), titulo)
        nota = avaliacao.get("nota", 0)
        for indice in range(5):
            estrela = QPainterPath()
            centro = QPointF(x + 12 + indice * 28, r.y() + 57)
            for ponto in range(10):
                angulo = -math.pi / 2 + ponto * math.pi / 5
                raio = 11 if ponto % 2 == 0 else 5
                posicao = centro + QPointF(math.cos(angulo) * raio, math.sin(angulo) * raio)
                if ponto == 0:
                    estrela.moveTo(posicao)
                else:
                    estrela.lineTo(posicao)
            estrela.closeSubpath()
            painter.fillPath(estrela, QColor("#606979"))
            painter.save()
            painter.setClipRect(QRectF(centro.x() - 11, centro.y() - 12,
                                      22 * max(0, min(1, nota_em_meias_estrelas(nota) / 2 - indice)), 24))
            painter.fillPath(estrela, QColor("#f5c86a"))
            painter.restore()
        painter.setFont(QFont("Segoe UI", 10))
        painter.setPen(QColor("#c1c7d2"))
        painter.drawText(QRectF(x + 152, r.y() + 45, largura - 152, 24),
                         f"{nota:g} / 10".replace(".", ","))
        painter.setPen(QColor("#e4e6eb"))
        painter.setClipRect(QRectF(x, r.y() + 81, largura, r.height() - 94))
        painter.drawText(QRectF(x, r.y() + 81, largura, r.height() - 94),
                         Qt.TextFlag.TextWordWrap, avaliacao.get("comentario") or "Sem comentário.")
        painter.restore()
