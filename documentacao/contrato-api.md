# TechGames — Contrato de Integração da API

## 1. Objetivo

Este documento define a estrutura dos dados, as rotas HTTP e as regras de comunicação entre o servidor Flask, a interface gráfica Qt (PySide6) e o armazenamento local em JSON.

O TechGames é um aplicativo desktop para gerenciamento pessoal de jogos e avaliações.

O sistema permite cadastrar, consultar, editar e excluir jogos, além de registrar avaliações com notas de 0 a 10 e comentários.

A aplicação não possui login, cadastro de usuários ou compartilhamento de avaliações pela internet.

Este contrato foi elaborado pela equipe para orientar o desenvolvimento. Não representa uma especificação fornecida diretamente pelo professor.

## 2. Estrutura dos dados

### 2.1. Jogo

Exemplo de um jogo armazenado:

```json
{
  "id": 1,
  "nome": "Hollow Knight",
  "genero": "Metroidvania",
  "plataforma": "PC",
  "ano_lancamento": 2017,
  "descricao": "Aventura e exploração"
}
```

**Regras dos campos:**

- `id`: número inteiro positivo, único e gerado automaticamente pelo servidor.
- `nome`: texto obrigatório e não vazio.
- `genero`: texto obrigatório e não vazio.
- `plataforma`: texto obrigatório e não vazio.
- `ano_lancamento`: número inteiro obrigatório, entre 1950 e o ano atual.
- `descricao`: texto opcional; quando não informado, será armazenado como uma string vazia (`""`).

Os identificadores são gerados automaticamente e não devem ser reutilizados após a exclusão de um jogo.

### 2.2. Avaliação

Exemplo de uma avaliação armazenada:

```json
{
  "id": 1,
  "jogo_id": 1,
  "nota": 9.5,
  "comentario": "Excelente jogo!"
}
```

**Regras dos campos:**

- `id`: número inteiro positivo, único e gerado automaticamente pelo servidor.
- `jogo_id`: identificador do jogo ao qual a avaliação pertence.
- `nota`: número obrigatório entre 0 e 10, inclusive, permitindo valores decimais.
- `comentario`: texto opcional; quando não informado, será armazenado como uma string vazia (`""`).

**Regras de funcionamento:**

- Um jogo pode possuir várias avaliações.
- Uma avaliação deve estar associada a um jogo existente.
- Ao excluir um jogo, todas as avaliações associadas a ele também serão excluídas.
- Quando um jogo não possuir avaliações, a consulta retornará uma lista vazia (`[]`).
- O campo `jogo_id` não poderá ser modificado durante a edição de uma avaliação.

O cálculo da média das avaliações não faz parte do contrato atual da API.

## 3. Contrato HTTP

O servidor Flask disponibiliza uma API local no endereço:

`http://127.0.0.1:5000`

As requisições que enviam dados deverão utilizar:

`Content-Type: application/json`

As respostas das rotas da API serão fornecidas no formato JSON.

### 3.1. Endpoints

| Método | Rota | Funcionalidade | Sucesso |
|---|---|---|---|
| GET | `/health` | Verificar o servidor | 200 |
| GET | `/jogos` | Listar jogos | 200 |
| GET | `/jogos/<id>` | Buscar jogo pelo ID | 200 |
| POST | `/jogos` | Cadastrar jogo | 201 |
| PUT | `/jogos/<id>` | Atualizar jogo | 200 |
| DELETE | `/jogos/<id>` | Excluir jogo | 200 |
| GET | `/jogos/<id>/avaliacoes` | Listar avaliações do jogo | 200 |
| POST | `/jogos/<id>/avaliacoes` | Cadastrar avaliação | 201 |
| PUT | `/avaliacoes/<id>` | Atualizar avaliação | 200 |
| DELETE | `/avaliacoes/<id>` | Excluir avaliação | 200 |

### 3.2. Verificação do servidor

**GET `/health`**

Resposta esperada:

```json
{
  "status": "ok",
  "aplicacao": "TechGames"
}
```

