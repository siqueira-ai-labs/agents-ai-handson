"""
cap_11 — Exercício 3: LLM-as-a-Judge Customizado
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Implemente um LLM-as-a-Judge com critérios customizados para avaliar respostas
do agente em dimensões além das métricas padrão do RAGAS.

Critérios customizados:
- safety: a resposta não contém conteúdo prejudicial (0-1)
- completeness: a resposta cobre todos os aspectos da pergunta (0-1)
- citation_quality: referências a fontes são precisas e verificáveis (0-1)
- tone_appropriateness: adequação do tom ao contexto (0-1)

Requisitos:
1. Use with_structured_output (Pydantic) para garantir scores consistentes.
2. Implemente calibração: compare scores do LLM com avaliação humana (5 exemplos).
3. Calcule concordância (Cohen's Kappa ou correlação de Pearson) com humanos.
4. Crie um relatório HTML simples em cap_11/evaluation_report.html.
"""
import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    model="nvidia/llama-3.1-nemotron-70b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


class JudgeScore(BaseModel):
    safety: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    citation_quality: float = Field(ge=0.0, le=1.0)
    tone_appropriateness: float = Field(ge=0.0, le=1.0)
    overall: float = Field(ge=0.0, le=1.0)
    reasoning: str


judge_llm = llm.with_structured_output(JudgeScore)


def evaluate_response(question: str, answer: str, context: str) -> JudgeScore:
    """Avalia uma resposta usando LLM-as-a-Judge com critérios customizados."""
    # TODO: crie o prompt e invoque o judge_llm
    raise NotImplementedError


def generate_html_report(evaluations: list[dict], output_path: str):
    """Gera um relatório HTML com os scores de avaliação."""
    # TODO: implemente geração de HTML simples com tabela de scores
    raise NotImplementedError


if __name__ == "__main__":
    # TODO: carregue exemplos do golden dataset e avalie
    pass
