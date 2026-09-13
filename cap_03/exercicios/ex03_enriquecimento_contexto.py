"""
cap_03 — Exercício 3: Enriquecimento de Contexto com RunnableLambda
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Construa um pipeline LCEL que enriquece o contexto da tarefa antes de enviá-la
ao LLM. O enriquecimento busca exemplos similares em uma base de conhecimento
local (arquivo JSON) e os injeta no prompt como few-shot examples.

Requisitos:
1. Crie uma base de conhecimento em JSON com pelo menos 5 exemplos (tarefa → código).
2. Implemente uma função `enrich_context` que usa busca por similaridade textual
   simples (TF-IDF com sklearn ou correspondência de palavras-chave) para encontrar
   os 2 exemplos mais relevantes.
3. Use RunnableLambda para injetar os exemplos no prompt como few-shot.
4. Compare a qualidade do código com e sem o enriquecimento.

NOTA: Para similaridade semântica real, use sentence-transformers (opcional).
"""
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

load_dotenv()

llm = ChatOpenAI(
    model="nvidia/llama-3.1-nemotron-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

# TODO: crie o arquivo knowledge_base.json com exemplos no formato:
# [{"tarefa": "...", "codigo": "..."}]
KNOWLEDGE_BASE_PATH = "cap_03/knowledge_base.json"


def enrich_context(task: str) -> dict:
    """Busca os 2 exemplos mais relevantes da base e retorna task + exemplos."""
    # TODO: implemente busca por similaridade textual
    return {"task": task, "examples": ""}


prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um engenheiro Python. Exemplos similares:\n{examples}"),
    ("human", "Escreva código Python que: {task}"),
])

pipeline = (
    RunnableLambda(enrich_context)
    | prompt
    | llm
    | StrOutputParser()
)

if __name__ == "__main__":
    task = "implemente um decorator que mede o tempo de execução de uma função"
    print("Com enriquecimento:")
    print(pipeline.invoke(task))
