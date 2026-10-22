# TechGames - Gerenciador de Avaliações de Jogos

Aplicação acadêmica em Python, Flask e Qt (PySide6), com persistência local em
JSON. Permite cadastrar jogos, publicar avaliações de 0 a 10 com comentários e
metadados, consultar médias e demonstrar Builder, Proxy e Observer.

Entrega planejada pela equipe: **23/10/2026**. O PDF disponível contém os cenários
de teste, mas não informa prazo nem exige executável. A necessidade de entregar
um executável sem Python ainda deve ser confirmada com o professor.

## Estrutura

```text
cliente/                   Interface Qt e comunicação HTTP
servidor/app.py            API Flask
servidor/patterns/         Builder, Proxy, serviço e Observer
servidor/storage/          Repository JSON e contadores
dados/                     Jogos e avaliações locais
testes/                    Testes automatizados com dados temporários
documentacao/              Requisitos, contrato, diagramas e validação
requirements.txt           Dependências
```

## Instalar no Windows

Requer Python 3.10 ou superior, 64 bits, pip e acesso à internet para baixar
dependências. Use uma pasta em que o usuário possa gravar os dados.
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
anterior do TechGames antes de iniciar outra.

Para apontar o cliente para outro servidor já iniciado:

```powershell
.\.venv\Scripts\python.exe -m cliente --servidor http://127.0.0.1:5000
```

## Avaliações e padrões

- Novas avaliações exigem `autor_id` inteiro positivo e nota entre 0 e 10.
  Comentário é opcional; `metadados` é objeto JSON opcional, com padrão `{}`.
- O Builder valida e constrói os dados antes da persistência.
- Para editar ou excluir individualmente, selecione o ID local do autor ou o
  moderador fictício **99**. O cliente envia `X-Ator-Id`; o Proxy verifica a regra.
- IDs locais servem à demonstração acadêmica, sem login ou autenticação.
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
- [Roteiro de demonstração T9.1 a T9.4](documentacao/entrega-design-patterns.md)
- [Validação e pendências de entrega](documentacao/validacao-entrega.md)
- [Responsabilidades e acompanhamento](documentacao/ACOMPANHAMENTO.md)
- [Uso da interface](cliente/README.md)

A execução pelo código está documentada. Não há executável empacotado validado.
A revisão visual presencial e o teste em outro computador continuam necessários
antes de declarar a entrega acadêmica concluída.
