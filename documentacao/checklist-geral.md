# Checklist geral do TechGamer

Revisão: **24/10/2026**. Código conferido: commit `2efd82c` da branch `main`.
Este checklist reúne a situação atual; os relatórios anteriores preservam os
resultados e as pendências existentes na data de cada execução.

**Resultado técnico:** 107 testes aprovados em 44,621 segundos, sem falhas,
erros ou testes ignorados. Há conferências de documentação e aceite da equipe
listadas ao final; aprovação automatizada não equivale ao aceite da entrega.

Legenda: `[x]` = verificado ou registrado na fonte indicada; `[ ]` = ação ou
confirmação pendente. Evidências relatadas no PDF estão identificadas como tal.

## 1. Funcionalidades e integração

- [x] Cadastrar, listar, consultar, editar e excluir jogos.
- [x] Publicar, listar, editar e excluir avaliações.
- [x] Aceitar notas de 0 a 10, incluindo valores decimais.
- [x] Validar campos obrigatórios, tipos, limites e metadados.
- [x] Excluir as avaliações vinculadas ao excluir um jogo.
- [x] Preservar dados e identificadores após reinicialização.
- [x] Exibir quantidade de avaliações e média calculada pelo servidor.
- [x] Integrar interface Qt, requisições HTTP, Flask e armazenamento JSON.
- [x] Consultar catálogo e Minhas avaliações em uma requisição por atualização.
- [x] Exercitar busca, filtros, ordenação, paginação e redimensionamento nos testes.
- [x] Exercitar perfis locais, troca de perfil e gerenciamento de avaliações.
- [x] Tratar falha de conexão, preservar formulário e manter tarefas fora da thread gráfica.

Evidência: suíte existente executada novamente em cópia temporária dos arquivos
versionados, com Qt sem janela visível. Os testes não constituem nova inspeção
visual interativa de todas as telas.

## 2. Padrões e critérios T9.1 a T9.4

- [x] Builder participa da construção de avaliações no fluxo da API.
- [x] Proxy permite edição/exclusão pelo autor ou moderador e bloqueia terceiros.
- [x] Observer atualiza o agregado após publicação, edição e exclusão.
- [x] T9.1: publicação, construção e persistência cobertas por testes.
- [x] T9.2: notas válidas/inválidas e comentário cobertos por testes.
- [x] T9.3: permissão e atualização da média cobertas por testes.
- [x] T9.4: comportamento integrado dos três padrões coberto por testes.
- [x] Disponibilizar [roteiro de demonstração](entrega-design-patterns.md).
- [ ] Ensaiar T9.1 a T9.4 pelos controles visíveis e definir quem explica cada padrão.
- [ ] Confirmar com o professor o escopo acadêmico de IDs fictícios, comentário opcional e capas remotas.

Referência: [plano fornecido](../plano_testes_aplicacoes_qt_flask.pdf), páginas 1 e 10,
e [matriz de requisitos](requisitos-e-aceitacao.md). A página 1 exige comportamento
observável dos padrões; a existência de classes, isoladamente, não basta.

## 3. Testes, ambiente e dados

| Grupo | Resultado desta revisão |
|---|---:|
| API Flask | 28 aprovados |
| Cliente Qt com HTTP | 33 aprovados |
| Design patterns | 13 aprovados |
| Integração dos padrões por HTTP | 10 aprovados |
| Persistência JSON | 23 aprovados |
| **Total** | **107 aprovados** |

- [x] Sintaxe dos 29 arquivos Python versionados válida.
- [x] As 18 versões instaladas coincidem com `requirements.txt`.
- [x] `pip check` sem incompatibilidades.
- [x] Comando de ajuda do cliente executado com sucesso.
- [x] Conferir 96 jogos e 4 avaliações: campos válidos, IDs positivos/únicos e vínculos existentes.
- [x] Conferir os 68 links locais em Markdown existentes antes deste checklist, sem destinos ausentes.
- [x] Preservar os arquivos versionados originais durante a auditoria, comprovado por SHA-256.
- [ ] Se exigido no aceite, repetir a instalação das dependências atuais em ambiente vazio; esta rodada usou a `.venv` existente.

