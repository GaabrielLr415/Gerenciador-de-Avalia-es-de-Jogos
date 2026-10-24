# Integração de Builder, Proxy e Observer

Os padrões estão conectados às rotas Flask e ao cliente Qt. Foram preparados
com auxílio do Codex nesta revisão; não são parte dos commits anteriores de Edino.

## Fluxo implementado

- POST /jogos/<id>/avaliacoes usa o serviço e o Builder, persiste o JSON e
  notifica o Observer. Mantém autor_id positivo, nota 0–10, comentário e metadados.
- PUT e DELETE /avaliacoes/<id> passam pelo Proxy. Exigem o header X-Ator-Id:
  inteiro de 1 a 2147483647. Ausente, inválido ou sem permissão: HTTP 403 com
  envelope JSON erro/detalhes. Somente autor ou moderador configurado pode alterar.
- MODERADORES_IDS é configurado no servidor, com (99,) para demonstração.
  O corpo da requisição não pode conceder papel de moderador nem alterar a autoria.
  Avaliações legadas sem autor continuam bloqueadas para alteração individual.
- GET /jogos/<id>/media retorna jogo_id, quantidade e media na escala 0–10.
  Sem avaliações: media null. Jogo inexistente: 404. Reconstrói o resultado a
  partir do JSON após reinício e reconhece exclusões em cascata.
- O serviço em app.extensions['avaliacoes'] acompanha o repositório ativo.
  Após publicação, edição e exclusão, o Observer atualiza média e quantidade.
  A interface recebe e apresenta o agregado do servidor, sem recalculá-lo no Qt.

Os identificadores são fictícios, sem login ou autenticação. A persistência
continua sem transação entre arquivos ou bloqueio de gravações simultâneas.
Observadores executam após gravar. Uma falha no observador é registrada, não
desfaz a gravação, não impede os demais observadores e mantém a resposta de
sucesso da operação. A consulta da média tenta reconstruir o resultado. Uma
falha de persistência anterior à notificação continua retornando erro.

## Demonstração T9.1 a T9.4

Use uma cópia separada do projeto, sem copiar `dados/` nem `.venv/`, para não
alterar a biblioteca real. Instale e execute conforme o [README](../README.md).
Os passos seguintes são um roteiro para a equipe; não representam aceite visual
já realizado por uma pessoa.

1. Reinicie Flask e Qt com o código atualizado.
2. Cadastre um jogo, use ID local 7 e publique uma avaliação.
3. Informe nota e, se desejar, comentário. O autor é identificado pelo ID local.
4. Confira a média retornada pelo servidor nos cards e detalhes.
5. Use ID local 8 e tente editar a avaliação do autor 7: HTTP 403, sem alteração.
6. Feche o formulário, escolha ID 7 e edite: a média deve mudar.
7. Use ID 99 para demonstrar edição e exclusão permitidas ao moderador.
8. Reinicie o servidor e confira a preservação das avaliações e da média.

### Resultados esperados para o ensaio

| Passo | Ação pela interface | Resultado esperado |
|---|---|---|
| T9.1 | Com ator local 7, publicar nota 8 e comentário opcional. | Sucesso, uma avaliação persistida, autor 7, metadados padrão `{}` e média 8. |
| T9.2 | Publicar outra avaliação de nota 6. | Duas avaliações e média 7. Metadados inválidos são verificados pelos testes da API e dos padrões, sem editor JSON no formulário. |
| T9.2 | Usar notas 0 e 10 em jogo separado; conferir comentário vazio. | Limites aceitos e média 5. Campo gráfico limita a faixa; API rejeita tipo/faixa inválidos conforme testes. |
| T9.3 | Voltar ao primeiro jogo, selecionar ator 8 e editar/excluir avaliação do autor 7. | Mensagem de acesso negado, sem alteração nem exclusão. |
| T9.3 | Selecionar ator 7 e alterar a primeira nota de 8 para 10. | Sucesso e média 8 entre as notas 10 e 6; autoria e vínculo preservados. |
| T9.3 | Selecionar moderador 99 e excluir a avaliação de nota 6. | Sucesso, uma avaliação restante e média 10. |
| T9.4 | Explicar o fluxo e mostrar os testes dos padrões. | Builder constrói, Proxy bloqueia/delega e Observer atualiza após persistir. |
| Persistência | Encerrar Flask e Qt e iniciar novamente a mesma cópia. | Dados, autor, metadados e média continuam disponíveis. |
| Falha de rede | Parar somente Flask e tentar salvar um formulário. | Erro compreensível, campos preservados e interface responsiva; sem confirmação de sucesso. |
| Recuperação | Reiniciar Flask e salvar novamente. | Uma operação concluída; conferir a listagem para evitar duplicidade. |
| Cascata | Cancelar a exclusão de um jogo e depois confirmar. | Cancelamento preserva dados; confirmação remove jogo e avaliações. |

A restrição a avaliações legadas é individual. Excluir o jogo que as contém
continua permitido; os testes de API e Repository comprovam esse cenário.

O plano fornecido, páginas 1 e 10, exige demonstração observável dos padrões.
IDs locais e comentário opcional refletem o escopo da equipe; Edino e Gabriel
devem confirmar a adequação ao enunciado completo. O enunciado AP2 exige execução
sem instalar softwares; foi preparado um [pacote portátil Windows](portatil.md).

## Execução

Na raiz do projeto, em terminais separados:

```powershell
.\.venv\Scripts\python.exe -m servidor.app
.\.venv\Scripts\python.exe -m cliente
```

Testes (dados temporários, sem alterar os JSON da biblioteca):

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s testes -p "test_*.py" -v
```

- test_design_patterns.py: padrões no serviço, validações, persistência e eventos.
- test_integracao_patterns_http.py: Builder/Observer no POST, Proxy no PUT/DELETE,
  bloqueios, moderador configurável, metadados e média após reinício (T9.1–T9.4).
- test_cliente_qt.py: fluxo Qt → HTTP → Flask, erro 403, moderador, preservação de metadados e
  apresentação da média recebida do servidor.

Registre o aceite visual e o teste em outro computador no
[relatório de entrega](validacao-entrega.md). A revisão dos diagramas e requisitos
pela equipe continua necessária antes de considerar a entrega concluída.
