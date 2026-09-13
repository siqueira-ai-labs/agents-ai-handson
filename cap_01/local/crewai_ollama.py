"""
cap_01 — Alternativa 100% Local: CrewAI + Ollama (sem API)
Modelo: qwen3.5:7b (melhor function calling para CrewAI)
"""
from crewai import Agent, Task, Crew, Process, LLM
from langchain_community.tools import DuckDuckGoSearchRun

ollama_llm = LLM(model="ollama/qwen3.5:7b", base_url="http://localhost:11434")
search_tool = DuckDuckGoSearchRun()

researcher = Agent(
    role="Pesquisador Sênior de IA",
    goal="Descobrir tendências de IA Agentiva",
    backstory="Especialista em sistemas autônomos.",
    tools=[search_tool],
    llm=ollama_llm,
    verbose=True,
)

writer = Agent(
    role="Redator Técnico",
    goal="Sintetizar pesquisas em relatórios objetivos",
    backstory="Escritor técnico especializado em IA.",
    llm=ollama_llm,
    verbose=True,
)

task1 = Task(
    description="Pesquise as principais tendências de IA Agentiva em 2025.",
    expected_output="Lista de tendências com descrições.",
    agent=researcher,
)

task2 = Task(
    description="Com base na pesquisa, escreva um relatório executivo de 200 palavras.",
    expected_output="Relatório em markdown.",
    agent=writer,
    context=[task1],
)

crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n### Relatório Final (CrewAI Local) ###")
    print(result)
