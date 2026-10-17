# Requisitos e critérios de aceitação

## Estado e fonte dos requisitos

Este documento organiza os comportamentos observáveis no servidor e no contrato
de API atualmente disponível. O `contrato-api.md` identifica suas regras como
proposta sujeita à aprovação da equipe. A lista oficial de requisitos e os
critérios fornecidos por João Pedro ainda não estão neste repositório; por isso,
os itens abaixo são uma base de integração, não substituem nem presumem essa
entrega. Confirmar e reconciliar o documento após recebê-la.

## Requisitos funcionais documentados

| ID | Requisito provisório | Evidência/estado |
|---|---|---|
| RF-01 | Criar, listar, consultar, editar e excluir jogos. | Rotas e `RepositorioJSON` disponíveis. |
| RF-02 | Criar, listar por jogo, consultar, editar e excluir avaliações. | Rotas e `RepositorioJSON` disponíveis. |
| RF-03 | Persistir jogos e avaliações em arquivos JSON locais entre execuções. | `dados/jogos.json` e `dados/avaliacoes.json`. |
| RF-04 | Excluir as avaliações de um jogo quando o jogo for removido. | Exclusão em cascata no repositório. |
| RF-05 | Gerar IDs inteiros positivos sem reutilizar IDs excluídos após reinício. | Histórico auxiliar em `.contadores_id.json`. |
| RF-06 | Iniciar os arquivos de dados ausentes como listas vazias e recuperar dados JSON inválidos preservando cópia `.bak`. | Comportamento do repositório; coberto por testes. |
| RF-07 | Validar campos de jogo e avaliação conforme o contrato da API. | Validação no servidor; confirmar limites com a equipe. |

## Critérios de aceitação provisórios para persistência

1. Dado que os arquivos de dados não existam, ao inicializar o repositório,
   ambos são criados contendo `[]`.
2. Dado um jogo válido, ao criá-lo e inicializar outro repositório apontando
   para os mesmos arquivos, o jogo permanece consultável.
3. Dada uma avaliação válida vinculada a um jogo, ao reiniciar o repositório,
   ela continua listada para esse jogo.
4. Ao editar um jogo ou uma avaliação, os novos campos continuam presentes
   depois de reinicializar o repositório.
5. Ao excluir um jogo, suas avaliações também deixam de existir.
6. Depois de excluir e reiniciar, o próximo ID do mesmo tipo é maior que o
   último ID emitido.
7. Diante de JSON malformado, o conteúdo original é copiado para `.bak` antes
   de a aplicação reconstituir o arquivo de dados como lista vazia.
8. Diante de um erro de leitura ou de backup, o erro é exposto e o arquivo
   original não é substituído como se a recuperação tivesse sido bem-sucedida.
9. Os testes usam diretório temporário e não alteram os arquivos de dados do
   projeto.

## Requisitos não funcionais e restrições documentadas

- Persistência exclusivamente local em arquivos JSON; não utilizar banco de
  dados ou serviço remoto.
- A escrita dos arquivos deve ser atômica para evitar arquivos parcialmente
  gravados.
- As camadas de persistência e API devem manter a interface definida no
  `contrato-api.md`.
- Falhas de armazenamento devem ser reportadas, não convertidas em sucesso.

## Pendências para aprovação

- **João Pedro:** adicionar aqui os requisitos e critérios oficiais e confirmar
  a rastreabilidade entre eles e os itens provisórios.
- **Gabriel:** confirmar o contrato, validar os critérios da API e revisar a
  documentação antes da entrega.
- **Edino:** fornecer as classes reais do cliente para documentar e validar o
  diagrama de classes do cliente.
