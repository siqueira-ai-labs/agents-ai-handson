"""
cap_01 — Solução do Exercício 1: Adicionando uma Nova Ferramenta
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

load_dotenv()


@tool
def get_current_datetime() -> str:
    """Retorna a data e hora atuais no formato ISO 8601."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

search_tool = TavilySearchResults(max_results=3)
tools = [search_tool, get_current_datetime]

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente útil. Use as ferramentas disponíveis quando necessário."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


if __name__ == "__main__":
    question = "Que horas são agora e qual é a principal tendência de IA Agentiva?"
    print(f"Pergunta: {question}")
    result = agent_executor.invoke({"input": question})
    print(f"\nResposta: {result['output']}")
