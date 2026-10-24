# Guia de leitura do código

O TechGamer tem duas partes executadas separadamente: a interface desktop
em Qt e a API HTTP em Flask. O servidor é responsável pelos arquivos JSON.
Para acompanhar o código, é útil conhecer funções, classes e dicionários em Python.

## Por onde começar

| Ordem | Arquivo | O que procurar |
|---|---|---|
| 1 | [Inicialização do cliente](../cliente/main.py) | Cria a aplicação Qt, escolhe o servidor e abre a janela. |
| 2 | [Janela principal](../cliente/telas/janela_principal.py) | `_montar_tela()` compõe as áreas; as demais ações coordenam navegação e operações. |
| 3 | [Cliente HTTP](../cliente/services/api_client.py) | Cada método corresponde a uma operação da API. `_request()` concentra envio, resposta e erros. |
| 4 | [Rotas Flask](../servidor/app.py) | Os decoradores `@app.get`, `post`, `put` e `delete` ligam uma URL à função que a atende. |
| 5 | [Validações](../servidor/validacoes.py) | Conferem os campos recebidos e devolvem dados normalizados ou uma mensagem de erro. |
| 6 | [Serviço e padrões](../servidor/patterns/avaliacoes.py) | Builder constrói avaliações, Proxy verifica permissões e Observer atualiza a média após gravação. |
| 7 | [Repositório JSON](../servidor/storage/repositorio_json.py) | Métodos públicos fazem CRUD; os auxiliares cuidam de leitura, escrita, backup e IDs. |

## Exemplo: publicar uma avaliação

1. A ação da janela abre `FormularioAvaliacao`, em [formularios.py](../cliente/telas/formularios.py).
2. O formulário reúne nota, comentário e autor e solicita o salvamento.
3. `ExecutorHTTP`, em [tarefas.py](../cliente/services/tarefas.py), executa a operação fora da thread gráfica.
4. `APIClient.cadastrar_avaliacao()` envia `POST /jogos/<id>/avaliacoes`.
5. A rota `cadastrar_avaliacao()` verifica o jogo e chama `validar_avaliacao()`.
6. `ServicoAvaliacoes.publicar()` usa o Builder e grava pelo repositório.
7. Após a gravação, o evento notifica o Observer para atualizar a média.
8. A resposta chega ao Qt por sinal. A janela mostra o resultado e atualiza os dados.

O [contrato da API](contrato-api.md) lista os campos, as rotas e os códigos de resposta.
Na edição e exclusão individual, o Proxy verifica o autor ou moderador antes da gravação.
Os IDs são locais e fictícios, sem autenticação real.
Metadados opcionais continuam disponíveis na API e no Builder. O formulário Qt
omite esse campo: no cadastro, o servidor usa `{}`; na edição, preserva os dados
atuais, inclusive se foram atualizados depois da abertura do formulário.

## Onde alterar cada parte

| Alteração | Local principal |
|---|---|
| Cores, bordas e estilos | `cliente/telas/tema.py` |
| Montagem do cabeçalho, busca ou filtros | Métodos `_montar_*` em `janela_principal.py` |
| Busca e ordenação do catálogo carregado | `_filtrar_catalogo()` em `janela_principal.py` |
| Campos dos formulários | `cliente/telas/formularios.py` |
| Desenho e carregamento das capas | `cliente/telas/cards.py` |
| Janela de detalhes e cartões de avaliações | `cliente/telas/detalhes.py` |
| Perfis locais e preferências | `cliente/telas/perfis.py` e uso de `QSettings` na janela |
| Paginação visual | `cliente/telas/paginacao.py` |
| Nova chamada HTTP | `cliente/services/api_client.py` e a rota em `servidor/app.py` |
| Regra dos campos enviados à API | `servidor/validacoes.py` |
| Construção, permissões e eventos de avaliações | `servidor/patterns/avaliacoes.py` |
| Persistência e geração de IDs | `servidor/storage/repositorio_json.py` |

As validações existem em mais de uma camada porque cada entrada tem seu papel:
o formulário orienta o usuário; a API confere o JSON recebido; o Builder e o
repositório protegem seus próprios contratos quando usados diretamente.
Os testes também chamam essas camadas separadamente.

## Convenções usadas

- Nomes de funções e variáveis são majoritariamente em português. Nomes de
  classes do Qt e métodos como `resizeEvent()` seguem a biblioteca.
- Métodos que começam com `_` são auxiliares de uso interno.
- Jogos e avaliações são dicionários. `jogo["id"]` acessa um campo obrigatório;
  `jogo.get("descricao", "")` fornece um valor padrão para um campo opcional.
- `lambda` é uma função curta, usada principalmente para conectar ações e
  entregar parâmetros a callbacks. Callbacks são funções executadas ao concluir uma operação.
- Sinais Qt conectam eventos a funções. O HTTP roda no `QThreadPool`, e os
  resultados retornam à thread gráfica antes de atualizar os widgets.

## Conferir uma alteração

Execute na raiz, com o ambiente instalado:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s testes -p "test_*.py"
```

Os testes usam arquivos e preferências temporários. Os testes Qt rodam sem
janela visível; a aparência precisa de conferência manual quando o layout mudar.
Os [documentos históricos](historico/README.md) preservam os registros anteriores;
o README e os documentos diretamente em `documentacao/` descrevem o estado atual.