Comando da suíte:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s testes -p "test_*.py" -v
```

Logs desta rodada ficam em `.local/checklist-geral/testes.log` e
`.local/checklist-geral/resultado.json`, ignorados pelo Git. Os resultados
publicáveis estão registrados aqui. O total de links acima corresponde à base
auditada, antes dos novos links deste checklist.

## 4. Pacote e GitHub

- [x] Repositório público com branch principal `main`.
- [x] Código local da base auditada coincide com a `main` remota (`2efd82c`).
- [x] PDF final publicado em `documentacao/` e acessível pelo README.
- [x] [Release v1.0.0](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/releases/tag/v1.0.0) publicada, sem marcação de rascunho.
- [x] ZIP Windows e arquivo `.sha256` presentes na release e com links correspondentes no README.
- [x] ZIP local íntegro, incluindo `TechGamer/TechGamer.exe`.
- [x] SHA-256 do ZIP local coincide com o arquivo de verificação e com o digest do asset publicado.
- [x] Nenhum pull request aberto na consulta desta revisão.
- [x] Execução portátil nesta máquina registrada no [relatório anterior](validacao-entrega.md).
- [x] Execução em outro computador sem instalar Python relatada na conclusão do PDF final, página 27.
- [ ] Complementar o relato externo com data, responsável, Windows, versão do ZIP e identificação do ambiente sem Python.
- [ ] Confirmar no ensaio o CRUD local sem internet, distinguindo a indisponibilidade de capas remotas.
- [ ] Publicar este checklist após a revisão da equipe; ele foi preparado localmente nesta rodada.

Arquivo conferido: `TechGamer-Windows-x64-20261024-151025.zip`.
SHA-256: `4d27f7a99ac8fec5745fc3d5663d0d64bdeaa67ce22b9296c1449a3e8ebe3a3e`.
O digest da release foi consultado pela API do GitHub; o ZIP remoto não foi
baixado novamente. O executável não foi iniciado novamente nesta auditoria.

## 5. Documentação final e apresentação

- [x] [PDF final](PROJETO%20TECHGAMER%20-%20FINAL.pdf) abre e contém 27 páginas.
- [x] Contém objetivos, funcionalidades, tecnologias, arquitetura, requisitos e regras de negócio.
- [x] Contém comunicação HTTP, padrões, diagramas do servidor e cliente e condições de aceitação.
- [x] Contém relato dos 107 testes, capturas da interface e evidências de persistência.
- [x] Contém instruções da versão portátil e conclusão.
- [x] Diagramas das páginas 13 e 14 renderizados e inspecionados; classes principais também conferidas no código.
- [ ] Conferir autoria da capa: aparecem quatro nomes; o acompanhamento registra cinco integrantes, incluindo Angélica. Confirmar a composição final da equipe antes de alterar.
- [ ] Revisar as indicações editoriais “DUAS FOTOS” nos títulos dos testes das páginas 19, 21, 22 e 24.
- [ ] Conciliar os registros antigos de validação/acompanhamento com a publicação já feita e as evidências agora incluídas no PDF.
- [ ] Conferir a versão final contra o enunciado completo, o formato de envio e o prazo oficial do professor.
- [ ] Dividir as falas e ensaiar a apresentação com o pacote que será entregue.
- [ ] Realizar o envio no canal solicitado pelo professor e guardar o comprovante.

A revisão do PDF identificou conteúdo e conferiu visualmente os diagramas e a
conclusão. Não representa revisão tipográfica de todas as páginas nem execução
independente dos testes manuais relatados. O PDF original foi preservado.

## 6. Organização e limites conhecidos

- [x] Guias de uso, API, código, requisitos, arquitetura e empacotamento disponíveis.
- [x] `.venv/`, `.local/`, `dist/`, caches e logs ignorados pelo Git.
- [ ] Revisar os checklists das [issues abertas](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/issues) #1 a #5 e encerrar somente as tarefas aceitas pelos responsáveis. Há itens ainda desmarcados que já têm evidência técnica nesta revisão.
- [ ] Confirmar que a equipe entende os limites de IDs locais, gravações concorrentes e restauração em cascata descritos abaixo.

Os perfis locais e o ID de moderador 99 demonstram permissões; não há autenticação.
O armazenamento tem escrita atômica por arquivo, mas não oferece transação entre
arquivos nem bloqueio global para gravações simultâneas. Não há sincronização
automática entre clientes. Esses limites estão documentados e devem ser
avaliados em relação ao escopo acadêmico, sem exigir funcionalidades novas por padrão.

## Próximas ações da equipe

1. Conferir autoria da capa e os títulos com “DUAS FOTOS” no arquivo de origem do PDF.
2. Completar os dados do teste em outro computador e atualizar os registros antigos.
3. Revisar as issues #1 a #5 com as evidências deste checklist.
4. Ensaiar T9.1 a T9.4 e confirmar formato/prazo da entrega.
5. Revisar e publicar o checklist; concluir o envio oficial e registrar o comprovante.
