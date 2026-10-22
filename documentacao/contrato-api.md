# Contrato da API - TechGames

Revisão técnica: 21/10/2026. Este documento descreve o comportamento implementado.
Mudanças futuras devem ser combinadas entre Flask, persistência e cliente HTTP.

## Transporte e rotas

Servidor local padrão: `http://127.0.0.1:5000`. Requisições com corpo usam
`Content-Type: application/json`. Sucessos e erros tratados pelas rotas abaixo
retornam JSON. Não há login; IDs de autor/ator são fictícios.

| Método | Rota | Sucesso | Resultado |
|---|---|---:|---|
| GET | `/health` | 200 | Estado e recursos disponíveis. |
| GET | `/jogos` | 200 | Lista de jogos; `[]` se vazia. |
| GET | `/jogos/<id>` | 200 | Jogo encontrado. |
| POST | `/jogos` | 201 | Jogo criado com ID gerado. |
| PUT | `/jogos/<id>` | 200 | Jogo atualizado. |
| DELETE | `/jogos/<id>` | 200 | Mensagem e exclusão em cascata. |
| GET | `/jogos/<id>/avaliacoes` | 200 | Lista de avaliações; `[]` se vazia. |
| POST | `/jogos/<id>/avaliacoes` | 201 | Avaliação criada pelo Builder e serviço. |
| PUT | `/avaliacoes/<id>` | 200 | Avaliação atualizada após verificação do Proxy. |
| DELETE | `/avaliacoes/<id>` | 200 | Mensagem após verificação do Proxy. |
| GET | `/jogos/<id>/media` | 200 | ID do jogo, quantidade e média. |

Não existe rota GET individual para avaliação; a consulta pública é por jogo.
Jogo ou avaliação inexistente nas operações correspondentes retorna 404.

## Verificação do servidor

```json
{
  "status": "ok",
  "aplicacao": "TechGames",
  "recursos": ["capa_url", "design_patterns", "media_servidor"]
}
```

## Listagem com médias

`GET /jogos?com_medias=1` inclui `media` e `quantidade_avaliacoes` em cada jogo.
Sem avaliações, os valores são `null` e `0`. A biblioteca Qt usa esta opção para
carregar o catálogo em uma requisição HTTP, sem consultas individuais de média.
O servidor lê as avaliações uma vez e calcula os agregados em memória, inclusive
após reinício ou alteração dos dados. Esses campos não são gravados em jogos.json.
`GET /jogos` sem o parâmetro mantém a resposta anterior, e a rota individual de
média continua disponível para os detalhes do jogo. Reinicie o Flask após atualizar.
As capas permanecem como links em `capa_url`.

## Jogos

Exemplo de corpo para POST e PUT:

```json
{
  "nome": "Celeste",
  "genero": "Plataforma",
  "plataforma": "PC",
  "ano_lancamento": 2018,
  "descricao": "Jogo de plataforma",
  "capa_url": ""
}
```

- Nome, gênero e plataforma: textos obrigatórios, não vazios após retirar espaços.
- Ano: inteiro de 1950 até o ano atual; booleano não é aceito como inteiro.
- Descrição: texto opcional, padrão `""`; omissão no PUT resulta em `""`.
- `capa_url`: texto opcional vazio ou URL HTTP/HTTPS com hostname. Na edição,
  omissão preserva a URL anterior; `""` remove o link. A validação não garante
  que a URL retorne uma imagem; o cliente trata falha de carregamento.
- O servidor gera `id`. Um ID enviado no corpo não substitui o identificador.
- PUT exige novamente os campos obrigatórios.
- DELETE remove também avaliações com e sem `autor_id`; não aplica o Proxy
  individual às avaliações da cascata.

Resposta de exclusão:

```json
{"mensagem": "Jogo excluído"}
```

## Avaliações

Exemplo de corpo para POST:

```json
{
  "autor_id": 7,
  "nota": 8.5,
  "comentario": "Gostei do jogo",
  "metadados": {"plataforma": "PC", "tags": ["campanha"]}
}
```

Resposta: objeto com os campos acima, `id` gerado e `jogo_id` obtido da rota.

| Campo | Regra |
|---|---|
| `id` | Gerado pelo repositório; não pode ser definido/substituído pelo cliente. |
| `jogo_id` | Obtido da rota no cadastro e preservado na edição. |
| `autor_id` | Inteiro positivo obrigatório em nova avaliação; booleano não é aceito. Preservado na edição. |
| `nota` | Número de 0 a 10, inclusive, permitindo decimais. Não aceita booleano, texto ou número não finito. |
| `comentario` | Texto opcional, padrão vazio; espaços externos são removidos. |
| `metadados` | Objeto JSON opcional, padrão `{}`. Rejeita NaN/Infinity e valores não serializáveis, inclusive aninhados. |

