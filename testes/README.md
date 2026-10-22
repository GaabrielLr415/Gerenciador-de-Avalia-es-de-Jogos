# Testes do TechGames

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

| Arquivo | Quantidade na revisão de 21/10/2026 | Cobertura principal |
|---|---:|---|
| `test_api_flask.py` | 23 | Rotas, CRUD, validações, 400/403/404/500, campos, cascata e persistência. |
| `test_repositorio_json.py` | 23 | Arquivos, CRUD, IDs, legado, JSON estrito, corrupção, backup e falhas de cascata/restauração. |
| `test_design_patterns.py` | 13 | T9.1 a T9.4 no serviço, cópia dos dados, permissões e eventos. |
| `test_integracao_patterns_http.py` | 10 | Padrões usados pelas rotas, média, reinício e falhas de armazenamento/observadores. |
| `test_cliente_qt.py` | 12 | Qt -> HTTP -> Flask, formulários, estrelas, capas, mensagens, Proxy, média e preservação de metadados em seção recolhível. |
| **Total** | **81** | Resultados no [relatório de validação](../documentacao/validacao-entrega.md). |

Testes existentes comprovam comportamento; não se limitam à presença das classes.
As notas de avaliação dos casos T9.1 a T9.4 e seus resultados esperados estão na
[matriz de requisitos](../documentacao/requisitos-e-aceitacao.md).

## Isolamento da revisão de entrega

Além dos diretórios temporários de cada teste, a revisão de entrega utiliza uma
cópia do código e um ambiente virtual novo. O `QSettings` é redirecionado para
arquivos INI temporários antes de criar widgets, evitando alterar preferências
do aplicativo instalado. Esse redirecionamento adicional não faz parte do
comando simples de descoberta acima.

As falhas simuladas são deliberadas: testes verificam a resposta HTTP e os
arquivos após erros de leitura, substituição, observação e restauração.
Não confundir logs esperados desses cenários com uma falha da suíte.

A suíte sem janela não certifica legibilidade, tamanho das telas ou uma instalação
em outro computador. Esses itens exigem o [roteiro manual](../documentacao/entrega-design-patterns.md).
