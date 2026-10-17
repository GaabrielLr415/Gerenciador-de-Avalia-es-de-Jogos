import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from servidor.storage.repositorio_json import AvaliacaoSemAutorError, RepositorioJSON


class RepositorioJSONTestes(unittest.TestCase):
    def setUp(self) -> None:
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.diretorio_temporario.cleanup)
        self.raiz = Path(self.diretorio_temporario.name)
        self.caminho_jogos = self.raiz / "jogos.json"
        self.caminho_avaliacoes = self.raiz / "avaliacoes.json"
        self.caminho_meta = self.raiz / "contadores.json"
        self.repositorio = self.criar_repositorio()

    def criar_repositorio(self) -> RepositorioJSON:
        return RepositorioJSON(
            self.caminho_jogos,
            self.caminho_avaliacoes,
            self.caminho_meta,
        )

    @staticmethod
    def dados_jogo(nome: str = "Hollow Knight") -> dict[str, object]:
        return {
            "nome": nome,
            "genero": "Metroidvania",
            "plataforma": "PC",
            "ano_lancamento": 2017,
            "descricao": "Exploração",
        }

    @staticmethod
    def dados_avaliacao(nota: float = 9.5) -> dict[str, object]:
        return {"autor_id": 7, "nota": nota, "comentario": "Excelente"}

    def test_cria_arquivos_json_ausentes(self) -> None:
        self.assertEqual(json.loads(self.caminho_jogos.read_text(encoding="utf-8")), [])
        self.assertEqual(
            json.loads(self.caminho_avaliacoes.read_text(encoding="utf-8")), []
        )

    def test_persiste_crud_de_jogos_e_avaliacoes_apos_reinicializar(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        avaliacao = self.repositorio.criar_avaliacao(
            jogo["id"], self.dados_avaliacao()
        )

        repositorio_reiniciado = self.criar_repositorio()
        self.assertEqual(repositorio_reiniciado.buscar_jogo(jogo["id"]), jogo)
        self.assertEqual(
            repositorio_reiniciado.listar_avaliacoes(jogo["id"]), [avaliacao]
        )

        jogo_editado = repositorio_reiniciado.atualizar_jogo(
            jogo["id"], self.dados_jogo("Celeste")
        )
        avaliacao_editada = repositorio_reiniciado.atualizar_avaliacao(
            avaliacao["id"], self.dados_avaliacao(8)
        )
        self.assertEqual(jogo_editado["nome"], "Celeste")
        self.assertEqual(avaliacao_editada["nota"], 8)
        self.assertEqual(avaliacao_editada["autor_id"], 7)
        self.assertEqual(avaliacao_editada["metadados"], {})

        self.assertTrue(repositorio_reiniciado.excluir_avaliacao(avaliacao["id"]))
        self.assertIsNone(repositorio_reiniciado.buscar_avaliacao(avaliacao["id"]))

    def test_exclui_avaliacoes_em_cascata_ao_excluir_jogo(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        avaliacao = self.repositorio.criar_avaliacao(
            jogo["id"], self.dados_avaliacao()
        )

        self.assertTrue(self.repositorio.excluir_jogo(jogo["id"]))
        self.assertIsNone(self.repositorio.buscar_jogo(jogo["id"]))
        self.assertIsNone(self.repositorio.buscar_avaliacao(avaliacao["id"]))
        self.assertEqual(self.repositorio.listar_avaliacoes(jogo["id"]), [])

    def test_ids_nao_sao_reutilizados_apos_exclusao_e_reinicio(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        self.assertTrue(self.repositorio.excluir_jogo(jogo["id"]))

        repositorio_reiniciado = self.criar_repositorio()
        proximo_jogo = repositorio_reiniciado.criar_jogo(self.dados_jogo("Celeste"))
        self.assertGreater(proximo_jogo["id"], jogo["id"])

        avaliacao = repositorio_reiniciado.criar_avaliacao(
            proximo_jogo["id"], self.dados_avaliacao()
        )
        self.assertTrue(repositorio_reiniciado.excluir_avaliacao(avaliacao["id"]))

        repositorio_reiniciado = self.criar_repositorio()
        proxima_avaliacao = repositorio_reiniciado.criar_avaliacao(
            proximo_jogo["id"], self.dados_avaliacao(8)
        )
        self.assertGreater(proxima_avaliacao["id"], avaliacao["id"])

    def test_json_invalido_e_preservado_em_backup_antes_da_recuperacao(self) -> None:
        conteudo_invalido = '{"registro":'
        self.caminho_jogos.write_text(conteudo_invalido, encoding="utf-8")
        self.caminho_avaliacoes.write_text(conteudo_invalido, encoding="utf-8")

        repositorio = self.criar_repositorio()

        self.assertEqual(repositorio.listar_jogos(), [])
        self.assertEqual(repositorio.listar_avaliacoes(1), [])
        self.assertEqual(
            self.caminho_jogos.with_suffix(".json.bak").read_text(encoding="utf-8"),
            conteudo_invalido,
        )
        self.assertEqual(
            self.caminho_avaliacoes.with_suffix(".json.bak").read_text(
                encoding="utf-8"
            ),
            conteudo_invalido,
        )

    def test_json_com_codificacao_invalida_e_preservado_em_backup(self) -> None:
        conteudo_invalido = b"\xff"
        self.caminho_jogos.write_bytes(conteudo_invalido)

        repositorio = self.criar_repositorio()

        self.assertEqual(repositorio.listar_jogos(), [])
        self.assertEqual(
            self.caminho_jogos.with_suffix(".json.bak").read_bytes(),
            conteudo_invalido,
        )

    def test_registros_com_id_invalido_sao_removidos_com_backup(self) -> None:
        registros = [
            {"id": 1, "nome": "Valido"},
            {"id": True, "nome": "Booleano não é ID válido"},
            {"id": 0, "nome": "ID não positivo"},
            {"nome": "Sem ID"},
        ]
        conteudo_original = json.dumps(registros)
        self.caminho_jogos.write_text(conteudo_original, encoding="utf-8")

        repositorio = self.criar_repositorio()

        self.assertEqual(repositorio.listar_jogos(), [registros[0]])
        self.assertEqual(
            self.caminho_jogos.with_suffix(".json.bak").read_text(encoding="utf-8"),
            conteudo_original,
        )

    def test_contadores_corrompidos_nao_sao_descartados_silenciosamente(self) -> None:
        conteudo_invalido = "{"
        self.caminho_meta.write_text(conteudo_invalido, encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "contadores de ID está corrompido"):
            self.repositorio.criar_jogo(self.dados_jogo())

        self.assertEqual(
            self.caminho_meta.with_suffix(".json.bak").read_text(encoding="utf-8"),
            conteudo_invalido,
        )

    def arquivos_atuais(self) -> dict[str, bytes]:
        return {p.name: p.read_bytes() for p in self.raiz.iterdir() if p.is_file()}

    def test_campos_da_avaliacao_persistem_sem_aceitar_ids_do_cliente(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        metadados = {"origem": "local", "tags": ["aventura"], "extra": {"ativo": True}}
        avaliacao = self.repositorio.criar_avaliacao(
            jogo["id"],
            {**self.dados_avaliacao(), "id": 999, "jogo_id": 999, "metadados": metadados},
        )
        self.assertEqual(avaliacao, {
            "id": 1, "jogo_id": jogo["id"], "autor_id": 7,
            "nota": 9.5, "comentario": "Excelente", "metadados": metadados,
        })
        reiniciado = self.criar_repositorio()
        self.assertEqual(reiniciado.buscar_avaliacao(avaliacao["id"]), avaliacao)
        self.assertEqual(reiniciado.listar_avaliacoes(jogo["id"]), [avaliacao])

    def test_edicao_preserva_autor_ids_e_metadados_omitidos(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        avaliacao = self.repositorio.criar_avaliacao(
            jogo["id"], {**self.dados_avaliacao(), "metadados": {"origem": "local"}},
        )
        atualizada = self.repositorio.atualizar_avaliacao(
            avaliacao["id"],
            {"nota": 8, "comentario": "Editada", "id": 999, "jogo_id": 999, "autor_id": 999},
        )
        self.assertEqual(atualizada, {**avaliacao, "nota": 8, "comentario": "Editada"})
        self.assertEqual(self.criar_repositorio().buscar_avaliacao(avaliacao["id"]), atualizada)

    def test_edicao_substitui_e_permite_limpar_metadados(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        avaliacao = self.repositorio.criar_avaliacao(
            jogo["id"], {**self.dados_avaliacao(), "metadados": {"anterior": True}},
        )
        for metadados in ({"novo": {"itens": [1, None]}}, {}):
            with self.subTest(metadados=metadados):
                atualizada = self.repositorio.atualizar_avaliacao(
                    avaliacao["id"], {"nota": 8, "metadados": metadados},
                )
                self.assertEqual(atualizada["metadados"], metadados)
                self.assertEqual(self.criar_repositorio().buscar_avaliacao(avaliacao["id"]), atualizada)

    def test_criacao_exige_autor_positivo_sem_consumir_id_em_erro(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        antes = self.arquivos_atuais()
        invalidos = [{"nota": 9}] + [
            {"autor_id": autor, "nota": 9}
            for autor in (None, True, False, 0, -1, 1.5, "7", [], {})
        ]
        for dados in invalidos:
            with self.subTest(dados=dados), self.assertRaises(ValueError):
                self.repositorio.criar_avaliacao(jogo["id"], dados)
            self.assertEqual(self.arquivos_atuais(), antes)

    def test_metadados_invalidos_nao_alteram_arquivos(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        avaliacao = self.repositorio.criar_avaliacao(jogo["id"], self.dados_avaliacao())
        antes = self.arquivos_atuais()
        for metadados in (None, [], "texto", 1, True):
            dados = {**self.dados_avaliacao(), "metadados": metadados}
            with self.subTest(metadados=metadados):
                with self.assertRaises(ValueError):
                    self.repositorio.criar_avaliacao(jogo["id"], dados)
                with self.assertRaises(ValueError):
                    self.repositorio.atualizar_avaliacao(avaliacao["id"], dados)
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_metadados_nao_finitos_sao_rejeitados_sem_gravar_ou_consumir_ids(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        avaliacao = self.repositorio.criar_avaliacao(jogo["id"], self.dados_avaliacao())
        antes = self.arquivos_atuais()
        for valor in (float("nan"), float("inf"), float("-inf")):
            for metadados in (
                {"valor": valor},
                {"lista": [1, valor]},
                {"objeto": {"lista": [None, {"valor": valor}]}},
            ):
                with self.subTest(metadados=metadados):
                    dados = {**self.dados_avaliacao(), "metadados": metadados}
                    with self.assertRaisesRegex(ValueError, "JSON estrito"):
                        self.repositorio.criar_avaliacao(jogo["id"], dados)
                    with self.assertRaisesRegex(ValueError, "JSON estrito"):
                        self.repositorio.atualizar_avaliacao(avaliacao["id"], dados)
                    self.assertEqual(self.arquivos_atuais(), antes)

    def test_metadados_nao_serializaveis_sao_rejeitados_sem_gravar(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        avaliacao = self.repositorio.criar_avaliacao(jogo["id"], self.dados_avaliacao())
        circular = {}
        circular["proprio"] = circular
        antes = self.arquivos_atuais()
        for metadados in ({"valor": {1, 2}}, {"valor": object()}, circular):
            with self.subTest(tipo=type(metadados.get("valor")).__name__):
                dados = {**self.dados_avaliacao(), "metadados": metadados}
                with self.assertRaisesRegex(ValueError, "JSON estrito"):
                    self.repositorio.criar_avaliacao(jogo["id"], dados)
                with self.assertRaisesRegex(ValueError, "JSON estrito"):
                    self.repositorio.atualizar_avaliacao(avaliacao["id"], dados)
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_metadados_json_validos_sao_preservados_sem_confundir_textos(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        metadados = {
            "textos": ["NaN", "Infinity", "-Infinity"],
            "objeto": {"valores": [None, True, False, 0, -2, 1.25, 1e200]},
        }
        avaliacao = self.repositorio.criar_avaliacao(
            jogo["id"], {**self.dados_avaliacao(), "metadados": metadados},
        )
        atualizada = self.repositorio.atualizar_avaliacao(avaliacao["id"], {
            "nota": 8, "metadados": metadados,
        })
        self.assertEqual(atualizada["metadados"], metadados)
        self.assertEqual(self.criar_repositorio().buscar_avaliacao(avaliacao["id"]), atualizada)
        json.loads(
            self.caminho_avaliacoes.read_text(encoding="utf-8"),
            parse_constant=lambda valor: self.fail(f"JSON inválido gravado: {valor}"),
        )

    def test_leitura_legada_nao_inventa_autor_nem_regrava_arquivo(self) -> None:
        legado = {"id": 3, "jogo_id": 1, "nota": 8, "comentario": "Antiga"}
        self.caminho_avaliacoes.write_text(json.dumps([legado]), encoding="utf-8")
        antes = self.arquivos_atuais()
        reiniciado = self.criar_repositorio()
        self.assertEqual(reiniciado.buscar_avaliacao(3), legado)
        self.assertEqual(reiniciado.listar_avaliacoes(1), [legado])
        self.assertEqual(self.arquivos_atuais(), antes)

    def test_legadas_nao_podem_ser_editadas_ou_excluidas_individualmente(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        legado = {"id": 3, "jogo_id": jogo["id"], "nota": 8, "comentario": "Antiga"}
        self.caminho_avaliacoes.write_text(json.dumps([legado]), encoding="utf-8")
        antes = self.arquivos_atuais()
        with self.assertRaises(AvaliacaoSemAutorError):
            self.repositorio.atualizar_avaliacao(3, self.dados_avaliacao())
        with self.assertRaises(AvaliacaoSemAutorError):
            self.repositorio.excluir_avaliacao(3)
        self.assertEqual(self.arquivos_atuais(), antes)

    def test_cascata_remove_legadas_e_novas_preservando_outros_jogos_e_ids(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        outro_jogo = self.repositorio.criar_jogo(self.dados_jogo("Celeste"))
        nova = self.repositorio.criar_avaliacao(jogo["id"], self.dados_avaliacao())
        mantida = self.repositorio.criar_avaliacao(outro_jogo["id"], self.dados_avaliacao())
        antiga = {"id": 3, "jogo_id": jogo["id"], "nota": 8, "comentario": "Antiga"}
        outra_antiga = {"id": 4, "jogo_id": outro_jogo["id"], "nota": 7}
        self.caminho_avaliacoes.write_text(
            json.dumps([nova, mantida, antiga, outra_antiga]), encoding="utf-8",
        )

        self.assertTrue(self.repositorio.excluir_jogo(jogo["id"]))
        reiniciado = self.criar_repositorio()
        self.assertIsNone(reiniciado.buscar_jogo(jogo["id"]))
        self.assertEqual(reiniciado.listar_avaliacoes(jogo["id"]), [])
        self.assertEqual(reiniciado.listar_avaliacoes(outro_jogo["id"]), [mantida, outra_antiga])
        self.assertEqual(reiniciado.buscar_jogo(outro_jogo["id"]), outro_jogo)
        proxima = reiniciado.criar_avaliacao(outro_jogo["id"], self.dados_avaliacao())
        self.assertGreater(proxima["id"], outra_antiga["id"])

    def test_autor_invalido_persistido_tambem_nao_autoriza_alteracao(self) -> None:
        for autor in (None, True, 0, -1, "7"):
            with self.subTest(autor=autor):
                legado = {"id": 3, "jogo_id": 1, "autor_id": autor, "nota": 8}
                self.caminho_avaliacoes.write_text(json.dumps([legado]), encoding="utf-8")
                antes = self.arquivos_atuais()
                with self.assertRaises(AvaliacaoSemAutorError):
                    self.repositorio.atualizar_avaliacao(3, self.dados_avaliacao())
                with self.assertRaises(AvaliacaoSemAutorError):
                    self.repositorio.excluir_avaliacao(3)
                self.assertEqual(self.arquivos_atuais(), antes)

    def test_registro_com_autor_sem_metadados_recebe_padrao_na_edicao(self) -> None:
        registro = {"id": 3, "jogo_id": 1, "autor_id": 7, "nota": 8, "comentario": ""}
        self.caminho_avaliacoes.write_text(json.dumps([registro]), encoding="utf-8")
        atualizada = self.repositorio.atualizar_avaliacao(3, {"nota": 9})
        self.assertEqual(atualizada, {**registro, "nota": 9, "metadados": {}})

    def test_falha_na_cascata_restaura_todos_os_campos(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        self.repositorio.criar_avaliacao(
            jogo["id"], {**self.dados_avaliacao(), "metadados": {"tags": ["local"]}},
        )
        antiga = {"id": 2, "jogo_id": jogo["id"], "nota": 8, "comentario": "Antiga"}
        avaliacoes = self.repositorio.listar_avaliacoes(jogo["id"])
        self.caminho_avaliacoes.write_text(json.dumps([*avaliacoes, antiga]), encoding="utf-8")
        contadores = self.repositorio._ler_contadores()
        contadores["ultimo_id_avaliacao"] = antiga["id"]
        self.repositorio._salvar_contadores(contadores)
        antes = self.arquivos_atuais()
        salvar = self.repositorio._salvar_lista

        def falhar_avaliacoes(caminho, dados):
            if caminho == self.caminho_avaliacoes:
                raise OSError("Falha simulada nas avaliações")
            return salvar(caminho, dados)

        with patch.object(self.repositorio, "_salvar_lista", side_effect=falhar_avaliacoes):
            with self.assertRaisesRegex(OSError, "Falha simulada nas avaliações"):
                self.repositorio.excluir_jogo(jogo["id"])
        self.assertEqual(self.arquivos_atuais(), antes)

    def test_falha_dupla_da_cascata_preserva_causas(self) -> None:
        jogo = self.repositorio.criar_jogo(self.dados_jogo())
        self.repositorio.criar_avaliacao(jogo["id"], self.dados_avaliacao())
        salvar = self.repositorio._salvar_lista
        falha_avaliacoes = OSError("Falha nas avaliações")
        falha_restauracao = OSError("Falha na restauração")
        gravacoes_jogos = 0

        def falhar(caminho, dados):
            nonlocal gravacoes_jogos
            if caminho == self.caminho_avaliacoes:
                raise falha_avaliacoes
            gravacoes_jogos += 1
            if gravacoes_jogos == 2:
                raise falha_restauracao
            return salvar(caminho, dados)

        with patch.object(self.repositorio, "_salvar_lista", side_effect=falhar):
            with self.assertRaisesRegex(RuntimeError, "inconsistentes") as contexto:
                self.repositorio.excluir_jogo(jogo["id"])
        self.assertIs(contexto.exception.__cause__, falha_restauracao)
        self.assertIs(falha_restauracao.__context__, falha_avaliacoes)


if __name__ == "__main__":
    unittest.main()
