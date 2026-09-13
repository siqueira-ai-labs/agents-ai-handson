"""
Testes unitários — Ex02: Mecanismo de Memória com Sumarização
"""
import os
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# ── Importação com LLM mockado ─────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ex02():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Resumo gerado pelo LLM.")
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import importlib, sys
            exercicios_path = str(
                __file__.replace("/testes/test_ex02_mecanismo_memoria.py", "/exercicios")
            )
            if exercicios_path not in sys.path:
                sys.path.insert(0, exercicios_path)
            import ex02_mecanismo_memoria_solucao as mod
            mod.llm = mock_llm          # substitui o LLM real pelo mock
            yield mod


@pytest.fixture
def historia(ex02):
    """Instância limpa de SummarizingMessageHistory para cada teste."""
    h = ex02.SummarizingMessageHistory()
    return h


# ── Testes: _intro (contexto fixo) ────────────────────────────────────────────

def test_primeiras_mensagens_vao_para_intro(historia, ex02):
    historia.add_messages([HumanMessage(content="Olá"), AIMessage(content="Oi!")])
    assert len(historia._intro) == ex02.FIXED_INTRO
    assert len(historia._messages) == 0


def test_mensagens_alem_do_intro_vao_para_messages(historia, ex02):
    historia.add_messages([HumanMessage(content="A"), AIMessage(content="B")])  # intro
    historia.add_messages([HumanMessage(content="C"), AIMessage(content="D")])  # _messages
    assert len(historia._intro) == ex02.FIXED_INTRO
    assert len(historia._messages) == 2


def test_property_messages_combina_intro_e_messages(historia):
    historia.add_messages([HumanMessage(content="X"), AIMessage(content="Y")])
    historia.add_messages([HumanMessage(content="Z"), AIMessage(content="W")])
    total = len(historia.messages)
    assert total == len(historia._intro) + len(historia._messages)


def test_clear_reseta_ambos_os_buffers(historia):
    historia.add_messages([HumanMessage(content="A"), AIMessage(content="B")])
    historia.add_messages([HumanMessage(content="C"), AIMessage(content="D")])
    historia.clear()
    assert historia._intro == []
    assert historia._messages == []
    assert historia.messages == []


# ── Testes: sumarização ────────────────────────────────────────────────────────

def _preenche_ate_limite(historia, ex02, extra=0):
    """Preenche _intro e _messages até MAX_MESSAGES + extra."""
    historia.add_messages([HumanMessage(content="Intro H"), AIMessage(content="Intro A")])
    for i in range(ex02.MAX_MESSAGES // 2 + extra):
        historia.add_messages([
            HumanMessage(content=f"Pergunta {i}"),
            AIMessage(content=f"Resposta {i}"),
        ])


def test_sem_sumarizacao_abaixo_do_limite(historia, ex02):
    historia.add_messages([HumanMessage(content="Intro H"), AIMessage(content="Intro A")])
    for _ in range(ex02.MAX_MESSAGES // 2):
        historia.add_messages([HumanMessage(content="P"), AIMessage(content="R")])
    assert not any(isinstance(m, SystemMessage) for m in historia._messages)


def test_sumarizacao_acionada_acima_do_limite(historia, ex02):
    _preenche_ate_limite(historia, ex02, extra=1)
    assert any(isinstance(m, SystemMessage) for m in historia._messages)


def test_apos_sumarizacao_messages_nao_excede_limite(historia, ex02):
    _preenche_ate_limite(historia, ex02, extra=3)
    # _messages pode ter no máximo MAX_MESSAGES + 1 (o próprio resumo)
    assert len(historia._messages) <= ex02.MAX_MESSAGES + 1


def test_llm_chamado_durante_sumarizacao(historia, ex02):
    ex02.llm.invoke.reset_mock()
    _preenche_ate_limite(historia, ex02, extra=1)
    assert ex02.llm.invoke.called


def test_resumo_armazenado_como_system_message(historia, ex02):
    _preenche_ate_limite(historia, ex02, extra=1)
    system_msgs = [m for m in historia._messages if isinstance(m, SystemMessage)]
    assert len(system_msgs) == 1
    assert system_msgs[0].content.startswith("[Resumo do histórico anterior]")


def test_intro_nunca_sumarizado(historia, ex02):
    _preenche_ate_limite(historia, ex02, extra=5)
    assert historia._intro[0].content == "Intro H"
    assert historia._intro[1].content == "Intro A"


# ── Testes: inject_summary ─────────────────────────────────────────────────────

def test_inject_summary_sem_resumo(ex02):
    resultado = ex02.inject_summary({
        "input": "Olá",
        "history": [HumanMessage(content="A"), AIMessage(content="B")],
    })
    assert resultado["summary"] == ""
    assert len(resultado["history"]) == 2


def test_inject_summary_extrai_system_message(ex02):
    sys_msg = SystemMessage(content="[Resumo do histórico anterior]\nCarlos analista.")
    resultado = ex02.inject_summary({
        "input": "Pergunta",
        "history": [sys_msg, HumanMessage(content="X"), AIMessage(content="Y")],
    })
    assert "Resumo do histórico anterior" in resultado["summary"]
    assert len(resultado["history"]) == 2  # SysMsg removida


def test_inject_summary_history_limpo(ex02):
    sys_msg = SystemMessage(content="[Resumo do histórico anterior]\nDados.")
    resultado = ex02.inject_summary({
        "input": "?",
        "history": [sys_msg, HumanMessage(content="H"), AIMessage(content="A")],
    })
    tipos = [type(m).__name__ for m in resultado["history"]]
    assert "SystemMessage" not in tipos


def test_inject_summary_preserva_input(ex02):
    resultado = ex02.inject_summary({"input": "minha pergunta", "history": []})
    assert resultado["input"] == "minha pergunta"
