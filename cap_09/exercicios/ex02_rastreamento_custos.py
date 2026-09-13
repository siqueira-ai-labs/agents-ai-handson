"""
cap_09 — Exercício 2: Rastreamento de Custos com Langfuse
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Configure o Langfuse para rastrear o custo por token de cada chamada do agente
e gere um relatório diário de consumo.

Requisitos:
1. Configure o callback do Langfuse com model prices para o OpenRouter.
2. Registre: tokens_input, tokens_output, custo_estimado por trace.
3. Implemente get_daily_cost_report() que consulta a API do Langfuse e agrega.
4. Exiba o relatório com: total de traces, tokens totais, custo estimado em USD.

DICA: langfuse.get_observations() retorna todos os spans com usage.
"""
import os
from dotenv import load_dotenv
from langfuse import Langfuse

load_dotenv()

# Preços aproximados do OpenRouter para nvidia/llama-3.1-nemotron-70b (USD por 1k tokens)
PRICE_INPUT_PER_1K = 0.00035
PRICE_OUTPUT_PER_1K = 0.0004


def get_daily_cost_report(langfuse_client: Langfuse, date_str: str) -> dict:
    """Gera relatório de custos para uma data específica (formato: YYYY-MM-DD)."""
    # TODO: consulte langfuse_client.get_observations() e calcule custos
    raise NotImplementedError


if __name__ == "__main__":
    client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )
    # TODO: gere e exiba o relatório de hoje
    from datetime import date
    report = get_daily_cost_report(client, str(date.today()))
    print(report)
