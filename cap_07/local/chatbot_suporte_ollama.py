"""
cap_07 — Alternativa 100% Local: Chatbot de Suporte via Ollama
Mesma arquitetura de projeto/chatbot_suporte_langgraph.py, trocando o LLM
de OpenRouter por Ollama local.

Modelo: qwen3.5:7b
"""
from typing import Annotated

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)

SYSTEM_PROMPT = (
    "Você é um chatbot de suporte ao cliente. Use search_knowledge_base para buscar "
    "respostas na base de conhecimento. Se a base não encontrar uma solução, use "
    "escalate_to_human para escalar o atendimento a um supervisor. Responda de forma "
    "direta e cordial."
)


@tool
def search_knowledge_base(query: str) -> str:
    """Busca na base de conhecimento por uma solução para a dúvida do cliente."""
    q = query.lower()
    if "senha" in q:
        return "Para resetar a senha, acesse 'Esqueci minha senha' e siga as instruções enviadas por e-mail."
    if "pagamento" in q:
        return "Problemas de pagamento geralmente são resolvidos verificando o cartão de crédito ou tentando um método alternativo."
    return "Não foi encontrada uma solução na base de conhecimento. Considere escalar para um supervisor."


@tool
def escalate_to_human(reason: str) -> str:
    """Escala o chat para um supervisor humano quando o problema é muito complexo."""
    return f"O chat foi transferido para um supervisor humano. Motivo: {reason}"


tools = [search_knowledge_base, escalate_to_human]
llm_with_tools = llm.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    return {"messages": [llm_with_tools.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])]}


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())


def run_chat(query: str, thread_id: str = "cap07-suporte-local") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    state = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    print(run_chat("Esqueci minha senha, como faço para resetar?"))
