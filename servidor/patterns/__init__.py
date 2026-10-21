"""Builder, Proxy e Observer independentes de Flask e Qt."""
from .avaliacoes import (
    AvaliacaoBuilder, ServicoAvaliacoes, AvaliacoesProxy,
    EventosAvaliacoes, NotaMediaObserver,
    AutorizacaoError,
)
