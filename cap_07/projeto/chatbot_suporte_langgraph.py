"""
cap_07 — Chatbot de Suporte ao Cliente com LangGraph
Módulo 8: Sistemas Multiagente com LangGraph e CrewAI

Fluxo cíclico (agente -> ferramenta -> agente) com escalonamento para humano
quando a base de conhecimento não tem a resposta.
"""
import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

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
    response = llm_with_tools.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
    return {"messages": [response]}


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())


def run_chat(query: str, thread_id: str = "cap07-suporte") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    state = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    print("Chatbot de Suporte — digite 'sair' para encerrar\n")
    config = {"configurable": {"thread_id": "suporte-cli"}}
    while True:
        user_input = input("Você: ").strip()
        if user_input.lower() == "sair":
            break
        state = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
        print(f"Bot: {state['messages'][-1].content}")
