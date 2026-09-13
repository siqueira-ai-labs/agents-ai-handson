"""
cap_11 — LLM-as-a-Judge Customizado
Módulo 12: Avaliação de Agentes (Agent Evaluation)

Avaliador que usa um LLM para pontuar respostas em critérios que métricas
prontas (RAGAS) não cobrem — aqui, faithfulness/relevance/completeness como
ponto de partida. Usa saída estruturada (Pydantic) para garantir scores
consistentes e parseáveis.
"""
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class JudgeScore(BaseModel):
    faithfulness: float = Field(ge=0.0, le=1.0, description="A resposta é fiel ao contexto?")
    relevance: float = Field(ge=0.0, le=1.0, description="A resposta é relevante à pergunta?")
    completeness: float = Field(ge=0.0, le=1.0, description="A resposta cobre tudo que o contexto permite?")
    reasoning: str = Field(description="Justificativa curta para os scores acima.")


JUDGE_PROMPT = ChatPromptTemplate.from_template(
    "Você é um avaliador especialista em sistemas RAG.\n\n"
    "Pergunta: {question}\n"
    "Contexto recuperado: {context}\n"
    "Resposta do agente: {answer}\n\n"
    "Avalie a resposta em três dimensões, cada uma de 0.0 a 1.0:\n"
    "- faithfulness: a resposta é fiel ao contexto (não inventa informação)?\n"
    "- relevance: a resposta é relevante à pergunta feita?\n"
    "- completeness: a resposta cobre tudo o que o contexto permite responder?\n"
)


def build_judge_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def build_judge_chain(llm: ChatOpenAI | None = None):
    llm = llm or build_judge_llm()
    return JUDGE_PROMPT | llm.with_structured_output(JudgeScore)


def evaluate_response(question: str, answer: str, context: str, judge_chain=None) -> JudgeScore:
    """Avalia uma única resposta usando o LLM-juiz."""
    judge_chain = judge_chain or build_judge_chain()
    return judge_chain.invoke({"question": question, "answer": answer, "context": context})


def judge_dataset(examples: list[dict], judge_chain=None) -> list[JudgeScore]:
    """Avalia uma lista de exemplos {question, answer, context}."""
    judge_chain = judge_chain or build_judge_chain()
    return [
        evaluate_response(ex["question"], ex["answer"], ex["context"], judge_chain=judge_chain)
        for ex in examples
    ]


if __name__ == "__main__":
    exemplos = [
        {
            "question": "O que é o padrão ReAct?",
            "context": "ReAct combina Reasoning e Acting: o agente pensa antes de agir, em um loop.",
            "answer": "ReAct é um padrão que alterna raciocínio e ação em um loop até resolver a tarefa.",
        },
        {
            "question": "O que é RAG?",
            "context": "RAG injeta documentos relevantes no prompt do LLM antes da geração.",
            "answer": "RAG é Retrieval-Augmented Generation, combina busca de documentos com geração de texto.",
        },
    ]
    scores = judge_dataset(exemplos)
    for ex, score in zip(exemplos, scores):
        print(f"\nQ: {ex['question']}")
        print(f"  Faithfulness: {score.faithfulness:.2f}")
        print(f"  Relevance:    {score.relevance:.2f}")
        print(f"  Completeness: {score.completeness:.2f}")
        print(f"  Reasoning:    {score.reasoning}")
