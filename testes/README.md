# Testes do TechGamer

Responsabilidades: Edino, padrões e T9.1 a T9.4; Gabriel, API Flask e integração;
Angélica, persistência; Fillipe e João Pedro, interface e comunicação.

## Executar

Na raiz do projeto, após instalar as dependências:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s testes -p "test_*.py" -v
```

`-B` evita gerar bytecode no processo principal. Os testes de persistência usam
arquivos temporários e os testes Qt usam um servidor real em porta temporária,
com `QT_QPA_PLATFORM=offscreen` por padrão.

## Cobertura

| Arquivo | Quantidade na revisão de 24/10/2026 | Cobertura principal |
|---|---:|---|
| `test_api_flask.py` | 28 | Rotas, CRUD, validações, 400/403/404/500, campos, cascata, persistência, catálogo com médias e consulta por autor com duas leituras de arquivos. |
| `test_repositorio_json.py` | 23 | Arquivos, CRUD, IDs, legado, JSON estrito, corrupção, backup e falhas de cascata/restauração. |
| `test_design_patterns.py` | 13 | T9.1 a T9.4 no serviço, cópia dos dados, permissões e eventos. |
| `test_integracao_patterns_http.py` | 10 | Padrões usados pelas rotas, média, reinício e falhas de armazenamento/observadores. |
| `test_cliente_qt.py` | 33 | Qt -> HTTP -> Flask, formulário sem editor JSON, estrelas, capas, mensagens, Proxy, média, preservação dos metadados atuais, perfis, filtros, paginação, Minhas avaliações em uma requisição e encerramento repetido do executor sem falha nativa. |
| **Total** | **107** | Resultados no [relatório de validação](../documentacao/validacao-entrega.md). |

Testes existentes comprovam comportamento; não se limitam à presença das classes.
As notas de avaliação dos casos T9.1 a T9.4 e seus resultados esperados estão na
[matriz de requisitos](../documentacao/requisitos-e-aceitacao.md).

## Isolamento

Os testes de dados usam diretórios temporários. A suíte Qt redireciona o
`QSettings` para arquivos INI temporários antes de criar a janela, preservando
as preferências do aplicativo. O repositório padrão também é redirecionado
antes da importação da API nos testes. Não são feitos cadastros nos dados reais.
No encerramento de cada teste Qt, as tarefas terminam e as exclusões adiadas
dos widgets são processadas antes de iniciar o próximo caso.
O teste de regressão do executor roda em subprocesso e alterna 100 ciclos de
sucesso e falha, conferindo o retorno à thread gráfica e a saída normal do processo.

As falhas simuladas são deliberadas: testes verificam a resposta HTTP e os
arquivos após erros de leitura, substituição, observação e restauração.
Não confundir logs esperados desses cenários com uma falha da suíte.

A suíte sem janela não certifica legibilidade, tamanho das telas ou uma instalação
em outro computador. Esses itens exigem o [roteiro manual](../documentacao/entrega-design-patterns.md).
