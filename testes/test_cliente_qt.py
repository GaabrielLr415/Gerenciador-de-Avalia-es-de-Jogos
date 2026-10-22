"""Integração Qt → HTTP real → Flask, usando apenas dados temporários."""

import importlib
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QSettings, QThread, QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from werkzeug.serving import make_server

from cliente.services.api_client import APIClient
from cliente.services.tarefas import ExecutorHTTP
from cliente.telas.estrelas import Estrelas
from cliente.telas.janela_principal import JanelaPrincipal
from servidor.storage import repositorio_json as storage


class ClienteQtTestes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])
        cls.qt.setQuitOnLastWindowClosed(False)
        cls.temporario_importacao = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temporario_importacao.cleanup)
        raiz = Path(cls.temporario_importacao.name)
        with (
            patch.object(storage, "ARQUIVO_JOGOS_PADRAO", raiz / "jogos.json"),
            patch.object(storage, "ARQUIVO_AVALIACOES_PADRAO", raiz / "avaliacoes.json"),
        ):
            cls.api = importlib.import_module("servidor.app")

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        raiz = Path(self.temporario.name)
        self.repo = storage.RepositorioJSON(raiz / "jogos.json", raiz / "avaliacoes.json")
        configuracao = patch.dict(self.api.app.config, {"REPOSITORIO": self.repo, "TESTING": True})
        configuracao.start()
        self.addCleanup(configuracao.stop)
        self.servidor = make_server("127.0.0.1", 0, self.api.app)
        self.thread = threading.Thread(target=self.servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        self.thread.start()
        self.addCleanup(self.parar_servidor)
        self.cliente = APIClient(f"http://127.0.0.1:{self.servidor.server_port}")
        preferencias = patch("cliente.telas.janela_principal.QSettings", side_effect=lambda *_:
                             QSettings(str(raiz / "preferencias.ini"), QSettings.Format.IniFormat))
        preferencias.start()
        self.addCleanup(preferencias.stop)
        self.janela = JanelaPrincipal(self.cliente, carregar=False)
        self.janela.show()
        self.addCleanup(self.fechar_janela)

    def parar_servidor(self):
        if self.thread.is_alive():
            self.servidor.shutdown()
            self.thread.join(timeout=2)
        self.servidor.server_close()

    def fechar_janela(self):
        self.esperar(lambda: not self.janela.executor.ocupado)
        self.janela.close()
        self.janela.deleteLater()
        self.qt.processEvents()

    def esperar(self, condicao, timeout=8):
        fim = time.monotonic() + timeout
        while time.monotonic() < fim:
            self.qt.processEvents()
            if condicao():
                return
            QTest.qWait(10)
        self.fail("A interface não concluiu a operação no prazo esperado.")

    def aguardar_http(self):
        self.esperar(lambda: not self.janela.executor.ocupado and not self.janela._busca_timer.isActive())

    @staticmethod
    def dados_jogo(nome="Hollow Knight"):
        return {"nome": nome, "genero": "Metroidvania", "plataforma": "PC", "ano_lancamento": 2017}

    def preencher_jogo(self, formulario, nome="Hollow Knight"):
        formulario.nome.setText(nome)
        formulario.genero.setText("Metroidvania")
        formulario.plataforma.setCurrentText("PC")
        formulario.ano.setValue(2017)

    def test_crud_pela_interface_com_estrelas_decimais_e_media(self):
        self.janela.atualizar()
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 0)
        QTest.mouseClick(self.janela.novo_jogo, Qt.MouseButton.LeftButton)
        formulario = self.janela.dialogo
        QTest.mouseClick(formulario.botao_salvar, Qt.MouseButton.LeftButton)
        self.assertTrue(formulario.erro.isVisible())
        self.assertEqual(self.repo.listar_jogos(), [])
        self.preencher_jogo(formulario)
        QTest.mouseClick(formulario.botao_salvar, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        self.assertEqual(self.janela.sucesso.text(), "Jogo cadastrado com sucesso.")
        jogo_id = self.janela.jogo["id"]
        self.assertEqual(self.janela.titulo.text(), "Hollow Knight")
        self.janela.abrir_detalhes()
        self.janela.janela_detalhes.acao_editar.trigger()
        formulario = self.janela.dialogo
        formulario.nome.setText("Hollow Knight — edição")
        QTest.mouseClick(formulario.botao_salvar, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        self.assertEqual(self.repo.buscar_jogo(jogo_id)["nome"], "Hollow Knight — edição")
        self.assertEqual(self.janela.sucesso.text(), "Jogo atualizado com sucesso.")

        QTest.mouseClick(self.janela.nova_avaliacao, Qt.MouseButton.LeftButton)
        formulario = self.janela.dialogo
        formulario.autor.setValue(7)
        QTest.mouseClick(formulario.estrelas, Qt.MouseButton.LeftButton, pos=QPoint(210, 24))
        self.assertEqual(formulario.nota.value(), 9)
        QTest.mouseClick(formulario.estrelas, Qt.MouseButton.LeftButton, pos=QPoint(222, 24))
        self.assertEqual(formulario.nota.value(), 10)
        self.assertEqual(formulario.valor_estrelas.text(), "5 / 5")
        formulario.comentario.setPlainText("Excelente aventura!")
        QTest.mouseClick(formulario.botao_salvar, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        avaliacao = self.repo.listar_avaliacoes(jogo_id)[0]
        self.assertEqual(avaliacao["nota"], 10)
        self.assertEqual(avaliacao["autor_id"], 7)
        self.assertIn("10,00 / 10", self.janela.media.text())
        self.assertEqual(self.janela.sucesso_detalhes.text(), "Avaliação publicada com sucesso.")
        self.assertTrue(self.janela.sucesso_detalhes.isVisible())

        # Editar no cliente deve preservar metadados existentes no servidor.
        self.repo.atualizar_avaliacao(avaliacao["id"], {"nota": 9.5, "metadados": {"origem": "teste"}})
        self.janela.atualizar()
        self.aguardar_http()
        QTest.mouseClick(self.janela.janela_detalhes.cartoes[avaliacao["id"]].botao_editar, Qt.MouseButton.LeftButton)
        formulario = self.janela.dialogo
        self.assertFalse(formulario.autor.isEnabled())
        self.assertEqual(formulario.nota.value(), 9.5)
        formulario.nota.setValue(0)
        formulario.comentario.clear()
        QTest.mouseClick(formulario.botao_salvar, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        atualizada = self.repo.buscar_avaliacao(avaliacao["id"])
        self.assertEqual(atualizada["nota"], 0)
        self.assertEqual(atualizada["metadados"], {"origem": "teste"})
        self.assertIn("0,00 / 10", self.janela.media.text())
        self.assertEqual(self.janela.sucesso.text(), "Avaliação atualizada com sucesso.")
        self.janela._selecionar_avaliacao(avaliacao["id"])
        with patch.object(self.janela, "_confirmar", return_value=False):
            self.janela.remover_avaliacao()
        self.assertIsNotNone(self.repo.buscar_avaliacao(avaliacao["id"]))
        with patch.object(self.janela, "_confirmar", return_value=True):
            self.janela.remover_avaliacao()
        self.aguardar_http()
        self.assertEqual(len(self.janela.janela_detalhes.cartoes), 0)
        self.assertEqual(self.janela.sucesso.text(), "Avaliação excluída com sucesso.")
        self.assertEqual(self.janela.media.text(), "Ainda sem avaliações")
        # A exclusão do jogo também deve atualizar a biblioteca vazia.
        self.repo.criar_avaliacao(jogo_id, {"autor_id": 7, "nota": 10})
        with patch.object(self.janela, "_confirmar", return_value=True):
            self.janela.remover_jogo()
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 0)
        self.assertEqual(self.repo.listar_avaliacoes(jogo_id), [])
        self.assertEqual(self.janela.sucesso.text(), "Jogo excluído com sucesso.")
        self.assertTrue(self.janela.sucesso.isVisible())

    def test_falha_de_rede_preserva_formulario_e_permite_cancelar(self):
        self.parar_servidor()
        self.janela.adicionar_jogo()
        formulario = self.janela.dialogo
        self.preencher_jogo(formulario, "Não perder este texto")
        formulario.enviar()
        self.aguardar_http()
        self.assertTrue(formulario.isVisible())
        self.assertTrue(formulario.erro.isVisible())
        self.assertIn("conectar", formulario.erro.text())
        self.assertEqual(formulario.nome.text(), "Não perder este texto")
        self.assertTrue(formulario.botao_salvar.isEnabled())
        self.assertEqual(self.repo.listar_jogos(), [])
        formulario.reject()
        self.janela.atualizar()
        self.aguardar_http()
        self.assertTrue(self.janela.erro.isVisible())
        self.assertTrue(self.janela.botao_atualizar.isEnabled())

    def test_busca_e_avaliacao_legada_com_alteracoes_bloqueadas(self):
        import json
        jogo = self.repo.criar_jogo(self.dados_jogo())
        self.repo.criar_jogo(self.dados_jogo("Celeste"))
        self.repo.caminho_avaliacoes.write_text(json.dumps([
            {"id": 1, "jogo_id": jogo["id"], "nota": 8, "comentario": "Legada"},
            {"id": 2, "jogo_id": jogo["id"], "autor_id": 7, "nota": 10, "comentario": "Nova"},
        ]), encoding="utf-8")
        self.janela.atualizar()
        self.aguardar_http()
        self.assertIn("9,00 / 10", self.janela.media.text())
        legada = self.janela.janela_detalhes.cartoes[1]
        nova = self.janela.janela_detalhes.cartoes[2]
        self.assertFalse(legada.botao_editar.isEnabled())
        self.assertFalse(legada.botao_excluir.isEnabled())
        self.assertEqual(legada.comentario.text(), "Legada")
        self.assertTrue(nova.botao_editar.isEnabled())
        QTest.keyClicks(self.janela.busca, "celeste")
        # A busca aguarda a digitação e não dispara HTTP a cada letra.
        self.assertFalse(self.janela.executor.ocupado)
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 1)
        self.assertEqual(self.janela.titulo.text(), "Celeste")
        self.janela.busca.setText("inexistente")
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 0)
        self.assertIsNone(self.janela.jogo)

    def test_link_capa_salvo_editado_e_carregado_sem_bloquear(self):
        from http.server import BaseHTTPRequestHandler, HTTPServer
        from PySide6.QtCore import QBuffer, QIODevice
        from PySide6.QtGui import QImage, QColor

        imagem = QImage(30, 40, QImage.Format.Format_RGB32)
        imagem.fill(QColor("#ff4248"))
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        imagem.save(buffer, "PNG")
        conteudo = bytes(buffer.data())

        class ImagemHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(conteudo)))
                self.end_headers()
                self.wfile.write(conteudo)

            def log_message(self, *args):
                pass

        servidor = HTTPServer(("127.0.0.1", 0), ImagemHandler)
        thread = threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
        thread.start()
        self.addCleanup(servidor.server_close)
        self.addCleanup(thread.join, 2)
        self.addCleanup(servidor.shutdown)
        url = f"http://127.0.0.1:{servidor.server_port}/capa.png"
        self.janela.adicionar_jogo()
        formulario = self.janela.dialogo
        self.preencher_jogo(formulario)
        formulario.capa_url.setText("imagem-invalida")
        formulario.enviar()
        self.assertTrue(formulario.erro.isVisible())
        self.assertEqual(self.repo.listar_jogos(), [])
        formulario.capa_url.setText(url)
        formulario.enviar()
        self.aguardar_http()
        jogo_id = self.janela.jogo["id"]
        self.assertEqual(self.cliente.buscar_jogo(jogo_id)["capa_url"], url)
        delegate = self.janela.lista.itemDelegate()
        self.esperar(lambda: url in delegate._capas)
        self.assertFalse(delegate._capas[url].isNull())
        self.assertEqual(self.janela.lista.currentItem().data(Qt.ItemDataRole.UserRole + 1)["capa_url"], url)
        self.janela.abrir_edicao_jogo()
        formulario = self.janela.dialogo
        self.assertEqual(formulario.capa_url.text(), url)
        formulario.capa_url.clear()
        formulario.enviar()
        self.aguardar_http()
        self.assertEqual(self.cliente.buscar_jogo(jogo_id)["capa_url"], "")
        with self.assertRaisesRegex(Exception, "HTTP 400"):
            self.cliente.cadastrar_jogo(dict(self.dados_jogo(), capa_url="file:///imagem.png"))

    def test_card_abre_consulta_e_permite_avaliar_o_jogo_clicado(self):
        self.repo.criar_jogo(self.dados_jogo("Primeiro"))
        segundo = self.repo.criar_jogo(self.dados_jogo("Segundo"))
        self.janela.atualizar()
        self.aguardar_http()
        self.assertFalse(self.janela.janela_detalhes.isVisible())
        self.assertIsNone(self.janela.dialogo)
        item = self.janela.lista.item(1)
        QTest.mouseClick(self.janela.lista.viewport(), Qt.MouseButton.LeftButton,
                         pos=self.janela.lista.visualItemRect(item).center())
        self.aguardar_http()
        self.assertTrue(self.janela.janela_detalhes.isVisible())
        self.assertEqual(self.janela.titulo.text(), "Segundo")
        self.assertIsNone(self.janela.dialogo)
        QTest.mouseClick(self.janela.nova_avaliacao, Qt.MouseButton.LeftButton)
        self.esperar(lambda: self.janela.dialogo is not None and self.janela.dialogo.isVisible())
        formulario = self.janela.dialogo
        self.assertIn("Segundo", formulario.windowTitle())
        formulario.nota.setValue(9)
        formulario.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.listar_avaliacoes(segundo["id"])[0]["nota"], 9)
        self.assertEqual(self.repo.listar_avaliacoes(1), [])
        self.assertTrue(self.janela.janela_detalhes.isVisible())

    def test_servidor_antigo_nao_descarta_link_silenciosamente(self):
        with patch.object(self.cliente, "_request", return_value={"status": "ok"}) as chamada:
            with self.assertRaisesRegex(Exception, "desatualizado"):
                self.cliente.cadastrar_jogo(dict(self.dados_jogo(), capa_url="https://example.com/capa.png"))
        chamada.assert_called_once_with("GET", "/health")

    def test_estrelas_por_mouse_teclado_e_limites(self):
        estrelas = Estrelas()
        estrelas.show()
        self.addCleanup(estrelas.close)
        QTest.mouseClick(estrelas, Qt.MouseButton.LeftButton, pos=QPoint(18, 24))
        self.assertEqual(estrelas.nota, 1)
        QTest.mouseClick(estrelas, Qt.MouseButton.LeftButton, pos=QPoint(222, 24))
        self.assertEqual(estrelas.nota, 10)
        QTest.keyClick(estrelas, Qt.Key.Key_Left)
        self.assertEqual(estrelas.nota, 9)
        QTest.keyClick(estrelas, Qt.Key.Key_Right)
        self.assertEqual(estrelas.nota, 10)
        QTest.mouseClick(estrelas, Qt.MouseButton.LeftButton, pos=QPoint(234, 24))
        self.assertEqual(estrelas.nota, 10)
        QTest.keyClick(estrelas, Qt.Key.Key_Right)
        self.assertEqual(estrelas.nota, 10)
        QTest.keyClick(estrelas, Qt.Key.Key_Home)
        QTest.keyClick(estrelas, Qt.Key.Key_Left)
        self.assertEqual(estrelas.nota, 0)
        estrelas.definir_nota(9.5)
        self.assertEqual(estrelas.nota, 9.5)
        QTest.keyClick(estrelas, Qt.Key.Key_Left)
        self.assertEqual(estrelas.nota, 9)
        QTest.keyClick(estrelas, Qt.Key.Key_Right)
        self.assertEqual(estrelas.nota, 10)

    def test_meias_estrelas_no_formulario_preservam_nota_antiga_ao_editar_comentario(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        avaliacao = self.repo.criar_avaliacao(jogo["id"], {"autor_id":7, "nota":9.5})
        self.janela.ator_local.setValue(7)
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.abrir_edicao_avaliacao(avaliacao["id"])
        formulario = self.janela.dialogo
        self.assertEqual(formulario.nota.value(), 9.5)
        formulario.comentario.setPlainText("Somente comentário alterado")
        formulario.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.buscar_avaliacao(avaliacao["id"])["nota"], 9.5)
        self.assertIn("9,50 / 10", self.janela.media.text())
        self.janela.abrir_edicao_avaliacao(avaliacao["id"])
        formulario = self.janela.dialogo
        formulario.nota.setValue(8.5)
        self.assertEqual(formulario.nota.value(), 9)
        self.assertEqual(formulario.valor_estrelas.text(), "4,5 / 5")
        formulario.reject()
        self.janela.adicionar_avaliacao()
        formulario = self.janela.dialogo
        self.assertEqual(formulario.nota.singleStep(), 1)
        self.assertEqual(formulario.nota.decimals(), 0)
        formulario.nota.setValue(8.5)
        self.assertEqual(formulario.nota.value(), 9)
        for nota, x in enumerate(range(12, 240, 24), start=1):
            QTest.mouseClick(formulario.estrelas, Qt.MouseButton.LeftButton, pos=QPoint(x, 24))
            self.assertEqual(formulario.nota.value(), nota)
            self.assertEqual(formulario.estrelas.nota, nota)
        formulario.reject()
        self.assertEqual(len(self.repo.listar_avaliacoes(jogo["id"])), 1)

    def test_http_nao_bloqueia_eventos_e_callback_roda_na_thread_grafica(self):
        executor = ExecutorHTTP()
        liberar = threading.Event()
        resultados = []
        temporizadores = []

        def operacao():
            liberar.wait(timeout=3)
            return 42

        def timer():
            temporizadores.append("interface respondeu")
            liberar.set()

        executor.executar(operacao, lambda valor: resultados.append((valor, QThread.currentThread())), self.fail)
        QTimer.singleShot(30, timer)
        self.esperar(lambda: bool(resultados))
        self.assertEqual(temporizadores, ["interface respondeu"])
        self.assertEqual(resultados[0], (42, self.qt.thread()))
        self.assertFalse(executor.ocupado)


    def test_proxy_qt_bloqueia_outro_e_permite_moderador(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        av = self.repo.criar_avaliacao(jogo["id"], {"nota":8,"autor_id":7})
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.ator_local.setValue(8)
        self.janela.abrir_edicao_avaliacao(av["id"])
        formulario = self.janela.dialogo
        formulario.nota.setValue(2)
        formulario.enviar()
        self.aguardar_http()
        self.assertTrue(formulario.isVisible())
        self.assertIn("403", formulario.erro.text())
        self.assertTrue(self.janela.sucesso.isHidden())
        self.assertEqual(self.janela.sucesso.text(), "")
        self.assertEqual(self.repo.buscar_avaliacao(av["id"])["nota"], 8)
        formulario.reject()
        self.janela.ator_local.setValue(99)
        self.janela.abrir_edicao_avaliacao(av["id"])
        formulario = self.janela.dialogo
        formulario.nota.setValue(6)
        formulario.metadados.setPlainText('{"origem":"moderacao"}')
        formulario.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.buscar_avaliacao(av["id"])["nota"], 6)
        self.assertEqual(self.repo.buscar_avaliacao(av["id"])["metadados"], {"origem":"moderacao"})
        self.assertIn("6,00 / 10", self.janela.media.text())
        with patch.object(self.janela, "_confirmar", return_value=True):
            self.janela.remover_avaliacao(av["id"])
        self.aguardar_http()
        self.assertIsNone(self.repo.buscar_avaliacao(av["id"]))
        self.assertEqual(self.janela.media.text(), "Ainda sem avaliações")

    def test_media_exibida_vem_do_servidor(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        self.repo.criar_avaliacao(jogo["id"], {"nota":8,"autor_id":7})
        with patch.object(self.cliente, "consultar_media", return_value={
            "jogo_id":jogo["id"],"quantidade":1,"media":3.5}) as consulta:
            self.janela.atualizar()
            self.aguardar_http()
        self.assertTrue(consulta.called)
        self.assertIn("3,50 / 10", self.janela.media.text())

    def test_metadados_invalidos_nao_sao_enviados(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.adicionar_avaliacao()
        formulario = self.janela.dialogo
        for texto in ('[]', '{', '{"valor":NaN}'):
            formulario.metadados.setPlainText(texto)
            formulario.enviar()
            self.assertTrue(formulario.erro.isVisible())
            self.assertFalse(self.janela.executor.ocupado)
        self.assertEqual(self.repo.listar_avaliacoes(jogo["id"]), [])
        formulario.reject()

    def test_detalhes_cartoes_operam_no_registro_correto(self):
        comentario = "Gostei dos desafios e da exploração. " * 16
        jogo = self.repo.criar_jogo(self.dados_jogo())
        primeira = self.repo.criar_avaliacao(jogo["id"], {
            "autor_id":7, "nota":8, "comentario":comentario, "metadados":{"origem":"primeira"}})
        segunda = self.repo.criar_avaliacao(jogo["id"], {
            "autor_id":7, "nota":4, "comentario":"Outra experiência", "metadados":{"origem":"segunda"}})
        self.entrar_perfil()
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.abrir_detalhes()
        popup = self.janela.janela_detalhes
        self.assertTrue(popup.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertEqual(popup.cartoes[primeira["id"]].autor.text(), "Ana · Você")
        self.assertEqual(popup.cartoes[primeira["id"]].comentario.text(), comentario.strip())
        self.assertEqual(popup.nota_estrelas.text(), "3,00 de 5")
        botao = popup.cartoes[segunda["id"]].botao_editar
        popup.scroll.ensureWidgetVisible(botao)
        self.qt.processEvents()
        QTest.mouseClick(botao, Qt.MouseButton.LeftButton)
        self.assertEqual(self.janela.dialogo.nota.value(), 4)
        self.janela.dialogo.nota.setValue(10)
        self.janela.dialogo.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.buscar_avaliacao(primeira["id"]), primeira)
        atualizada = self.repo.buscar_avaliacao(segunda["id"])
        self.assertEqual(atualizada["nota"], 10)
        self.assertEqual(atualizada["metadados"], {"origem":"segunda"})
        self.assertEqual(popup.nota_estrelas.text(), "4,50 de 5")
        with patch.object(self.janela, "_confirmar", return_value=True):
            popup.cartoes[primeira["id"]].botao_excluir.click()
        self.aguardar_http()
        self.assertIsNone(self.repo.buscar_avaliacao(primeira["id"]))
        self.assertEqual(self.repo.buscar_avaliacao(segunda["id"]), atualizada)
        self.assertEqual(len(popup.cartoes), 1)

    def test_detalhes_menu_capa_descricao_e_fechamento(self):
        from PySide6.QtGui import QPixmap
        jogo = self.repo.criar_jogo(dict(self.dados_jogo(), descricao="<b>Texto literal</b>"))
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.abrir_detalhes()
        popup = self.janela.janela_detalhes
        self.assertEqual(popup.descricao.textFormat(), Qt.TextFormat.PlainText)
        self.assertEqual(popup.descricao.text(), "<b>Texto literal</b>")
        self.assertTrue(popup.sem_avaliacoes.isVisible())
        imagem = QPixmap(100, 140)
        imagem.fill(Qt.GlobalColor.red)
        caminho = str(self.repo.caminho_jogos.parent / "capa.png")
        self.assertTrue(imagem.save(caminho))
        with patch("cliente.telas.janela_principal.QFileDialog.getOpenFileName", return_value=(caminho, "")):
            popup.acao_capa.trigger()
        self.assertFalse(popup.capa.pixmap().isNull())
        self.assertEqual(self.janela.preferencias.value(f"capas/{jogo['id']}"), caminho)
        QTest.keyClick(popup, Qt.Key.Key_Escape)
        self.assertFalse(popup.isVisible())
        self.assertEqual(self.repo.buscar_jogo(jogo["id"]), jogo)

    def entrar_perfil(self, nome="Ana", identificador=7):
        self.janela.abrir_perfil()
        dialogo = self.janela.dialogo_perfil
        dialogo.nome.setEditText(nome)
        dialogo.identificador.setValue(identificador)
        QTest.mouseClick(dialogo.entrar, Qt.MouseButton.LeftButton)
        self.qt.processEvents()
        self.assertEqual(self.janela.perfil["id"], identificador)

    def test_perfil_local_persiste_e_nao_altera_avaliacoes(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        original = self.repo.criar_avaliacao(jogo["id"], {"autor_id":7, "nota":8})
        self.entrar_perfil()
        self.assertEqual(self.cliente.ator_id, 7)
        self.assertEqual(self.janela.botao_perfil.text(), "A")
        self.assertEqual(self.janela.acao_nome_perfil.text(), "Ana")
        outra = JanelaPrincipal(self.cliente, carregar=False)
        try:
            self.assertEqual(outra.perfil, {"nome":"Ana", "id":7})
            self.assertEqual(outra.ator_local.value(), 7)
            self.assertTrue(outra.ator_local.isReadOnly())
        finally:
            outra.close()
            outra.deleteLater()
        self.assertEqual(self.repo.buscar_avaliacao(original["id"]), original)
        self.janela.abrir_perfil()
        dialogo = self.janela.dialogo_perfil
        dialogo.nome.setEditText("Bruno")
        self.assertNotEqual(dialogo.identificador.value(), 7)
        dialogo.nome.setEditText("Ana")
        self.assertEqual(dialogo.identificador.value(), 7)
        dialogo.reject()
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.adicionar_avaliacao()
        formulario = self.janela.dialogo
        self.assertTrue(formulario.autor.isReadOnly())
        self.assertEqual(formulario.autor.value(), 7)
        formulario.nota.setValue(9)
        formulario.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.listar_avaliacoes(jogo["id"])[-1]["autor_id"], 7)
        with self.assertRaises(ValueError):
            self.janela.perfis.entrar("", 9)
        with self.assertRaises(ValueError):
            self.janela.perfis.entrar("Outra pessoa", 7)
        with self.assertRaises(ValueError):
            self.janela.perfis.entrar("Ana", 9)

    def test_avatar_menu_e_saida_preservam_dados_e_limpam_sessao(self):
        from cliente.telas.perfis import DialogoPerfil
        jogo = self.repo.criar_jogo(self.dados_jogo())
        original = self.repo.criar_avaliacao(jogo["id"], {"autor_id":7, "nota":8})
        self.entrar_perfil()
        self.janela.abrir_minhas_avaliacoes()
        self.aguardar_http()
        self.assertEqual(self.janela.lista_minhas.count(), 1)
        avatar = self.janela.botao_perfil
        self.assertEqual(avatar.text(), "A")
        self.assertEqual(avatar.width(), avatar.height())
        QTest.mouseClick(avatar, Qt.MouseButton.LeftButton)
        self.qt.processEvents()
        self.assertTrue(self.janela.menu_perfil.isVisible())
        self.assertEqual(self.janela.acao_nome_perfil.text(), "Ana")
        QTest.mouseClick(self.janela.menu_perfil, Qt.MouseButton.LeftButton,
                         pos=self.janela.menu_perfil.actionGeometry(self.janela.acao_sair_perfil).center())
        self.aguardar_http()
        QTest.qWait(150)
        self.assertIsNone(self.janela.perfil)
        self.assertIsNone(self.janela.perfis.ativo())
        self.assertIsNone(self.cliente.ator_id)
        self.assertEqual(self.janela.botao_perfil.text(), "Entrar")
        self.assertEqual(self.janela.lista_minhas.count(), 0)
        self.assertEqual(self.janela.conteudo_paginas.currentIndex(), 0)
        self.assertEqual(self.repo.buscar_avaliacao(original["id"]), original)
        self.assertFalse(any(d.isVisible() for d in self.janela.findChildren(DialogoPerfil)))
        self.janela.adicionar_avaliacao()
        self.assertTrue(self.janela.dialogo_perfil.isVisible())
        self.janela.dialogo_perfil.reject()
        self.assertEqual(len(self.repo.listar_avaliacoes(jogo["id"])), 1)
        self.entrar_perfil()
        self.assertEqual(self.cliente.ator_id, 7)
        self.assertEqual(self.janela.botao_perfil.text(), "A")

    def test_filtros_combinados_paginacao_e_logo_voltam_ao_inicio(self):
        for indice in range(25):
            dados = self.dados_jogo(f"Jogo {indice:02}")
            dados.update(genero="RPG, Ação" if indice % 2 == 0 else "Plataforma",
                         plataforma="PC" if indice % 3 == 0 else "PlayStation",
                         ano_lancamento=2018 + indice % 3)
            self.repo.criar_jogo(dados)
        self.janela.atualizar()
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 12)
        primeiros = {self.janela.lista.item(i).data(Qt.ItemDataRole.UserRole) for i in range(12)}
        self.janela.paginacao.ir_para(2)
        self.aguardar_http()
        seguintes = {self.janela.lista.item(i).data(Qt.ItemDataRole.UserRole) for i in range(12)}
        self.assertFalse(primeiros & seguintes)
        self.janela.paginacao.ir_para(3)
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 1)
        self.janela.filtro_genero.setCurrentIndex(self.janela.filtro_genero.findData("RPG"))
        self.aguardar_http()
        self.assertEqual(self.janela.paginacao.pagina, 1)
        self.janela.filtro_plataforma.setCurrentIndex(self.janela.filtro_plataforma.findData("PC"))
        self.aguardar_http()
        self.janela.filtro_ano.setCurrentIndex(self.janela.filtro_ano.findData("2018"))
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 5)
        self.janela.busca.setText("Jogo 00")
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 1)
        QTest.mouseClick(self.janela.botao_inicio_logo, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        self.assertEqual(self.janela.conteudo_paginas.currentIndex(), 0)
        self.assertEqual(self.janela.lista.count(), 12)
        self.assertEqual(self.janela.paginacao.quantidade, 3)
        self.assertEqual(self.janela.busca.text(), "")
        self.assertEqual(self.janela.filtro_genero.currentData(), "")

    def test_painel_filtros_preserva_escolhas_e_limpa_sem_apagar_busca(self):
        self.repo.criar_jogo(dict(self.dados_jogo("Alpha PC"), plataforma="PC"))
        self.repo.criar_jogo(dict(self.dados_jogo("Alpha Console"), plataforma="PlayStation"))
        self.repo.criar_jogo(self.dados_jogo("Beta"))
        self.janela.atualizar()
        self.aguardar_http()
        self.assertFalse(self.janela.painel_filtros.isVisible())
        self.janela.busca.setText("Alpha")
        self.aguardar_http()
        self.assertEqual(self.janela.lista.count(), 2)
        QTest.mouseClick(self.janela.botao_filtros, Qt.MouseButton.LeftButton)
        self.assertTrue(self.janela.painel_filtros.isVisible())
        combo = self.janela.filtro_plataforma
        combo.showPopup()
        self.qt.processEvents()
        indice = combo.model().index(combo.findData("PC"), 0)
        QTest.mouseClick(combo.view().viewport(), Qt.MouseButton.LeftButton,
                         pos=combo.view().visualRect(indice).center())
        self.aguardar_http()
        self.assertTrue(self.janela.painel_filtros.isVisible())
        self.assertEqual(self.janela.lista.count(), 1)
        self.janela.ordenacao.setCurrentIndex(self.janela.ordenacao.findData("nome"))
        self.aguardar_http()
        self.assertEqual(self.janela.botao_filtros.text(), "Filtros · 2")
        QTest.mouseClick(self.janela.concluir_filtros, Qt.MouseButton.LeftButton)
        self.assertFalse(self.janela.painel_filtros.isVisible())
        QTest.mouseClick(self.janela.botao_filtros, Qt.MouseButton.LeftButton)
        self.assertEqual(combo.currentData(), "PC")
        self.assertEqual(self.janela.ordenacao.currentData(), "nome")
        QTest.mouseClick(self.janela.limpar_filtros, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        self.assertEqual(self.janela.busca.text(), "Alpha")
        self.assertEqual(self.janela.lista.count(), 2)
        self.assertEqual(self.janela.botao_filtros.text(), "Filtros")
        self.assertEqual(self.janela.ordenacao.currentData(), "cadastro")
        QTest.keyClick(self.janela.painel_filtros, Qt.Key.Key_Escape)
        self.qt.processEvents()
        self.assertFalse(self.janela.painel_filtros.isVisible())

    def test_minhas_avaliacoes_isoladas_por_perfil_e_crud(self):
        import json
        jogo = self.repo.criar_jogo(self.dados_jogo())
        minha = self.repo.criar_avaliacao(jogo["id"], {"autor_id":7, "nota":8, "comentario":"Minha opinião"})
        outra = self.repo.criar_avaliacao(jogo["id"], {"autor_id":8, "nota":4, "comentario":"Outro perfil"})
        legada = {"id":50, "jogo_id":jogo["id"], "nota":6, "comentario":"Sem autor"}
        self.repo.caminho_avaliacoes.write_text(json.dumps([minha, outra, legada]), encoding="utf-8")
        self.entrar_perfil()
        QTest.mouseClick(self.janela.botao_minhas, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        self.assertEqual(self.janela.lista_minhas.count(), 1)
        self.assertEqual(self.janela._minha_selecionada()["avaliacao"]["id"], minha["id"])
        QTest.mouseClick(self.janela.editar_minha, Qt.MouseButton.LeftButton)
        self.janela.dialogo.nota.setValue(9)
        self.janela.dialogo.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.buscar_avaliacao(minha["id"])["nota"], 9)
        self.assertEqual(self.repo.buscar_avaliacao(minha["id"])["autor_id"], 7)
        with patch.object(self.janela, "_confirmar", return_value=True):
            self.janela.excluir_minha_avaliacao()
        self.aguardar_http()
        self.assertIsNone(self.repo.buscar_avaliacao(minha["id"]))
        self.assertEqual(self.janela.lista_minhas.count(), 0)
        self.assertTrue(self.janela.vazio_minhas.isVisible())
        self.assertEqual(self.repo.buscar_avaliacao(legada["id"]), legada)
        self.entrar_perfil("Bruno", 8)
        self.aguardar_http()
        self.assertEqual(self.janela.lista_minhas.count(), 1)
        self.assertEqual(self.janela._minha_selecionada()["avaliacao"]["id"], outra["id"])
        QTest.mouseClick(self.janela.botao_inicio_logo, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        self.assertEqual(self.janela.conteudo_paginas.currentIndex(), 0)
        # A média pública inclui também a avaliação legada (nota 6).
        self.assertIn("5,00 / 10", self.janela.media.text())

    def test_minhas_paginam_pesquisam_e_tratam_falha_de_rede(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        for indice in range(8):
            self.repo.criar_avaliacao(jogo["id"], {"autor_id":7, "nota":indice,
                                                 "comentario":f"Análise {indice}"})
        self.entrar_perfil()
        self.janela.abrir_minhas_avaliacoes()
        self.aguardar_http()
        self.assertEqual(self.janela.lista_minhas.count(), 6)
        self.janela.paginacao_minhas.ir_para(2)
        self.qt.processEvents()
        self.assertEqual(self.janela.lista_minhas.count(), 2)
        self.janela.busca.setText("Análise 3")
        self.aguardar_http()
        self.assertEqual(self.janela.lista_minhas.count(), 1)
        self.assertEqual(self.janela.paginacao_minhas.pagina, 1)
        self.parar_servidor()
        self.janela.atualizar()
        self.aguardar_http()
        self.assertTrue(self.janela.erro.isVisible())
        self.assertTrue(self.janela.botao_atualizar.isEnabled())
        self.assertEqual(len(self.repo.listar_avaliacoes(jogo["id"])), 8)

    def test_opcoes_adicionais_preservam_dados_e_revelam_json_invalido(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        original = self.repo.criar_avaliacao(jogo["id"], {
            "autor_id": 7, "nota": 8,
            "metadados": {"plataforma": "PC", "tags": ["campanha"]},
        })
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.ator_local.setValue(7)
        self.janela.abrir_edicao_avaliacao(original["id"])
        formulario = self.janela.dialogo
        self.assertTrue(formulario.opcoes_metadados.isChecked())
        formulario.opcoes_metadados.click()
        self.assertFalse(formulario.area_metadados.isVisible())
        self.assertEqual(formulario.dados()["metadados"], original["metadados"])

        formulario.metadados.setPlainText('{"nota":NaN}')
        formulario.enviar()
        self.assertTrue(formulario.opcoes_metadados.isChecked())
        self.assertTrue(formulario.area_metadados.isVisible())
        self.assertTrue(formulario.erro.isVisible())
        self.assertEqual(self.repo.buscar_avaliacao(original["id"]), original)

        formulario.metadados.setPlainText('{"tags":["revisado"]}')
        formulario.opcoes_metadados.click()
        formulario.nota.setValue(9)
        formulario.enviar()
        self.aguardar_http()
        atualizada = self.repo.buscar_avaliacao(original["id"])
        self.assertEqual(atualizada["metadados"], {"tags": ["revisado"]})
        self.assertEqual(atualizada["autor_id"], 7)
        self.assertEqual(atualizada["nota"], 9)


if __name__ == "__main__":
    unittest.main()
