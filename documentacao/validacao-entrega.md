# Validação da entrega - TechGamer

Revisão atual: **24/10/2026**. Base: commit `45fcdf4` (merge do PR #21),
com correções locais de consulta por autor, dependências, documentação e
organização do código. As alterações desta revisão ainda não foram commitadas
nem enviadas ao GitHub.

## Resultado manual informado por Gabriel — 24/10/2026

Gabriel informou: “os testes manuais deram certo”. O resultado geral foi
registrado como **aprovado conforme relato do responsável pela execução**.
Não foram informados os resultados individuais de cada cenário, a máquina
utilizada ou se ela não tinha Python instalado. As capturas e o documento Word
também não foram apresentados nesta confirmação.

Este registro atualiza o status geral dos testes manuais. A comprovação da
execução em outro computador sem Python, as evidências no Word e a demonstração
formal dos cenários T9.1 a T9.4 continuam aguardando confirmação ou registro.

## Nova rodada de testes internos — 24/10/2026, 15h17

A pedido da equipe, os testes internos foram executados novamente. Os testes
manuais pela interface e o registro das capturas ficam com Gabriel; não foram
marcados como concluídos por esta execução automatizada.

- **107 testes aprovados em 43,690 segundos**, sem falhas, erros ou ignorados:
  API 28, Qt com HTTP 33, padrões 13, integração HTTP 10 e persistência 23.
- A suíte rodou numa cópia temporária com **54 arquivos publicáveis**, sem
  `.venv/`, `.local/` ou `dist/`, usando o Python do ambiente existente.
- Hashes antes e depois confirmaram a preservação dos arquivos originais.
- Sintaxe válida dos **29 arquivos Python** e **65 links locais** conferidos.
- As **18 dependências** coincidem com `requirements.txt`; `pip check` não
  encontrou incompatibilidades. A ajuda do cliente também abriu corretamente.
- Os **96 jogos e 4 avaliações** passaram nas validações de campos, IDs únicos
  e vínculos entre jogo e avaliação, sem alterar os JSONs.
- O ZIP `TechGamer-Windows-x64-20261024-151025.zip` passou na verificação de
  integridade e SHA-256. Extraído numa pasta temporária, o `.exe` rodou com
  PATH limitado às pastas do Windows, sem variáveis de ambiente Python.
- A conferência do executável confirmou Qt, logo, HTTP local, cadastro,
  publicação/edição de avaliação, média, consulta por autor e exclusão em cascata.
  Usou dados descartáveis; os dados reais e os dados distribuídos no ZIP
  permaneceram iguais após o teste.

Logs técnicos locais: `.local/testes-internos/20261024-151646/suite-completa.log`
e `suite-completa.json`, `.local/teste-interno-executavel.json` e
`.local/teste-interno-estatico.json`. Esses arquivos são ignorados pelo Git;
este documento registra os resultados destinados à entrega.

Esta rodada não instalou dependências num ambiente novo nem certifica outro
computador sem Python. Permanecem pendentes o teste manual, as capturas para
o Word, a conferência visual dos diagramas e a publicação no GitHub.

## Ambiente e dependências

- Windows, 64 bits, Python **3.13.5**, ambiente `.venv` existente.
- Dependências principais: Flask **3.1.3**, PySide6 **6.12.0** e Requests **2.34.2**.
- `requirements.txt` fixa as dependências diretas e transitivas presentes neste ambiente.
- `python -m pip check`: **No broken requirements found.**
- `python -m pip install --dry-run --no-index -r requirements.txt`: todos os
  requisitos já satisfeitos, sem baixar ou alterar pacotes.

A revisão atual verifica o ambiente instalado. Não foi feita nova instalação
em ambiente vazio ou em outro computador. Python 3.13.5 é a versão efetivamente
testada; a faixa aceita pelas dependências não representa teste de todas as versões.

## Resultados automatizados atuais

| Verificação | Resultado |
|---|---:|
| API Flask | 28 aprovados |
| Persistência JSON | 23 aprovados |
| Builder, Proxy e Observer | 13 aprovados |
| Integração dos padrões por HTTP | 10 aprovados |
| Qt com HTTP real, sem janela visível | 33 aprovados |
| **Total** | **107 aprovados; 0 falhas, 0 erros, 0 ignorados** |

A execução após a consulta por autor levou **38,410 segundos**. A suíte completa
foi repetida após a reorganização e após a simplificação do formulário.
A execução final em cópia isolada levou **44,331 segundos**, com os **107 testes
aprovados**. Ela inclui o ajuste de exibição das notas inteiras e a regressão
do ciclo de vida do executor HTTP.
Comando de descoberta:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s testes -p "test_*.py"
```

Os testes usam arquivos temporários. A suíte Qt redireciona o `QSettings`
para INI temporário e usa servidor HTTP local em porta temporária. Jogos,
avaliações e preferências reais não são usados para cadastros de ensaio.
Falhas simuladas de leitura, gravação, restauração e observadores são cenários
esperados; seus logs não significam que a suíte falhou.

## Consulta de Minhas avaliações

Antes, cada atualização consultava o catálogo e as avaliações de cada jogo:
com 97 jogos, eram **98 requisições HTTP**. Agora, o Qt consulta
`GET /autores/<autor_id>/avaliacoes` em **uma requisição por atualização**.
O servidor lê jogos e avaliações uma vez cada e cruza os registros em memória.
A resposta inclui os jogos correspondentes e vem em ordem decrescente do ID
da avaliação. Downloads de capas são operações separadas.

Evidências acrescentadas nesta revisão:

- `test_avaliacoes_por_autor_filtra_ordena_e_le_arquivos_uma_vez`: catálogo
  com 97 jogos, autoria, ordem, campos completos, duas leituras e ausência de
  gravação; exclui legadas, autor inválido e registros sem jogo correspondente.
- `test_avaliacoes_por_autor_vazias_e_autor_zero`: ausência de avaliações ou
  autor desconhecido retorna lista vazia; ID zero retorna 400.
- `test_avaliacoes_por_autor_refletem_edicao_exclusao_cascata_e_reinicio`:
  consulta reconhece alteração persistida, reinício, exclusão e cascata.
- `test_minhas_carregam_97_jogos_em_uma_requisicao_por_atualizacao`: Qt usa
  uma requisição ao abrir e atualizar a lista; busca não inicia novo HTTP.

Os testes existentes continuam cobrindo troca de perfil, edição/exclusão,
paginação, busca, falha de rede e preservação de dados. As regras do Proxy
continuam aplicadas à edição e exclusão individual.

## Organização e leitura do código

- A montagem da janela foi dividida em métodos por área. `_montar_tela()`
  apresenta a composição; busca e filtros do catálogo têm etapas identificadas.
- As validações dos corpos JSON foram extraídas para `servidor/validacoes.py`.
  As rotas continuam em `servidor/app.py`, usando essas mesmas regras.
- O fluxo antigo de avaliação direta pelo card, sem chamadas ou sinais ligados,
  foi removido. O card continua abrindo detalhes, onde o usuário pode avaliar.
- Foram removidos placeholders `.gitkeep` e um arquivo de saída do Git na raiz.
  Os documentos em subpastas repetidas foram preservados em `historico/`.
- O [guia do código](guia-do-codigo.md) explica a ordem de leitura e onde alterar cada parte.

## Formulário de avaliação simplificado

O editor de metadados JSON e a seção Opções adicionais foram removidos do Qt.
O formulário apresenta estrelas, nota, comentário opcional e identificação local
do autor. O suporte a metadados continua na API, no Builder e no armazenamento.
O formulário omite esse campo nas requisições: novas avaliações recebem `{}` e
edições preservam os valores atuais no servidor, sem reenviar uma cópia antiga.

Os testes Qt de cadastro e edição foram adaptados para conferir o formulário
sem editor JSON, os campos enviados e a preservação de metadados alterados
depois da abertura do formulário. O teste de moderação também confere a
preservação desses dados. As validações de JSON permanecem cobertas pela API,
pelo repositório e pelos padrões.

As primeiras execuções após essa mudança foram interrompidas por uma falha
nativa do Qt. O encerramento das janelas de teste foi ajustado para aguardar
as tarefas e processar as exclusões adiadas antes do próximo caso. A checagem
final em cópia isolada voltou a reproduzir a falha e motivou a correção do
executor descrita abaixo.

Capturas offscreen do cadastro em 580 x 660 e da edição em 540 x 500 foram
inspecionadas com dados fictícios. O editor técnico não aparece; as ações ficam
visíveis e os campos podem ser rolados no tamanho compacto.

Os documentos principais refletem a navegação atual: Início, Minhas avaliações,
Atualizar, busca e avatar; filtros e Adicionar jogo junto à coleção; detalhes
abertos pelo card; perfis locais sem senha; paginação adaptável à janela.
A logo SVG existente e os formatos alternativos estão descritos no README do
cliente. Contrato, diagramas e matriz de requisitos incluem a consulta por autor.

A conferência desta revisão usou testes, leitura do código e as capturas do
formulário descritas acima. Não houve inspeção visual interativa de toda a aplicação.

## Checagem final em cópia isolada

Foram copiados **49 arquivos** que compõem a árvore publicável, considerando os
arquivos novos e as exclusões locais. `.git/`, `.venv/`, `.local/`, logs e caches
ficaram fora da cópia. Os testes rodaram nessa pasta temporária, com o Python e
as dependências já instaladas. Não se trata de uma nova instalação de pacotes.

A falha nativa foi reproduzida em um programa pequeno que criava e encerrava
executores repetidamente. Os objetos de sinais agora pertencem ao executor
na thread gráfica, a conclusão usa conexão enfileirada e a liberação usa
`deleteLater()`. Esse tratamento segue as regras de propriedade e threads de
[QObject](https://doc.qt.io/qt-6/qobject.html) e
[QThreadPool](https://doc.qt.io/qt-6/qthreadpool.html).

O programa que falhava passou por **300 ciclos** após a correção. Foi acrescentado
`test_executor_pode_ser_encerrado_apos_sucesso_ou_falha_sem_erro_nativo`, que executa
100 ciclos alternando sucesso e falha em subprocesso, verifica callbacks na
thread gráfica e exige saída normal. A suíte completa terminou com 107 aprovados.

Também passaram: `python -m cliente --help`, `pip check`, sintaxe de todos os
arquivos Python, links locais da documentação e conferência das versões fixadas.
Hashes dos arquivos locais antes e depois da execução confirmaram sua preservação.
Os dados atuais passaram nas validações: **96 jogos e 4 avaliações**, IDs únicos,
referências válidas entre registros e campos compatíveis com a API. Nenhum jogo
estava com a descrição vazia nessa conferência.

## Histórico das revisões anteriores

Em 21/10/2026, o relatório anterior registrou instalação em ambiente virtual
novo, 27 requisições de conferência com Flask em processo separado e inspeção
de capturas offscreen da biblioteca, detalhes e formulários. As etapas de
layout/popup elevaram a suíte de 80 para 81 testes. A revisão histórica de
22/10/2026 registrou 95 testes e a otimização do catálogo; esse trabalho foi
integrado pelo PR #21. Essas contagens correspondem ao código de cada época.
A referência atual é a tabela de **107 testes** acima.

Essas evidências anteriores não substituem o aceite humano da interface atual
ou uma instalação em outra máquina. O [registro de 22/10](revisao-issues-2026-10-22.md)
preserva a auditoria das issues daquela data; nenhuma issue foi atualizada
ou encerrada nesta revisão.

## Aceite que ainda depende da equipe

- [ ] Edino e Gabriel: conferir o escopo com o enunciado completo, incluindo
  identificação fictícia, comentário opcional e links de capas.
- [ ] Confirmar com o professor o prazo oficial. O planejamento da equipe usava
  23/10/2026; o enunciado não fixa a data.
- [x] Gerar e conferir o pacote portátil Windows, incluindo Python, Flask e Qt.
- [x] Receber o resultado geral dos testes manuais: Gabriel informou aprovação em 24/10/2026.
- [ ] Abrir o pacote em outro computador sem Python e registrar a execução no Word.
- [ ] Registrar os resultados por cenário, as capturas e a resolução/escala usada nos testes manuais.
- [ ] Ensaiar a apresentação e definir as falas de cada integrante.
- [ ] Revisar e integrar as alterações locais.

## Preparação dos arquivos para o GitHub

As notas de consultas da internet e o backup `.patch` foram preservados em
`.local/`, ignorada pelo Git. O arquivo `.notas-internet.json` saiu da raiz
versionada. O ambiente `.venv/`, caches, logs e contadores locais também são
ignorados; bibliotecas instaladas não fazem parte dos arquivos versionados.
Sintaxe, links da documentação, dependências e integridade dos JSONs foram conferidos.

Os arquivos `dados/jogos.json` e `dados/avaliacoes.json` têm alterações locais
da biblioteca e foram preservados. Devem ser revisados antes de incluí-los no
commit. Nenhum commit, push ou alteração de issue foi feito nesta preparação.

| Item | Integrante / data | Resultado ou ajuste necessário |
|---|---|---|
| Pacote portátil nesta máquina | 24/10/2026 | Executável, HTTP, Qt e CRUD aprovados; ver portatil.md |
| Testes manuais, resultado geral | Gabriel / 24/10/2026 | Aprovados conforme relato; sem evidências anexadas |
| Execução em outro computador sem Python | A preencher | Não informada na confirmação manual |
| CRUD pela interface, navegação e mensagens | A preencher | Resultado individual não registrado; aprovação geral informada acima |
| T9.1 a T9.4 | A preencher | Pendente de demonstração presencial |
| Reinício e falha de conexão | A preencher | Resultado individual não registrado |
| Formato e prazo da entrega | A preencher | Confirmar com o professor |

## Limites conhecidos

Não há transação entre arquivos nem bloqueio global de gravações simultâneas.
A restauração da cascata é uma tentativa e pode falhar. IDs locais não autenticam
usuários; a consulta por autor é pública, assim como a consulta por jogo.
Não há sincronização automática entre clientes. O pacote Windows foi conferido
nesta máquina; sua validação manual em outro computador permanece pendente.
Reinicie Flask e Qt após atualizar o código para usar a nova rota.

## Execução sem instalação adicional

O enunciado exige execução sem instalar outros softwares. Foi preparado o pacote
`TechGamer-Windows-x64-20261024-151025.zip`, com interpretador e dependências
incluídos, iniciado por `TechGamer.exe`. A extração do ZIP foi testada numa pasta
temporária, com Python removido do PATH e variáveis de ambiente Python removidas.
O executável confirmou Qt, logo, HTTP, cadastro, avaliação, edição, média e
exclusão em cascata com dados temporários. Os dados reais foram preservados.
A suíte completa continuou com 107 aprovados após essas alterações.

Consulte [pacote portátil e procedimento de teste](portatil.md). A exigência tem
uma solução implementada e conferida localmente; o aceite final depende do teste
manual num computador sem Python, das evidências no Word e da disponibilização
do ZIP junto ao repositório público. Nenhuma publicação foi feita nesta etapa.
