"""
cap_02 — Exercício 2: Implementando Reflexion Simples
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Adicione um nó de auto-avaliação (reflection) ao grafo ReAct. Após o agente
gerar uma resposta, um segundo LLM avalia a qualidade e decide se é necessário
iterar mais ou se a resposta é satisfatória.

Requisitos:
1. Crie um nó `reflection_node` que recebe a resposta do agente.
2. O nó usa o LLM para gerar uma crítica estruturada ({"approved": bool, "feedback": str}).
3. Se approved=False, o feedback é adicionado ao estado e o agente itera.
4. Limite a 3 iterações para evitar loops infinitos.
5. Teste com uma tarefa de pesquisa que exige alta qualidade.

DICA: Use output structured (with_structured_output) para garantir JSON consistente.
"""
import os
from typing import Annotated, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

load_dotenv()

llm = ChatOpenAI(
    model="nvidia/llama-3.1-nemotron-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

MAX_ITERATIONS = 3


# Schema de avaliação estruturada
class ReflectionOutput(BaseModel):
    approved: bool = Field(description="True se a resposta é satisfatória")
    feedback: str = Field(description="Crítica construtiva para melhorar a resposta")


# TODO: crie o LLM com structured output para reflexão
# reflection_llm = llm.with_structured_output(ReflectionOutput)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    iteration: int
    approved: bool


# TODO: implemente agent_node, reflection_node e a lógica de roteamento condicional
# A condição: se approved ou iteration >= MAX_ITERATIONS → END, senão → agent


if __name__ == "__main__":
    print("Agente com Reflexion — máximo", MAX_ITERATIONS, "iterações")
    # TODO: teste com uma tarefa de pesquisa
