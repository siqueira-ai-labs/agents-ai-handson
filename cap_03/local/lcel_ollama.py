"""
cap_03 — Alternativa 100% Local: LCEL via Ollama
Modelo: llama4.1:8b
"""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

llm = ChatOllama(model="llama4.1:8b", temperature=0, base_url="http://localhost:11434")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um engenheiro Python sênior. Gere apenas código Python."),
    ("human", "Escreva uma função Python que: {task}"),
])


def validate_syntax(code: str) -> str:
    try:
        compile(code, "<string>", "exec")
        return code
    except SyntaxError as e:
        return f"# ERRO DE SINTAXE: {e}\n{code}"


pipeline = prompt | llm | StrOutputParser() | RunnableLambda(validate_syntax)

if __name__ == "__main__":
    result = pipeline.invoke({"task": "ordena uma lista de dicionários por uma chave específica"})
    print(result)