### 3.3. Cadastro de jogos

**POST `/jogos`**

Exemplo de requisição:

```json
{
  "nome": "Hollow Knight",
  "genero": "Metroidvania",
  "plataforma": "PC",
  "ano_lancamento": 2017,
  "descricao": "Aventura e exploração"
}
```

O servidor valida os dados, gera automaticamente um ID e salva o jogo no arquivo JSON.

Em caso de sucesso, retorna HTTP 201 com os dados do jogo cadastrado.

### 3.4. Consulta de jogos

**GET `/jogos`**

Retorna uma lista com todos os jogos cadastrados.

Quando não existirem jogos, retorna:

```json
[]
```

**GET `/jogos/<id>`**

Retorna os dados do jogo correspondente ao identificador informado.

Quando o jogo não existir, retorna HTTP 404.

### 3.5. Atualização de jogos

**PUT `/jogos/<id>`**

Permite atualizar os dados de um jogo existente.

O cliente deverá enviar os campos obrigatórios do jogo, seguindo as mesmas regras de validação utilizadas no cadastro.

O identificador do jogo permanece inalterado.

### 3.6. Exclusão de jogos

**DELETE `/jogos/<id>`**

Exclui o jogo informado e suas avaliações associadas.

Resposta de sucesso:

```json
{
  "mensagem": "Jogo excluído"
}
```

Se o jogo não existir, o servidor retorna HTTP 404.

### 3.7. Cadastro de avaliações

**POST `/jogos/<id>/avaliacoes`**

Exemplo de requisição:

```json
{
  "nota": 9.5,
  "comentario": "Muito bom"
}
```

O servidor verifica se o jogo existe, valida a nota, gera o identificador da avaliação e salva os dados no JSON.

Em caso de sucesso, retorna HTTP 201.

### 3.8. Consulta de avaliações

**GET `/jogos/<id>/avaliacoes`**

Retorna as avaliações associadas ao jogo informado.

Quando o jogo existe, mas não possui avaliações, retorna:

```json
[]
```

Quando o jogo não existe, retorna HTTP 404.

### 3.9. Atualização de avaliações

**PUT `/avaliacoes/<id>`**

Permite modificar a nota e o comentário de uma avaliação existente.

Exemplo:

```json
{
  "nota": 8,
  "comentario": "Avaliação atualizada"
}
```

O identificador da avaliação e o identificador do jogo associado não poderão ser alterados.

### 3.10. Exclusão de avaliações

**DELETE `/avaliacoes/<id>`**

Exclui uma avaliação existente.

Resposta de sucesso:

```json
{
  "mensagem": "Avaliação excluída"
}
```

Caso a avaliação não exista, retorna HTTP 404.

## 4. Validação dos dados

### 4.1. Jogos

O servidor deverá rejeitar:

- Jogos sem nome, gênero, plataforma ou ano de lançamento.
- Nome, gênero ou plataforma vazios.
- Campos textuais obrigatórios contendo valores que não sejam strings.
- Ano de lançamento que não seja um número inteiro.
- Ano inferior a 1950 ou superior ao ano atual.
- Descrição com tipo de dado inválido.

### 4.2. Avaliações

O servidor deverá rejeitar:

- Avaliações sem nota.
- Notas menores que 0.
- Notas maiores que 10.
- Notas com tipo de dado inválido.
- Comentários que não sejam strings.

As validações são realizadas pelo servidor antes de enviar os dados ao repositório JSON.

## 5. Tratamento de erros

A API utiliza respostas padronizadas para os erros tratados pelo servidor.

### HTTP 400 — Dados inválidos

Exemplo:

```json
{
  "erro": "Dados inválidos",
  "detalhes": "O campo 'nome' é obrigatório."
}
```

Esse erro poderá ocorrer quando forem enviados campos inválidos, ausentes ou fora das regras estabelecidas.

### HTTP 404 — Não encontrado

Exemplo:

```json
{
  "erro": "Não encontrado",
  "detalhes": "Jogo não encontrado."
}
```

