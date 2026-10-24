# TechGamer - Gerenciador de Avaliações de Jogos

Aplicação acadêmica em Python, Flask e Qt (PySide6), com persistência local em
JSON. Permite cadastrar jogos, publicar avaliações de 0 a 10 com comentários e
metadados, consultar médias e demonstrar Builder, Proxy e Observer. O catálogo
tem busca, filtros, ordenação e paginação; perfis locais permitem consultar
e gerenciar as próprias avaliações.

O enunciado exige execução sem instalar outros softwares. Para isso, foi criada
uma versão portátil para **Windows de 64 bits**, com Python, Flask e Qt incluídos.
O código-fonte continua disponível para leitura, testes e desenvolvimento.

## Usar sem instalar

1. Baixe o pacote **TechGamer-Windows-x64** da entrega e extraia o ZIP inteiro.
2. Entre na pasta `TechGamer` e abra `TechGamer.exe` com dois cliques.
3. Use a interface; o servidor Flask inicia e encerra automaticamente.

Mantenha a pasta `_internal` junto ao executável. Jogos e avaliações ficam em
`dados/`; perfis e preferências ficam em `preferencias/`. Use uma pasta com
permissão de gravação. As capas por URL dependem de internet.

O ZIP portátil é diferente do **Download ZIP** do código-fonte do GitHub.
Consulte [como gerar, conferir e entregar o pacote](documentacao/portatil.md).

## Estrutura

```text
cliente/                   Interface Qt e comunicação HTTP
servidor/app.py            API Flask
servidor/validacoes.py      Validação dos corpos JSON da API
servidor/patterns/         Builder, Proxy, serviço e Observer
servidor/storage/          Repository JSON e contadores
dados/                     Jogos e avaliações locais
testes/                    Testes automatizados com dados temporários
documentacao/              Requisitos, contrato, diagramas e validação
requirements.txt           Dependências
iniciar.py                 Inicializador do pacote portátil
ferramentas/empacotar.py    Geração do ZIP Windows
```

O Git ignora `.venv/`, caches Python, logs e `.local/`. O ambiente virtual contém
as bibliotecas instaladas; `.local/` guarda notas e backups locais, usados apenas
durante o desenvolvimento. Essas pastas não precisam ser enviadas ao GitHub.

## Preparar o código para desenvolvimento no Windows

Requer Python 3.10 a 3.15, 64 bits, pip e acesso à internet para baixar
dependências. Use uma pasta em que o usuário possa gravar os dados.
Para reproduzir o ambiente validado, use Python **3.13.5**. As dependências
diretas e transitivas desse ambiente estão fixadas em `requirements.txt`.
A versão efetivamente testada está no [relatório de validação](documentacao/validacao-entrega.md);
a declaração de versão mínima não representa teste de todas as versões do Python.

Baixe o ZIP do repositório e extraia-o, ou use sua cópia local atualizada.
Abra o PowerShell na raiz, onde está este README:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Os comandos usam o Python do ambiente diretamente; não é necessário ativar
scripts nem alterar a política de execução do PowerShell.

## Executar

No primeiro terminal, a partir da raiz:

```powershell
.\.venv\Scripts\python.exe -m servidor.app
```

Confira `http://127.0.0.1:5000/health`: deve retornar `status: ok` e os recursos
`capa_url`, `design_patterns` e `media_servidor`.

Em outro terminal, também na raiz:

```powershell
.\.venv\Scripts\python.exe -m cliente
```

Mantenha o terminal Flask aberto durante o uso. Encerre a interface pela janela
e o servidor com Ctrl+C. Se a porta 5000 já estiver ocupada, encerre a instância
anterior do TechGamer antes de iniciar outra.

Para apontar o cliente para outro servidor já iniciado:

```powershell
.\.venv\Scripts\python.exe -m cliente --servidor http://127.0.0.1:5000
```

## Avaliações e padrões

- Novas avaliações exigem `autor_id` inteiro positivo e nota entre 0 e 10.
  Comentário é opcional. Na API, `metadados` é um objeto JSON opcional, com
  padrão `{}`. O formulário Qt omite esse campo e preserva os valores existentes
  ao editar nota e comentário.
- O Builder valida e constrói os dados antes da persistência.
- Para editar ou excluir individualmente, selecione o ID local do autor ou o
  moderador fictício **99**. O cliente envia `X-Ator-Id`; o Proxy verifica a regra.
- IDs locais servem à demonstração acadêmica, sem login ou autenticação.
- O perfil local guarda nome e ID neste computador. O menu do avatar permite
  trocar perfil ou sair; sair preserva os jogos e as avaliações.
- **Minhas avaliações** consulta as avaliações do perfil em uma requisição
  HTTP, com busca e paginação locais. Reinicie Flask e Qt após atualizar o código.
- Autor, ID da avaliação e vínculo com o jogo são preservados na edição.
- Avaliações antigas sem autor podem ser lidas, mas não alteradas individualmente.
  A exclusão de um jogo continua removendo todas as suas avaliações em cascata.
- O Observer atualiza a média no servidor; o Qt consulta e apresenta o resultado.

## Persistência

O servidor cria `dados/jogos.json` e `dados/avaliacoes.json` quando ausentes.
`dados/.contadores_id.json` preserva os IDs históricos e não é versionado.
Para transportar dados existentes, copie os três arquivos com o servidor parado,
incluindo o contador oculto. Não remova o contador para reiniciar o aplicativo.

Arquivos de dados inválidos podem gerar backup `.bak` antes da recuperação.
Na cascata, há tentativa de restauração se uma gravação falhar. O armazenamento
não oferece transação entre arquivos ou bloqueio entre múltiplos processos.
Use uma instância local para a demonstração.

Não teste cadastros de demonstração sobre os dados reais. Para ensaiar,
extraia uma cópia separada do projeto, sem copiar `dados/` nem `.venv/`.

## Testes

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s testes -p "test_*.py" -v
```

Os testes de dados usam diretórios temporários. Os testes Qt usam interface
sem janela visível e um servidor HTTP local em porta temporária.
Consulte [a cobertura](testes/README.md) e o
[relatório de validação](documentacao/validacao-entrega.md).

## Documentação e apresentação

- [Requisitos e critérios de aceitação](documentacao/requisitos-e-aceitacao.md)
- [Contrato da API](documentacao/contrato-api.md)
- [Arquitetura e diagramas do servidor e cliente](documentacao/arquitetura-e-padroes.md)
- [Guia de leitura e organização do código](documentacao/guia-do-codigo.md)
- [Roteiro de demonstração T9.1 a T9.4](documentacao/entrega-design-patterns.md)
- [Validação e pendências de entrega](documentacao/validacao-entrega.md)
- [Responsabilidades e acompanhamento](documentacao/ACOMPANHAMENTO.md)
- [Uso da interface](cliente/README.md)

O executável foi conferido nesta máquina, com Python removido do PATH do processo,
incluindo Qt, HTTP e operações com dados temporários. Gabriel informou aprovação
dos testes manuais em 24/10/2026. A execução em outro computador sem Python e o
registro das telas ainda aguardam confirmação no relatório de validação.
