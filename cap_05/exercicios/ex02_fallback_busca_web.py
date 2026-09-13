"""
cap_05 — Exercício 2: Fallback Explícito para Busca Web
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Quando a base vetorial não retornar resultados relevantes (score abaixo do
limiar), o agente deve fazer fallback automático para busca web via Tavily.

Requisitos:
1. Defina um limiar de relevância (ex: score < 0.5).
2. Implemente um nó de avaliação que verifica o score dos documentos recuperados.
3. Se insuficiente, roteie para o nó de busca web.
4. Integre o resultado da busca web de volta ao contexto do agente.
"""
import os
from dotenv import load_dotenv

load_dotenv()

RELEVANCE_THRESHOLD = 0.5


def evaluate_retrieval(docs_with_scores: list) -> bool:
    """Retorna True se os documentos são suficientemente relevantes."""
    if not docs_with_scores:
        return False
    best_score = max(score for _, score in docs_with_scores)
    return best_score >= RELEVANCE_THRESHOLD


# TODO: implemente o grafo com roteamento vetorial → (aprovado | fallback web)


if __name__ == "__main__":
    query = "Qual é a perspectiva do mercado de EV no Brasil para 2026?"
    print(f"Query: {query}")
    # TODO: invoque o agente
