"""
cap_03 — Solução Exercício 1: Adicionando um Filtro de Idioma
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

generation_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um engenheiro Python sênior. Gere apenas código Python, sem markdown."),
    ("human",
     "Escreva uma função Python que: {task}\n\n"
     "Escreva todas as docstrings e comentários em {idioma}."),
])

pipeline = generation_prompt | llm | StrOutputParser()


if __name__ == "__main__":
    task = "ordena uma lista de dicionários por uma chave específica"
    for idioma in ["inglês", "português"]:
        print(f"\n--- Idioma: {idioma} ---")
        result = pipeline.invoke({"task": task, "idioma": idioma})
        print(result)
