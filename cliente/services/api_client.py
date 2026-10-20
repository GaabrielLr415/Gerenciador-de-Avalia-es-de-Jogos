
import requests


class APIClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")
        self.timeout = 5


    def verificar_servidor(self):
        return self._request("GET", "/health")


    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )

            response.raise_for_status()

            if response.status_code == 204 or not response.content:
                return None

            return response.json()

        except requests.exceptions.HTTPError as erro:
            resposta = erro.response
            mensagem = "O servidor retornou um erro."

            try:
                dados_erro = resposta.json()

                if isinstance(dados_erro, dict):
                    mensagem = (
                        dados_erro.get("detalhes")
                        or dados_erro.get("erro")
                        or mensagem
                    )
                else:
                    mensagem = str(dados_erro)

            except ValueError:
                if resposta.text:
                    mensagem = resposta.text

            raise Exception(
                f"Erro HTTP {resposta.status_code}: {mensagem}"
            ) from erro

        except requests.exceptions.ConnectionError as erro:
            raise Exception(
                "Não foi possível conectar ao servidor Flask."
            ) from erro

        except requests.exceptions.Timeout as erro:
            raise Exception(
                "O servidor demorou para responder."
            ) from erro

        except requests.exceptions.RequestException as erro:
            raise Exception(
                f"Erro na requisição HTTP: {erro}"
            ) from erro

        except ValueError as erro:
            raise Exception(
                "O servidor retornou uma resposta JSON inválida."
            ) from erro



    
    def listar_jogos(self):
        return self._request("GET", "/jogos")

    def buscar_jogo(self, jogo_id):
        return self._request("GET", f"/jogos/{jogo_id}")

    def cadastrar_jogo(self, dados):
        self._verificar_suporte_capa(dados)
        return self._request("POST", "/jogos", json=dados)

    def editar_jogo(self, jogo_id, dados):
        self._verificar_suporte_capa(dados)
        return self._request("PUT", f"/jogos/{jogo_id}", json=dados)

    def _verificar_suporte_capa(self, dados):
        if dados.get("capa_url"):
            estado = self.verificar_servidor()
            if "capa_url" not in estado.get("recursos", []):
                raise Exception(
                    "O servidor aberto está desatualizado e não salva links de capa. "
                    "No terminal do servidor, pressione Ctrl+C e execute novamente "
                    "python -m servidor.app. Depois tente Salvar outra vez."
                )

    def excluir_jogo(self, jogo_id):
        return self._request("DELETE", f"/jogos/{jogo_id}")


    
    def listar_avaliacoes(self, jogo_id):
        return self._request(
            "GET",
            f"/jogos/{jogo_id}/avaliacoes"
        )

    def cadastrar_avaliacao(self, jogo_id, dados):
        return self._request(
            "POST",
            f"/jogos/{jogo_id}/avaliacoes",
            json=dados
        )

    def editar_avaliacao(self, avaliacao_id, dados):
        return self._request(
            "PUT",
            f"/avaliacoes/{avaliacao_id}",
            json=dados
        )

    def excluir_avaliacao(self, avaliacao_id):
        return self._request(
            "DELETE",
            f"/avaliacoes/{avaliacao_id}"
        )
    
