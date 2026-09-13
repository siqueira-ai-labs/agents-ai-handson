"""
cap_07 — Solução Exercício 2: Processo Hierárquico com CrewAI
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

llm = LLM(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

manager_llm = LLM(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

pesquisador = Agent(
    role="Pesquisador de Mercado",
    goal="Coletar e sumarizar informações públicas sobre a empresa e o setor",
    backstory="Especialista em pesquisa de mercado com 10 anos de experiência em análise de empresas públicas.",
    llm=llm,
    verbose=False,
    allow_delegation=False,
)

analista_fundamental = Agent(
    role="Analista Fundamentalista",
    goal="Analisar indicadores fundamentalistas: P/L, P/VP, crescimento de receita, margens",
    backstory="CFA com 15 anos de experiência em análise fundamentalista de ações brasileiras.",
    llm=llm,
    verbose=False,
    allow_delegation=False,
)

analista_risco = Agent(
    role="Analista de Risco",
    goal="Identificar e quantificar riscos: regulatórios, mercado, liquidez, macroeconômicos",
    backstory="Risk Manager com experiência em gestão de portfólio e análise de risco em mercados emergentes.",
    llm=llm,
    verbose=False,
    allow_delegation=False,
)


def build_crew_sequential(ticker: str) -> Crew:
    t1 = Task(
        description=f"Pesquise informações gerais sobre {ticker}: setor, modelo de negócio, posição competitiva.",
        expected_output="Resumo de 200-300 palavras com informações da empresa.",
        agent=pesquisador,
    )
    t2 = Task(
        description=f"Com base na pesquisa, analise os fundamentos de {ticker}: valuation, crescimento e qualidade.",
        expected_output="Análise fundamentalista com recomendação COMPRAR/AGUARDAR/VENDER.",
        agent=analista_fundamental,
        context=[t1],
    )
    return Crew(
        agents=[pesquisador, analista_fundamental],
        tasks=[t1, t2],
        process=Process.sequential,
        verbose=False,
    )


def build_crew_hierarchical(ticker: str) -> Crew:
    t1 = Task(
        description=f"Pesquise informações gerais sobre {ticker}: setor, modelo de negócio, posição competitiva.",
        expected_output="Resumo de 200-300 palavras com informações da empresa.",
        agent=pesquisador,
    )
    t2 = Task(
        description=f"Analise os fundamentos de {ticker}: valuation, crescimento, margens e qualidade dos lucros.",
        expected_output="Análise fundamentalista detalhada com recomendação.",
        agent=analista_fundamental,
    )
    t3 = Task(
        description=f"Identifique e avalie os principais riscos de investir em {ticker}.",
        expected_output="Relatório de risco com classificação: Baixo/Médio/Alto e principais fatores.",
        agent=analista_risco,
    )
    return Crew(
        agents=[pesquisador, analista_fundamental, analista_risco],
        tasks=[t1, t2, t3],
        process=Process.hierarchical,
        manager_llm=manager_llm,
        verbose=False,
    )


def run_analysis(ticker: str, mode: str = "hierarchical") -> str:
    if mode == "sequential":
        crew = build_crew_sequential(ticker)
    else:
        crew = build_crew_hierarchical(ticker)
    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)


if __name__ == "__main__":
    ticker = "PETR4.SA"
    print(f"=== Análise SEQUENCIAL: {ticker} ===")
    print(run_analysis(ticker, mode="sequential"))

    print(f"\n=== Análise HIERÁRQUICA: {ticker} ===")
    print(run_analysis(ticker, mode="hierarchical"))
