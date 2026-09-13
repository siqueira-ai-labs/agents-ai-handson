# cap_05 — Módulo 6: RAG Agentivo (Agentic RAG)

## Objetivo
Evoluir do RAG tradicional para um loop de controle agentivo com roteamento
adaptativo de estratégia (Adaptive RAG).

## Setup
```bash
source cap_05/.myenv/bin/activate
pip install -r cap_05/requirements-cap05.txt
```

## Projetos Principais
| Arquivo | Descrição |
|---|---|
| `projeto/analisador_vendas_llamaindex.py` | Agente ReAct com LlamaIndex sobre `project_data/vendas.csv` e `produtos.csv` (embeddings locais via HuggingFace, LLM via OpenRouter) |
| `projeto/pesquisa_mercado_cohere.py` | Agente de pesquisa de mercado com Cohere + LangGraph (Tavily para busca web) |

Dados de exemplo já incluídos em `projeto/project_data/` (`vendas.csv`,
`produtos.csv`, `devolucoes.json` — este último usado no Exercício 1).

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_nova_fonte_dados.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_fallback_busca_web.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_roteador_relevancia.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama llama-index-llms-ollama
ollama pull qwen3.5:7b
```
Ver `local/analisador_vendas_llamaindex_ollama.py` e `local/pesquisa_mercado_ollama.py`
(troca Cohere/Tavily por Ollama/DuckDuckGo — sem API paga).