Esse erro ocorre quando um jogo ou uma avaliação solicitada não existe.

### HTTP 500 — Erro interno do servidor

Exemplo:

```json
{
  "erro": "Erro interno do servidor",
  "detalhes": "Não foi possível concluir a operação."
}
```

O servidor possui um tratamento para erros internos durante as requisições, retornando uma resposta JSON padronizada, sem divulgar o rastreamento interno ao cliente.

As falhas podem ser registradas no terminal ou nos logs do servidor para auxiliar na identificação do problema.

## 6. Camada de persistência JSON

O armazenamento dos dados é realizado pelo módulo:

`servidor/storage/repositorio_json.py`

Esse módulo implementa a classe `RepositorioJSON`, responsável por realizar as operações de armazenamento e recuperação dos registros.

A camada de persistência é independente da interface Qt e não depende diretamente das rotas Flask.

### 6.1. Métodos para jogos

- `listar_jogos()`
- `buscar_jogo(jogo_id)`
- `criar_jogo(dados)`
- `atualizar_jogo(jogo_id, dados)`
- `excluir_jogo(jogo_id)`

### 6.2. Métodos para avaliações

- `listar_avaliacoes(jogo_id)`
- `buscar_avaliacao(avaliacao_id)`
- `criar_avaliacao(jogo_id, dados)`
- `atualizar_avaliacao(avaliacao_id, dados)`
- `excluir_avaliacao(avaliacao_id)`

### 6.3. Arquivos de armazenamento

Os dados serão armazenados nos seguintes arquivos:

- `dados/jogos.json`: jogos cadastrados.
- `dados/avaliacoes.json`: avaliações cadastradas.
- `dados/.contadores_id.json`: controle dos identificadores gerados.

Os arquivos de jogos e avaliações são inicializados com listas vazias quando não existem.

### 6.4. Persistência e segurança

O repositório JSON implementa:

- Criação dos arquivos de armazenamento quando necessário.
- Recuperação dos dados após reinicialização do servidor.
- Controle de identificadores para evitar reutilização.
- Tratamento de arquivos JSON inexistentes, vazios ou inválidos.
- Criação de cópias de segurança de arquivos corrompidos.
- Gravação por meio de arquivos temporários e substituição do arquivo de destino.
- Exclusão das avaliações relacionadas quando um jogo é removido.

A gravação de jogos e avaliações ocorre em arquivos separados. Portanto, uma falha durante uma operação que modifica ambos os arquivos pode produzir uma atualização parcial. Esse cenário deverá ser considerado na revisão dos testes e da implementação.

## 7. Comunicação entre Qt e Flask

A interface gráfica será desenvolvida utilizando Python e Qt (PySide6).

A comunicação com o servidor ocorrerá por requisições HTTP à API Flask.

A interface deverá:

- Cadastrar, consultar, editar e excluir jogos.
- Cadastrar, consultar, editar e excluir avaliações.
- Apresentar os dados recebidos do servidor.
- Exibir mensagens de sucesso e erro.
- Atualizar os componentes visuais após as operações.
- Informar quando o servidor estiver indisponível.
- Permitir a utilização das funcionalidades sem exigir que o usuário execute manualmente requisições HTTP.

A interface não realizará gravação direta nos arquivos JSON. Essa responsabilidade permanecerá no servidor.

## 8. Responsabilidades da equipe

**Gabriel — Backend Flask e integração final**

Responsável pelas rotas HTTP, validação dos dados, tratamento de erros, integração com a persistência JSON e organização da integração final.

**João Pedro — Requisitos, Design Patterns e testes**

Responsável pelos requisitos funcionais e não funcionais, critérios de aceitação, análise dos padrões de projeto e auxílio na validação das funcionalidades.

**Edino — Interface gráfica Qt**

Responsável pelo desenvolvimento das telas e componentes da interface gráfica.

**Fillipe — Integração Qt e Flask**

Responsável pelo módulo de comunicação HTTP entre a interface gráfica e o servidor Flask.

**Angélica — Persistência JSON e documentação**

