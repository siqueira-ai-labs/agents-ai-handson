"""
cap_04 — Exercício 3: Checkpointing Persistente e Auditoria
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Substitua o MemorySaver (em memória) por SqliteSaver (persistente em disco)
e implemente uma funcionalidade de auditoria que lista o histórico de todas
as sessões com timestamps e operações realizadas.

Requisitos:
1. Use SqliteSaver com banco de dados em cap_04/checkpoints.db.
2. Implemente função list_sessions() que retorna todos os thread_ids.
3. Implemente função get_session_history(thread_id) que retorna as mensagens.
4. Exiba um relatório de auditoria com: thread_id, timestamp, ferramentas usadas.
5. Garanta que após reiniciar o processo, o histórico seja preservado.

DICA: from langgraph.checkpoint.sqlite import SqliteSaver
"""
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "cap_04/checkpoints.db"


# TODO: importe SqliteSaver e reconfigure o grafo


def list_sessions(db_path: str) -> list:
    """Lista todos os thread_ids com checkpoints salvos."""
    # TODO: implemente consultando o SQLite diretamente
    raise NotImplementedError


def get_session_history(db_path: str, thread_id: str) -> list:
    """Retorna o histórico de mensagens de uma sessão."""
    # TODO: use app.get_state_history(config) para recuperar snapshots
    raise NotImplementedError


def print_audit_report(db_path: str):
    """Exibe relatório de auditoria de todas as sessões."""
    sessions = list_sessions(db_path)
    for thread_id in sessions:
        history = get_session_history(db_path, thread_id)
        print(f"\n[Sessão: {thread_id}]")
        for snap in history:
            print(f"  Mensagens: {len(snap.values.get('messages', []))}")


if __name__ == "__main__":
    print_audit_report(DB_PATH)
