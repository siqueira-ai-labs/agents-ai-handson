"""
cap_13 — Solução Exercício 2: Hibridização RAG como Fallback
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import math
import os
import pathlib
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from rag_pipeline import answer as rag_answer  # noqa: E402
from rag_pipeline import build_rag_chain  # noqa: E402

CONFIDENCE_THRESHOLD = 0.7
# ID do modelo fine-tunado (retornado por finetuning_openai.check_status() após o
# job terminar). Sem um valor real configurado, cai em um modelo base como demo.
FINETUNED_MODEL = os.getenv("FINETUNED_MODEL_ID", "gpt-4o-mini")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_model_confidence(response) -> float:
    """Extrai confiança da resposta a partir dos logprobs (média de exp(logprob)
    por token, ou seja, a probabilidade média que o modelo deu ao token escolhido)."""
    choice = response.choices[0]
    if not choice.logprobs or not choice.logprobs.content:
        return 0.0
    token_probs = [math.exp(t.logprob) for t in choice.logprobs.content]
    return sum(token_probs) / len(token_probs)


def query_finetuned(question: str, model: str = FINETUNED_MODEL):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você é um assistente financeiro especializado."},
            {"role": "user", "content": question},
        ],
        logprobs=True,
        temperature=0,
    )


def hybrid_query(question: str, threshold: float = CONFIDENCE_THRESHOLD, rag_chain=None) -> tuple[str, str]:
    """Responde com o modelo fine-tunado ou RAG fallback. Retorna (resposta, fonte)."""
    response = query_finetuned(question)
    confianca = get_model_confidence(response)

    if confianca >= threshold:
        return response.choices[0].message.content, "fine-tuned"

    rag_chain = rag_chain or build_rag_chain()
    return rag_answer(question, chain=rag_chain), "rag-fallback"


if __name__ == "__main__":
    questions = [
        "Qual é a alíquota do IR sobre dividendos no Brasil?",
        "Explique a teoria dos mercados eficientes.",
    ]
    for q in questions:
        answer, source = hybrid_query(q)
        print(f"[{source}] {q}\n→ {answer[:100]}\n")
