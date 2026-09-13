# cap_12 — Módulo 13: Segurança e Guardrails Avançados

## Objetivo
Proteger o agente contra prompt injection, data exfiltration e conteúdo
prejudicial usando NeMo Guardrails e Llama Guard.

## Estrutura do Projeto invest-bot
```
cap_12/
├── config/
│   ├── config.yml      ← configuração NeMo Guardrails
│   ├── actions.py      ← ações personalizadas
│   └── prompts.yml     ← prompts de auto-avaliação
├── projeto/
│   └── app.py          ← aplicação Flask com guardrails
└── exercicios/
    ├── ex01_bloqueio_pii.py
    ├── ex02_novo_fluxo_nemo.py
    └── ex03_moderacao_llama_guard.py
```

## Setup
```bash
source cap_12/.myenv/bin/activate
pip install -r cap_12/requirements-cap12.txt
```

> **Pré-requisito de sistema:** o `nemoguardrails` depende de `annoy`, que só
> distribui *source dist* no PyPI (sem wheels pré-compiladas) — a instalação
> compila uma extensão C++ e exige um compilador C++ disponível (`g++`/Xcode
> Command Line Tools/Build Tools do Visual Studio, dependendo do SO).

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_bloqueio_pii.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_novo_fluxo_nemo.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_moderacao_llama_guard.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
Ver `local/app_ollama.py` — reaproveita toda a config em `config/` (prompts,
actions, fluxo de prompt injection), só troca o LLM para Ollama. Para o
exercício 3 (Llama Guard), veja a nota já no enunciado sobre `ollama pull llama-guard3`.
