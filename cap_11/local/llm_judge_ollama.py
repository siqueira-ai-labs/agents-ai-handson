"""
cap_11 — Alternativa 100% Local: LLM-as-a-Judge via Ollama
Mesma arquitetura de projeto/llm_judge.py, trocando o LLM-juiz de OpenRouter
por Ollama local. qwen3.5:7b tende a pontuar de forma mais consistente que
modelos menores em avaliação de golden datasets.

Modelo: qwen3.5:7b
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


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


def build_judge_llm() -> ChatOllama:
    return ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)


def build_judge_chain(llm: ChatOllama | None = None):
    llm = llm or build_judge_llm()
    return JUDGE_PROMPT | llm.with_structured_output(JudgeScore)


def evaluate_response(question: str, answer: str, context: str, judge_chain=None) -> JudgeScore:
    judge_chain = judge_chain or build_judge_chain()
    return judge_chain.invoke({"question": question, "answer": answer, "context": context})


def judge_dataset(examples: list[dict], judge_chain=None) -> list[JudgeScore]:
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
    ]
    for ex, score in zip(exemplos, judge_dataset(exemplos)):
        print(f"Q: {ex['question']}")
        print(f"  Faithfulness={score.faithfulness:.2f} Relevance={score.relevance:.2f} Completeness={score.completeness:.2f}")
        print(f"  Reasoning: {score.reasoning}")
