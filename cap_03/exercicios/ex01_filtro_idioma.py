"""
cap_03 — Exercício 1: Adicionando um Filtro de Idioma
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Modifique o pipeline do assistente de código para aceitar uma variável `idioma`.
O código gerado deve conter docstrings e comentários no idioma especificado.

Requisitos:
1. Adicione `idioma` como variável ao PromptTemplate inicial.
2. O restante do pipeline (validação, correção) não deve ser alterado.
3. Teste com idioma="inglês" e idioma="português".
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    model="nvidia/llama-3.1-nemotron-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

# TODO: modifique o prompt para incluir a variável `idioma`
generation_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um engenheiro Python sênior."),
    ("human", "Escreva uma função Python que: {task}"),
    # TODO: adicione instrução de idioma
])

pipeline = generation_prompt | llm | StrOutputParser()

if __name__ == "__main__":
    # TODO: teste com os dois idiomas
    for idioma in ["inglês", "português"]:
        print(f"\n--- Idioma: {idioma} ---")
        # result = pipeline.invoke({"task": "ordena uma lista de dicionários por chave", "idioma": idioma})
        # print(result)
