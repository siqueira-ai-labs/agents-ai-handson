# cap_14 — Módulo 15: Gerenciamento de Estado Distribuído em Produção

## Objetivo
Substituir MemorySaver (in-memory) por persistência híbrida PostgreSQL + Redis
para checkpointing distribuído e resiliente em produção.

## Infraestrutura necessária
```bash
# Subir PostgreSQL e Redis com Docker
docker run -d --name pg -e POSTGRES_PASSWORD=secret -p 5432:5432 postgres:16
docker run -d --name redis -p 6379:6379 redis:7

# Ou com Docker Compose (recomendado):
docker compose -f cap_14/docker-compose.yml up -d
```

## Setup
```bash
source cap_14/.myenv/bin/activate
pip install -r cap_14/requirements-cap14.txt
```

## Projeto Principal
| Arquivo | Descrição |
|---|---|
| `projeto/postgres_redis_saver.py` | Implementação do PostgresRedisSaver |
| `projeto/exemplo_uso.py` | Agente simples usando o saver híbrido |
| `docker-compose.yml` | PostgreSQL 16 + Redis 7 para desenvolvimento |

## Exercícios
| # | Arquivo | Dificuldade | Tempo |
|---|---|---|---|
| 1 | `exercicios/ex01_inspecionar_estado.py` | Fácil | ~20 min |
| 2 | `exercicios/ex02_resiliencia_lock_redis.py` | Médio | ~45 min |
| 3 | `exercicios/ex03_controle_concorrencia.py` | Difícil | ~2-3h |

## Alternativa Local
```bash
pip install langchain-ollama
ollama pull qwen3.5:7b
```
Ver `local/exemplo_uso_ollama.py`. PostgreSQL e Redis continuam via Docker
— só o LLM é local.
