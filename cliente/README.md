# Cliente Qt — TechGamer

Interface PySide6 integrada ao Flask por `services/api_client.py`. A aplicação
permite buscar, cadastrar, editar e excluir jogos e avaliações. Os dados são
sempre consultados pela API; a interface não acessa os arquivos JSON.

## Executar

Na raiz do projeto, com Python 3.10 a 3.15 (validado em 3.13.5):

```powershell
python -m pip install -r requirements.txt
python servidor/app.py
```

Em outro terminal, também na raiz e com o mesmo ambiente virtual:

```powershell
python -m cliente
```

Também é possível iniciar com `python cliente/main.py`. Para outro endereço:

```powershell
python -m cliente --servidor http://127.0.0.1:5000
```

## Navegação e perfis

A barra superior contém marca, **Início**, **Minhas avaliações**, **Atualizar**,
busca e avatar do perfil. **Adicionar jogo** e **Filtros** ficam junto à coleção.
Os filtros combinam gênero, plataforma e ano; a ordenação permite cadastro,
nome, maior nota ou lançamento. Limpar filtros preserva a busca; Início ou a
logo retornam ao catálogo sem filtros. A grade e sua paginação se ajustam à janela.
O tema usa destaques vermelhos e fundo cinza escuro. Estado da conexão e ID
local ficam no rodapé.

Na primeira abertura sem perfil ativo, o aplicativo solicita nome e ID local.
O menu do avatar permite trocar perfil ou sair. Os perfis ficam no `QSettings`
deste computador; não há senha ou autenticação real. Sair encerra a identificação
ativa e preserva os dados. **Minhas avaliações** lista somente avaliações do ID
do perfil ativo, permite buscar por jogo/comentário, paginar, editar e excluir.
A atualização usa uma requisição HTTP para receber avaliações e seus jogos;
busca e paginação dessa lista são locais. Reinicie Flask e Qt após atualizar.

O cabeçalho busca a logo na pasta `imagem/`, na ordem: `logo.svg`,
`logo techgamer.svg.svg`, `logo.png`, `logo.webp`, `logo.jpg` e `logo.jpeg`.
O primeiro arquivo existente é usado, preservando as proporções.
O caminho é resolvido a partir do código, sem depender da pasta do terminal.
Se o arquivo estiver ausente ou inválido, a identificação textual permanece.
A média das avaliações aparece em um indicador circular. Clique em um
card para consultar suas avaliações e comentários. Nessa janela, use
**Avaliar jogo** para criar uma avaliação com estrelas, nota e comentário.
O popup de avaliação tem cabeçalho próprio, fechamento por botão ou Esc e
nota numérica sincronizada às estrelas, comentário opcional e identificação do autor.
O formulário não exibe campos técnicos de JSON. Em janelas menores, os campos podem ser rolados,
mantendo os botões de ação disponíveis.
Os formulários de adicionar e editar jogos usam o mesmo painel arredondado,
com campos identificados acima dos controles, gênero/plataforma/ano agrupados
e uma seção própria para selecionar a capa local ou informar seu link.
Clique em um card para abrir a janela de detalhes, com descrição, média,
avaliações e comentários. O menu dessa janela permite escolher capa, editar
ou excluir o jogo. A ação principal permite criar uma avaliação ou editar
a avaliação já existente do perfil naquele jogo.
Em **Escolher capa**, selecione uma imagem PNG, JPG ou WebP do computador.
A preferência da capa local fica salva neste computador, sem alterar os dados da API.
O aplicativo guarda o caminho escolhido, sem copiar a imagem. Os arquivos podem
ser organizados manualmente em uma pasta como `dados/capas/`, mas movê-los ou
copiar o projeto para outro computador pode exigir selecionar as capas novamente.
Armazenar e transportar automaticamente as imagens não faz parte desta revisão visual.
No cadastro e na edição, o campo **Link da capa** aceita um endereço HTTP ou
HTTPS direto para uma imagem. Esse link é salvo pela API e a imagem é carregada
sem bloquear a interface. Ao salvar um link, ele substitui a preferência local.
Se a capa falhar, passe o mouse sobre o card para ler o motivo e clique em
**Atualizar** para tentar novamente. Após atualizar o código do servidor,
reinicie o processo Flask; o cliente avisa se o servidor ainda não suporta capas.
Mantenha o arquivo de imagem no local escolhido. Jogos sem capa usam uma arte
provisória com o nome; jogos sem avaliações exibem um traço no indicador.

