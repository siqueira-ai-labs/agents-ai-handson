"""
cap_11 — Pipeline de Avaliação RAG com RAGAS
Módulo 12: Avaliação de Agentes (Agent Evaluation)

Constrói uma cadeia RAG simples (FAISS + OpenRouter) e a avalia com as
métricas do RAGAS (faithfulness, answer_relevancy), que não exigem
comparação com um "ground truth" para funcionar.

Embeddings rodam localmente via HuggingFace (não dependem de API paga);
o LLM de geração e o LLM-juiz usam OpenRouter, como no resto do livro.
"""
import os

from datasets import Dataset
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import answer_relevancy, faithfulness

load_dotenv()

EMBED_MODEL_NAME = os.getenv(
    "EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

DOCUMENTOS = [
    "ReAct combina Reasoning e Acting: o agente alterna entre pensar e agir em um loop até resolver a tarefa.",
    "RAG (Retrieval-Augmented Generation) recupera documentos relevantes e os injeta no prompt do LLM antes da geração.",
    "LangGraph modela agentes como grafos de estado, permitindo ciclos e interrupções para human-in-the-loop.",
    "RAGAS avalia pipelines RAG com métricas como faithfulness e answer_relevancy, sem precisar de ground truth.",
]

EVAL_QUESTIONS = [
    {"question": "O que é o padrão ReAct?", "ground_truth": "ReAct alterna raciocínio e ação em um loop até resolver a tarefa."},
    {"question": "Como o RAGAS avalia um pipeline RAG?", "ground_truth": "O RAGAS usa métricas como faithfulness e answer_relevancy, sem exigir ground truth."},
]


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def build_rag_chain(llm: ChatOpenAI):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    vector_store = FAISS.from_texts(DOCUMENTOS, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})

    prompt = ChatPromptTemplate.from_template(
        "Responda à pergunta com base apenas no contexto abaixo.\n\n"
        "Contexto:\n{context}\n\nPergunta: {question}"
    )

    def format_docs(docs):
        return "\n".join(d.page_content for d in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def build_eval_dataset(chain, retriever, questions: list[dict]) -> Dataset:
    """Executa a cadeia RAG sobre as perguntas e monta o dataset no schema do RAGAS
    (colunas user_input/response/retrieved_contexts/reference — ragas >= 0.2)."""
    rows = {"user_input": [], "response": [], "retrieved_contexts": [], "reference": []}
    for item in questions:
        pergunta = item["question"]
        docs = retriever.invoke(pergunta)
        rows["user_input"].append(pergunta)
        rows["response"].append(chain.invoke(pergunta))
        rows["retrieved_contexts"].append([d.page_content for d in docs])
        rows["reference"].append(item["ground_truth"])
    return Dataset.from_dict(rows)


def run_evaluation(questions: list[dict] | None = None):
    llm = build_llm()
    chain, retriever = build_rag_chain(llm)
    dataset = build_eval_dataset(chain, retriever, questions or EVAL_QUESTIONS)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=LangchainLLMWrapper(llm),
        embeddings=LangchainEmbeddingsWrapper(embeddings),
    )
    return result


if __name__ == "__main__":
    resultado = run_evaluation()
    print(resultado)