O cadastro verifica a existência do jogo, valida, utiliza o Builder e persiste.
Apenas após persistir são enviados os eventos de atualização da média.

### Edição e exclusão individual

Enviar o cabeçalho `X-Ator-Id`: dígitos ASCII que representem inteiro de
1 a 2147483647, com até 10 caracteres. O Proxy permite o autor original ou
moderador configurado em `MODERADORES_IDS` no servidor; o padrão de demonstração
é `(99,)`. Um campo `moderador` no corpo não concede permissão.

Exemplo de PUT com `X-Ator-Id: 7`:

```json
{
  "nota": 10,
  "comentario": "Avaliação revisada",
  "metadados": {"plataforma": "PC"}
}
```

- Nota é obrigatória; comentário omitido fica vazio, seguindo o PUT existente.
- Metadados omitidos preservam os anteriores; objeto enviado substitui os
  anteriores; `{}` permite limpá-los.
- `id`, `jogo_id` e `autor_id` do corpo não alteram os valores originais.
- Ausência de identificação válida ou falta de permissão retorna 403.
- Avaliações legadas sem autor são lidas sem inventar autoria; edição e exclusão
  individual ficam bloqueadas, inclusive para moderador. A cascata do jogo é mantida.
- A API aceita inteiro positivo para autor; a interface e o cabeçalho de ator
  trabalham até 2147483647. Use esse intervalo na demonstração para que o autor
  também possa se identificar ao editar. Esse limite não é autenticação.

Resposta de DELETE:

```json
{"mensagem": "Avaliação excluída"}
```

### Média

`GET /jogos/<id>/media` retorna média aritmética na escala 0-10:

```json
{"jogo_id": 1, "quantidade": 2, "media": 8.5}
```

Sem avaliações:

```json
{"jogo_id": 1, "quantidade": 0, "media": null}
```

A nulidade se aplica ao agregado sem notas, não ao objeto jogo nem à lista de
avaliações. A consulta reconstrói o resultado a partir do JSON após reinício
e reconhece exclusões em cascata. O Qt recebe a média do servidor.

## Erros tratados

| Status | Campo `erro` | Situação |
|---|---|---|
| 400 | Dados inválidos | Corpo ausente/inválido, campo obrigatório, tipo ou valor inválido. |
| 403 | Acesso negado | Identificação/permissão inválida ou alteração individual de legado sem autor. |
| 404 | Não encontrado | Jogo ou avaliação inexistente nas rotas de dados. |
| 500 | Erro interno do servidor | Falha interna ou de leitura/gravação, inclusive permissão de arquivos. |

Formato:

```json
{"erro": "Dados inválidos", "detalhes": "O campo 'nota' é obrigatório."}
```

Em falha interna, `detalhes` é `"Não foi possível concluir a operação."`,
sem expor caminhos ou rastreamento ao cliente. Falhas dos observadores após
salvamento são registradas, os outros observadores continuam e o sucesso da
operação persistida é mantido. A próxima consulta da média tenta reconstruí-la.
Isso não converte uma falha anterior de persistência em sucesso.

O envelope acima se refere aos erros tratados da aplicação. Não se promete
esse formato para toda URL ou método não existente no Flask.

## Persistência e limites

`RepositorioJSON` mantém jogos, avaliações e histórico em
`dados/jogos.json`, `dados/avaliacoes.json` e `dados/.contadores_id.json`.
Os métodos públicos estão no [diagrama](arquitetura-e-padroes.md).

IDs não são reduzidos após exclusão. Contadores podem ser elevados ao preservar
registros preexistentes, mesmo se uma exclusão depois falhar. Isso evita reutilização.
Arquivos ausentes são criados; conteúdo inválido pode gerar backup e recuperação.
Contadores corrompidos geram erro.

A gravação é atômica por arquivo. Na cascata, falha ao gravar avaliações provoca
tentativa de restauração dos jogos. Uma falha de restauração também é informada.
Não há transação entre arquivos nem bloqueio global de concorrência.

## Responsabilidades e validação

Gabriel: Flask e integração. Angélica: JSON e documentação. Edino: requisitos,
padrões e T9.1 a T9.4. Fillipe: Qt. João Pedro: comunicação HTTP.

Consulte [a matriz de requisitos](requisitos-e-aceitacao.md),
[os testes](../testes/README.md) e [o relatório](validacao-entrega.md).
A conferência visual, instalação em outra máquina e eventual exigência de
executável permanecem itens de aceite da equipe.
