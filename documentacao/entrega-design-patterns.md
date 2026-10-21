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
Observadores executam após gravar: uma falha posterior não desfaz a gravação;
não repetir publicações automaticamente após erro desse tipo.

## Demonstração T9.1 a T9.4

1. Reinicie Flask e Qt com o código atualizado.
2. Cadastre um jogo, use ID local 7 e publique uma avaliação.
3. Informe nota, comentário e, opcionalmente, um objeto em Metadados (JSON).
4. Confira a média retornada pelo servidor nos cards e detalhes.
5. Use ID local 8 e tente editar a avaliação do autor 7: HTTP 403, sem alteração.
6. Feche o formulário, escolha ID 7 e edite: a média deve mudar.
7. Use ID 99 para demonstrar edição e exclusão permitidas ao moderador.
8. Reinicie o servidor e confira a preservação das avaliações e da média.

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
- test_cliente_qt.py: fluxo Qt → HTTP → Flask, erro 403, moderador, metadados e
  apresentação da média recebida do servidor.

A revisão final de requisitos, diagramas e demais documentos da equipe continua
necessária antes de considerar a entrega acadêmica concluída.
