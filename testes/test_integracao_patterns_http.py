"""T9.1–T9.4 através das rotas Flask, com JSON temporário."""
import importlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from servidor.storage import repositorio_json as storage
from servidor.patterns import AvaliacaoBuilder


class IntegracaoPadroesHTTP(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.raiz = Path(temp.name)
        with (patch.object(storage, 'ARQUIVO_JOGOS_PADRAO', self.raiz/'jogos.json'),
              patch.object(storage, 'ARQUIVO_AVALIACOES_PADRAO', self.raiz/'avaliacoes.json')):
            self.api = importlib.import_module('servidor.app')
        self.repo = storage.RepositorioJSON(self.raiz/'jogos.json', self.raiz/'avaliacoes.json')
        config = patch.dict(self.api.app.config, {'REPOSITORIO': self.repo,
            'TESTING': True, 'MODERADORES_IDS': (99,), 'PROPAGATE_EXCEPTIONS': False})
        config.start()
        self.addCleanup(config.stop)
        self.client = self.api.app.test_client()
        jogo = self.client.post('/jogos', json={'nome':'Celeste', 'genero':'Plataforma',
            'plataforma':'PC', 'ano_lancamento':2018}).get_json()
        self.jogo_id = jogo['id']
        self.rota = f'/jogos/{self.jogo_id}/avaliacoes'
        self.media = f'/jogos/{self.jogo_id}/media'

    def publicar(self, nota=8):
        r = self.client.post(self.rota, json={'nota':nota, 'autor_id':7,
            'metadados':{'tags':['PC']}})
        self.assertEqual(r.status_code, 201)
        return r.get_json()

    def test_t91_builder_e_observer_utilizados_pelo_post(self):
        with patch.object(AvaliacaoBuilder, 'construir', autospec=True,
                          side_effect=AvaliacaoBuilder.construir) as construir:
            av = self.publicar(8.5)
        self.assertEqual(construir.call_count, 1)
        self.assertEqual(self.repo.buscar_avaliacao(av['id'])['metadados'], {'tags':['PC']})
        servico = self.api.obter_servico()
        # Verifica a atualização pelo evento antes de consultar a rota de média.
        self.assertEqual(servico.media._resultados[self.jogo_id]['media'], 8.5)
        self.assertEqual(self.client.get(self.media).get_json()['media'], 8.5)

    def test_t93_proxy_bloqueia_ausente_outro_e_papel_forjado(self):
        av = self.publicar()
        rota = f"/avaliacoes/{av['id']}"
        antes = {p.name:p.read_bytes() for p in self.raiz.iterdir()}
        for ator in (None, '8', '0', '-1', 'abc', '7.0', '9'*100):
            headers = {} if ator is None else {'X-Ator-Id':ator}
            with self.subTest(ator=ator):
                r = self.client.put(rota, headers=headers,
                    json={'nota':1, 'autor_id':7, 'moderador':True})
                self.assertEqual(r.status_code, 403)
                self.assertTrue(r.is_json)
                self.assertEqual(self.client.delete(rota, headers=headers).status_code, 403)
        self.assertEqual({p.name:p.read_bytes() for p in self.raiz.iterdir()}, antes)
        self.assertEqual(self.api.obter_servico().media._resultados[self.jogo_id]['media'], 8)

    def test_t93_autor_moderador_e_notificacoes_apos_put_delete(self):
        av = self.publicar(4)
        self.publicar(8)
        rota = f"/avaliacoes/{av['id']}"
        self.assertEqual(self.client.put(rota, headers={'X-Ator-Id':'7'},
            json={'nota':10}).status_code, 200)
        self.assertEqual(self.api.obter_servico().media._resultados[self.jogo_id]['media'], 9)
        self.assertEqual(self.client.delete(rota, headers={'X-Ator-Id':'99'}).status_code, 200)
        self.assertEqual(self.api.obter_servico().media._resultados[self.jogo_id]['media'], 8)

    def test_t92_invalido_nao_notifica_ou_grava(self):
        self.publicar()
        servico = self.api.obter_servico()
        with patch.object(servico.eventos, 'notificar') as evento:
            for nota in (-1, 11, True, '8'):
                self.assertEqual(self.client.post(self.rota,
                    json={'nota':nota,'autor_id':7}).status_code, 400)
            self.assertEqual(self.client.put('/avaliacoes/1', headers={'X-Ator-Id':'7'},
                json={'nota':5,'comentario':12}).status_code, 400)
        evento.assert_not_called()
        self.assertEqual(len(self.repo.listar_avaliacoes(self.jogo_id)), 1)

    def test_media_vazia_inexistente_e_reconstruida_apos_reinicio(self):
        self.assertEqual(self.client.get(self.media).get_json(),
            {'jogo_id':self.jogo_id,'quantidade':0,'media':None})
        self.assertEqual(self.client.get('/jogos/999/media').status_code, 404)
        self.publicar(6)
        reiniciado = storage.RepositorioJSON(self.raiz/'jogos.json', self.raiz/'avaliacoes.json')
        self.api.app.config['REPOSITORIO'] = reiniciado
        self.assertEqual(self.client.get(self.media).get_json()['media'], 6)
        self.assertIs(self.api.obter_servico().repositorio, reiniciado)

    def test_moderadores_definidos_apenas_na_configuracao(self):
        av = self.publicar()
        self.api.app.config['MODERADORES_IDS'] = (42,)
        rota = f"/avaliacoes/{av['id']}"
        self.assertEqual(self.client.delete(rota, headers={'X-Ator-Id':'99'}).status_code, 403)
        self.assertEqual(self.client.delete(rota, headers={'X-Ator-Id':'42'}).status_code, 200)
        self.assertIsNone(self.client.get(self.media).get_json()['media'])


if __name__ == '__main__':
    unittest.main()
