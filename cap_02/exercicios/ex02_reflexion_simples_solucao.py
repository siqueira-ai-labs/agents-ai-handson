"""
cap_02 — Solução Exercício 2: Implementando Reflexion Simples
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import json
import os
import re
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

MAX_ITERATIONS = 3


# Schema da avaliação estruturada (documentação + validação no reflection_node)
class ReflectionOutput(BaseModel):
    approved: bool = Field(description="True se a resposta é satisfatória")
    feedback: str = Field(description="Crítica construtiva para melhorar a resposta")


class State(TypedDict):
    messages: Annotated[list, add_messages]
    iteration: int
    approved: bool


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

tools = [TavilySearchResults(max_results=3)]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools)


def reflection_node(state: State) -> dict:
    """Avalia a última resposta do agente e decide se aprova ou pede revisão."""
    last_response = state["messages"][-1].content or ""
    iteration = state.get("iteration", 0)

    prompt = (
        "Avalie a resposta abaixo quanto a completude, precisão e clareza.\n"
        "Retorne APENAS um JSON válido (sem markdown) com:\n"
        '  {"approved": true|false, "feedback": "sua crítica"}\n\n'
        f"Resposta:\n{last_response}"
    )
    raw = llm.invoke(prompt)

    try:
        text = raw.content.strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(match.group()) if match else {}
        result = ReflectionOutput(
            approved=bool(data.get("approved", False)),
            feedback=str(data.get("feedback", "Melhore a resposta.")),
        )
    except Exception:
        result = ReflectionOutput(approved=False, feedback="Erro na avaliação — tente novamente.")

    new_messages = []
    if not result.approved:
        new_messages.append(
            HumanMessage(content=f"[Avaliador — iteração {iteration + 1}]: {result.feedback}")
        )

    return {
        "messages": new_messages,
        "iteration": iteration + 1,
        "approved": result.approved,
    }


def should_reflect(state: State) -> Literal["tools", "reflection"]:
    """Depois do agente: vai para tools se houver tool_calls, senão reflete."""
    last_msg = state["messages"][-1]
    if getattr(last_msg, "tool_calls", None):
        return "tools"
    return "reflection"


def should_continue(state: State) -> Literal["agent", "__end__"]:
    """Depois da reflexão: repete se não aprovado e dentro do limite."""
    if state["approved"] or state.get("iteration", 0) >= MAX_ITERATIONS:
        return END
    return "agent"


def build_reflection_graph():
    graph = StateGraph(State)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.add_node("reflection", reflection_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_reflect, {"tools": "tools", "reflection": "reflection"})
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges("reflection", should_continue, {"agent": "agent", "__end__": END})
    return graph.compile()


if __name__ == "__main__":
    app = build_reflection_graph()
    print(f"Agente com Reflexion — máximo {MAX_ITERATIONS} iterações")
    result = app.invoke({
        "messages": [("human", "Explique o padrão ReAct em sistemas de IA agentiva.")],
        "iteration": 0,
        "approved": False,
    })
    print("\n### Resposta Final ###")
    print(result["messages"][-1].content)
    print(f"Iterações realizadas: {result['iteration']}")
