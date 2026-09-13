"""
cap_01 — Abordagem 2: Agente de Pesquisa com CrewAI
Módulo 2: Fundamentos da IA Agentiva

Provider: OpenRouter (openrouter.ai)
"""
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# --- LLM via OpenRouter ---
# CrewAI usa LiteLLM internamente: prefixo "openrouter/" roteia para o OpenRouter
model_name = os.getenv("OPENROUTER_MODEL", "openrouter/openai/gpt-oss-120b:free")
llm = LLM(
    model=model_name,
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Wrapper para tornar DuckDuckGoSearchRun compatível com CrewAI
class DuckDuckGoTool(BaseTool):
    name: str = "DuckDuckGo Search"
    description: str = "Searches the web using DuckDuckGo. Input should be a search query string."

    def _run(self, query: str) -> str:
        return DuckDuckGoSearchRun().run(query)

search_tool = DuckDuckGoTool()

# --- Agentes ---
researcher = Agent(
    role="Pesquisador Sênior de IA",
    goal="Descobrir as tendências e o futuro da IA Agentiva",
    backstory="Especialista em IA com foco em sistemas autônomos.",
    tools=[search_tool],
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Redator Técnico",
    goal="Transformar pesquisas em relatórios claros e objetivos",
    backstory="Escritor especializado em tecnologia com habilidade de síntese.",
    llm=llm,
    verbose=True,
)

# --- Tarefas ---
task1 = Task(
    description="Pesquise as principais tendências de IA Agentiva em 2025.",
    expected_output="Lista de tendências com fontes e descrições.",
    agent=researcher,
)

task2 = Task(
    description="Com base na pesquisa, escreva um relatório executivo de 300 palavras.",
    expected_output="Relatório estruturado em markdown.",
    agent=writer,
    context=[task1],
)

# --- Crew ---
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n### Relatório Final (CrewAI) ###")
    print(result)
