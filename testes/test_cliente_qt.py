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

from PySide6.QtCore import QPoint, QThread, QTimer, Qt
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
        QTest.mouseClick(self.janela.editar_jogo, Qt.MouseButton.LeftButton)
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
        self.assertEqual(formulario.nota.value(), 9.5)
        self.assertEqual(formulario.valor_estrelas.text(), "4,75 / 5")
        formulario.comentario.setPlainText("Excelente aventura!")
        QTest.mouseClick(formulario.botao_salvar, Qt.MouseButton.LeftButton)
        self.aguardar_http()
        avaliacao = self.repo.listar_avaliacoes(jogo_id)[0]
        self.assertEqual(avaliacao["nota"], 9.5)
        self.assertEqual(avaliacao["autor_id"], 7)
        self.assertIn("9,50 / 10", self.janela.media.text())
        self.assertEqual(self.janela.sucesso_detalhes.text(), "Avaliação publicada com sucesso.")
        self.assertTrue(self.janela.sucesso_detalhes.isVisible())

        # Editar no cliente deve preservar metadados existentes no servidor.
        self.repo.atualizar_avaliacao(avaliacao["id"], {"nota": 9.5, "metadados": {"origem": "teste"}})
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.tabela.setCurrentCell(0, 0)
        QTest.mouseClick(self.janela.editar_avaliacao, Qt.MouseButton.LeftButton)
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
        self.janela.tabela.setCurrentCell(0, 0)
        with patch.object(self.janela, "_confirmar", return_value=False):
            self.janela.remover_avaliacao()
        self.assertIsNotNone(self.repo.buscar_avaliacao(avaliacao["id"]))
        with patch.object(self.janela, "_confirmar", return_value=True):
            self.janela.remover_avaliacao()
        self.aguardar_http()
        self.assertEqual(self.janela.tabela.rowCount(), 0)
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
        self.janela.tabela.setCurrentCell(0, 0)
        self.assertFalse(self.janela.editar_avaliacao.isEnabled())
        self.assertFalse(self.janela.excluir_avaliacao.isEnabled())
        self.assertEqual(self.janela.comentario.toPlainText(), "Legada")
        self.janela.tabela.setCurrentCell(1, 0)
        self.assertTrue(self.janela.editar_avaliacao.isEnabled())
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

    def test_card_abre_avaliacao_em_outra_janela_para_o_jogo_clicado(self):
        self.repo.criar_jogo(self.dados_jogo("Primeiro"))
        segundo = self.repo.criar_jogo(self.dados_jogo("Segundo"))
        self.janela.atualizar()
        self.aguardar_http()
        self.assertFalse(self.janela.janela_detalhes.isVisible())
        self.assertIsNone(self.janela.dialogo)
        item = self.janela.lista.item(1)
        QTest.mouseClick(self.janela.lista.viewport(), Qt.MouseButton.LeftButton,
                         pos=self.janela.lista.visualItemRect(item).center())
        self.esperar(lambda: self.janela.dialogo is not None and self.janela.dialogo.isVisible())
        formulario = self.janela.dialogo
        self.assertIn("Segundo", formulario.windowTitle())
        formulario.nota.setValue(8.5)
        formulario.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.listar_avaliacoes(segundo["id"])[0]["nota"], 8.5)
        self.assertEqual(self.repo.listar_avaliacoes(1), [])
        self.assertFalse(self.janela.janela_detalhes.isVisible())

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
        self.assertEqual(estrelas.nota, 9.5)
        QTest.keyClick(estrelas, Qt.Key.Key_Left)
        self.assertEqual(estrelas.nota, 9)
        QTest.keyClick(estrelas, Qt.Key.Key_Right)
        self.assertEqual(estrelas.nota, 9.5)
        QTest.mouseClick(estrelas, Qt.MouseButton.LeftButton, pos=QPoint(234, 24))
        self.assertEqual(estrelas.nota, 10)
        QTest.keyClick(estrelas, Qt.Key.Key_Right)
        self.assertEqual(estrelas.nota, 10)
        QTest.keyClick(estrelas, Qt.Key.Key_Home)
        QTest.keyClick(estrelas, Qt.Key.Key_Left)
        self.assertEqual(estrelas.nota, 0)
        estrelas.definir_nota(9.5)
        self.assertEqual(estrelas.nota, 9.5)

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
        self.janela.tabela.setCurrentCell(0, 0)
        self.janela.abrir_edicao_avaliacao()
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
        self.janela.abrir_edicao_avaliacao()
        formulario = self.janela.dialogo
        formulario.nota.setValue(6)
        formulario.metadados.setPlainText('{"origem":"moderacao"}')
        formulario.enviar()
        self.aguardar_http()
        self.assertEqual(self.repo.buscar_avaliacao(av["id"])["nota"], 6)
        self.assertEqual(self.repo.buscar_avaliacao(av["id"])["metadados"], {"origem":"moderacao"})
        self.assertIn("6,00 / 10", self.janela.media.text())
        self.janela.tabela.setCurrentCell(0, 0)
        with patch.object(self.janela, "_confirmar", return_value=True):
            self.janela.remover_avaliacao()
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

    def test_opcoes_adicionais_preservam_dados_e_revelam_json_invalido(self):
        jogo = self.repo.criar_jogo(self.dados_jogo())
        original = self.repo.criar_avaliacao(jogo["id"], {
            "autor_id": 7, "nota": 8,
            "metadados": {"plataforma": "PC", "tags": ["campanha"]},
        })
        self.janela.atualizar()
        self.aguardar_http()
        self.janela.ator_local.setValue(7)
        self.janela.tabela.setCurrentCell(0, 0)
        self.janela.abrir_edicao_avaliacao()
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
        formulario.nota.setValue(9.5)
        formulario.enviar()
        self.aguardar_http()
        atualizada = self.repo.buscar_avaliacao(original["id"])
        self.assertEqual(atualizada["metadados"], {"tags": ["revisado"]})
        self.assertEqual(atualizada["autor_id"], 7)
        self.assertEqual(atualizada["nota"], 9.5)


if __name__ == "__main__":
    unittest.main()
