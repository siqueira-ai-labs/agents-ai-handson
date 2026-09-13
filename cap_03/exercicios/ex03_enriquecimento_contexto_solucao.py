"""
cap_03 — Solução Exercício 3: Enriquecimento de Contexto com RunnableLambda
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import json
import os
import pathlib
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

KNOWLEDGE_BASE_PATH = pathlib.Path(__file__).parent.parent / "knowledge_base.json"

with open(KNOWLEDGE_BASE_PATH, encoding="utf-8") as f:
    _KNOWLEDGE_BASE: list[dict] = json.load(f)

_TAREFAS = [ex["tarefa"] for ex in _KNOWLEDGE_BASE]


def enrich_context(task: str) -> dict:
    """Busca os 2 exemplos mais relevantes via TF-IDF e retorna task + exemplos."""
    corpus = _TAREFAS + [task]
    vectorizer = TfidfVectorizer().fit(corpus)
    vecs = vectorizer.transform(corpus)
    scores = cosine_similarity(vecs[-1], vecs[:-1]).flatten()
    top_indices = scores.argsort()[-2:][::-1]
    examples_text = ""
    for i, idx in enumerate(top_indices, 1):
        ex = _KNOWLEDGE_BASE[idx]
        examples_text += f"\nExemplo {i} — {ex['tarefa']}:\n```python\n{ex['codigo']}\n```"
    return {"task": task, "examples": examples_text}


prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Você é um engenheiro Python sênior. "
     "Use os exemplos similares abaixo como referência de estilo e qualidade.\n{examples}"),
    ("human", "Escreva uma função Python que: {task}"),
])

pipeline = RunnableLambda(enrich_context) | prompt | llm | StrOutputParser()

pipeline_sem_enriquecimento = (
    ChatPromptTemplate.from_messages([
        ("system", "Você é um engenheiro Python sênior."),
        ("human", "Escreva uma função Python que: {task}"),
    ])
    | llm
    | StrOutputParser()
)


if __name__ == "__main__":
    task = "implemente um decorator que mede o tempo de execução de uma função"

    print("=== SEM enriquecimento ===")
    print(pipeline_sem_enriquecimento.invoke({"task": task}))

    print("\n=== COM enriquecimento ===")
    print(pipeline.invoke(task))
