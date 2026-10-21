import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from servidor.storage import repositorio_json as storage


class APIFlaskTestes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Importar app inicializa o repositório padrão: redireciona-o antes da importação.
        temporario = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporario.cleanup)
        raiz = Path(temporario.name)
        with (
            patch.object(storage, "ARQUIVO_JOGOS_PADRAO", raiz / "jogos.json"),
            patch.object(storage, "ARQUIVO_AVALIACOES_PADRAO", raiz / "avaliacoes.json"),
        ):
            cls.api = importlib.import_module("servidor.app")

    def setUp(self) -> None:
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.raiz = Path(temporario.name)
        self.repositorio = self.criar_repositorio()
        configuracao = patch.dict(self.api.app.config, {
            "REPOSITORIO": self.repositorio,
            "TESTING": True,
            "PROPAGATE_EXCEPTIONS": False,
        })
        configuracao.start()
        self.addCleanup(configuracao.stop)
        self.cliente = self.api.app.test_client()
        self.cliente.environ_base["HTTP_X_ATOR_ID"] = "7"

    def criar_repositorio(self):
        return storage.RepositorioJSON(
            self.raiz / "jogos.json",
            self.raiz / "avaliacoes.json",
            self.raiz / "contadores.json",
        )

    @staticmethod
    def dados_jogo():
        return {
            "nome": "Hollow Knight", "genero": "Metroidvania",
            "plataforma": "PC", "ano_lancamento": 2017,
        }

    @staticmethod
    def dados_avaliacao():
        return {"autor_id": 7, "nota": 9.5, "comentario": "Excelente"}

    def criar_jogo(self):
        resposta = self.cliente.post("/jogos", json=self.dados_jogo())
        self.assertEqual(resposta.status_code, 201)
        return resposta.get_json()

    def criar_avaliacao(self, jogo_id, **campos):
        resposta = self.cliente.post(
            f"/jogos/{jogo_id}/avaliacoes", json={**self.dados_avaliacao(), **campos},
        )
        self.assertEqual(resposta.status_code, 201)
        return resposta.get_json()

    def arquivos_atuais(self):
        return {p.name: p.read_bytes() for p in self.raiz.iterdir() if p.is_file()}

    def verificar_erro(self, resposta, status):
        self.assertEqual(resposta.status_code, status)
        self.assertTrue(resposta.is_json)
        self.assertEqual(set(resposta.get_json()), {"erro", "detalhes"})

    def test_health_e_endpoints_preservados(self):
        self.assertEqual(self.cliente.get("/health").get_json(), {
            "status": "ok", "aplicacao": "TechGames", "recursos": ["capa_url", "design_patterns", "media_servidor"],
        })
        rotas = {
            (metodo, regra.rule)
            for regra in self.api.app.url_map.iter_rules() if regra.endpoint != "static"
            for metodo in regra.methods - {"OPTIONS", "HEAD"}
        }
        self.assertEqual(rotas, {
            ("GET", "/health"), ("GET", "/jogos"), ("POST", "/jogos"),
            ("GET", "/jogos/<int:jogo_id>"), ("PUT", "/jogos/<int:jogo_id>"),
            ("DELETE", "/jogos/<int:jogo_id>"),
            ("GET", "/jogos/<int:jogo_id>/avaliacoes"),
            ("GET", "/jogos/<int:jogo_id>/media"),
            ("POST", "/jogos/<int:jogo_id>/avaliacoes"),
            ("PUT", "/avaliacoes/<int:avaliacao_id>"),
            ("DELETE", "/avaliacoes/<int:avaliacao_id>"),
        })

    def test_crud_jogos(self):
        self.assertEqual(self.cliente.get("/jogos").get_json(), [])
        jogo = self.criar_jogo()
        rota = f"/jogos/{jogo['id']}"
        self.assertEqual(self.cliente.get(rota).get_json(), jogo)
        self.assertEqual(self.cliente.get("/jogos").get_json(), [jogo])
        resposta = self.cliente.put(rota, json={**self.dados_jogo(), "nome": "Celeste", "id": 999})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["nome"], "Celeste")
        self.assertEqual(resposta.get_json()["id"], jogo["id"])
        self.assertEqual(self.cliente.delete(rota).status_code, 200)
        self.verificar_erro(self.cliente.get(rota), 404)

    def test_crud_avaliacoes_com_todos_os_campos(self):
        jogo = self.criar_jogo()
        rota = f"/jogos/{jogo['id']}/avaliacoes"
        self.assertEqual(self.cliente.get(rota).get_json(), [])
        metadados = {"origem": "local", "tags": ["aventura"], "extra": {"ativo": True}}
        avaliacao = self.criar_avaliacao(jogo["id"], metadados=metadados)
        self.assertEqual(avaliacao, {
            "id": 1, "jogo_id": jogo["id"], **self.dados_avaliacao(), "metadados": metadados,
        })
        self.assertEqual(self.cliente.get(rota).get_json(), [avaliacao])
        resposta = self.cliente.put(f"/avaliacoes/{avaliacao['id']}", json={
            "nota": 8, "comentario": "  Editada  ", "metadados": {"novo": [1, None]},
        })
        self.assertEqual(resposta.status_code, 200)
        atualizada = resposta.get_json()
        self.assertEqual(atualizada, {
            **avaliacao, "nota": 8, "comentario": "Editada", "metadados": {"novo": [1, None]},
        })
        reiniciado = self.criar_repositorio()
        self.assertEqual(reiniciado.buscar_avaliacao(avaliacao["id"]), atualizada)
        self.assertEqual(self.cliente.delete(f"/avaliacoes/{avaliacao['id']}").status_code, 200)
        self.assertEqual(self.cliente.get(rota).get_json(), [])

    def test_metadados_omitidos_sao_vazios_no_cadastro_e_preservados_na_edicao(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        self.assertEqual(avaliacao["metadados"], {})
        rota = f"/avaliacoes/{avaliacao['id']}"
        self.assertEqual(self.cliente.put(rota, json={"nota": 8, "metadados": {"x": 1}}).status_code, 200)
        resposta = self.cliente.put(rota, json={"nota": 7})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["metadados"], {"x": 1})
        self.assertEqual(resposta.get_json()["autor_id"], 7)
        resposta = self.cliente.put(rota, json={"nota": 6, "metadados": {}})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["metadados"], {})

    def test_identificadores_e_autor_nao_podem_ser_sobrescritos(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"], id=999)
        # Envia jogo_id no corpo sem conflitar com o argumento do helper.
        resposta = self.cliente.post(f"/jogos/{jogo['id']}/avaliacoes", json={
            **self.dados_avaliacao(), "id": 999, "jogo_id": 999,
        })
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.get_json()["jogo_id"], jogo["id"])
        self.assertNotEqual(resposta.get_json()["id"], 999)
        for autor in (999, None, "outro"):
            with self.subTest(autor=autor):
                resposta = self.cliente.put(f"/avaliacoes/{avaliacao['id']}", json={
                    "nota": 8, "id": 999, "jogo_id": 999, "autor_id": autor,
                    "metadados": {"autor_id": 999, "id": 999},
                })
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(resposta.get_json()["id"], avaliacao["id"])
                self.assertEqual(resposta.get_json()["jogo_id"], jogo["id"])
                self.assertEqual(resposta.get_json()["autor_id"], 7)

    def test_http400_autor_obrigatorio_e_inteiro_positivo(self):
        jogo = self.criar_jogo()
        invalidos = [{"nota": 9}] + [
            {"nota": 9, "autor_id": autor}
            for autor in (None, True, False, 0, -1, 1.5, "7", [], {})
        ]
        antes = self.arquivos_atuais()
        for dados in invalidos:
            with self.subTest(dados=dados):
                self.verificar_erro(self.cliente.post(f"/jogos/{jogo['id']}/avaliacoes", json=dados), 400)
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_http400_metadados_invalidos_no_cadastro_e_edicao(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        antes = self.arquivos_atuais()
        for metadados in (None, [], "texto", 1, True):
            for metodo, rota in (
                ("POST", f"/jogos/{jogo['id']}/avaliacoes"),
                ("PUT", f"/avaliacoes/{avaliacao['id']}"),
            ):
                with self.subTest(metadados=metadados, metodo=metodo):
                    self.verificar_erro(self.cliente.open(
                        rota, method=metodo, json={**self.dados_avaliacao(), "metadados": metadados},
                    ), 400)
                    self.assertEqual(self.arquivos_atuais(), antes)

    def test_http400_metadados_nao_finitos_inclusive_aninhados(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"], metadados={"original": True})
        antes = self.arquivos_atuais()
        for valor in (float("nan"), float("inf"), float("-inf")):
            for metadados in (
                {"valor": valor},
                {"lista": [1, valor]},
                {"objeto": {"lista": [None, {"valor": valor}]}},
            ):
                for metodo, rota in (
                    ("POST", f"/jogos/{jogo['id']}/avaliacoes"),
                    ("PUT", f"/avaliacoes/{avaliacao['id']}"),
                ):
                    with self.subTest(metadados=metadados, metodo=metodo):
                        resposta = self.cliente.open(rota, method=metodo, json={
                            **self.dados_avaliacao(), "metadados": metadados,
                        })
                        self.verificar_erro(resposta, 400)
                        self.assertIn("JSON estrito", resposta.get_json()["detalhes"])
                        self.assertEqual(self.arquivos_atuais(), antes)

    def test_http400_metadados_com_expoente_que_excede_float(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        antes = self.arquivos_atuais()
        for metodo, rota in (
            ("POST", f"/jogos/{jogo['id']}/avaliacoes"),
            ("PUT", f"/avaliacoes/{avaliacao['id']}"),
        ):
            with self.subTest(metodo=metodo):
                resposta = self.cliente.open(
                    rota, method=metodo, content_type="application/json",
                    data='{"autor_id":7,"nota":8,"metadados":{"lista":[{"valor":1e400}]}}',
                )
                self.verificar_erro(resposta, 400)
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_metadados_json_validos_inclusive_textos_nan_e_infinity(self):
        jogo = self.criar_jogo()
        metadados = {
            "textos": ["NaN", "Infinity", "-Infinity"],
            "objeto": {"valores": [None, True, False, 0, -2, 1.25, 1e200]},
        }
        avaliacao = self.criar_avaliacao(jogo["id"], metadados=metadados)
        self.assertEqual(avaliacao["metadados"], metadados)
        resposta = self.cliente.put(f"/avaliacoes/{avaliacao['id']}", json={
            "nota": 8, "metadados": metadados,
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()["metadados"], metadados)
        json.loads(
            resposta.get_data(as_text=True),
            parse_constant=lambda valor: self.fail(f"Resposta JSON inválida: {valor}"),
        )
        self.assertEqual(
            self.criar_repositorio().buscar_avaliacao(avaliacao["id"]), resposta.get_json(),
        )

    def test_validacoes_existentes_de_avaliacoes(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        invalidos = [{"autor_id": 7}] + [
            {"autor_id": 7, "nota": nota} for nota in (None, True, -0.1, 10.1, "9", [])
        ] + [{**self.dados_avaliacao(), "comentario": comentario} for comentario in (None, 1, [])]
        for dados in invalidos:
            for metodo, rota in (
                ("POST", f"/jogos/{jogo['id']}/avaliacoes"), ("PUT", f"/avaliacoes/{avaliacao['id']}"),
            ):
                with self.subTest(dados=dados, metodo=metodo):
                    self.verificar_erro(self.cliente.open(rota, method=metodo, json=dados), 400)
        for nota in (0, 10, 5.25):
            self.criar_avaliacao(jogo["id"], nota=nota)

    def test_validacoes_existentes_de_jogos(self):
        jogo = self.criar_jogo()
        invalidos = [{}]
        for campo in ("nome", "genero", "plataforma", "ano_lancamento"):
            dados = self.dados_jogo()
            del dados[campo]
            invalidos.append(dados)
        for campo in ("nome", "genero", "plataforma"):
            for valor in (None, "", "  ", 42):
                invalidos.append({**self.dados_jogo(), campo: valor})
        for ano in (1949, datetime.now().year + 1, True, "2017", 2017.5):
            invalidos.append({**self.dados_jogo(), "ano_lancamento": ano})
        invalidos.append({**self.dados_jogo(), "descricao": None})
        for dados in invalidos:
            for metodo, rota in (("POST", "/jogos"), ("PUT", f"/jogos/{jogo['id']}")):
                with self.subTest(dados=dados, metodo=metodo):
                    self.verificar_erro(self.cliente.open(rota, method=metodo, json=dados), 400)

    def test_corpos_invalidos_retornam_http400(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        for metodo, rota in (
            ("POST", "/jogos"), ("PUT", f"/jogos/{jogo['id']}"),
            ("POST", f"/jogos/{jogo['id']}/avaliacoes"), ("PUT", f"/avaliacoes/{avaliacao['id']}"),
        ):
            for corpo, tipo in (("{", "application/json"), ("null", "application/json"),
                                ("[]", "application/json"), ("", "application/json"), ("{}", "text/plain")):
                with self.subTest(metodo=metodo, rota=rota, corpo=corpo):
                    self.verificar_erro(self.cliente.open(rota, method=metodo, data=corpo, content_type=tipo), 400)

    def test_registros_inexistentes_retornam_http404(self):
        for metodo, rota in (
            ("GET", "/jogos/999"), ("PUT", "/jogos/999"), ("DELETE", "/jogos/999"),
            ("GET", "/jogos/999/avaliacoes"), ("POST", "/jogos/999/avaliacoes"),
            ("PUT", "/avaliacoes/999"), ("DELETE", "/avaliacoes/999"),
        ):
            with self.subTest(metodo=metodo, rota=rota):
                self.verificar_erro(self.cliente.open(rota, method=metodo, json=self.dados_avaliacao()), 404)

    def test_legadas_sao_lidas_sem_autoria_e_bloqueadas_para_alteracao(self):
        jogo = self.criar_jogo()
        legado = {"id": 5, "jogo_id": jogo["id"], "nota": 8, "comentario": "Antiga"}
        self.repositorio.caminho_avaliacoes.write_text(json.dumps([legado]), encoding="utf-8")
        antes = self.arquivos_atuais()
        self.assertEqual(self.cliente.get(f"/jogos/{jogo['id']}/avaliacoes").get_json(), [legado])
        self.assertEqual(self.criar_repositorio().buscar_avaliacao(5), legado)
        for metodo, rota in (("PUT", "/avaliacoes/5"), ("DELETE", "/avaliacoes/5")):
            with self.subTest(metodo=metodo, rota=rota):
                self.verificar_erro(self.cliente.open(rota, method=metodo, json=self.dados_avaliacao()), 403)
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_exclusao_de_jogo_com_avaliacao_legada_retorna200(self):
        jogo = self.criar_jogo()
        legado = {"id": 5, "jogo_id": jogo["id"], "nota": 8, "comentario": "Antiga"}
        self.repositorio.caminho_avaliacoes.write_text(json.dumps([legado]), encoding="utf-8")
        resposta = self.cliente.delete(f"/jogos/{jogo['id']}")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json(), {"mensagem": "Jogo excluído"})
        reiniciado = self.criar_repositorio()
        self.assertIsNone(reiniciado.buscar_jogo(jogo["id"]))
        self.assertEqual(reiniciado.listar_avaliacoes(jogo["id"]), [])
        self.assertIsNone(reiniciado.buscar_avaliacao(legado["id"]))
        self.api.app.config["REPOSITORIO"] = reiniciado
        proximo_jogo = self.criar_jogo()
        proxima_avaliacao = self.criar_avaliacao(proximo_jogo["id"])
        self.assertGreater(proxima_avaliacao["id"], legado["id"])

    def test_cascata_preserva_avaliacoes_de_outro_jogo(self):
        primeiro, segundo = self.criar_jogo(), self.criar_jogo()
        self.criar_avaliacao(primeiro["id"], metadados={"x": 1})
        mantida = self.criar_avaliacao(segundo["id"], autor_id=8, metadados={"y": 2})
        self.assertEqual(self.cliente.delete(f"/jogos/{primeiro['id']}").status_code, 200)
        reiniciado = self.criar_repositorio()
        self.assertEqual(reiniciado.listar_avaliacoes(primeiro["id"]), [])
        self.assertEqual(reiniciado.listar_avaliacoes(segundo["id"]), [mantida])

    def test_http500_nas_rotas_de_dados_nao_expoe_causa(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        casos = (
            ("GET", "/jogos", "listar_jogos", None),
            ("POST", "/jogos", "criar_jogo", self.dados_jogo()),
            ("GET", f"/jogos/{jogo['id']}", "buscar_jogo", None),
            ("PUT", f"/jogos/{jogo['id']}", "atualizar_jogo", self.dados_jogo()),
            ("DELETE", f"/jogos/{jogo['id']}", "excluir_jogo", None),
            ("GET", f"/jogos/{jogo['id']}/avaliacoes", "listar_avaliacoes", None),
            ("POST", f"/jogos/{jogo['id']}/avaliacoes", "criar_avaliacao", self.dados_avaliacao()),
            ("PUT", f"/avaliacoes/{avaliacao['id']}", "atualizar_avaliacao", {"nota": 8}),
            ("DELETE", f"/avaliacoes/{avaliacao['id']}", "excluir_avaliacao", None),
        )
        antes = self.arquivos_atuais()
        for metodo, rota, operacao, corpo in casos:
            with self.subTest(rota=rota, metodo=metodo):
                with patch.object(self.repositorio, operacao, side_effect=OSError("Causa simulada")):
                    with self.assertLogs(self.api.app.logger, level="ERROR"):
                        resposta = self.cliente.open(rota, method=metodo, json=corpo)
                self.verificar_erro(resposta, 500)
                self.assertEqual(resposta.get_json(), {
                    "erro": "Erro interno do servidor", "detalhes": "Não foi possível concluir a operação.",
                })
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_permissionerror_de_leitura_retorna500_sem_expor_caminhos(self):
        jogo = self.criar_jogo()
        self.criar_avaliacao(jogo["id"])
        antes = self.arquivos_atuais()
        ler = Path.read_text
        casos = (
            ("/jogos", self.repositorio.caminho_jogos),
            (f"/jogos/{jogo['id']}/avaliacoes", self.repositorio.caminho_avaliacoes),
            (f"/jogos/{jogo['id']}/media", self.repositorio.caminho_avaliacoes),
        )
        for rota, arquivo in casos:
            with self.subTest(rota=rota):
                def falhar(caminho, *args, **kwargs):
                    if caminho == arquivo:
                        raise PermissionError(13, "Acesso negado", str(arquivo))
                    return ler(caminho, *args, **kwargs)

                with patch.object(Path, "read_text", new=falhar):
                    with self.assertLogs(self.api.app.logger, level="ERROR"):
                        resposta = self.cliente.get(rota)
                self.verificar_erro(resposta, 500)
                self.assertEqual(resposta.get_json(), {
                    "erro": "Erro interno do servidor", "detalhes": "Não foi possível concluir a operação.",
                })
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_permissionerror_de_gravacao_retorna500_e_preserva_dados(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        antes = self.arquivos_atuais()
        substituir = storage.os.replace
        casos = (
            ("PUT", f"/jogos/{jogo['id']}", self.dados_jogo(), self.repositorio.caminho_jogos),
            ("PUT", f"/avaliacoes/{avaliacao['id']}", {"nota": 6}, self.repositorio.caminho_avaliacoes),
            ("DELETE", f"/avaliacoes/{avaliacao['id']}", None, self.repositorio.caminho_avaliacoes),
            ("DELETE", f"/jogos/{jogo['id']}", None, self.repositorio.caminho_avaliacoes),
        )
        for metodo, rota, corpo, arquivo in casos:
            with self.subTest(metodo=metodo, rota=rota):
                def falhar(origem, destino):
                    if Path(destino) == arquivo:
                        raise PermissionError(13, "Acesso negado", str(arquivo))
                    return substituir(origem, destino)

                with patch.object(storage.os, "replace", side_effect=falhar):
                    with self.assertLogs(self.api.app.logger, level="ERROR"):
                        resposta = self.cliente.open(rota, method=metodo, json=corpo)
                self.verificar_erro(resposta, 500)
                self.assertEqual(resposta.get_json(), {
                    "erro": "Erro interno do servidor", "detalhes": "Não foi possível concluir a operação.",
                })
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_falha_na_cascata_retorna500_e_restaura_jogo(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"], metadados={"origem": "local"})
        antes = self.arquivos_atuais()
        substituir = storage.os.replace

        def falhar_avaliacoes(origem, destino):
            if Path(destino) == self.repositorio.caminho_avaliacoes:
                raise OSError("Falha simulada")
            return substituir(origem, destino)

        with patch.object(storage.os, "replace", side_effect=falhar_avaliacoes):
            with self.assertLogs(self.api.app.logger, level="ERROR"):
                resposta = self.cliente.delete(f"/jogos/{jogo['id']}")
        self.verificar_erro(resposta, 500)
        self.assertEqual(self.arquivos_atuais(), antes)
        self.assertEqual(self.criar_repositorio().buscar_avaliacao(avaliacao["id"]), avaliacao)

    def test_campos_persistem_em_outro_processo_python(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"], metadados={"extra": {"tags": ["local"]}})
        resposta = self.cliente.put(f"/avaliacoes/{avaliacao['id']}", json={"nota": 8, "comentario": "Editada"})
        self.assertEqual(resposta.status_code, 200)
        codigo = (
            "import json,sys; from pathlib import Path; "
            "from servidor.storage.repositorio_json import RepositorioJSON; "
            "p=Path(sys.argv[1]); r=RepositorioJSON(p/'jogos.json',p/'avaliacoes.json',p/'contadores.json'); "
            "print(json.dumps(r.buscar_avaliacao(int(sys.argv[2]))))"
        )
        resultado = subprocess.run(
            [sys.executable, "-B", "-c", codigo, str(self.raiz), str(avaliacao["id"])],
            cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, check=True,
        )
        self.assertEqual(json.loads(resultado.stdout), resposta.get_json())

    def test_ids_nao_reutilizados_apos_cascata_e_reinicio(self):
        jogo = self.criar_jogo()
        avaliacao = self.criar_avaliacao(jogo["id"])
        self.assertEqual(self.cliente.delete(f"/jogos/{jogo['id']}").status_code, 200)
        self.api.app.config["REPOSITORIO"] = self.criar_repositorio()
        proximo_jogo = self.criar_jogo()
        proxima_avaliacao = self.criar_avaliacao(proximo_jogo["id"])
        self.assertGreater(proximo_jogo["id"], jogo["id"])
        self.assertGreater(proxima_avaliacao["id"], avaliacao["id"])


if __name__ == "__main__":
    unittest.main()
