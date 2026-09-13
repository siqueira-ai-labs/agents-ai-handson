"""
cap_14 — Exercício 1: Inspecionando o Estado no Postgres
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Use psycopg2 para inspecionar diretamente as tabelas de checkpoint do LangGraph
no PostgreSQL e visualize o histórico de estados de uma sessão.

Requisitos:
1. Liste todas as threads (thread_id) ativas na tabela `checkpoints`.
2. Para um thread_id específico, mostre o histórico de estados em ordem temporal.
3. Exiba: timestamp, step_number, tamanho do estado (em bytes).
4. Identifique o estado mais recente e o mais antigo de cada thread.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/langgraph")


def list_threads(conn) -> list[str]:
    """Lista todos os thread_ids com checkpoints no banco."""
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id")
        return [row[0] for row in cur.fetchall()]


def get_thread_history(conn, thread_id: str) -> list[dict]:
    """Retorna o histórico de estados de um thread."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT thread_id, checkpoint_id, checkpoint_ns,
                   octet_length(checkpoint::text) AS size_bytes,
                   metadata
            FROM checkpoints
            WHERE thread_id = %s
            ORDER BY checkpoint_id
        """, (thread_id,))
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


if __name__ == "__main__":
    with psycopg2.connect(DB_URL) as conn:
        threads = list_threads(conn)
        print(f"Threads ativas: {len(threads)}")
        for thread_id in threads[:5]:  # mostra os primeiros 5
            history = get_thread_history(conn, thread_id)
            print(f"\n[{thread_id}] — {len(history)} checkpoints")
            for h in history:
                print(f"  step {h['checkpoint_id']}: {h['size_bytes']} bytes")
