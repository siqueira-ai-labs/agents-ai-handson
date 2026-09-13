"""
cap_13 — Pipeline RAG de Referência (para comparação com fine-tuning)
Módulo 14: Fine-Tuning vs. RAG

Pipeline RAG simples sobre uma pequena base de conhecimento financeiro,
usado como baseline para comparar contra o modelo fine-tunado de
finetuning_openai.py: mesmo domínio, abordagens diferentes (conhecimento
via contexto recuperado vs conhecimento internalizado nos pesos).

Embeddings rodam localmente via HuggingFace; o LLM usa OpenRouter, como no
resto do livro.
"""
import os

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

load_dotenv()

EMBED_MODEL_NAME = os.getenv(
    "EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

DOCUMENTOS = [
    "A alíquota do Imposto de Renda sobre dividendos de ações brasileiras é 0% (isento) para pessoa física.",
    "A teoria dos mercados eficientes afirma que os preços dos ativos refletem toda a informação disponível.",
    "Ações ON (ordinárias) dão direito a voto; ações PN (preferenciais) têm prioridade no recebimento de dividendos.",
    "Diversificação de carteira reduz o risco não sistemático ao distribuir investimentos entre ativos diferentes.",
    "O Índice de Sharpe mede o retorno ajustado ao risco de um investimento, dividindo o excesso de retorno pela volatilidade.",
]


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def build_rag_chain(llm: ChatOpenAI | None = None):
    llm = llm or build_llm()
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
    return chain


def answer(question: str, chain=None) -> str:
    chain = chain or build_rag_chain()
    return chain.invoke(question)


if __name__ == "__main__":
    perguntas = [
        "Qual é a alíquota do IR sobre dividendos no Brasil?",
        "Explique a teoria dos mercados eficientes.",
    ]
    chain = build_rag_chain()
    for pergunta in perguntas:
        print(f"\n> {pergunta}")
        print(answer(pergunta, chain=chain))
