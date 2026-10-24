# Coordenação da equipe - TechGamer

Revisão: 24/10/2026. Prazo de trabalho adotado: **23/10/2026**, conforme informado
pela equipe. O PDF do plano de testes não informa a data oficial da entrega.

| Issue | Responsável | Escopo |
|---|---|---|
| #1 | Gabriel | Backend Flask, integração e revisão final. |
| #2 | Edino | Requisitos, Builder, Proxy, Observer e testes T9.1 a T9.4. |
| #3 | Fillipe | Interface gráfica Qt. |
| #4 | João Pedro | Comunicação HTTP e integração Qt/Flask. |
| #5 | Angélica | Persistência JSON e documentação com Gabriel. |

A tabela representa a divisão de responsabilidades das issues, não a autoria
individual de cada alteração no histórico Git.

## Situação técnica

Flask, JSON, Qt, HTTP e os três padrões estão integrados. Há testes de API,
persistência, padrões, integração HTTP e interface. Os resultados reproduzidos,
as versões testadas e os limites estão no [relatório de validação](validacao-entrega.md).

Na revisão final de 24/10/2026, os **107 testes** passaram. Minhas avaliações passou a
usar uma requisição por atualização, e as versões do ambiente foram fixadas em
`requirements.txt`. README, uso do cliente, contrato, diagramas, requisitos e
relatório foram atualizados. Essas correções estão locais, sem commit ou envio.
Na checagem final em cópia isolada, foi corrigido o ciclo de vida dos sinais do
executor HTTP e incluída uma regressão para encerramentos repetidos com sucesso e falha.

Os checklists das issues não foram atualizados automaticamente. Cada integrante
deve conferir suas evidências antes de marcar um item ou encerrar a tarefa.

## Prioridades para a entrega

- [x] Conferir as páginas relevantes do plano T9.1 a T9.4.
- [x] Documentar as classes reais do servidor e do cliente.
- [x] Atualizar as instruções de instalação e execução pelo código.
- [x] Relacionar requisitos aos testes automatizados existentes.
- [ ] Edino e Gabriel: comparar o escopo com o enunciado completo do professor.
- [x] Preparar e conferir localmente o pacote portátil para atender à execução sem instalação adicional.
- [x] Gabriel: informar o resultado geral dos testes manuais — aprovados em 24/10/2026.
- [ ] Equipe: registrar os resultados por cenário e as capturas dos testes manuais.
- [ ] Equipe: executar o pacote em outro computador sem Python e registrar no Word.
- [ ] Gabriel e Angélica: revisar os documentos preparados localmente.
- [ ] Cada integrante: revisar e atualizar manualmente sua issue.
- [ ] Equipe: ensaiar a apresentação, dividir as falas e conferir a versão entregue.

A instalação em ambiente virtual novo no mesmo computador não substitui o
teste em outra máquina. Não declarar empacotamento concluído sem artefato testado.

O [pacote portátil](portatil.md) já foi gerado e conferido nesta máquina com
Python fora do PATH do processo. Qt, HTTP e CRUD passaram; os 107 testes do
código também passaram. A publicação do ZIP e o teste manual externo estão pendentes.

Na nova rodada interna de 24/10/2026, às 15h17, os 107 testes passaram em uma
cópia isolada com 54 arquivos, em 43,690 segundos. O executável foi conferido
novamente, sem alterar os dados. Os resultados estão no relatório de validação;
Gabriel ficou responsável pelos testes manuais e pelo registro das telas no Word.
Em 24/10/2026, às 15h30, informou que os testes manuais deram certo. O resultado
geral está registrado; a máquina utilizada, a execução sem Python e as capturas
para o Word não foram informadas nessa confirmação.

## Documentos principais

- [README e instalação](../README.md)
- [Requisitos e critérios de aceitação](requisitos-e-aceitacao.md)
- [Contrato HTTP](contrato-api.md)
- [Arquitetura e diagramas](arquitetura-e-padroes.md)
- [Roteiro dos padrões](entrega-design-patterns.md)
- [Resultados e aceite pendente](validacao-entrega.md)

Os registros anteriores de requisitos e arquitetura estão em `historico/`.
O conteúdo foi preservado; a navegação principal usa os documentos acima.
O [guia do código](guia-do-codigo.md) apresenta uma ordem de leitura para novos integrantes.
