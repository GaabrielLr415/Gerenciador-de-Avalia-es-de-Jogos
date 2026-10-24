# Pacote portátil Windows

O enunciado pede execução sem configurações ou instalação de outros softwares.
O pacote inclui o interpretador Python, Flask, Qt e as bibliotecas utilizadas.
O destinatário extrai o ZIP e abre `TechGamer/TechGamer.exe` em Windows de 64 bits.
Não precisa instalar Python, executar pip ou abrir terminais.

## Funcionamento

`iniciar.py` inicia o servidor Flask em `127.0.0.1`, numa porta livre escolhida
pelo sistema, e abre o cliente Qt apontado para esse endereço. São os mesmos
módulos do projeto, comunicando-se por HTTP local. Ao fechar a janela, o servidor
encerra. O pacote não publica serviços na internet.

```text
TechGamer/
  TechGamer.exe
  LEIA-ME.txt
  _internal/       Python, bibliotecas e imagens da interface
  dados/           jogos.json, avaliacoes.json e contador de IDs
  preferencias/    Criada durante o uso: perfis e preferências locais
```

Extraia a pasta inteira; copiar somente o `.exe` não funciona. Guarde-a numa
pasta em que o usuário possa gravar. Para transportar a biblioteca, feche a
aplicação e copie a pasta inteira, incluindo arquivos ocultos de `dados/`.
O pacote inclui uma cópia dos jogos e avaliações existentes no momento da geração.
As capas remotas continuam dependendo de internet; o servidor e os dados são locais.

## Gerar novamente

Estes comandos são somente para quem prepara a entrega. Exigem Windows de 64 bits
e o ambiente de desenvolvimento descrito no [README](../README.md).
As ferramentas de empacotamento ficam separadas das dependências da aplicação.

```powershell
.\.venv\Scripts\python.exe -m pip install --target .local/empacotamento/lib -r requirements-build.txt
.\.venv\Scripts\python.exe -B ferramentas/empacotar.py
```

O script usa [PyInstaller](https://www.pyinstaller.org/en/stable/usage.html)
em modo de pasta. Gera uma nova pasta em `dist/`, um ZIP e seu SHA-256, sem
substituir pacotes anteriores. Python e dependências do computador de geração
não precisam existir no computador de destino. Gere um novo pacote após alterar
código, imagens ou dados; o executável não acompanha essas alterações automaticamente.

Para a entrega no GitHub, mantenha código e dados no repositório público e
anexe o ZIP portátil e o SHA-256 a uma Release. `dist/` é ignorada pelo Git;
enviar apenas o código-fonte não disponibiliza o executável. Nenhuma Release
foi publicada nesta preparação.

## Verificação realizada em 24/10/2026

- Pacote: `TechGamer-Windows-x64-20261024-151025.zip`, 51.008.863 bytes.
- SHA-256: `4d27f7a99ac8fec5745fc3d5663d0d64bdeaa67ce22b9296c1449a3e8ebe3a3e`.
- O ZIP foi extraído numa pasta temporária com espaços no nome.
- O executável rodou com PATH limitado a pastas do Windows e sem `PYTHONHOME`,
  `PYTHONPATH` ou `VIRTUAL_ENV`. O relatório confirmou execução empacotada.
- Passaram: HTTP local, inicialização Qt, logo SVG, cadastro de jogo, publicação
  e edição de avaliação, média, consulta por autor e exclusão em cascata.
- A verificação usou dados temporários e preservou os JSONs reais e os do pacote.
- A suíte do código permaneceu com **107 testes aprovados, sem falhas ou erros**.

O modo técnico de conferência gera um relatório JSON, sem modificar a biblioteca:

```powershell
.\TechGamer.exe --verificar "$env:TEMP\techgamer-verificacao.json"
```

Essa execução ocorreu no computador de desenvolvimento. Remover Python do PATH
não substitui o teste em um computador que nunca teve Python instalado.

## Teste manual e evidências para o Word

Use uma cópia extraída do ZIP para o ensaio, preservando o pacote original.
Registre no Word a versão do pacote, o Windows, a data, quem executou, o resultado
esperado, o observado e as capturas feitas durante cada caso.

1. Em outro computador sem Python, extraia o ZIP e abra o `.exe` com dois cliques.
   Registre a tela inicial e confirme que nenhum instalador ou terminal foi necessário.
2. Cadastre um jogo de teste e confira busca, filtros, detalhes e descrição.
3. Execute os cenários T9.1 a T9.4 do [roteiro](entrega-design-patterns.md),
   capturando as notas, médias e a mensagem de acesso negado.
4. Feche, abra novamente e confirme a persistência do jogo e das avaliações.
5. Exclua o jogo de teste e confira a remoção das avaliações vinculadas.
6. Desconecte a internet e confirme o funcionamento do CRUD local; as capas
   por URL podem ficar indisponíveis. Registre essa condição separadamente.

Inclua os diagramas de classes do servidor e do cliente, baseados em
[arquitetura e padrões](arquitetura-e-padroes.md). As capturas, os resultados
manuais e o aceite em outro computador ainda não foram produzidos nesta etapa.
