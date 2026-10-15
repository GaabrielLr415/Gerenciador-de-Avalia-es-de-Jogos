import json
import tempfile
import unittest
from pathlib import Path

from servidor.storage.repositorio_json import RepositorioJSON


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
        return {"nota": nota, "comentario": "Excelente"}

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


if __name__ == "__main__":
    unittest.main()
