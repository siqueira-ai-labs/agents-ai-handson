"""
cap_14 — Exercício 2: Resiliência no Lock do Redis
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Implemente um mecanismo de lock distribuído no Redis com TTL automático e
liberação em caso de falha do processo que adquiriu o lock.

Requisitos:
1. Use SET ... NX EX (atomic lock) em vez de SETNX + EXPIRE separados.
2. O lock deve ter TTL de 30s para liberar automaticamente em caso de crash.
3. Implemente acquire_lock() com retry (máximo 5 tentativas, backoff de 1s).
4. Implemente release_lock() que verifica o owner antes de liberar.
5. Teste com 3 threads concorrentes tentando o mesmo lock.
"""
import os
import time
import uuid
import threading
from dotenv import load_dotenv
import redis

load_dotenv()

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
LOCK_TTL = 30
MAX_RETRIES = 5
RETRY_DELAY = 1.0


def acquire_lock(lock_name: str, owner_id: str, ttl: int = LOCK_TTL) -> bool:
    """Tenta adquirir o lock de forma atômica. Retorna True se adquiriu."""
    # SET lock_name owner_id NX EX ttl — operação atômica no Redis
    result = r.set(f"lock:{lock_name}", owner_id, nx=True, ex=ttl)
    return result is True


def acquire_lock_with_retry(lock_name: str, owner_id: str) -> bool:
    """Tenta adquirir o lock com retry."""
    for attempt in range(MAX_RETRIES):
        if acquire_lock(lock_name, owner_id):
            return True
        time.sleep(RETRY_DELAY)
    return False


def release_lock(lock_name: str, owner_id: str) -> bool:
    """Libera o lock apenas se o owner_id corresponde ao detentor atual."""
    key = f"lock:{lock_name}"
    current_owner = r.get(key)
    if current_owner and current_owner.decode() == owner_id:
        r.delete(key)
        return True
    return False


def worker(thread_id: int, lock_name: str, results: list):
    owner = f"thread-{thread_id}-{uuid.uuid4().hex[:8]}"
    acquired = acquire_lock_with_retry(lock_name, owner)
    if acquired:
        print(f"Thread {thread_id} adquiriu o lock.")
        time.sleep(0.5)  # simula trabalho
        release_lock(lock_name, owner)
        results.append(f"thread-{thread_id}: OK")
    else:
        results.append(f"thread-{thread_id}: falhou após {MAX_RETRIES} tentativas")


if __name__ == "__main__":
    results = []
    threads = [threading.Thread(target=worker, args=(i, "test-lock", results)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("\nResultados:")
    for r_item in results:
        print(f"  {r_item}")
