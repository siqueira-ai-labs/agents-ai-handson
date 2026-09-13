"""
cap_05 — Alternativa 100% Local: Analisador de Vendas via Ollama
Mesma arquitetura de projeto/analisador_vendas_llamaindex.py (agente ReAct
do LlamaIndex + índice vetorial por fonte de dados), trocando apenas o LLM
de OpenRouter para Ollama local. Embeddings já são locais (HuggingFace) nas
duas versões.

Modelo: qwen3.5:7b (bom em tool calling / ReAct)
"""
import pathlib

import pandas as pd
from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

DATA_DIR = pathlib.Path(__file__).parent.parent / "projeto" / "project_data"
EMBED_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def build_tool_from_csv(csv_path: pathlib.Path, name: str, description: str, llm: Ollama) -> QueryEngineTool:
    df = pd.read_csv(csv_path)
    document = Document(text=df.to_csv(index=False), metadata={"fonte": csv_path.name})
    index = VectorStoreIndex.from_documents([document])
    query_engine = index.as_query_engine(llm=llm)
    return QueryEngineTool.from_defaults(query_engine=query_engine, name=name, description=description)


def build_agent() -> ReActAgent:
    llm = Ollama(model="qwen3.5:7b", base_url="http://localhost:11434", request_timeout=120.0)
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)

    tools = [
        build_tool_from_csv(
            DATA_DIR / "vendas.csv", "vendas",
            "Consulta dados de vendas: data, produto, quantidade, valor, vendedor e região.", llm,
        ),
        build_tool_from_csv(
            DATA_DIR / "produtos.csv", "produtos",
            "Consulta catálogo de produtos: categoria, preço unitário, estoque e fornecedor.", llm,
        ),
    ]
    return ReActAgent(tools=tools, llm=llm)


async def run_query(query: str) -> str:
    agent = build_agent()
    response = await agent.run(query)
    return str(response)


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(run_query("Qual categoria teve maior faturamento?")))
