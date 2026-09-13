# Apêndice E — LLMs Open-Source na Prática

## Heurística do livro para escolha de modelo

| Tarefa | Modelo recomendado | RAM |
|---|---|---|
| Exercícios fáceis (geração de texto) | `llama4.1:8b` | 8 GB |
| Function calling, ReAct | `qwen3.5:7b` | 8 GB |
| Raciocínio em cadeia | `mistral:7b` | 8 GB |
| Embeddings locais | `nomic-embed-text` | 274 MB |
| Tarefas avançadas (16 GB+) | `qwen3.5:14b-instruct` | 16 GB |

## Setup em 3 minutos

```bash
bash apendice-e-llms-opensource/setup_opensource.sh
```

## Guia de Migração: OpenRouter → Ollama

Ver `migration_guide.py` para substituições drop-in por framework.

### LangChain / LangGraph
```python
# Antes (OpenRouter):
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="nvidia/...", base_url="https://openrouter.ai/api/v1", api_key=KEY)

# Depois (Ollama local):
from langchain_ollama import ChatOllama
llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434")
```

### CrewAI
```python
# Antes:
llm = LLM(model="openai/nvidia/...", base_url="https://openrouter.ai/api/v1", api_key=KEY)

# Depois:
llm = LLM(model="ollama/qwen3.5:7b", base_url="http://localhost:11434")
```

## Benchmark de desempenho local
Ver `benchmark.py` para resultados de tarefas agentivas em hardware consumer.
