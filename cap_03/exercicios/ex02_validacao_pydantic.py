"""
cap_03 — Exercício 2: Validação Estruturada com Pydantic
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Substitua a saída de texto livre do pipeline por saída estruturada com Pydantic.
O LLM deve retornar um objeto com campos específicos.

Requisitos:
1. Crie um schema Pydantic com: assunto_email, corpo_email, nivel_agressividade_venda (1-5).
2. Use `llm.with_structured_output(EmailSchema)` na última etapa da chain.
3. Valide que nivel_agressividade_venda está entre 1 e 5 usando Field(ge=1, le=5).
4. Teste com diferentes tópicos e verifique a consistência do JSON retornado.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatOpenAI(
    model="nvidia/llama-3.1-nemotron-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


# TODO: defina o schema Pydantic
class EmailSchema(BaseModel):
    assunto_email: str = Field(description="Assunto do e-mail de vendas")
    corpo_email: str = Field(description="Corpo completo do e-mail")
    nivel_agressividade_venda: int = Field(
        description="Nível de agressividade comercial de 1 (suave) a 5 (urgente)",
        # TODO: adicione ge=1, le=5
    )


# TODO: configure o pipeline com with_structured_output


if __name__ == "__main__":
    topicos = ["software de gestão para PMEs", "curso de Python avançado"]
    for topico in topicos:
        print(f"\n--- Produto: {topico} ---")
        # result = pipeline.invoke({"produto": topico})
        # print(result.model_dump_json(indent=2))
