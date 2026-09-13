"""
cap_05 — Exercício 3: Roteador com Avaliação de Relevância
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Substitua o roteador padrão por um fluxo customizado onde um LLM menor avalia
se a query do usuário tem aderência semântica com a descrição de cada ferramenta
antes de invocar a mais cara.

Requisitos:
1. Use um modelo leve (ex: llama4.1:8b via Ollama) como juiz de relevância.
2. O juiz retorna {"tool": "nome_da_ferramenta", "confidence": 0.0-1.0}.
3. Só invoca a ferramenta se confidence >= 0.7; caso contrário, usa fallback.
4. Registre as decisões de roteamento para análise posterior.
5. Compare o custo (tokens) com e sem o roteador de relevância.

DICA: structured output com Pydantic garante JSON consistente do juiz.
"""
import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

CONFIDENCE_THRESHOLD = 0.7


class RoutingDecision(BaseModel):
    tool: str = Field(description="Nome da ferramenta mais adequada")
    confidence: float = Field(description="Confiança de 0.0 a 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="Justificativa em uma linha")


# TODO: implemente o roteador com LLM juiz e o grafo de decisão


if __name__ == "__main__":
    queries = [
        "Qual foi o faturamento do Q3?",
        "Quais são as tendências de mercado para 2026?",
        "Quantos produtos foram devolvidos em março?",
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        # TODO: execute o roteador e mostre a decisão + resultado
