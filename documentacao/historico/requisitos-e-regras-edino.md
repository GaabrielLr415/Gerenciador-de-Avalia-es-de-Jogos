# Requisitos e Condições de Aceitação - TechGames

## 1. Requisitos Funcionais (RF)
* **RF01:** O sistema deve permitir o cadastro de novos jogos informando nome, gênero, plataforma, ano de lançamento e descrição opcional.
* **RF02:** O sistema deve listar todos os jogos cadastrados na biblioteca pessoal.
* **RF03:** O sistema deve permitir consultar os detalhes de um jogo específico e suas avaliações.
* **RF04:** O sistema deve permitir editar as informações de um jogo existente.
* **RF05:** O sistema deve permitir excluir um jogo, removendo em cascata todas as avaliações a ele associadas.
* **RF06:** O sistema deve permitir cadastrar avaliações (nota de 0 a 10 com suporte a decimais e comentário opcional) para um jogo existente.
* **RF07:** O sistema deve permitir listar, editar e excluir avaliações.
* **RF08:** O sistema deve validar os campos enviados, rejeitando dados inválidos ou fora do escopo.
* **RF09:** O sistema deve persistir os dados localmente em arquivos JSON, garantindo que estejam disponíveis após reiniciar a aplicação.

## 2. Requisitos Não-Funcionais (RNF)
* **RNF01:** A aplicação deve ser desenvolvida em linguagem Python.
* **RNF02:** O backend do servidor deve utilizar o framework Flask.
* **RNF03:** A interface gráfica do cliente deve ser desenvolvida em Qt (PySide/PyQt).
* **RNF04:** Não será permitida a utilização de bancos de dados relacionais/não-relacionais, APIs de terceiros, nuvem ou inteligência artificial.
* **RNF05:** A comunicação entre cliente e servidor deve ocorrer estritamente via protocolo HTTP consumindo os endpoints da API.
* **RNF06:** O código-fonte deve ser versionado e disponibilizado em um repositório público no GitHub sem exigir configurações complexas de softwares externos.

## 3. Condições de Aceitação
* **Cadastro e Listagem:** Um jogo válido é inserido e listado corretamente na interface.
* **Exclusão em Cascata:** Ao deletar um jogo, as avaliações vinculadas a ele desaparecem do armazenamento JSON de forma automática e segura.
* **Persistência:** O reinicio do servidor não pode apagar os dados salvos previamente nos arquivos JSON.
* **Validação de Notas:** O sistema deve recusar notas fora do intervalo de 0 a 10.
