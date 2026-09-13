"""
cap_14 — Exercício 3: Controle de Concorrência Otimista
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Implemente controle de concorrência otimista no PostgresRedisSaver para
permitir múltiplos agentes lendo o mesmo thread simultaneamente, mas
detectando conflitos na escrita.

Conceito: cada snapshot tem um `version` incrementado atomicamente.
Na escrita, verifica-se se a versão atual == versão esperada; se não,
há conflito (outra instância escreveu antes).

Requisitos:
1. Adicione coluna `version` (INTEGER, DEFAULT 0) à tabela checkpoints.
2. Implemente optimistic_update(thread_id, expected_version, new_state).
3. Se versão diferente: levante ConcurrencyConflictError (custom exception).
4. Implemente retry automático em caso de conflito (máximo 3 tentativas).
5. Simule 2 agentes concorrentes escrevendo no mesmo thread e verifique detecção.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/langgraph")


class ConcurrencyConflictError(Exception):
    """Levantada quando a versão do checkpoint foi alterada por outro processo."""
    pass


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
    """Atualiza com retry em caso de conflito."""
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
    raise ConcurrencyConflictError("Máximo de tentativas atingido")


if __name__ == "__main__":
    print("Controle de concorrência otimista — requer PostgreSQL rodando")
    print("Execute: docker compose -f cap_14/docker-compose.yml up -d")
