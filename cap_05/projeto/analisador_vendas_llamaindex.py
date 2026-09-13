"""
cap_05 — Analisador de Vendas com LlamaIndex (RAG Agentivo)
Módulo 6: RAG Agentivo (Agentic RAG)

Agente ReAct com um QueryEngineTool por fonte de dados (vendas e produtos).
Cada fonte vira um índice vetorial local; o agente decide sozinho qual
ferramenta consultar (ou várias) para responder a pergunta do usuário.

Embeddings rodam localmente via HuggingFace (não dependem de API paga);
o LLM de raciocínio usa OpenRouter, como no resto do livro.
"""
import asyncio
import os
import pathlib

import pandas as pd
from dotenv import load_dotenv
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

load_dotenv()

DATA_DIR = pathlib.Path(__file__).parent / "project_data"
EMBED_MODEL_NAME = os.getenv(
    "EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def build_llm() -> OpenAILike:
    return OpenAILike(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
        api_base="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        is_chat_model=True,
        context_window=8192,
    )


def build_tool_from_csv(csv_path: pathlib.Path, name: str, description: str, llm: OpenAILike) -> QueryEngineTool:
    df = pd.read_csv(csv_path)
    document = Document(text=df.to_csv(index=False), metadata={"fonte": csv_path.name})
    index = VectorStoreIndex.from_documents([document])
    query_engine = index.as_query_engine(llm=llm)
    return QueryEngineTool.from_defaults(query_engine=query_engine, name=name, description=description)


def build_agent() -> ReActAgent:
    llm = build_llm()
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    tools = [
        build_tool_from_csv(
            DATA_DIR / "vendas.csv",
            name="vendas",
            description="Consulta dados de vendas: data, produto, quantidade, valor, vendedor e região.",
            llm=llm,
        ),
        build_tool_from_csv(
            DATA_DIR / "produtos.csv",
            name="produtos",
            description="Consulta catálogo de produtos: categoria, preço unitário, estoque e fornecedor.",
            llm=llm,
        ),
    ]
    return ReActAgent(tools=tools, llm=llm)


async def run_query(query: str) -> str:
    agent = build_agent()
    response = await agent.run(query)
    return str(response)


if __name__ == "__main__":
    print("Analisador de Vendas Agentivo — digite 'sair' para encerrar\n")
    while True:
        pergunta = input("Sua pergunta: ").strip()
        if pergunta.lower() == "sair":
            break
        resposta = asyncio.run(run_query(pergunta))
        print(f"\n>> Resposta:\n{resposta}\n")
