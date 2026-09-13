"""
cap_13 — Alternativa 100% Local: Pipeline RAG de Referência via Ollama
Mesma arquitetura de projeto/rag_pipeline.py, trocando o LLM de OpenRouter
por Ollama local. O fine-tuning com QLoRA (a outra metade do capítulo) já é
100% local por natureza — veja exercicios/ex03_quantizacao_deploy_local_solucao.py.

Modelo: qwen3.5:7b
"""
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

EMBED_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

DOCUMENTOS = [
    "A alíquota do Imposto de Renda sobre dividendos de ações brasileiras é 0% (isento) para pessoa física.",
    "A teoria dos mercados eficientes afirma que os preços dos ativos refletem toda a informação disponível.",
    "Ações ON (ordinárias) dão direito a voto; ações PN (preferenciais) têm prioridade no recebimento de dividendos.",
    "Diversificação de carteira reduz o risco não sistemático ao distribuir investimentos entre ativos diferentes.",
    "O Índice de Sharpe mede o retorno ajustado ao risco de um investimento, dividindo o excesso de retorno pela volatilidade.",
]


def build_llm() -> ChatOllama:
    return ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)


def build_rag_chain(llm: ChatOllama | None = None):
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

    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def answer(question: str, chain=None) -> str:
    chain = chain or build_rag_chain()
    return chain.invoke(question)


if __name__ == "__main__":
    chain = build_rag_chain()
    print(answer("Qual é a alíquota do IR sobre dividendos no Brasil?", chain=chain))
