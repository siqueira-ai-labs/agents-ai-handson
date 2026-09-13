"""
cap_02 — Solução Exercício 3: Testando o Agente com VCR.py
Dificuldade: Difícil | Tempo estimado: ~2-3h

Modo de uso:
  Gravar cassetes (requer API keys reais):
      VCR_RECORD_MODE=new_episodes pytest ex03_testes_vcrpy_solucao.py

  Replay determinístico (padrão, sem chamadas à API):
      pytest ex03_testes_vcrpy_solucao.py
"""
import json
import os
import pathlib
import re
import sys

import pytest
import vcr
from langchain_core.messages import AIMessage, ToolMessage

from ex01_nova_tool_react_solucao import build_react_graph

# ── Configuração VCR ──────────────────────────────────────────────────────────

CASSETTES_DIR = str(pathlib.Path(__file__).parent.parent / "cassettes")

# Seguro para CI (none); desenvolvedor usa VCR_RECORD_MODE=new_episodes para regravar
_RECORD_MODE = os.getenv("VCR_RECORD_MODE", "none")


def _scrub_request(request):
    """Remove api_key do corpo de requisições POST antes de gravar no cassete."""
    if request.body:
        try:
            body = json.loads(request.body)
            if "api_key" in body:
                body["api_key"] = "REDACTED"
                request.body = json.dumps(body).encode()
        except (ValueError, TypeError):
            if isinstance(request.body, bytes):
                request.body = re.sub(
                    rb'"api_key"\s*:\s*"[^"]*"', b'"api_key": "REDACTED"', request.body
                )
    return request


my_vcr = vcr.VCR(
    cassette_library_dir=CASSETTES_DIR,
    record_mode=_RECORD_MODE,
    filter_headers=["authorization", "x-api-key"],
    filter_query_parameters=["api_key"],
    filter_post_data_parameters=["api_key"],
    before_record_request=_scrub_request,
    match_on=["method", "scheme", "host", "port", "path", "query"],
    decode_compressed_response=True,
)


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def agent():
    """Retorna o grafo ReAct compilado com módulo recarregado.

    O reload garante que a instância usa o LLM real (credenciais do .env),
    mesmo quando os testes unitários já cachearam o módulo com um mock.
    """
    import importlib

    mod = importlib.reload(sys.modules["ex01_nova_tool_react_solucao"])
    return mod.build_react_graph()


# ── Testes com cassetes VCR ───────────────────────────────────────────────────

@my_vcr.use_cassette("react_pesquisa_basica.yaml")
def test_pesquisa_basica(agent):
    """Agente responde a query simples de pesquisa."""
    result = agent.invoke({"messages": [("human", "O que é o padrão ReAct em IA?")]})

    assert result["messages"], "Nenhuma mensagem retornada"
    last = result["messages"][-1]
    assert isinstance(last, AIMessage), f"Última mensagem deveria ser AIMessage, não {type(last)}"
    assert last.content.strip(), "Conteúdo da resposta está vazio"


@my_vcr.use_cassette("react_calculadora.yaml")
def test_calculadora(agent):
    """Agente usa a ferramenta calculator para resolver uma expressão matemática."""
    result = agent.invoke({
        "messages": [("human", "Quanto é a raiz quadrada de 144 multiplicada por 7?")]
    })

    last = result["messages"][-1]
    assert isinstance(last, AIMessage)
    # O resultado correto é √144 × 7 = 12 × 7 = 84
    assert "84" in last.content, f"Esperava '84' na resposta, obteve: {last.content}"


@my_vcr.use_cassette("react_multiplas_ferramentas.yaml")
def test_multiplas_ferramentas(agent):
    """Agente encadeia busca web e cálculo na mesma resposta."""
    result = agent.invoke({
        "messages": [(
            "human",
            "Pesquise quantos parâmetros tem o GPT-4 e calcule 1% desse número.",
        )]
    })

    assert result["messages"], "Nenhuma mensagem retornada"
    last = result["messages"][-1]
    assert isinstance(last, AIMessage)
    assert last.content.strip(), "Conteúdo vazio"

    # Verifica que o agente chamou pelo menos uma ferramenta durante o trace
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert tool_messages, "Agente não usou nenhuma ferramenta — encadeamento não ocorreu"
