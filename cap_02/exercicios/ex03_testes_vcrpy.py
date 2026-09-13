"""
cap_02 — Exercício 3: Testando o Agente com VCR.py e Mocks
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Use vcrpy para gravar as interações HTTP do agente (chamadas à API OpenRouter e
Tavily) e criar testes determinísticos reproduzíveis sem custo de API.

Requisitos:
1. Crie um cassete VCR para 3 cenários de teste do agente ReAct.
2. Na primeira execução (record_mode="new_episodes"), grave as respostas reais.
3. Nas execuções seguintes, use os cassetes gravados (sem chamadas reais).
4. Implemente os testes com pytest, verificando estrutura e conteúdo da resposta.
5. Adicione um fixture pytest para o grafo compilado.

DICA: Configure vcr.filter_headers para remover OPENROUTER_API_KEY dos cassetes.
Cassetes ficam em cap_02/cassettes/ e NÃO devem ser commitados se contiverem dados sensíveis.
"""
import os
import pytest
import vcr
from dotenv import load_dotenv

load_dotenv()

# Configuração do VCR — filtra a chave de API dos cassetes gravados
my_vcr = vcr.VCR(
    cassette_library_dir="cap_02/cassettes",
    record_mode="none",  # troque para "new_episodes" para regravar
    filter_headers=["authorization", "x-api-key"],
    filter_query_parameters=["api_key"],
)


# TODO: importe o build_react_graph de cap_02/projeto/react_assistant.py


@pytest.fixture
def agent():
    """Fixture que retorna o grafo compilado."""
    # TODO: retorne o grafo compilado
    pass


@my_vcr.use_cassette("react_pesquisa_basica.yaml")
def test_pesquisa_basica(agent):
    """Verifica que o agente responde a uma query simples de pesquisa."""
    # TODO: invoque o agente e verifique que:
    # - result["messages"] não está vazio
    # - a última mensagem é do tipo AIMessage
    # - o conteúdo não está vazio
    pass


@my_vcr.use_cassette("react_pergunta_calculadora.yaml")
def test_calculadora(agent):
    """Verifica que o agente usa a ferramenta de calculadora corretamente."""
    # TODO: invoque com uma pergunta matemática e verifique o resultado
    pass


@my_vcr.use_cassette("react_multiplas_ferramentas.yaml")
def test_multiplas_ferramentas(agent):
    """Verifica que o agente encadeia múltiplas ferramentas quando necessário."""
    # TODO: invoque com uma pergunta que exige busca + cálculo
    pass
