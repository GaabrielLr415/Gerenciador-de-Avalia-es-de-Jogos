# TechGames — Contrato da API

## 1. Estrutura de Jogo

```json
{
  "id": 1,
  "nome": "Hollow Knight",
  "genero": "Metroidvania",
  "plataforma": "PC",
  "ano_lancamento": 2017,
  "descricao": "Jogo de aventura e exploração"
}
```

Regras:
- O ID é gerado pelo servidor.
- Nome, gênero, plataforma e ano de lançamento são obrigatórios.
- Descrição é opcional.
- Um jogo pode possuir várias avaliações.

## 2. Estrutura de Avaliação

```json
{
  "id": 1,
  "jogo_id": 1,
  "nota": 9,
  "comentario": "Excelente jogo!"
}
```

Regras:
- O ID é gerado pelo servidor.
- Cada avaliação pertence a um jogo existente.
- A nota deve estar entre 0 e 10.
- O comentário é opcional.
- Ao excluir um jogo, suas avaliações também serão excluídas.

## 3. Endpoints

| Método | Endpoint | Função |
|---|---|---|
| GET | /health | Verificar servidor |
| GET | /jogos | Listar jogos |
| GET | /jogos/1 | Consultar jogo |
| POST | /jogos | Cadastrar jogo |
| PUT | /jogos/1 | Editar jogo |
| DELETE | /jogos/1 | Excluir jogo |
| GET | /jogos/1/avaliacoes | Listar avaliações |
| POST | /jogos/1/avaliacoes | Criar avaliação |
| PUT | /avaliacoes/1 | Editar avaliação |
| DELETE | /avaliacoes/1 | Excluir avaliação |

## 4. Comunicação

- Cliente e servidor utilizarão JSON.
- O servidor será desenvolvido com Flask.
- O cliente utilizará Qt (PySide6).
- A comunicação ocorrerá localmente por HTTP.
- O armazenamento será realizado em arquivos JSON.
- Não serão utilizados banco de dados, APIs externas ou serviços de nuvem.

## 5. Integração

Gabriel será responsável pelos endpoints Flask.

Angélica implementará o armazenamento local, respeitando os modelos definidos.

Edino desenvolverá as telas conforme os campos especificados.

Fillipe implementará a comunicação HTTP utilizando os endpoints deste documento.

João Pedro verificará os requisitos, as validações e os testes.

Qualquer alteração neste contrato deverá ser comunicada e aprovada pela equipe antes da implementação.
