# cap_11 — Módulo 12: Avaliação de Agentes (Agent Evaluation)

## Objetivo
Implementar um ciclo de avaliação automatizada com RAGAS, TruLens e
LLM-as-a-Judge para medir qualidade de respostas de forma escalável.

## Setup
```bash
source cap_11/.myenv/bin/activate
pip install -r cap_11/requirements-cap11.txt
```

## Projeto Principal
| Arquivo | Descrição |
|---|---|
| `projeto/avaliacao_ragas.py` | Pipeline de avaliação com RAGAS (faithfulness, relevancy) |
| `projeto/llm_judge.py` | LLM-as-a-Judge customizado para critérios específicos |

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_answer_relevancy.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_golden_dataset.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_llm_judge_customizado.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
Ver `local/llm_judge_ollama.py` (RAGAS já usa embeddings locais por padrão;
o LLM-juiz troca de OpenRouter para Ollama).
