# Entrega complementar da issue #2

Implementação preparada com auxílio do Codex. Não atribuir esta implementação aos commits anteriores de Edino.

## Componentes

- `AvaliacaoBuilder`: valida autor positivo, nota numérica de 0 a 10 (inclui decimais, exclui booleanos e números não finitos), comentário opcional em texto e metadados JSON opcionais. Retorna cópias independentes.
- `AvaliacoesProxy`: delega publicação, edição e exclusão ao serviço; edição/exclusão exigem autor ou moderador configurado no servidor. Identificadores são fictícios, sem login. Avaliações legadas sem autor continuam bloqueadas conforme a regra do repositório existente.
- `EventosAvaliacoes`: Subject que permite inscrição, remoção e notificação de observadores.
- `NotaMediaObserver`: Observer que recalcula a média aritmética na escala 0–10 e a quantidade de avaliações após gravações. Sem avaliações, `media` é `None`. A consulta reconstrói o resultado a partir do JSON, inclusive após reinício.
- `ServicoAvaliacoes`: combina Builder, repositório e notificações. As notificações ocorrem depois da persistência. Falha em um observador pode ocorrer após a gravação; não repetir a publicação automaticamente nesse caso.

## Utilização e integração do Gabriel

```python
from servidor.patterns import ServicoAvaliacoes, AvaliacoesProxy

servico = ServicoAvaliacoes(repositorio)
proxy = AvaliacoesProxy(servico, ator_id=7, moderadores=(99,))
avaliacao = proxy.publicar(jogo_id, {"nota": 8.5, "comentario": "Bom"})
proxy.editar(avaliacao["id"], {"nota": 9})
resultado = servico.media.consultar(jogo_id)
proxy.excluir(avaliacao["id"])
```

Gabriel deverá manter um serviço por repositório da aplicação e construir o Proxy para a identificação local de cada operação. A lista de moderadores deve vir da configuração do servidor; não aceitar um booleano `moderador` enviado pelo cliente. Não substituir silenciosamente ator ausente pelo autor armazenado.

Mapeamento esperado: ValueError → 400, PermissionError → 403, LookupError → 404; falhas inesperadas → 500. A interface e o cliente HTTP precisarão transmitir o ator local nas edições e exclusões. A definição do campo/header HTTP e a integração às rotas existentes ficam para Gabriel; não foram modificados app.py, o contrato existente nem as telas.

A consulta da média deve verificar antes a existência do jogo na rota Flask. Exclusão em cascata de jogos continua no repositório existente; consultar a média a reconstrói do JSON. Este módulo não adiciona bloqueio para gravações simultâneas nem transação entre arquivos.

## Testes

Na raiz do projeto:

```powershell
python -m unittest discover -s testes -p "test_design_patterns.py" -v
python -m unittest discover -s testes -p "test_*.py" -v
```

T9.1: construção, publicação, persistência e reinício.
T9.2: limites, notas decimais, tipos inválidos, comentário e metadados.
T9.3: autor/moderador, bloqueio de outro ator e atualização da média.
T9.4: cópias do Builder, delegação do Proxy e notificações reais aos Observers no serviço.

Os testes novos utilizam apenas diretórios temporários. Eles comprovam os padrões no serviço; a demonstração pelo fluxo HTTP/Qt depende da integração do Gabriel e de testes adicionais dessa integração. As checklists da issue não devem ser marcadas como totalmente concluídas antes dessa etapa.
