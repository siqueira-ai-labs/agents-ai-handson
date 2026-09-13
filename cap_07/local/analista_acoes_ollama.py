"""
cap_07 — Alternativa 100% Local: Analista de Ações via Ollama
Mesma arquitetura de projeto/analista_acoes_crewai.py (tripulação
sequencial: Pesquisador -> Analista Financeiro -> Conselheiro de
Investimentos), trocando o LLM de OpenRouter por Ollama local via LiteLLM
(prefixo "ollama/").

Modelo: qwen3.5:7b
"""
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from duckduckgo_search import DDGS

llm = LLM(model="ollama/qwen3.5:7b", base_url="http://localhost:11434")


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
        description=f"Colete informações sobre as últimas notícias e tendências relacionadas à ação {stock}.",
        expected_output="Um resumo conciso de 3 parágrafos das notícias e tendências mais importantes.",
        agent=pesquisador,
    )
    analise_task = Task(
        description=f"Com base na pesquisa, analise os fundamentos de {stock}: receita, lucro, P/L.",
        expected_output="Uma análise da saúde financeira da empresa, destacando pontos fortes e fracos.",
        agent=analista_financeiro,
        context=[pesquisa_task],
    )
    recomendacao_task = Task(
        description=(
            f"Formule uma recomendação de investimento para {stock}. A recomendação final DEVE "
            f"ser uma única palavra: COMPRAR, VENDER ou MANTER, seguida de uma tese de investimento."
        ),
        expected_output="A recomendação final e uma tese de investimento bem fundamentada.",
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
    print(run_analysis("TSLA"))
