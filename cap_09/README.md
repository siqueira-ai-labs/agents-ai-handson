# cap_09 — Módulo 10: Observabilidade de Agentes

## Objetivo
Instrumentar agentes com Langfuse, LangSmith e AgentOps para tracing,
avaliação, gestão de prompts e resiliência (retry + circuit breaker).

## Setup
```bash
source cap_09/.myenv/bin/activate
pip install -r cap_09/requirements-cap09.txt

# Langfuse self-hosted (opcional)
docker compose up -d   # usa docker-compose.yml oficial do Langfuse
```

## Variáveis necessárias (.env)
```
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGSMITH_API_KEY=
LANGSMITH_TRACING=true
```

## Projeto Principal
| Arquivo | Descrição |
|---|---|
| `projeto/agent.py` | Agente LangGraph com tracing Langfuse + LangSmith |
| `projeto/mcp_server_purchases.py` | Servidor MCP mínimo de exemplo |

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_tags_langsmith.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_rastreamento_custos.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_alertas_latencia.py` | Difícil | ~2-3h |

## Seção 5.7 — Resiliência
Ver `projeto/resiliencia.py` para os padrões de retry com backoff exponencial,
fallback de provider e circuit breaker.

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
Ver `local/agent_ollama.py`. O Langfuse continua funcionando normalmente
self-hospedado via Docker — só o LLM do agente é local.
