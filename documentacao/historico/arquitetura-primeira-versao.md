# Arquitetura e Padrões de Projeto (Design Patterns) - TechGames

O projeto **TechGames** adota uma arquitetura limpa e desacoplada, dividida entre Cliente (Qt) e Servidor (Flask), utilizando padrões de projeto para garantir a organização, manutenibilidade e escalabilidade do código.

---

## 1. Padrão Repository (Repositório)
* **Onde é aplicado:** No módulo de persistência do servidor (`servidor/storage/` e `repositorio_json.py`).
* **Problema que resolve:** Isola a lógica de acesso a dados (leitura e gravação em arquivos JSON) da lógica de negócios da aplicação e das rotas da API.
* **Justificativa:** Evita que comandos de manipulação de arquivos fiquem espalhados pelo código do Flask, centralizando as operações de CRUD (Criar, Ler, Atualizar, Deletar) em uma interface única.
* **Módulos envolvidos:** `repositorio_json.py`, classes de manipulação de entidades de Jogos e Avaliações.

---

## 2. Padrão Controller / Routes (Controlador / Rotas)
* **Onde é aplicado:** No servidor Flask (`servidor/routes/` ou `app.py`).
* **Problema que resolve:** Organiza o tratamento das requisições HTTP recebidas do cliente.
* **Justificativa:** Separa o recebimento das rotas (`GET`, `POST`, `PUT`, `DELETE`) das regras internas de validação e persistência, mantendo o código modular e limpo.

---

## 3. Padrão MVC / Separação de Componentes (Cliente Qt)
* **Onde é aplicado:** No cliente desktop (`cliente/`).
* **Problema que resolve:** Organiza a interface gráfica separando a camada visual (telas e widgets Qt) da lógica de comunicação de rede (requisições HTTP via `requests`).
* **Justificativa:** Permite que o Fillipe estruture as chamadas de API de forma isolada dos botões e tabelas da interface, facilitando a manutenção e a visualização dos dados.
