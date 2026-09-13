"""
cap_07 — Solução Exercício 1: Adicionando um Novo Agente (FAQ) ao LangGraph
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import os
from typing import Annotated, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

load_dotenv()

FAQ_DB = {
    "horário": "Nosso atendimento funciona de segunda a sexta, das 8h às 18h.",
    "prazo": "O prazo de entrega padrão é de 5 a 7 dias úteis.",
    "cancelamento": "Para cancelar um pedido, acesse Minha Conta > Pedidos > Cancelar.",
    "devolução": "Aceitamos devoluções em até 30 dias após a entrega. Acesse Minha Conta > Pedidos > Devolver.",
    "pagamento": "Aceitamos cartão de crédito, débito, PIX e boleto bancário.",
    "rastreamento": "Acesse Minha Conta > Pedidos > Rastrear para ver a localização do seu pacote.",
    "troca": "Para solicitar uma troca, acesse Minha Conta > Pedidos > Solicitar Troca.",
}

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def faq_lookup(query: str) -> str | None:
    """Busca resposta por palavras-chave no FAQ_DB. Retorna None se não encontrar."""
    q_lower = query.lower()
    for keyword, answer in FAQ_DB.items():
        if keyword in q_lower:
            return answer
    return None


def router_node(state: State) -> Literal["faq_agent", "llm_agent"]:
    last_msg = state["messages"][-1]
    query = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    return "faq_agent" if faq_lookup(query) else "llm_agent"


def faq_agent_node(state: State) -> dict:
    last_msg = state["messages"][-1]
    query = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    answer = faq_lookup(query) or "Não encontrei esta informação no FAQ."
    return {"messages": [AIMessage(content=f"[FAQ] {answer}")]}


def llm_agent_node(state: State) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


graph = StateGraph(State)
graph.add_node("router", lambda s: s)  # pass-through para trigger do conditional
graph.add_node("faq_agent", faq_agent_node)
graph.add_node("llm_agent", llm_agent_node)
graph.set_entry_point("router")
graph.add_conditional_edges("router", router_node, {
    "faq_agent": "faq_agent",
    "llm_agent": "llm_agent",
})
graph.add_edge("faq_agent", END)
graph.add_edge("llm_agent", END)

app = graph.compile(checkpointer=MemorySaver())


def run_chatbot(query: str, thread_id: str = "cap07-ex01") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    state = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    test_queries = [
        "Qual é o horário de atendimento?",
        "Como faço para cancelar meu pedido?",
        "Quais são as formas de pagamento aceitas?",
        "Preciso de ajuda com um problema técnico no meu produto.",
    ]
    for q in test_queries:
        print(f"\nUsuário: {q}")
        print(f"Bot: {run_chatbot(q, thread_id=f'cap07-{hash(q)}')}")
