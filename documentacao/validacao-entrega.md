# Validação da entrega - TechGames

Data: **21/10/2026**. Base de código: commit `10f48eb`, integrado na `main`
pelo merge `7d39326` (PR #17). A etapa inicial preparou a documentação local.
Uma etapa posterior, descrita ao final, adaptou o layout Qt a pedido da equipe.

## Ambiente e instalação

- Windows, 64 bits, Python **3.13.5**.
- Ambiente virtual novo em diretório temporário, sem reutilizar o `.venv` do projeto.
- Instalação a partir de `requirements.txt`: aprovada.
- Dependências principais instaladas: Flask **3.1.3**, PySide6 **6.12.0** e
  Requests **2.34.2**.
- `python -m pip check`: **No broken requirements found.**
- Código de `servidor/`, `cliente/` e `testes/` copiado para pasta temporária.
- Dados de teste e preferências Qt isolados; `QSettings` redirecionado para INI
  temporário. Nenhum cadastro de ensaio foi feito na biblioteca real.

As versões acima registram o ambiente testado. `requirements.txt` não fixa
versões; instalações futuras podem resolver versões diferentes. Python 3.10+
é a versão mínima declarada, mas somente 3.13.5 foi validado nesta execução.

## Resultados automatizados

| Verificação | Resultado |
|---|---|
| API Flask | 23 testes aprovados. |
| Persistência JSON | 23 testes aprovados. |
| Builder, Proxy e Observer | 13 testes aprovados. |
| Integração dos padrões pelas rotas | 10 testes aprovados. |
| Qt -> HTTP real -> Flask | 11 testes aprovados, sem janela visível. |
| Total | **80 aprovados; 0 falhas, 0 erros, 0 ignorados.** |
| Sintaxe | **22 arquivos Python** compilados em memória, sem erro. |

A execução completa no ambiente novo levou aproximadamente 19 segundos.
As falhas simuladas de leitura, gravação, restauração e observadores são
cenários esperados dos testes. Os testes T9.1 a T9.4 verificam construção,
persistência, validação, permissões e atualização após eventos.

Comando de descoberta usado pela revisão, em processo com preferências Qt
redirecionadas e dentro da cópia temporária:

```powershell
python -B -m unittest discover -s testes -p "test_*.py" -v
```

## Conferência adicional com HTTP real

Foram conferidas **27 requisições**, com Flask em processo separado e porta
local temporária, usando o ambiente recém-instalado:

- `/health`, cadastro, listagem, consulta, edição e exclusão de jogos.
- Publicação, listagem, edição e exclusão de avaliações.
- Duas notas 8 e 6 resultam em média 7.
- Nota fora da faixa, comentário de tipo inválido e NaN em metadados aninhados
  retornam 400 e deixam os arquivos inalterados.
- Ator 8 não pode editar nem excluir avaliação do autor 7: 403 sem gravação.
- Autor 7 edita nota 8 para 10: média passa a 8, preservando autor, IDs e
  metadados, mesmo com tentativa de sobrescrever identificadores no corpo.
- Moderador 99 exclui a nota 6: média passa a 10.
- Registro inexistente retorna 404.
- Servidor encerrado e iniciado em outro processo: dados, autor, metadados e
  média continuam disponíveis; IDs excluídos não são reutilizados.
- Entrada do cliente Qt executada com o endereço temporário; loop de eventos
  iniciado e encerrado por temporizador, sem falha. Esse teste usa modo
  `offscreen` e não constitui inspeção visual humana.
- Exclusão do jogo remove suas avaliações do JSON na cópia de teste.

HTTP 500, erros de permissão de arquivos, cascata de avaliações legadas e
falha dupla de gravação/restauração foram verificados pela suíte automatizada.
Não foram provocadas falhas nos arquivos reais.

## Conferência visual por capturas

Biblioteca (1280 x 850), detalhes do jogo e formulário de avaliação foram
renderizados e inspecionados com dados fictícios. Textos, botões, campos,
lista de avaliações e média estavam legíveis nas capturas conferidas.

O modo `offscreen` não descobriu fontes do sistema automaticamente. Foram
carregadas Segoe UI, sua variante em negrito e as fontes de símbolos/emoji
somente no processo temporário de inspeção. Após esse ajuste do ambiente,
textos e estrelas foram renderizados corretamente. Não houve alteração no Qt
do projeto. As capturas não substituem o aceite interativo em uma tela real,
com a resolução e a escala de exibição usadas na apresentação.

## Conferência documental

- Requisitos ligados aos testes em [requisitos-e-aceitacao.md](requisitos-e-aceitacao.md).
- Diagramas com classes reais do servidor e do cliente em
  [arquitetura-e-padroes.md](arquitetura-e-padroes.md).
- Instruções de instalação sem necessidade de ativar scripts no PowerShell no
  [README](../README.md).
- Contrato alinhado a autor, metadados, Proxy, média e erros tratados.
- [Roteiro de demonstração](entrega-design-patterns.md) com ações e resultados
  esperados. A divisão de responsabilidades segue as issues #1 a #5.
- Classes e métodos exibidos nos diagramas comparados à árvore sintática do
  código; links locais e blocos Markdown conferidos.
- Arquivos de código, testes e dados comparados por hash com o estado anterior
  à revisão: preservados. Somente documentos foram alterados nesta etapa.

O plano de testes disponível foi lido, e suas páginas 1 e 10 foram conferidas
visualmente. Ele pede demonstração observável dos padrões e traz os títulos
T9.1 a T9.4, mas não fixa prazo nem exige executável. Os detalhes do roteiro
foram adaptados ao contrato implementado, conforme orientação do próprio plano.

## Aceite que ainda depende da equipe

Não considerar os itens abaixo aprovados apenas pelo resultado dos testes:

- [ ] Edino e Gabriel: comparar o escopo com o enunciado completo, incluindo
  uso de IDs fictícios, comentário opcional e eventual uso de links de capas.
- [ ] Confirmar com o professor se exige executável sem instalação de Python.
  Em 21/10/2026, a equipe informou que isso ainda não foi confirmado.
- [ ] Confirmar o prazo oficial. O planejamento usa **23/10/2026**, informado
  pela equipe; o PDF não estabelece a data.
- [ ] Instalar a partir do README em **outro computador**, sem copiar `.venv`.
- [ ] Executar o roteiro pelos controles visíveis: legibilidade, navegação,
  mensagens, confirmação/cancelamento e comportamento durante falha de conexão.
- [ ] Ensaiar a apresentação e definir quais partes cada integrante explicará.
- [ ] Revisar as alterações locais antes dos commits manuais.

### Registro da validação presencial

| Item | Integrante / data | Resultado ou ajuste necessário |
|---|---|---|
| Instalação em outro computador | A preencher | Pendente. |
| CRUD de jogos e avaliações pela interface | A preencher | Pendente de aceite visual. |
| T9.1 e T9.2 | A preencher | Pendente de demonstração presencial. |
| T9.3 e T9.4 | A preencher | Pendente de demonstração presencial. |
| Reinício e falha de conexão | A preencher | Pendente de aceite visual. |
| Formato e prazo da entrega | A preencher | Confirmar com o professor. |

## Limites conhecidos

Não há transação entre arquivos nem bloqueio global de gravações simultâneas.
A restauração de cascata é uma tentativa e pode falhar. IDs locais não
autenticam usuários. Não há executável empacotado validado. Esses limites estão
documentados e devem ser explicados no escopo acadêmico, sem prometer garantias
que o código não oferece.

## Revisão posterior da interface

A interface recebeu identificação visual própria, destaques vermelhos e fundo
cinza escuro mais suave. Após revisão
do layout, a navegação foi colocada em uma barra horizontal no topo, com marca,
Início, Atualizar, Detalhes, busca e Adicionar jogo. Foram removidos a coluna
lateral e os títulos que apresentavam a tela como biblioteca. Os cards mantêm
capas e médias. Início limpa a pesquisa; Detalhes fica indisponível quando não
há um jogo carregado. Identificação local e estado da conexão ficam no rodapé.

Arquivos de código alterados nesta etapa: `cliente/telas/janela_principal.py`,
`cliente/telas/tema.py` e `cliente/telas/cards.py`. O backend, o armazenamento
JSON e a comunicação HTTP não foram alterados. O armazenamento das capas
também permanece igual: caminho local nas preferências Qt ou URL no JSON.

A suíte completa foi repetida: **80 aprovados, sem falhas, erros ou ignorados**.
Biblioteca, busca sem resultado, retorno à coleção e detalhes foram conferidos
com dados fictícios. Capturas em **1440 x 900** e **900 x 650** foram inspecionadas;
busca, ações e controles superiores permaneceram dentro da janela. As fontes
foram carregadas apenas no processo temporário de inspeção `offscreen`.

As alterações permanecem locais. Nenhum commit, push, PR ou merge foi executado
nestas etapas.

## Revisão do popup de avaliação

O formulário de avaliação recebeu painel com cantos arredondados, cabeçalho e
botão de fechamento próprios, título do jogo também na edição e destaque para
estrelas e nota numérica. Comentário e autor continuam disponíveis; os metadados
ficam numa seção recolhível. Em erro de JSON, essa seção é aberta e o editor
é trazido à área visível. Os botões permanecem fora da área de rolagem.

O formulário de jogos também recebeu o painel moderno, com campos reorganizados
e seção de capa local/link. As prévias de cadastro, edição e tamanho compacto
foram inspecionadas; os campos rolam sem retirar as ações da área visível.
O fechamento durante salvamento continua bloqueado; uma falha mantém os valores e reabilita as ações.
O fluxo de HTTP, JSON e regras de avaliação não foi alterado.

Foi adicionado um teste de integração Qt para comprovar que recolher os metadados
não descarta valores, que JSON inválido é revelado sem gravação e que uma edição
válida preserva o autor. O total passou a **81 testes aprovados**, sem falhas,
erros ou ignorados. Capturas do popup normal e do erro foram conferidas com
fontes carregadas no processo de teste, dados fictícios e preferências temporárias.

## Logo e paleta

Os destaques de navegação, botões, foco e seleção foram alinhados ao vermelho.
O fundo principal é cinza escuro (`#282b33`), com painéis e campos mais claros.
Notas mantêm suas cores de leitura. Os 81 testes continuaram aprovados.

O cabeçalho está preparado para a logo em `imagem/logo.png` (também aceita
WebP/JPG/JPEG). O carregamento foi conferido com uma imagem temporária de teste,
inclusive na janela de 900 x 650 e sem depender do diretório atual. Essa imagem
de teste não substitui a logo da equipe. Na revisão, a pasta `imagem/` estava
vazia e o caminho do arquivo original enviado na conversa foi solicitado.