## Avaliações por estrelas

- Cinco estrelas correspondem à nota 10; um quarto de estrela corresponde a 0,5 ponto.
- Clique em uma das quatro partes da estrela ou use as setas do teclado.
  Por exemplo, 4,75 estrelas correspondem à nota 9,5/10.
- O botão **Zerar** e a tecla **Home** permitem nota zero.
- O campo numérico aceita decimais, como 9,5. Notas já cadastradas com até duas
  casas decimais são preservadas no formulário; as estrelas mostram o preenchimento
  proporcional. A API recebe sempre a escala 0–10.
- A identificação do autor é obrigatória no cadastro. O ID local não é login
  nem autenticação. Para editar ou excluir, escolha o ator local na janela:
  autor ou moderador fictício 99. O cliente envia `X-Ator-Id` e o Proxy do
  servidor bloqueia terceiros com HTTP 403.
- A edição mantém o autor e os metadados já salvos. O formulário envia apenas
  nota e comentário; o servidor preserva os metadados atuais. No cadastro,
  os metadados recebem o padrão `{}`. O campo continua disponível pela API.
- Avaliações antigas sem autor ficam disponíveis para leitura, com edição e
  exclusão individual desabilitadas conforme a regra atual do servidor.

## Comportamento das telas

As requisições são executadas em `QThreadPool`; os resultados chegam à interface
por sinais Qt. Os controles de navegação ficam temporariamente indisponíveis
durante a operação, sem bloquear o loop de eventos. As ações deste cliente são
serializadas. Isso não substitui o controle de concorrência no servidor.

Falhas no salvamento mantêm o formulário aberto com os valores preenchidos.
Exclusões exigem confirmação, com cancelar como escolha padrão. Após alterações,
a tela consulta novamente a API e apresenta a média calculada no servidor.
O botão **Atualizar** (F5) permite recuperar de falhas e consultar mudanças feitas
por outro cliente. Não há sincronização automática entre clientes.

## Verificar a entrega

```powershell
python -m unittest discover -s testes -p "test_cliente_qt.py" -v
```

Os testes usam Qt sem janela visível, servidor HTTP local em porta temporária e
arquivos temporários. Cobrem CRUD pelos formulários, conversão de estrelas,
precisão decimal, atualização da média, busca, filtros, paginação, perfis locais,
Minhas avaliações em uma requisição, avaliações legadas, falha de rede e resposta
do loop de eventos durante requisições.

Roteiro manual para apresentação:

1. Iniciar Flask e Qt; cadastrar um jogo com nome, gênero, plataforma e ano.
2. Buscar o jogo e editar sua descrição.
3. Publicar uma avaliação com 4,5 estrelas (nota 9) e outra com nota decimal 9,5.
4. Conferir a média 9,25/10; editar e excluir uma avaliação e conferir a atualização.
5. Parar o servidor, tentar salvar e verificar a mensagem com os campos preservados.
6. Reiniciar o servidor e repetir o salvamento; reiniciar o cliente e conferir os dados.
7. Cancelar uma exclusão; depois confirmar a exclusão de um jogo e suas avaliações.

Os três padrões estão integrados: publicação pelo Builder, edição/exclusão pelo
Proxy e atualização da média pelo Observer. A identificação é fictícia para a
demonstração acadêmica. Avaliações legadas continuam sendo removidas na cascata
ao excluir seu jogo. Consulte o [roteiro T9.1 a T9.4](../documentacao/entrega-design-patterns.md)
e o [relatório de validação](../documentacao/validacao-entrega.md).
