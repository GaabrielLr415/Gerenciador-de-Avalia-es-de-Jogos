# Revisão das issues e carregamento da biblioteca

Data: 22/10/2026. Base integrada: `78fae73` (PR #20). A otimização descrita
abaixo ainda é alteração local, sem commit ou integração à main nesta revisão.
As issues #1 a #5 foram consultadas no GitHub e continuam abertas.
Esta revisão comprova funcionalidades presentes no repositório, não autoria
individual nem reuniões, comunicações ou aprovações pessoais da equipe.

## Validação desta revisão

Suíte completa: **95 testes aprovados**, sem falhas ou erros, em 31,193 segundos.
Comando: `.\.venv\Scripts\python.exe -m unittest discover -s testes -v`.
Dados e preferências dos testes são temporários. As alterações preexistentes
em `dados/avaliacoes.json` não fazem parte desta implementação.

| Área | Testes |
|---|---:|
| API Flask | 25 |
| Persistência JSON | 23 |
| Builder, Proxy e Observer | 13 |
| Integração dos padrões por HTTP | 10 |
| Interface Qt com HTTP real | 24 |
| Total | 95 |

## Carregamento otimizado

- Qt usa `GET /jogos?com_medias=1` para receber jogos, média e quantidade de avaliações.
- Para 97 jogos, a carga do catálogo passa de 98 para **1 requisição HTTP**.
- O servidor lê jogos e avaliações uma vez cada, agrupando as notas por jogo.
- A média continua calculada no servidor, sem gravar campos derivados no JSON.
- Jogos sem avaliações retornam média nula e quantidade zero.
- A rota sem parâmetro e a consulta individual de média mantêm seus contratos.
- Consultas dos detalhes de um jogo e downloads das capas são operações separadas;
  a contagem de uma requisição refere-se à carga do catálogo, não a toda a tela.
- Capas continuam por URL, sem baixar arquivos para o repositório.
- Reiniciar Flask e Qt após atualizar os dois componentes.

Evidências novas:
`test_catalogo_com_medias_le_avaliacoes_uma_vez_sem_gravar`,
`test_medias_do_catalogo_refletem_edicao_exclusao_e_reinicio` e
`test_biblioteca_carrega_97_jogos_em_uma_requisicao_com_medias`.

## Issue #1 — Gabriel

[Issue original](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/issues/1).

Implementado e testado: rotas Flask; CRUD de jogos e avaliações; validações e
erros HTTP; integração com JSON; Builder na publicação; Proxy na edição/exclusão;
Observer e média; campos de autor e metadados; integração real com Qt.
Evidências: `test_api_flask.py`, `test_integracao_patterns_http.py`,
`test_cliente_qt.py` e contrato da API. A funcionalidade já está integrada
na main; a otimização de carregamento desta revisão ainda precisa de commit/PR.

Ainda não encerrar a issue inteira: revisar documentação final com Angélica,
registrar o aceite do aplicativo e organizar a entrega. Os itens sobre comunicar
campos aos colegas, revisar PRs e acompanhar entregas exigem confirmação da equipe;
um teste não comprova essas ações. Há instruções e diagramas no repositório,
mas o relatório antigo e o README do cliente descrevem versões anteriores da tela.

## Issue #2 — Edino

[Issue original](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/issues/2).

Concluída tecnicamente: requisitos funcionais/não funcionais e aceitação em
`requisitos-e-aceitacao.md` e no documento histórico de requisitos; classes em
`servidor/patterns/avaliacoes.py`; testes T9.1 a T9.4 e validações de API.
Builder constrói e valida, Proxy verifica autor/moderador e Observer recebe
eventos após persistência. Testes verificam comportamento e falhas, não apenas
existência das classes. Implementação e testes estão na main.

Pode receber os checks técnicos de conclusão. O item que cita um PR da branch
`feature/requisitos-testes` deve registrar os PRs reais que entregaram a
funcionalidade (incluindo #14 e #15), sem inventar um PR nessa branch.
Confirmação pessoal de Edino e comunicação de resultados não podem ser atribuídas
pela auditoria. Conclusão técnica não significa autoria exclusiva do responsável.

## Issue #3 — Fillipe

[Issue original](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/issues/3).

Implementado e testado: janela e navegação; listagem, formulários e detalhes;
CRUD de jogos e avaliações; notas/comentários/metadados; confirmação/cancelamento
de exclusões; mensagens de sucesso, dados inválidos, autorização e conexão;
estados vazios; médias; interface separada do HTTP; perfis locais sem senha;
grade responsiva e enquadramento das capas. Evidências em `test_cliente_qt.py`.
O aplicativo abre sem login; perfil local identifica o autor para demonstrar
permissões. Os padrões continuam no servidor.

Os checks de implementação podem ser atualizados. Para encerramento com aceite
visual, registrar o ensaio pelos controles visíveis na resolução/escala usadas
pela equipe. Testes offscreen e capturas anteriores não comprovam esse aceite.

## Issue #4 — João Pedro

[Issue original](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/issues/4).

Concluída tecnicamente: `APIClient` executa GET/POST/PUT/DELETE, interpreta JSON,
envia autor/metadados e X-Ator-Id, consulta médias e trata erros HTTP, timeout,
conexão e JSON inválido. `ExecutorHTTP` executa fora da thread gráfica.
Formulários e listagens estão ligados ao Flask; testes Qt cobrem operações,
rejeições do Proxy, dados inválidos e servidor indisponível com campos preservados.
Evidências em `test_cliente_qt.py` e `cliente/services/`.

Pode receber os checks técnicos de conclusão. A otimização adicional desta revisão
precisa ser integrada antes de ser citada como parte da main. Os itens de acordo
e trabalho em conjunto com colegas dependem de confirmação dos integrantes.

## Issue #5 — Angélica

[Issue original](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/issues/5).

Persistência concluída tecnicamente: CRUD, novos campos, autor e metadados,
reinício, IDs, arquivos ausentes/inválidos, backups, cascata e tentativa de
restauração estão cobertos por 23 testes de repositório, além da integração.
O agregado é reconstruído das avaliações e não exige arquivo de médias.

Requisitos, diagramas do cliente/servidor, padrões, contrato e instruções estão
disponíveis. Ainda não encerrar a issue inteira: revisar a documentação final
com Gabriel e atualizar trechos antigos do cliente e do relatório de validação
(contagens 80/81, cabeçalho/identificação antigos e alegação de logo ausente).
Esta auditoria registra a situação atual, mas não substitui essa revisão completa.

## Atualização e encerramento

1. Integrar a otimização por commit e PR, mantendo avaliações locais fora do commit.
2. Atualizar checks técnicos com as evidências acima e preservar pendências reais.
3. Confirmar com os responsáveis os itens de comunicação/aprovação pessoal.
4. Edino e João Pedro têm escopo técnico atendido; Fillipe aguarda registro visual;
   Gabriel e Angélica aguardam a revisão documental/entrega descrita acima.
5. Encerrar cada issue quando seus critérios pendentes forem resolvidos, sem
   marcar instalação em outro computador ou aprovação humana como realizadas.

Nenhuma issue foi alterada ou encerrada nesta auditoria. Executável e teste em
outro computador pertencem à preparação geral da entrega; não são funcionalidades
faltantes do módulo de Edino ou do módulo HTTP de João Pedro.
