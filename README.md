# TechGames — Gerenciador de Avaliações de Jogos

Aplicação acadêmica para cadastro de jogos e avaliações, desenvolvida em Python.
O servidor fornece uma API REST com Flask e persiste os dados em arquivos JSON
locais, sem banco de dados. A interface Qt permite gerenciar jogos e avaliações
por estrelas, integrada ao servidor via HTTP.

## Tecnologias

- Python
- Flask (servidor)
- PySide6 (interface desktop)
- Requests (cliente HTTP)
- Arquivos JSON locais (persistência)

## Estrutura do repositório

```text
cliente/                   Interface Qt e cliente HTTP
dados/                     Arquivos JSON de jogos e avaliações
documentacao/              Contrato, arquitetura e acompanhamento
servidor/app.py            API Flask e validação
servidor/storage/          Repositório de persistência JSON
testes/                    Testes automatizados
requirements.txt           Dependências Python
```

## Requisitos

- Python 3.10 ou superior (o código usa anotações de tipo com `|`).
- Pip para instalar as dependências de `requirements.txt`.

## Instalação e execução no Windows

No PowerShell, a partir da raiz do repositório:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python servidor\app.py
```

O servidor de desenvolvimento ficará disponível em `http://127.0.0.1:5000`.
Confira se está ativo em `http://127.0.0.1:5000/health`. Em outro terminal, com o
mesmo ambiente virtual ativado, inicie a interface:

```powershell
python -m cliente
```

Consulte [as instruções da interface](cliente/README.md) para o uso das estrelas,
configuração do endereço e roteiro de apresentação. O servidor integrado é o
servidor de desenvolvimento do Flask, voltado ao uso local.

## Persistência

O servidor cria `dados/jogos.json` e `dados/avaliacoes.json` com conteúdo `[]`
quando ainda não existem. Um arquivo auxiliar oculto,
`dados/.contadores_id.json`, mantém os IDs mesmo após exclusões. Dados JSON
malformados são preservados em um arquivo `.bak` antes da recuperação. Os testes
operam somente em diretórios temporários.

## Testes

Com o ambiente virtual ativado, execute:

```powershell
python -m unittest discover -s testes -p "test_*.py" -v
```

## Documentação

- [Contrato da API](documentacao/contrato-api.md) — proposta de integração ainda
  sujeita à aprovação da equipe.
- [Requisitos e critérios de aceitação](documentacao/requisitos-e-aceitacao.md)
  — base provisória; aguarda os requisitos oficiais de João Pedro.
- [Arquitetura e padrões](documentacao/arquitetura-e-padroes.md) — organização,
  padrões, diagrama do servidor e pendência do diagrama do cliente.
- [Acompanhamento da equipe](documentacao/ACOMPANHAMENTO.md)
- [Notas do cliente](cliente/README.md)
- [Notas de testes](testes/README.md)

## Estado da entrega

Builder, Proxy e Observer estão integrados ao Flask e à interface Qt. Para
editar/excluir avaliações, escolha o ID local do autor ou o moderador fictício
99. A interface recebe a média do servidor e permite metadados JSON opcionais.
Não há login. Consulte o [roteiro dos padrões](documentacao/entrega-design-patterns.md)
para demonstrar os cenários T9.1 a T9.4. A revisão final dos requisitos e dos
outros documentos da equipe continua necessária antes da entrega acadêmica.
