"""
cap_03 — Solução Exercício 2: Validação Estruturada com Pydantic
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


class EmailSchema(BaseModel):
    assunto_email: str = Field(description="Assunto do e-mail de vendas")
    corpo_email: str = Field(description="Corpo completo do e-mail")
    nivel_agressividade_venda: int = Field(
        description="Nível de agressividade comercial de 1 (suave) a 5 (urgente)",
        ge=1,
        le=5,
    )


prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Você é especialista em copywriting de vendas B2B. "
     "Gere e-mails comerciais eficazes e profissionais."),
    ("human", "Crie um e-mail de vendas para o produto: {produto}"),
])

structured_llm = llm.with_structured_output(EmailSchema)
pipeline = prompt | structured_llm


if __name__ == "__main__":
    topicos = ["software de gestão para PMEs", "curso de Python avançado"]
    for topico in topicos:
        print(f"\n--- Produto: {topico} ---")
        result = pipeline.invoke({"produto": topico})
        print(result.model_dump_json(indent=2))
