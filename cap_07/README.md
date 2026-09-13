# cap_07 — Módulo 8: Sistemas Multiagente com LangGraph e CrewAI

## Objetivo
Orquestrar times de agentes especializados. Dois projetos paralelos:
chatbot de suporte com LangGraph e analista de ações com CrewAI.

## Setup
```bash
source cap_07/.myenv/bin/activate
pip install -r cap_07/requirements-cap07.txt
```

## Projetos Principais
| Arquivo | Descrição |
|---|---|
| `projeto/chatbot_suporte_langgraph.py` | Chatbot multiagente com roteamento por especialidade |
| `projeto/analista_acoes_crewai.py` | Equipe de analistas financeiros com CrewAI |

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_novo_agente.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_processo_hierarquico.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_ferramentas_dados_realtime.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
Ver `local/chatbot_suporte_ollama.py` e `local/analista_acoes_ollama.py`
(CrewAI usa Ollama via LiteLLM, prefixo `ollama/`).
