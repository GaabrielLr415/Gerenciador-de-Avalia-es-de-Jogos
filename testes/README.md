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

Ainda faltam testes automatizados das rotas Flask e dos fluxos da interface Qt.
