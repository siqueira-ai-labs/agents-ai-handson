"""
cap_14 — Solução Exercício 3: Controle de Concorrência Otimista
Dificuldade: Difícil | Tempo estimado: ~2-3h

NOTA: a tabela `checkpoints` real do langgraph-checkpoint-postgres tem chave
primária composta (thread_id, checkpoint_ns, checkpoint_id) — várias linhas
por thread_id (uma por checkpoint). Este exercício simplifica para uma linha
"estado atual" por thread_id (ex: uma tabela separada `thread_state`), que é
o modelo mais comum quando se implementa concorrência otimista por conta
própria em vez de usar o histórico completo de checkpoints do LangGraph.
"""
import os
import random
import time

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/langgraph")


class ConcurrencyConflictError(Exception):
    """Levantada quando a versão do checkpoint foi alterada por outro processo."""


def optimistic_update(conn, thread_id: str, expected_version: int, new_state: dict) -> int:
    """
    Atualiza o estado se a versão atual == expected_version.
    Retorna a nova versão ou levanta ConcurrencyConflictError.
    """
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE checkpoints
            SET checkpoint = %s, version = version + 1
            WHERE thread_id = %s AND version = %s
            RETURNING version
        """, (str(new_state), thread_id, expected_version))

        row = cur.fetchone()
        if row is None:
            raise ConcurrencyConflictError(
                f"Conflito de concorrência: thread={thread_id}, versão esperada={expected_version}"
            )
        conn.commit()
        return row[0]


def update_with_retry(conn, thread_id: str, new_state: dict, max_retries: int = 3) -> int:
    """Atualiza com retry (backoff exponencial + jitter) em caso de conflito."""
    for attempt in range(max_retries):
        with conn.cursor() as cur:
            cur.execute("SELECT version FROM checkpoints WHERE thread_id = %s LIMIT 1", (thread_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Thread não encontrada: {thread_id}")
            current_version = row[0]
        try:
            return optimistic_update(conn, thread_id, current_version, new_state)
        except ConcurrencyConflictError:
            if attempt == max_retries - 1:
                raise
            backoff = (2 ** attempt) + random.uniform(0, 1)  # exponencial + jitter
            time.sleep(backoff)
    raise ConcurrencyConflictError("Máximo de tentativas atingido")


if __name__ == "__main__":
    print("Controle de concorrência otimista — requer PostgreSQL rodando")
    print("Execute: docker compose -f cap_14/docker-compose.yml up -d")
    print("""
ALTER TABLE checkpoints ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 0;
""")
