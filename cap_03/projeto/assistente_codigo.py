"""
cap_03 — Assistente de Codificação Auto-Corretivo com LCEL
Módulo 4: LangChain e LCEL na Prática

Pipeline: entrada → geração de código → validação de sintaxe → correção → saída
"""
import os
import subprocess
import sys
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


# --- Etapa 1: Geração de código ---
generation_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um engenheiro Python sênior. Gere apenas código Python, sem markdown."),
    ("human", "Escreva uma função Python que: {task}"),
])
code_generator = generation_prompt | llm | StrOutputParser()


# --- Etapa 2: Validação de sintaxe ---
def validate_syntax(code: str) -> dict:
    """Verifica sintaxe sem executar o código."""
    try:
        compile(code, "<string>", "exec")
        return {"code": code, "valid": True, "error": None}
    except SyntaxError as e:
        return {"code": code, "valid": False, "error": str(e)}


# --- Etapa 3: Correção (se necessário) ---
correction_prompt = ChatPromptTemplate.from_messages([
    ("system", "Corrija o erro de sintaxe Python abaixo. Retorne apenas o código corrigido."),
    ("human", "Código com erro:\n{code}\n\nErro: {error}"),
])
code_corrector = correction_prompt | llm | StrOutputParser()


def maybe_correct(result: dict) -> str:
    if result["valid"]:
        return result["code"]
    corrected = code_corrector.invoke({"code": result["code"], "error": result["error"]})
    return corrected


# --- Pipeline LCEL completo ---
pipeline = (
    {"task": RunnablePassthrough()}
    | RunnableLambda(lambda x: code_generator.invoke(x))
    | RunnableLambda(validate_syntax)
    | RunnableLambda(maybe_correct)
)

if __name__ == "__main__":
    task = "calcule o n-ésimo número de Fibonacci usando memoização"
    print(f"Task: {task}\n")
    result = pipeline.invoke(task)
    print("Código gerado e validado:\n")
    print(result)
