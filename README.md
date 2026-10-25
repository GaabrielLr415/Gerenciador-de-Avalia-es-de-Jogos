# TechGamer

Organize sua coleção de jogos, escreva avaliações e acompanhe as notas em um
aplicativo para Windows.

**[⬇ Baixar TechGamer para Windows — 64 bits](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/releases/download/v1.0.0/TechGamer-Windows-x64-20261024-151025.zip)**

Versão **1.0.0** · [Ver a Release e o arquivo de verificação](https://github.com/GaabrielLr415/Gerenciador-de-Avalia-es-de-Jogos/releases/tag/v1.0.0)

## Baixar e abrir

1. Clique no link de download acima.
2. Clique com o botão direito no ZIP baixado e escolha **Extrair Tudo**.
3. Abra a pasta extraída e entre na pasta **TechGamer**.
4. Dê dois cliques em **TechGamer.exe**.

**Pronto: a interface e o servidor local iniciam automaticamente.**
Python, Flask, Qt e as bibliotecas necessárias já acompanham o pacote.
Você não precisa instalar dependências nem abrir um terminal.

Mantenha a pasta `_internal` junto ao executável e extraia o programa numa pasta
em que você possa salvar arquivos, como Documentos.

> Para usar o programa, baixe o ZIP pelo link acima. O botão **Code → Download ZIP**
> do GitHub baixa o código-fonte, que exige um ambiente de desenvolvimento.

## O que você pode fazer

- Cadastrar jogos com nome, gênero, plataforma, ano, descrição e capa.
- Buscar jogos, combinar filtros e ordenar o catálogo.
- Avaliar com estrelas e notas de **0 a 10**, incluindo notas como **9,5**.
- Escrever comentários e consultar a média das avaliações de cada jogo.
- Criar perfis locais e acessar **Minhas avaliações** para gerenciar suas notas.
- Editar ou excluir jogos e avaliações.

## Primeiro acesso

1. Quando solicitado, crie um perfil com seu nome e um número de identificação.
   Esse perfil é local e não exige cadastro em um serviço online.
2. Escolha um jogo do catálogo ou clique em **Adicionar jogo**.
3. Abra os detalhes do jogo e clique em **Avaliar jogo**.
4. Para consultar ou editar suas avaliações, acesse **Minhas avaliações**.

Os perfis usam IDs locais, sem senha ou autenticação. Para os testes de permissão,
o ID **99** representa o moderador de demonstração.

Consulte o [guia da interface](cliente/README.md) para conhecer os filtros,
as estrelas, os perfis e as opções de capa.

## Onde ficam meus dados?

No pacote portátil, jogos e avaliações ficam em `dados/`, ao lado de
`TechGamer.exe`. Perfis e preferências ficam em `preferencias/`.
Os dados permanecem salvos ao fechar o aplicativo.

Para fazer uma cópia de segurança, feche o programa e copie a pasta inteira
`TechGamer`, incluindo os arquivos ocultos. Capas escolhidas do computador
continuam nos caminhos originais; mantenha também esses arquivos.

**As capas por link dependem de internet.** O cadastro, as avaliações e as consultas
usam o servidor local e arquivos JSON, sem banco de dados ou serviços de IA.

## Como o projeto funciona

O TechGamer é um projeto acadêmico da disciplina **Paradigmas de Programação**,
com dois módulos que se comunicam por HTTP local:

| Parte | Tecnologia | Responsabilidade |
|---|---|---|
| Cliente | Qt / PySide6 | Exibir as telas e enviar as ações do usuário à API. |
| Servidor | Flask | Validar as operações, aplicar as regras e salvar os dados. |
| Persistência | Arquivos JSON | Guardar jogos, avaliações e histórico de IDs. |

O projeto aplica três padrões: **Builder**, para construir avaliações;
**Proxy**, para verificar permissões de edição e exclusão; e **Observer**,
para atualizar a média após alterações nas avaliações.

## Para quem vai desenvolver

<details>
<summary><strong>Ver instalação, execução pelo código e testes</strong></summary>

### Preparar o ambiente

Ambiente validado: **Windows de 64 bits com Python 3.13.5**.
A instalação das dependências exige internet. As versões estão fixadas em
`requirements.txt`.

Clone o repositório ou baixe o código em **Code → Download ZIP**.
Abra o PowerShell na raiz do projeto, onde está este README, e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Os comandos usam o Python do ambiente diretamente, sem precisar ativá-lo.

### Abrir a aplicação pelo código

Para iniciar o servidor e o cliente juntos:

```powershell
.\.venv\Scripts\python.exe -B iniciar.py
```

Para executar os módulos separadamente, abra dois terminais na raiz.
No primeiro, inicie o servidor:

```powershell
.\.venv\Scripts\python.exe -m servidor.app
```

No segundo, inicie o cliente:

```powershell
.\.venv\Scripts\python.exe -m cliente
```

Nesse modo, o servidor usa `http://127.0.0.1:5000`.
A rota `/health` informa o estado da API. Feche o cliente pela janela
e encerre o servidor com **Ctrl+C**. Use uma instância por pasta de dados.

### Executar os testes

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s testes -p "test_*.py" -v
```

A última rodada registrada teve **107 testes aprovados**, sem falhas ou erros.
Os testes usam dados temporários; a interface é exercitada sem janela visível,
com comunicação HTTP local.

Consulte a [cobertura dos testes](testes/README.md) e o
[relatório de validação](documentacao/validacao-entrega.md) para ver os resultados
e os limites dessa verificação.

### Onde alterar o código

```text
cliente/                   Interface Qt e comunicação HTTP
servidor/app.py            Endpoints da API Flask
servidor/validacoes.py     Validação dos dados recebidos
servidor/patterns/         Builder, Proxy e Observer
servidor/storage/          Persistência JSON e contadores de IDs
dados/                     Jogos e avaliações
testes/                    Testes automatizados
documentacao/              Guias, requisitos, diagramas e validação
iniciar.py                 Inicialização automática de servidor e cliente
ferramentas/empacotar.py    Geração do pacote portátil
```

Comece pelo [guia do código](documentacao/guia-do-codigo.md).
Para gerar outro executável, siga o [guia de empacotamento](documentacao/portatil.md).

O Git ignora `.venv/`, `.local/`, `dist/`, caches e logs.
As bibliotecas instaladas e os arquivos temporários ficam fora do repositório.

</details>

## Documentação

| Quero consultar… | Onde encontrar |
|---|---|
| Documentação final do projeto | [PROJETO TECHGAMER - FINAL (PDF)](documentacao/PROJETO%20TECHGAMER%20-%20FINAL.pdf) |
| Situação geral e pendências da entrega | [Checklist geral](documentacao/checklist-geral.md) |
| Como usar as telas | [Guia da interface](cliente/README.md) |
| Requisitos funcionais, restrições e condições de aceitação | [Requisitos e aceitação](documentacao/requisitos-e-aceitacao.md) |
| Classes e design patterns do cliente e do servidor | [Arquitetura e diagramas](documentacao/arquitetura-e-padroes.md) |
| Rotas, campos e respostas HTTP | [Contrato da API](documentacao/contrato-api.md) |
| Organização e leitura do projeto | [Guia do código](documentacao/guia-do-codigo.md) |
| Resultados dos testes e pendências | [Relatório de validação](documentacao/validacao-entrega.md) |
| Como gerar o executável | [Pacote portátil](documentacao/portatil.md) |
| Roteiro da apresentação | [Demonstração dos padrões](documentacao/entrega-design-patterns.md) |
| Responsabilidades da equipe | [Acompanhamento](documentacao/ACOMPANHAMENTO.md) |

Os testes manuais foram aprovados conforme relato de Gabriel.
A execução em outro computador sem Python ainda aguarda confirmação.
