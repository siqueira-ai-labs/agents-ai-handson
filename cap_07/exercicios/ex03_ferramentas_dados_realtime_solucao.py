"""
cap_07 — Solução Exercício 3: Ferramentas Customizadas e Dados em Tempo Real
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
import yfinance as yf
import pandas as pd

load_dotenv()

llm = LLM(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


@tool("Fundamentos da Ação")
def get_fundamentals(ticker: str) -> str:
    """Retorna métricas fundamentalistas de uma ação: P/L, dividend yield, ROE, market cap."""
    try:
        info = yf.Ticker(ticker).info
        return (
            f"=== Fundamentos: {ticker} ===\n"
            f"Nome: {info.get('longName', 'N/A')}\n"
            f"Setor: {info.get('sector', 'N/A')}\n"
            f"P/L (trailing): {info.get('trailingPE', 'N/A')}\n"
            f"P/VP: {info.get('priceToBook', 'N/A')}\n"
            f"Dividend Yield: {info.get('dividendYield', 'N/A')}\n"
            f"ROE: {info.get('returnOnEquity', 'N/A')}\n"
            f"Market Cap: {info.get('marketCap', 'N/A')}\n"
            f"Preço atual: {info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}\n"
            f"52w Alta: {info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"52w Baixa: {info.get('fiftyTwoWeekLow', 'N/A')}"
        )
    except Exception as e:
        return f"Erro ao buscar fundamentos de {ticker}: {e}. Use análise qualitativa."


@tool("Notícias Recentes")
def get_recent_news(ticker: str) -> str:
    """Busca as últimas notícias sobre o ticker via yfinance."""
    try:
        t = yf.Ticker(ticker)
        news = t.news
        if not news:
            return f"Nenhuma notícia recente encontrada para {ticker}."
        lines = [f"=== Notícias recentes: {ticker} ==="]
        for item in news[:5]:
            title = item.get("title", item.get("content", {}).get("title", "N/A"))
            lines.append(f"• {title}")
        return "\n".join(lines)
    except Exception as e:
        return f"Erro ao buscar notícias de {ticker}: {e}. Considere o contexto macroeconômico geral."


@tool("Análise Técnica")
def calculate_technical(ticker: str) -> str:
    """Calcula médias móveis de 20 e 50 dias e variação recente de preço."""
    try:
        hist = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if hist.empty:
            return f"Sem dados históricos para {ticker}."
        close = hist["Close"]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]
        last_price = close.iloc[-1]
        variation_5d = ((last_price - close.iloc[-6]) / close.iloc[-6] * 100).item()
        signal = "ALTA" if ma20 > ma50 else "BAIXA"
        return (
            f"=== Análise Técnica: {ticker} ===\n"
            f"Preço atual: R${last_price:.2f}\n"
            f"MM20: R${ma20:.2f}\n"
            f"MM50: R${ma50:.2f}\n"
            f"Tendência (MM20 vs MM50): {signal}\n"
            f"Variação 5 dias: {variation_5d:.2f}%"
        )
    except Exception as e:
        return f"Erro ao calcular análise técnica de {ticker}: {e}."


analista = Agent(
    role="Analista de Investimentos",
    goal="Gerar relatório completo de análise de ações com dados fundamentalistas, técnicos e notícias recentes",
    backstory=(
        "Analista CFA com 20 anos de experiência em mercados emergentes. "
        "Especialista em combinar análise técnica, fundamentalista e análise de sentimento."
    ),
    tools=[get_fundamentals, get_recent_news, calculate_technical],
    llm=llm,
    verbose=False,
)


def run_full_analysis(ticker: str) -> str:
    task = Task(
        description=(
            f"Realize uma análise completa de {ticker} usando TODAS as ferramentas disponíveis:\n"
            f"1. Busque os fundamentos com get_fundamentals\n"
            f"2. Verifique as notícias recentes com get_recent_news\n"
            f"3. Calcule a análise técnica com calculate_technical\n"
            f"Gere um relatório estruturado com: resumo executivo, pontos positivos, riscos e recomendação."
        ),
        expected_output="Relatório completo de análise com fundamentais, análise técnica, notícias e recomendação COMPRAR/AGUARDAR/VENDER.",
        agent=analista,
    )
    crew = Crew(agents=[analista], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)


if __name__ == "__main__":
    ticker = "VALE3.SA"
    print(f"Análise completa em tempo real: {ticker}\n")
    print(run_full_analysis(ticker))
