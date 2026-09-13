"""
cap_09 — Solução Exercício 1: Adicionando Tags no LangSmith
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import os
import pathlib
import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from agent import app  # noqa: E402

# O LangSmith lê o projeto da variável de ambiente LANGCHAIN_PROJECT — não há
# um parâmetro de "project name" no RunnableConfig por invocação.
os.environ.setdefault("LANGCHAIN_PROJECT", "agents-ai-handson-cap09")

config = RunnableConfig(
    tags=["cap_09", "finance-agent", "production"],
    metadata={"user_id": "test-user", "session_id": "abc123"},
    run_name="finance-agent-cap09",
)


def run_with_tags(query: str) -> str:
    state = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    print("Verificar traces em app.langsmith.com → project: agents-ai-handson-cap09")
    print(run_with_tags("Qual o preço atual da ação da Apple (AAPL)?"))
