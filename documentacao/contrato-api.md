# TechGames — Contrato de integração (proposta para aprovação da equipe)

> Documento de alinhamento técnico. Gabriel e João Pedro devem validar estas decisões com o grupo até 13/10/2026. Não são especificações fornecidas pelo professor.

## 1. Objetos e campos

### Jogo
```json
{"id":1,"nome":"Hollow Knight","genero":"Metroidvania","plataforma":"PC","ano_lancamento":2017,"descricao":"Aventura e exploração"}
```
- `id`: inteiro positivo, único, gerado no servidor.
- `nome`, `genero`, `plataforma`: strings obrigatórias, não vazias depois de remover espaços.
- `ano_lancamento`: inteiro obrigatório entre 1950 e o ano atual (regra proposta, sujeito à confirmação).
- `descricao`: string opcional; omissão corresponde a `""`.

### Avaliação
```json
{"id":1,"jogo_id":1,"nota":9,"comentario":"Excelente jogo!"}
```
- `id`: inteiro positivo e único, gerado no servidor.
- `jogo_id`: inteiro positivo que identifica jogo existente.
- `nota`: número obrigatório de 0 a 10, inclusive (pode ter casas decimais).
- `comentario`: string opcional; omissão corresponde a `""`.
- Um jogo pode ter várias avaliações. Ao excluir um jogo, excluir também suas avaliações.
- Jogo sem avaliações: `media` deve ser `null`, não `0`.

## 2. Contrato HTTP

Base URL local: `http://127.0.0.1:5000`. Requisições com corpo usam `Content-Type: application/json`; respostas usam JSON.

| Método | Rota | Corpo enviado | Resposta de sucesso |
|---|---|---|---|
| GET | `/health` | — | 200, `{"status":"ok","aplicacao":"TechGames"}` |
| GET | `/jogos` | — | 200, lista `[Jogo, ...]` |
| GET | `/jogos/<id>` | — | 200, `Jogo` |
| POST | `/jogos` | Jogo sem `id` | 201, `Jogo` criado |
| PUT | `/jogos/<id>` | Campos de Jogo sem `id` | 200, `Jogo` atualizado |
| DELETE | `/jogos/<id>` | — | 200, `{"mensagem":"Jogo excluído"}` |
| GET | `/jogos/<id>/avaliacoes` | — | 200, lista `[Avaliacao, ...]` |
| POST | `/jogos/<id>/avaliacoes` | `{"nota":9,"comentario":"..."}` | 201, `Avaliacao` criada |
| PUT | `/avaliacoes/<id>` | `{"nota":8,"comentario":"..."}` | 200, `Avaliacao` atualizada |
| DELETE | `/avaliacoes/<id>` | — | 200, `{"mensagem":"Avaliação excluída"}` |

As rotas de PUT usam substituição dos campos editáveis; o cliente envia todos os campos necessários. `jogo_id` de uma avaliação não pode ser alterado.

### Exemplos

`POST /jogos`
```json
{"nome":"Hollow Knight","genero":"Metroidvania","plataforma":"PC","ano_lancamento":2017,"descricao":""}
```

`POST /jogos/1/avaliacoes`
```json
{"nota":9.5,"comentario":"Muito bom"}
```

### Erros (padrão único)
```json
{"erro":"Dados inválidos","detalhes":"O campo nome é obrigatório"}
```
- 400: JSON inválido, formato/campo inadequado ou nota fora do intervalo.
- 404: jogo ou avaliação inexistente.
- 500: falha inesperada do servidor (não divulgar rastreamento no cliente).

## 3. Contrato da camada de persistência

**Angélica** implementa um módulo `servidor/storage/repositorio_json.py`, sem importar Flask ou Qt. Interface proposta (nomes precisam ser mantidos após aprovação):

```python
class RepositorioJSON:
    def listar_jogos(self) -> list[dict]: ...
    def buscar_jogo(self, jogo_id: int) -> dict | None: ...
    def criar_jogo(self, dados: dict) -> dict: ...
    def atualizar_jogo(self, jogo_id: int, dados: dict) -> dict | None: ...
    def excluir_jogo(self, jogo_id: int) -> bool: ...
    def listar_avaliacoes(self, jogo_id: int) -> list[dict]: ...
    def buscar_avaliacao(self, avaliacao_id: int) -> dict | None: ...
    def criar_avaliacao(self, jogo_id: int, dados: dict) -> dict: ...
    def atualizar_avaliacao(self, avaliacao_id: int, dados: dict) -> dict | None: ...
    def excluir_avaliacao(self, avaliacao_id: int) -> bool: ...
```

- Armazenar dados em `dados/jogos.json` e `dados/avaliacoes.json`; iniciar ambos com `[]`.
- IDs gerados pela camada de dados; não reutilizar IDs existentes, mesmo após exclusões.
- Leitura e gravação devem lidar com arquivo inexistente sem apagar informações válidas.
- Para não bloquear Gabriel, ele pode usar um repositório de memória temporário com a **mesma interface**.
- Angélica e Gabriel definem conjuntamente como serão tratados arquivos corrompidos e gravação segura.

## 4. Responsabilidades e integração
- **Gabriel:** rotas Flask, validação e integração com `RepositorioJSON`.
- **João Pedro:** requisitos, casos de teste e padrões de projeto adequados ao código.
- **Edino:** telas Qt com os nomes de campos definidos acima; usar dados simulados inicialmente.
- **Fillipe:** cliente HTTP que consome os endpoints e apresenta os erros tratados.
- **Angélica:** persistência JSON e documentação com Gabriel.

## 5. Restrições e aprovação
- Flask no servidor e Qt no cliente, sem banco de dados, APIs de terceiros, nuvem ou serviços de IA **na aplicação entregue**.
- Testar cedo a execução autocontida exigida pelo professor; `requirements.txt` sozinho não cumpre essa regra.
- Qualquer mudança de campo, rota ou formato de resposta precisa ser discutida antes da implementação.
- **Aprovação pendente:** registrar confirmação do grupo na Issue #1 antes de considerar este contrato definitivo.
