# Arquitetura e padrões

Revisão técnica: 21/10/2026. Os diagramas representam as classes presentes no
código. Jogos e avaliações trafegam como dicionários, sem classes de entidade
separadas.

## Organização

| Componente | Implementação | Responsabilidade |
|---|---|---|
| API Flask | `servidor/app.py` | Rotas, validação, respostas e composição dos serviços. |
| Padrões | `servidor/patterns/avaliacoes.py` | Builder, Proxy, eventos e cálculo da média. |
| Repository | `servidor/storage/repositorio_json.py` | CRUD, JSON e histórico de IDs. |
| Inicialização Qt | `cliente/main.py` | Configura a aplicação e abre a janela principal. |
| Interface | `cliente/telas/` | Biblioteca, formulários, estrelas e capas. |
| Cliente HTTP | `cliente/services/api_client.py` | Requisições e interpretação das respostas. |
| Execução assíncrona | `cliente/services/tarefas.py` | HTTP fora da thread gráfica, resultados por sinais. |

O Qt acessa os dados pelo HTTP. Somente o servidor lê e grava jogos, avaliações
e contadores. Preferências visuais, como caminhos de capas locais, ficam no
`QSettings` do cliente.

## Diagrama de classes do servidor

`AplicacaoFlask` representa o módulo de rotas, não uma classe Python adicional.
`ArquivosJSON` representa os arquivos persistidos.

```mermaid
classDiagram
    class AplicacaoFlask {
        <<modulo>>
        +obter_repositorio()
        +obter_servico()
        +obter_proxy()
        +cadastrar_avaliacao(jogo_id)
        +atualizar_avaliacao(avaliacao_id)
        +excluir_avaliacao(avaliacao_id)
        +consultar_media(jogo_id)
    }
    class AvaliacaoBuilder {
        +com_autor(autor_id)
        +com_nota(nota)
        +com_comentario(comentario)
        +com_metadados(metadados)
        +construir()
        +de_dados(dados)
    }
    class AvaliacoesProxy {
        +ator_id
        +moderadores
        +publicar(jogo_id, dados)
        +editar(avaliacao_id, dados)
        +excluir(avaliacao_id)
    }
    class ServicoAvaliacoes {
        +repositorio
        +eventos
        +media
        +publicar(jogo_id, dados)
        +editar(avaliacao_id, dados)
        +excluir(avaliacao_id)
    }
    class EventosAvaliacoes {
        +inscrever(observador)
        +remover(observador)
        +notificar(jogo_id)
    }
    class NotaMediaObserver {
        +atualizar(jogo_id)
        +consultar(jogo_id)
    }
    class RepositorioJSON {
        +listar_jogos()
        +buscar_jogo(jogo_id)
        +criar_jogo(dados)
        +atualizar_jogo(jogo_id, dados)
        +excluir_jogo(jogo_id)
        +listar_avaliacoes(jogo_id)
        +buscar_avaliacao(avaliacao_id)
        +criar_avaliacao(jogo_id, dados)
        +atualizar_avaliacao(avaliacao_id, dados)
        +excluir_avaliacao(avaliacao_id)
    }
    class ArquivosJSON {
        <<persistencia>>
        jogos.json
        avaliacoes.json
        .contadores_id.json
    }
    AplicacaoFlask --> RepositorioJSON : jogos e consultas
    AplicacaoFlask --> ServicoAvaliacoes : publicar e consultar media
    AplicacaoFlask --> AvaliacoesProxy : editar e excluir avaliacao
    AvaliacoesProxy --> ServicoAvaliacoes : autoriza e delega
    ServicoAvaliacoes ..> AvaliacaoBuilder : valida e constroi
    ServicoAvaliacoes --> RepositorioJSON : persiste
    ServicoAvaliacoes --> EventosAvaliacoes : notifica apos gravar
    ServicoAvaliacoes --> NotaMediaObserver : consulta agregado
    EventosAvaliacoes o--> NotaMediaObserver : observador inscrito
    NotaMediaObserver --> RepositorioJSON : recupera notas
    RepositorioJSON --> ArquivosJSON : le e substitui arquivos
```

## Diagrama de classes do cliente

Os métodos omitidos são auxiliares de desenho e montagem. As setas representam
dependências e relações presentes nos módulos do cliente.

