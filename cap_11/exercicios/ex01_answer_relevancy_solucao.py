"""
cap_11 — Solução Exercício 1: Adicionando Answer Relevancy ao Pipeline RAGAS
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import pathlib
import sys

from datasets import Dataset
from dotenv import load_dotenv
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import answer_relevancy, faithfulness

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from avaliacao_ragas import EMBED_MODEL_NAME, build_llm, build_rag_chain  # noqa: E402
from langchain_huggingface import HuggingFaceEmbeddings  # noqa: E402

QUESTIONS = [
    {"question": "O que é RAG?", "ground_truth": "RAG combina recuperação de documentos com geração de texto."},
    {"question": "O que é o padrão ReAct?", "ground_truth": "ReAct alterna raciocínio e ação em um loop até resolver a tarefa."},
    {"question": "Como o RAGAS avalia um pipeline RAG?", "ground_truth": "O RAGAS usa métricas como faithfulness e answer_relevancy, sem exigir ground truth."},
]


def build_eval_dataset() -> Dataset:
    llm = build_llm()
    chain, retriever = build_rag_chain(llm)

    rows = {"user_input": [], "response": [], "retrieved_contexts": [], "reference": []}
    for item in QUESTIONS:
        docs = retriever.invoke(item["question"])
        rows["user_input"].append(item["question"])
        rows["response"].append(chain.invoke(item["question"]))
        rows["retrieved_contexts"].append([d.page_content for d in docs])
        rows["reference"].append(item["ground_truth"])
    return Dataset.from_dict(rows), llm


def run_evaluation_with_relevancy():
    dataset, llm = build_eval_dataset()
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)

    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=LangchainLLMWrapper(llm),
        embeddings=LangchainEmbeddingsWrapper(embeddings),
    )
    return result


def piores_answer_relevancy(result, n: int = 2) -> list[tuple[str, float]]:
    """Retorna as n perguntas com menor answer_relevancy."""
    df = result.to_pandas()
    piores = df.sort_values("answer_relevancy").head(n)
    return list(zip(piores["user_input"], piores["answer_relevancy"]))


if __name__ == "__main__":
    resultado = run_evaluation_with_relevancy()
    df = resultado.to_pandas()
    print("=== Scores individuais ===")
    print(df[["user_input", "faithfulness", "answer_relevancy"]])

    print("\n=== Médias ===")
    print(df[["faithfulness", "answer_relevancy"]].mean())

    print("\n=== 2 piores em answer_relevancy ===")
    for pergunta, score in piores_answer_relevancy(resultado):
        print(f"  {score:.2f} — {pergunta}")
