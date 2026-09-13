"""
cap_07 — Exercício 3: Ferramentas Customizadas e Dados em Tempo Real
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Implemente ferramentas customizadas que buscam dados financeiros em tempo real
(via yfinance e scraping de notícias) e integre ao analista CrewAI.

Requisitos:
1. Ferramenta `get_fundamentals(ticker)`: P/L, dividend yield, ROE via yfinance.
2. Ferramenta `get_recent_news(ticker)`: últimas 5 notícias via DuckDuckGo + BeautifulSoup.
3. Ferramenta `calculate_technical(ticker)`: médias móveis 20/50 dias.
4. Use @tool do CrewAI para registrar as ferramentas.
5. Gere um relatório de análise completo com os dados em tempo real.
"""
import os
from dotenv import load_dotenv
from crewai_tools import tool
import yfinance as yf

load_dotenv()


@tool("Fundamentos da Ação")
def get_fundamentals(ticker: str) -> str:
    """Retorna métricas fundamentalistas de uma ação."""
    # TODO: implemente com yf.Ticker(ticker).info
    raise NotImplementedError


@tool("Notícias Recentes")
def get_recent_news(ticker: str) -> str:
    """Busca as últimas notícias sobre o ticker."""
    # TODO: implemente com DuckDuckGo + BeautifulSoup
    raise NotImplementedError


@tool("Análise Técnica")
def calculate_technical(ticker: str) -> str:
    """Calcula médias móveis de 20 e 50 dias."""
    # TODO: implemente com yf.download e pandas rolling()
    raise NotImplementedError


# TODO: configure o Crew com as ferramentas customizadas


if __name__ == "__main__":
    ticker = "VALE3.SA"
    print(f"Análise completa em tempo real: {ticker}")
    # TODO: execute o crew
