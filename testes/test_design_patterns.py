"""T9.1–T9.4: padrões reais sobre persistência JSON em diretório temporário."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from servidor.patterns import AvaliacaoBuilder, ServicoAvaliacoes, AvaliacoesProxy
from servidor.storage.repositorio_json import RepositorioJSON


class TestPadroes(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raiz = Path(self.temp.name)
        self.repo = RepositorioJSON(self.raiz / 'jogos.json', self.raiz / 'avaliacoes.json')
        self.jogo = self.repo.criar_jogo(dict(nome='Celeste', genero='Plataforma',
                                            plataforma='PC', ano_lancamento=2018))
        self.servico = ServicoAvaliacoes(self.repo)
        self.autor = AvaliacoesProxy(self.servico, 7)
        self.outro = AvaliacoesProxy(self.servico, 8)
        self.moderador = AvaliacoesProxy(self.servico, 99, moderadores=(99,))

    def publicar(self, nota=8):
        return self.autor.publicar(self.jogo['id'], {'nota': nota, 'comentario': ' Bom '})

    def arquivos(self):
        return {p.name: p.read_bytes() for p in self.raiz.iterdir() if p.is_file()}

    def test_t91_publicar_construir_persistir_e_reiniciar(self):
        av = self.autor.publicar(self.jogo['id'], {
            'nota': 8.5, 'comentario': ' Bom ', 'metadados': {'tags': ['PC']}})
        reiniciado = RepositorioJSON(self.raiz/'jogos.json', self.raiz/'avaliacoes.json')
        self.assertEqual(reiniciado.buscar_avaliacao(av['id']), av)
        self.assertEqual(av['autor_id'], 7)
        self.assertEqual(av['comentario'], 'Bom')
        self.assertEqual(av['metadados'], {'tags': ['PC']})
        self.assertEqual(ServicoAvaliacoes(reiniciado).media.consultar(self.jogo['id'])['media'], 8.5)

    def test_t92_notas_limites_e_decimais(self):
        for nota in (0, 10, 5.25):
            with self.subTest(nota=nota):
                self.assertEqual(self.publicar(nota)['nota'], nota)

    def test_t92_invalidos_nao_alteram_arquivos(self):
        antes = self.arquivos()
        for nota in (-1, 11, True, None, '8', float('nan'), float('inf')):
            with self.subTest(nota=nota), self.assertRaises(ValueError):
                self.publicar(nota)
            self.assertEqual(self.arquivos(), antes)
        for comentario in (None, 1, [], {}):
            with self.subTest(comentario=comentario), self.assertRaises(ValueError):
                self.autor.publicar(self.jogo['id'], {'nota': 7, 'comentario': comentario})
        self.assertEqual(self.arquivos(), antes)

    def test_t92_metadados_invalidos(self):
        for metadados in ([], None, {'x': float('inf')}, {'lista': [float('nan')]}):
            with self.subTest(metadados=metadados), self.assertRaises(ValueError):
                self.autor.publicar(self.jogo['id'], {'nota': 7, 'metadados': metadados})

    def test_t93_autor_edita_e_media_atualiza(self):
        av = self.publicar(4)
        self.publicar(8)
        self.assertEqual(self.servico.media.consultar(self.jogo['id'])['media'], 6)
        editada = self.autor.editar(av['id'], {'nota': 10, 'autor_id': 123, 'jogo_id': 999})
        self.assertEqual(editada['autor_id'], 7)
        self.assertEqual(editada['jogo_id'], self.jogo['id'])
        self.assertEqual(self.servico.media._resultados[self.jogo['id']]['media'], 9)

    def test_t93_moderador_edita_e_exclui(self):
        av = self.publicar()
        self.assertEqual(self.moderador.editar(av['id'], {'nota': 6})['nota'], 6)
        self.assertTrue(self.moderador.excluir(av['id']))
        self.assertIsNone(self.servico.media._resultados[self.jogo['id']]['media'])
        self.assertEqual(self.servico.media.consultar(self.jogo['id'])['quantidade'], 0)

    def test_t93_outro_ator_bloqueado_sem_gravacao(self):
        av = self.publicar()
        antes = self.arquivos()
        with self.assertRaises(PermissionError):
            self.outro.editar(av['id'], {'nota': 1, 'autor_id': 8, 'moderador': True})
        with self.assertRaises(PermissionError):
            self.outro.excluir(av['id'])
        self.assertEqual(self.arquivos(), antes)

    def test_t94_builder_independente_e_copia_profunda(self):
        metadados = {'tags': ['PC']}
        builder = AvaliacaoBuilder().com_autor(7).com_nota(9).com_metadados(metadados)
        metadados['tags'].append('externo')
        av = builder.construir()
        av['metadados']['tags'].append('resultado')
        self.assertEqual(builder.construir()['metadados'], {'tags': ['PC']})
        with self.assertRaises(ValueError):
            AvaliacaoBuilder().construir()

    def test_t94_notifica_apos_publicar_editar_excluir(self):
        observador = Mock()
        self.servico.eventos.inscrever(observador)
        av = self.publicar()
        self.autor.editar(av['id'], {'nota': 5})
        self.autor.excluir(av['id'])
        self.assertEqual(observador.atualizar.call_count, 3)
        observador.atualizar.assert_called_with(self.jogo['id'])
        self.servico.eventos.remover(observador)
        self.publicar()
        self.assertEqual(observador.atualizar.call_count, 3)

    def test_falha_de_persistencia_nao_notifica(self):
        observador = Mock()
        self.servico.eventos.inscrever(observador)
        with patch.object(self.repo, 'criar_avaliacao', side_effect=OSError('Disco indisponível')):
            with self.assertRaises(OSError):
                self.publicar()
        observador.atualizar.assert_not_called()

    def test_ator_invalido_e_autoria_falsa(self):
        for ator in (None, True, 0, -1, '7'):
            with self.subTest(ator=ator), self.assertRaises(PermissionError):
                AvaliacoesProxy(self.servico, ator)
        with self.assertRaises(PermissionError):
            self.autor.publicar(self.jogo['id'], {'nota': 8, 'autor_id': 9})

    def test_registros_inexistentes(self):
        with self.assertRaises(LookupError):
            self.autor.publicar(999, {'nota': 8})
        with self.assertRaises(LookupError):
            self.autor.editar(999, {'nota': 8})
        with self.assertRaises(LookupError):
            self.autor.excluir(999)


if __name__ == '__main__':
    unittest.main()
