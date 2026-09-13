"""
cap_07 — Analista de Ações com CrewAI
Módulo 8: Sistemas Multiagente com LangGraph e CrewAI

Tripulação sequencial: Pesquisador -> Analista Financeiro -> Conselheiro de
Investimentos, produzindo uma recomendação final (COMPRAR/VENDER/MANTER).
"""
import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv()

llm = LLM(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


@tool("Busca na Web")
def search_web(query: str) -> str:
    """Busca notícias e informações recentes na web via DuckDuckGo."""
    try:
        resultados = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"Busca indisponível no momento ({e}). Baseie-se no seu conhecimento geral."
    if not resultados:
        return f"Nenhum resultado encontrado para '{query}'."
    return "\n".join(f"- {r['title']}: {r['body']}" for r in resultados)


pesquisador = Agent(
    role="Analista de Pesquisa de Mercado",
    goal="Coletar e resumir as últimas notícias e tendências de mercado para a ação {stock}",
    backstory=(
        "Você é um experiente analista de pesquisa de mercado, especializado em encontrar "
        "as informações mais relevantes e recentes que podem impactar o preço de uma ação."
    ),
    tools=[search_web],
    llm=llm,
    verbose=False,
    allow_delegation=False,
)

analista_financeiro = Agent(
    role="Analista Financeiro",
    goal="Analisar os dados financeiros da empresa {stock} e avaliar sua saúde financeira",
    backstory=(
        "Você é um analista financeiro sênior com um olhar apurado para números. Você examina "
        "balanços e demonstrações de resultado para avaliar o valor intrínseco e a estabilidade "
        "financeira de uma empresa."
    ),
    llm=llm,
    verbose=False,
    allow_delegation=False,
)

conselheiro = Agent(
    role="Conselheiro de Investimentos",
    goal="Sintetizar a pesquisa de mercado e a análise financeira em uma recomendação para {stock}",
    backstory=(
        "Você é um conselheiro de investimentos experiente que combina análises quantitativas "
        "e qualitativas para tomar decisões informadas. Sua recomendação final é sempre "
        "COMPRAR, VENDER ou MANTER."
    ),
    llm=llm,
    verbose=False,
    allow_delegation=False,
)


def build_crew(stock: str) -> Crew:
    pesquisa_task = Task(
        description=(
            f"Colete informações sobre as últimas notícias, sentimento do mercado e eventos "
            f"significativos relacionados à ação {stock}. Concentre-se em notícias recentes."
        ),
        expected_output="Um resumo conciso de 3 parágrafos das notícias e tendências mais importantes.",
        agent=pesquisador,
    )
    analise_task = Task(
        description=(
            f"Com base na pesquisa, analise os fundamentos de {stock}: receita, lucro, P/L "
            f"e outras métricas-chave. Simule a análise se dados exatos não estiverem disponíveis."
        ),
        expected_output="Uma análise da saúde financeira da empresa, destacando pontos fortes e fracos.",
        agent=analista_financeiro,
        context=[pesquisa_task],
    )
    recomendacao_task = Task(
        description=(
            f"Use os insights da pesquisa de mercado e da análise financeira para formular uma "
            f"recomendação de investimento para {stock}. A recomendação final DEVE ser uma única "
            f"palavra: COMPRAR, VENDER ou MANTER, seguida de uma tese de investimento de 3-5 "
            f"parágrafos justificando a escolha."
        ),
        expected_output="A recomendação final (COMPRAR, VENDER ou MANTER) e uma tese de investimento bem fundamentada.",
        agent=conselheiro,
        context=[pesquisa_task, analise_task],
    )
    return Crew(
        agents=[pesquisador, analista_financeiro, conselheiro],
        tasks=[pesquisa_task, analise_task, recomendacao_task],
        process=Process.sequential,
        verbose=False,
    )


def run_analysis(stock: str) -> str:
    crew = build_crew(stock)
    result = crew.kickoff(inputs={"stock": stock})
    return result.raw if hasattr(result, "raw") else str(result)


if __name__ == "__main__":
    ticker = os.getenv("STOCK_TICKER", "TSLA")
    print(f"--- Analisando a ação: {ticker} ---")
    print(run_analysis(ticker))
