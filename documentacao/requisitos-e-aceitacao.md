# Requisitos e critérios de aceitação

Revisão: 21/10/2026. Responsável pelos requisitos: **Edino**; integração e revisão
final: **Gabriel**; organização documental: **Angélica**.

## Fontes e alcance

- [Plano de testes fornecido](../plano_testes_aplicacoes_qt_flask.pdf), páginas 1
  e 10: comportamento observável de um padrão criacional, estrutural e
  comportamental, testes T9.1 a T9.4 e validação da interface, dados e HTTP.
- [Requisitos registrados por Edino](documentacao/requisitos-e-regras-edino.md):
  RF01 a RF09, tecnologias e condições de aceitação.
- Issues #1 a #5: responsabilidades e escopo acordado pela equipe.
- Código e testes atuais: evidência técnica da implementação.

Este documento consolida essas fontes para revisão da equipe; não substitui
um enunciado completo do professor. O PDF não informa data de entrega, formato
de empacotamento, autenticação real ou exigência de sincronização entre clientes.
O escopo acordado usa JSON e IDs fictícios, sem login.

## Requisitos funcionais e evidências

| ID | Comportamento e aceitação | Evidência automatizada |
|---|---|---|
| RF01-RF04 | Cadastrar, listar, consultar e editar jogos com nome, gênero, plataforma, ano e descrição opcional; refletir alterações na interface. | `test_crud_jogos`; `test_crud_pela_interface_com_estrelas_decimais_e_media`. |
| RF05 | Excluir jogo e suas avaliações, inclusive legadas; preservar outros jogos e avaliações. | `test_cascata_remove_legadas_e_novas_preservando_outros_jogos_e_ids`; `test_cascata_preserva_avaliacoes_de_outro_jogo`. |
| RF06 | Publicar avaliação de jogo existente com autor positivo, nota 0-10, comentário e metadados opcionais. | `test_t91_publicar_construir_persistir_e_reiniciar`; `test_t91_builder_e_observer_utilizados_pelo_post`. |
| RF07 | Listar, editar e excluir avaliações; manter autor e IDs; autor ou moderador configurado pode editar/excluir; outro ator recebe 403 sem gravar. | `test_identificadores_e_autor_nao_podem_ser_sobrescritos`; testes `test_t93_*`. |
| RF08 | Rejeitar campos ausentes, tipos inválidos, notas fora da faixa e metadados incompatíveis com JSON estrito, inclusive números não finitos aninhados. | Testes de validação em `test_api_flask.py`, `test_repositorio_json.py` e `test_design_patterns.py`. |
| RF09 | Persistir dados e preservar IDs após reinício, sem reutilizar IDs excluídos. | `test_campos_persistem_em_outro_processo_python`; `test_ids_nao_reutilizados_apos_cascata_e_reinicio`. |
| RF10 | Construir avaliações pelo Builder e atualizar média pelo Observer após publicação, edição e exclusão. Sem avaliações, quantidade zero e média nula. | `test_t94_notifica_apos_publicar_editar_excluir`; `test_media_vazia_inexistente_e_reconstruida_apos_reinicio`. |
| RF11 | Usar HTTP entre Qt e Flask; mostrar sucesso, dados inválidos, acesso negado e falha de conexão; manter formulário após falha. | `test_cliente_qt.py`; `test_integracao_patterns_http.py`. |

RF01 a RF09 mantêm a numeração do documento de Edino. RF10 e RF11 explicitam
a integração dos padrões e a apresentação dos resultados; não são funcionalidades
novas.

## Cenários obrigatórios do plano

| Cenário | Critério observável | Evidência |
|---|---|---|
| T9.1 | Publicar pela interface; avaliação construída, persistida e consultável. | Testes T9.1 de serviço/HTTP e CRUD Qt. |
| T9.2 | Aceitar limites 0 e 10 e notas decimais; rejeitar notas e comentários de tipo inválido sem gravação indevida. Comentário é opcional no escopo acordado. | Testes T9.2 e validações da API. |
| T9.3 | Autor/moderador edita; terceiro recebe 403 sem alterar os dados; média é atualizada. | Testes T9.3 de serviço/HTTP e `test_proxy_qt_bloqueia_outro_e_permite_moderador`. |
| T9.4 | Builder participa da construção; Proxy decide permissões; Observer recebe evento após gravar e atualiza o agregado. | Testes T9.4, instrumentação do Builder no POST e verificações do agregado antes da consulta. |

O [roteiro de apresentação](entrega-design-patterns.md) descreve as ações pela
interface. Aprovação automatizada não substitui a revisão visual pelos integrantes.

## Restrições e qualidade

- Python, Flask, Qt/PySide6 e HTTP; dados locais em JSON.
- Sem banco de dados, login, serviços de nuvem ou inteligência artificial na
  aplicação. Capas por URL já são opcionais; confirmar com o professor se
  imagens remotas são permitidas na demonstração. O fluxo principal não as exige.
- Rejeições de dados retornam 400; falta de permissão, 403; registros inexistentes
  nas rotas, 404; falhas de armazenamento, 500 sem expor detalhes internos.
- Escrita atômica por arquivo. Cascata tenta restauração, mas não há transação
  entre arquivos nem bloqueio contra gravações concorrentes.
- Falhas de observador não transformam gravação já concluída em erro de operação.
- Dados de teste são temporários; não substituir os arquivos reais da biblioteca.
- A interface usa tarefas assíncronas para manter o loop gráfico responsivo.
- Identificação local é demonstração de permissão, não proteção contra falsificação
  de identidade. Confirmar a adequação desse escopo acadêmico com o professor.

## Pendências de aceite humano

- Edino e Gabriel: conferir esta matriz com o enunciado completo e os critérios
  do professor, especialmente identificação fictícia e comentário opcional.
- Equipe: demonstrar T9.1 a T9.4 pelos controles visíveis e conferir legibilidade,
  mensagens, cancelamento e ausência de travamentos.
- Gabriel e Angélica: testar a instalação em outro computador e confirmar se
  a entrega exige executável sem Python.
- Prazo de trabalho adotado: **23/10/2026**, informado pela equipe. O PDF não
  comprova o prazo oficial.