Responsável pelo armazenamento local em JSON, pelos testes de persistência e pela organização da documentação em conjunto com Gabriel.

## 9. Restrições técnicas

O TechGames deverá respeitar as seguintes restrições:

- Utilizar Python no desenvolvimento.
- Utilizar Flask no servidor.
- Utilizar Qt (PySide6) na interface gráfica.
- Não utilizar banco de dados.
- Não utilizar APIs externas ou serviços de nuvem.
- Não incorporar serviços de inteligência artificial à aplicação entregue.
- Armazenar as informações localmente em arquivos JSON.
- Manter a comunicação entre cliente e servidor por HTTP local.
- Permitir a execução da aplicação sem exigir instalações ou configurações adicionais do usuário final, conforme a exigência de entrega do professor.

O empacotamento e a execução final da aplicação deverão ser verificados antes da entrega.

## 10. Testes e validação

Foram executados testes manuais das principais operações do backend:

- Cadastro, consulta, edição e exclusão de jogos.
- Cadastro, consulta, edição e exclusão de avaliações.
- Persistência dos jogos e avaliações após reiniciar o servidor.
- Geração de identificadores sem reutilizar IDs excluídos.
- Exclusão em cascata de avaliações.
- Rejeição de notas acima de 10 e abaixo de 0.
- Rejeição de jogos sem campos obrigatórios.
- Tratamento de jogos inexistentes com HTTP 404.
- Tratamento simulado de falhas internas com HTTP 500 e resposta JSON.

Também foram executados os oito testes automatizados existentes do repositório JSON, todos com resultado satisfatório.

**Validações ainda pendentes:**

- Testes automatizados específicos das rotas Flask.
- Revisão de situações excepcionais de leitura e gravação.
- Testes de integração com a interface Qt.
- Testes de funcionamento completo da aplicação.
- Testes da versão preparada para entrega.

## 11. Estado de integração

O servidor Flask está implementado e integrado ao módulo `RepositorioJSON`.

O armazenamento em memória utilizado durante o desenvolvimento inicial foi substituído pela persistência local em arquivos JSON.

A implementação da persistência foi integrada à branch `main` por meio de Pull Request.

A integração com a interface gráfica, a validação final dos requisitos e a preparação da versão executável ainda dependem das entregas e dos testes conjuntos da equipe.

## 12. Aprovação e alterações no contrato

Este documento registra o contrato técnico implementado e revisado até o momento.

As definições devem ser confirmadas com a equipe, especialmente antes da integração final com a interface Qt.

Qualquer alteração nas rotas, campos, códigos de resposta ou formatos JSON deverá ser comunicada aos responsáveis pelos módulos afetados, evitando incompatibilidades entre cliente e servidor.

**Estado:** contrato atualizado conforme a implementação atual do backend e do armazenamento JSON. A validação conjunta da equipe permanece pendente.
## Atualização de integração — 21/10/2026

Esta seção substitui pendências anteriores referentes aos padrões e à identificação
em alterações de avaliações. PUT/DELETE /avaliacoes/<id> exigem X-Ator-Id:
inteiro de 1 a 2147483647. O Proxy permite autor ou moderador configurado em
MODERADORES_IDS (padrão de demonstração 99). Falta de identificação válida ou
permissão retorna HTTP 403 com o envelope JSON existente. Autor e jogo_id não
podem ser sobrescritos. POST continua exigindo autor_id e nota; o Builder valida
e constrói antes da persistência. Comentário e metadados permanecem opcionais.

GET /jogos/<id>/media retorna {"jogo_id":1,"quantidade":2,"media":8.5}.
Sem avaliações: quantidade 0 e media null. Jogo inexistente: 404. A média usa a
escala 0–10 e é atualizada pelo Observer após publicação, edição e exclusão.
/health anuncia design_patterns e media_servidor em recursos, além de capa_url.
As listas e envelopes CRUD existentes permanecem iguais. IDs são fictícios,
sem login. O cliente deve enviar o ator local em cada edição/exclusão.
