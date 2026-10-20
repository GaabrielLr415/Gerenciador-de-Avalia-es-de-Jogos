# Testes

Responsável: João Pedro; apoio de toda a equipe.

## Executar

Na raiz do projeto, com as dependências instaladas:

```powershell
python -m unittest discover -s testes -p "test_*.py" -v
```

## Cobertura existente

`test_repositorio_json.py` verifica inicialização dos arquivos, operações CRUD,
persistência ao recriar o repositório, IDs não reutilizados, exclusão em
cascata, recuperação de JSON/codificação inválidos e preservação dos dados em
backup. Os arquivos de teste são criados em diretório temporário; os JSON de
`dados/` não são alterados.

`test_api_flask.py` cobre as rotas Flask, validações, erros e persistência.

`test_cliente_qt.py` cobre o fluxo Qt → HTTP → Flask em uma porta temporária,
com dados isolados: CRUD pelos formulários, estrelas e notas decimais, média,
busca, avaliações legadas, falhas de conexão e responsividade da interface.
Requer PySide6, Flask e Requests. Por padrão usa `QT_QPA_PLATFORM=offscreen`,
sem abrir janelas durante a execução.
