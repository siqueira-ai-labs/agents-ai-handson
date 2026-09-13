"""
cap_09 — Solução Exercício 2: Rastreamento de Custos com Langfuse
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import os
from datetime import datetime, timedelta
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

load_dotenv()

llm_triagem = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL_TRIAGEM", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)
llm_final = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def triagem_node(state: State) -> dict:
    resposta = llm_triagem.invoke(
        [SystemMessage(content="Classifique a pergunta do usuário em 1-3 palavras (categoria).")]
        + state["messages"]
    )
    return {"messages": [resposta]}


def final_node(state: State) -> dict:
    resposta = llm_final.invoke(
        [SystemMessage(content="Responda a pergunta original do usuário de forma completa.")]
        + [m for m in state["messages"] if isinstance(m, HumanMessage)]
    )
    return {"messages": [resposta]}


graph = StateGraph(State)
graph.add_node("triagem", triagem_node)
graph.add_node("final", final_node)
graph.set_entry_point("triagem")
graph.add_edge("triagem", "final")
graph.add_edge("final", END)
app = graph.compile()


def run_two_step(query: str, langfuse_handler: CallbackHandler) -> str:
    """Executa triagem + resposta final em uma única invocação, garantindo que
    ambas as chamadas fiquem aninhadas na mesma trace do Langfuse."""
    result = app.invoke(
        {"messages": [HumanMessage(content=query)]},
        config={"callbacks": [langfuse_handler]},
    )
    return result["messages"][-1].content


def get_daily_cost_report(langfuse_client: Langfuse, date_str: str) -> dict:
    """Gera relatório de custos para uma data específica (formato: YYYY-MM-DD)."""
    day_start = datetime.strptime(date_str, "%Y-%m-%d")
    day_end = day_start + timedelta(days=1)
    observations = langfuse_client.get_observations(
        from_start_time=day_start, to_start_time=day_end
    ).data

    total_tokens = sum(o.usage.total or 0 for o in observations if o.usage)
    total_cost = sum(o.calculated_total_cost or 0 for o in observations if o.calculated_total_cost)
    trace_ids = {o.trace_id for o in observations if o.trace_id}

    return {
        "date": date_str,
        "total_traces": len(trace_ids),
        "total_observations": len(observations),
        "total_tokens": total_tokens,
        "total_cost_usd": round(total_cost, 6),
    }


if __name__ == "__main__":
    client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )
    handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )

    print(run_two_step("Qual o cenário macroeconômico atual para o setor de tecnologia?", handler))
    handler.flush()

    from datetime import date

    report = get_daily_cost_report(client, str(date.today()))
    print(report)
