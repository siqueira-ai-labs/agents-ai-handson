"""
cap_14 — Solução Exercício 1: Inspecionando o Estado no Postgres
Dificuldade: Fácil | Tempo estimado: ~20 min
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
    """Retorna o histórico de estados de um thread, do mais antigo ao mais recente."""
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


def summarize_thread(history: list[dict]) -> dict:
    """Identifica o checkpoint mais antigo e o mais recente de um thread."""
    if not history:
        return {"oldest": None, "newest": None, "count": 0}
    return {"oldest": history[0], "newest": history[-1], "count": len(history)}


if __name__ == "__main__":
    with psycopg2.connect(DB_URL) as conn:
        threads = list_threads(conn)
        print(f"Threads ativas: {len(threads)}")
        for thread_id in threads[:5]:  # mostra os primeiros 5
            history = get_thread_history(conn, thread_id)
            resumo = summarize_thread(history)
            print(f"\n[{thread_id}] — {resumo['count']} checkpoints")
            for h in history:
                print(f"  step {h['checkpoint_id']}: {h['size_bytes']} bytes")
