# Coordenação da equipe — TechGames

Prazo final: **24/10/2026**; meta de versão completa: **23/10/2026**.

| Issue | Responsável | Entrega principal |
|---|---|---|
| #1 | Gabriel | Estrutura e servidor Flask — 18/10 |
| #2 | João Pedro | Requisitos, patterns e testes — 21/10 (requisitos até 13/10) |
| #3 | Edino | Interface Qt — 19/10 (primeira janela até 14/10) |
| #4 | Fillipe | Integração HTTP — 21/10 (módulo HTTP até 15/10) |
| #5 | Angélica | JSON até 15/10, documentação até 22/10, README até 23/10 |

Cada integrante cria uma branch a partir de `main` atualizada, abre PR com referência à Issue e solicita revisão. Sem alterações diretas em `main`.

**Bloqueios:** comentar na Issue o que está faltando e usar simuladores/contratos para desenvolver em paralelo.

**Pendências imediatas:** aprovar `contrato-api.md`, atribuir Assignees, confirmar convites, testar `/health` localmente, testar empacotamento com antecedência.

## Tarefa de Angélica — persistência e documentação

- **Persistência JSON:** implementação em `servidor/storage/repositorio_json.py`,
  com listas JSON, IDs persistentes, gravação atômica, recuperação com backup e
  testes isolados em diretórios temporários.
- **Documentação existente:** contrato provisório, critérios organizados e
  diagrama do servidor registrados em `documentacao/`.
- **Revisões ainda necessárias:** obter os requisitos oficiais e critérios de
  João Pedro; validar o contrato e documentação com Gabriel; obter de Edino as
  classes do cliente para completar o diagrama correspondente.
- **README final:** instruções de instalação, execução, persistência, testes e
  links para a documentação foram consolidadas no README da raiz; confirmar
  dependências e fluxo de execução com a equipe antes da versão final.

Documentos relacionados:

- [Requisitos e critérios de aceitação](requisitos-e-aceitacao.md)
- [Arquitetura e padrões](arquitetura-e-padroes.md)
