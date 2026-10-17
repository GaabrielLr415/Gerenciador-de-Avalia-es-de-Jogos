# TechGames — Gerenciador de Avaliações de Jogos

Aplicação acadêmica para cadastro de jogos e avaliações, desenvolvida em Python.
O servidor fornece uma API REST com Flask e persiste os dados em arquivos JSON
locais, sem banco de dados. A interface Qt e a integração HTTP estão em
desenvolvimento.

## Tecnologias

- Python
- Flask (servidor)
- PySide6 (interface prevista)
- Requests (cliente HTTP previsto)
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
Confira se está ativo em `http://127.0.0.1:5000/health`. O servidor usa modo de
depuração para desenvolvimento local; não o publique diretamente na internet.

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

A persistência JSON está implementada e coberta por testes focados. A
documentação final depende de confirmar o contrato com Gabriel, incorporar os
requisitos oficiais de João Pedro e receber de Edino as classes reais do
cliente. Consulte o documento de acompanhamento antes de considerar a entrega
final aprovada.
