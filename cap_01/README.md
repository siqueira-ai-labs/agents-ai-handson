# cap_01 — Módulo 2: Fundamentos da IA Agentiva

## Objetivo
Diferenciar IA Agentiva de IA Generativa e implementar o primeiro sistema de
pesquisa com dois frameworks distintos.

## Setup

```bash
source cap_01/.myenv/bin/activate
pip install -r cap_01/requirements-cap01.txt
cp cap_01/.env.example cap_01/.env
# edite cap_01/.env com suas chaves
```

## Projeto Principal

| Arquivo | Descrição |
|---|---|
| `projeto/abordagem1_langgraph.py` | Agente de pesquisa com LangGraph (StateGraph) |
| `projeto/abordagem2_crewai.py` | Mesmo agente com CrewAI (Pesquisador + Escritor) |

## Exercícios

| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_nova_ferramenta.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_mecanismo_memoria.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_ciclo_pca_manual.py` | Difícil | ~2-3h |

## Alternativa Local (Ollama)

```bash
ollama pull llama4.1:8b   # exercícios fáceis
ollama pull qwen3.5:7b    # bom function calling
pip install langchain-ollama
```

Ver `local/langgraph_ollama.py` e `local/crewai_ollama.py`.
