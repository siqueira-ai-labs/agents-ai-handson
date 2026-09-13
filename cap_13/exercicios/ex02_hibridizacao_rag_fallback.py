"""
cap_13 — Exercício 2: Hibridização RAG como Fallback
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Construa um sistema híbrido onde o modelo fine-tunado responde perguntas
de domínio e, quando incerto, usa RAG para buscar contexto adicional.

Requisitos:
1. Use a perplexidade ou logprobs para medir a confiança do modelo fine-tunado.
2. Se confiança < limiar (ex: 0.7), ative o pipeline RAG como fallback.
3. Registre qual sistema respondeu cada query.
4. Compare precisão: fine-tuned solo vs fine-tuned + RAG fallback no golden dataset.
"""
import os
from dotenv import load_dotenv

load_dotenv()

CONFIDENCE_THRESHOLD = 0.7


def get_model_confidence(response: dict) -> float:
    """Extrai confiança da resposta usando logprobs."""
    # TODO: implemente usando logprobs da API OpenAI
    # logprobs=True no request retorna probabilidades por token
    raise NotImplementedError


def hybrid_query(question: str) -> tuple[str, str]:
    """Responde com o modelo fine-tunado ou RAG fallback. Retorna (resposta, fonte)."""
    # TODO: tente o modelo fine-tunado primeiro
    # TODO: se confiança < CONFIDENCE_THRESHOLD, use RAG
    raise NotImplementedError


if __name__ == "__main__":
    questions = [
        "Qual é a alíquota do IR sobre dividendos no Brasil?",
        "Explique a teoria dos mercados eficientes.",
    ]
    for q in questions:
        try:
            answer, source = hybrid_query(q)
            print(f"[{source}] {q}\n→ {answer[:100]}\n")
        except NotImplementedError:
            print(f"TODO: implementar hybrid_query() | {q}")
