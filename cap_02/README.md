# cap_02 — Módulo 3: Arquiteturas e Padrões de Design

## Objetivo
Implementar o padrão ReAct (Reasoning and Acting) com LangGraph e aplicar
os conceitos de Percepção-Cognição-Ação, Reflection e Planning.

## Setup
```bash
source cap_02/.myenv/bin/activate
pip install -r cap_02/requirements-cap02.txt
```

## Projeto Principal
| Arquivo | Descrição |
|---|---|
| `projeto/react_assistant.py` | Assistente de pesquisa com padrão ReAct + LangGraph |

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_nova_tool_react.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_reflexion_simples.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_testes_vcrpy.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
ollama pull mistral:7b   # bom raciocínio em cadeia, 8 GB RAM
ollama pull qwen3.5:7b   # melhor para ex03 (saídas estruturadas para VCR)
```
