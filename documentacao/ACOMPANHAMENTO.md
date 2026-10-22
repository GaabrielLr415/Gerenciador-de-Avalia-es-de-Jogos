# Coordenação da equipe - TechGames

Revisão: 21/10/2026. Prazo de trabalho adotado: **23/10/2026**, conforme informado
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

Os checklists das issues não foram atualizados automaticamente. Cada integrante
deve conferir suas evidências antes de marcar um item ou encerrar a tarefa.

## Prioridades para a entrega

- [x] Conferir as páginas relevantes do plano T9.1 a T9.4.
- [x] Documentar as classes reais do servidor e do cliente.
- [x] Atualizar as instruções de instalação e execução pelo código.
- [x] Relacionar requisitos aos testes automatizados existentes.
- [ ] Edino e Gabriel: comparar o escopo com o enunciado completo do professor.
- [ ] Equipe: confirmar se a entrega exige executável sem Python.
- [ ] Equipe: executar o roteiro pelos controles visíveis e registrar o aceite visual.
- [ ] Equipe: instalar e executar em outro computador.
- [ ] Gabriel e Angélica: revisar os documentos preparados localmente.
- [ ] Cada integrante: revisar e atualizar manualmente sua issue.
- [ ] Equipe: ensaiar a apresentação, dividir as falas e conferir a versão entregue.

A instalação em ambiente virtual novo no mesmo computador não substitui o
teste em outra máquina. Não declarar empacotamento concluído sem artefato testado.

## Documentos principais

- [README e instalação](../README.md)
- [Requisitos e critérios de aceitação](requisitos-e-aceitacao.md)
- [Contrato HTTP](contrato-api.md)
- [Arquitetura e diagramas](arquitetura-e-padroes.md)
- [Roteiro dos padrões](entrega-design-patterns.md)
- [Resultados e aceite pendente](validacao-entrega.md)

Os arquivos em subpastas repetidas de `documentacao/` registram material anterior.
A navegação principal usa os documentos acima; a organização dos arquivos
históricos pode ser revisada depois, preservando o conteúdo dos colegas.