```mermaid
classDiagram
    class JanelaPrincipal {
        +api
        +executor
        +atualizar()
        +adicionar_jogo()
        +abrir_edicao_jogo()
        +remover_jogo()
        +adicionar_avaliacao()
        +abrir_edicao_avaliacao()
        +remover_avaliacao()
    }
    class Formulario {
        +salvo
        +dados()
        +enviar()
        +mostrar_erro(mensagem)
    }
    class FormularioJogo {
        +dados()
        +escolher_imagem()
    }
    class FormularioAvaliacao {
        +dados()
    }
    class Estrelas {
        +nota_alterada
        +nota()
        +definir_nota(nota)
    }
    class CardsDelegate {
        +tentar_novamente()
        +paint(painter, option, index)
    }
    class APIClient {
        +base_url
        +ator_id
        +verificar_servidor()
        +listar_jogos()
        +buscar_jogo(jogo_id)
        +cadastrar_jogo(dados)
        +editar_jogo(jogo_id, dados)
        +excluir_jogo(jogo_id)
        +listar_avaliacoes(jogo_id)
        +cadastrar_avaliacao(jogo_id, dados)
        +editar_avaliacao(avaliacao_id, dados)
        +excluir_avaliacao(avaliacao_id)
        +consultar_media(jogo_id)
    }
    class ExecutorHTTP {
        +ocupado_alterado
        +ocupado
        +executar(operacao, sucesso, falha)
    }
    class _Tarefa {
        +operacao
        +sinais
        +run()
    }
    class _Sinais {
        +concluido
    }
    Formulario <|-- FormularioJogo
    Formulario <|-- FormularioAvaliacao
    JanelaPrincipal --> APIClient : operacoes HTTP
    JanelaPrincipal *-- ExecutorHTTP
    JanelaPrincipal ..> FormularioJogo : abre
    JanelaPrincipal ..> FormularioAvaliacao : abre
    JanelaPrincipal --> CardsDelegate : desenha biblioteca
    Formulario --> ExecutorHTTP : envia salvamento
    FormularioAvaliacao *-- Estrelas
    ExecutorHTTP ..> _Tarefa : agenda em QThreadPool
    _Tarefa *-- _Sinais
    _Sinais ..> ExecutorHTTP : devolve resultado por sinal
```

`JanelaPrincipal` herda de `QMainWindow`, `Formulario` de `QDialog`, `Estrelas`
de `QWidget`, `CardsDelegate` de `QStyledItemDelegate`, `ExecutorHTTP` e `_Sinais`
de `QObject`, e `_Tarefa` de `QRunnable`.

## Aplicação dos padrões

- **Builder (criacional):** reúne autor, nota, comentário e metadados, valida
  os valores e devolve cópia dos dados. O repositório gera o ID.
- **Proxy (estrutural):** controla edição e exclusão individual. Autor e
  moderadores configurados podem agir; avaliações sem autor ficam para leitura.
  Os IDs são fictícios e não constituem autenticação.
- **Observer (comportamental):** eventos após publicação, edição e exclusão
  atualizam média aritmética e quantidade. A consulta reconstrói o resultado
  após reinício ou exclusão em cascata.
- **Repository:** concentra leitura, gravação e geração de IDs.

Publicação: Qt -> HTTP -> Flask -> serviço -> Builder -> JSON -> evento ->
Observer. Edição e exclusão individual passam pelo Proxy antes do serviço.
Excluir um jogo utiliza a cascata do repositório, inclusive para avaliações
legadas, sem autorização individual de cada avaliação removida.

## Persistência, falhas e limites

- Escrita atômica por arquivo: temporário no mesmo diretório e `os.replace`.
- Contadores preservam o maior ID histórico; exclusões não os reduzem.
- JSON inválido é preservado em `.bak` antes da recuperação. Contadores
  corrompidos geram erro, evitando reinicialização silenciosa do histórico.
- A cascata prepara jogos, avaliações e contadores antes das gravações da
  exclusão. Se a escrita das avaliações falha, tenta restaurar os jogos. Se
  a restauração falha, informa as duas falhas. Não é transação entre arquivos
  nem recuperação garantida após encerramento abrupto do processo.
- Falhas de observadores são registradas sem desfazer a operação persistida
  nem impedir os demais observadores. Falhas de persistência continuam como erro.
- O cliente serializa suas tarefas HTTP; o servidor não implementa bloqueio
  global contra gravações simultâneas de vários clientes ou processos.
- O Flask inicia com `app.run(debug=False)`, para demonstração local.
- Capas locais dependem do arquivo escolhido; links dependem do endereço
  informado. As operações principais podem ser demonstradas sem capas.

## Evidências

Consulte [os testes](../testes/README.md), os
[requisitos e critérios](requisitos-e-aceitacao.md) e o
[roteiro T9.1 a T9.4](entrega-design-patterns.md).
