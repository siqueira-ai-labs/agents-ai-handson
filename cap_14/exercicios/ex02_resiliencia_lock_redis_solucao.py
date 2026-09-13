"""
cap_14 — Solução Exercício 2: Resiliência no Lock do Redis
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import os
import threading
import time
import uuid

import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
LOCK_TTL = 30
MAX_RETRIES = 5
RETRY_DELAY = 1.0


def acquire_lock(lock_name: str, owner_id: str, ttl: int = LOCK_TTL, client=r) -> bool:
    """Tenta adquirir o lock de forma atômica. Retorna True se adquiriu."""
    # SET lock_name owner_id NX EX ttl — operação atômica no Redis: NX garante
    # que só adquire se a chave não existir, EX define o TTL na mesma chamada
    # (evita a janela de corrida entre SETNX e EXPIRE separados).
    result = client.set(f"lock:{lock_name}", owner_id, nx=True, ex=ttl)
    return result is True


def acquire_lock_with_retry(lock_name: str, owner_id: str, client=r) -> bool:
    """Tenta adquirir o lock com retry."""
    for attempt in range(MAX_RETRIES):
        if acquire_lock(lock_name, owner_id, client=client):
            return True
        time.sleep(RETRY_DELAY)
    return False


def release_lock(lock_name: str, owner_id: str, client=r) -> bool:
    """Libera o lock apenas se o owner_id corresponde ao detentor atual."""
    key = f"lock:{lock_name}"
    current_owner = client.get(key)
    if current_owner and current_owner.decode() == owner_id:
        client.delete(key)
        return True
    return False


def worker(thread_id: int, lock_name: str, results: list, client=r, crash_before_release: bool = False):
    owner = f"thread-{thread_id}-{uuid.uuid4().hex[:8]}"
    acquired = acquire_lock_with_retry(lock_name, owner, client=client)
    if acquired:
        print(f"Thread {thread_id} adquiriu o lock.")
        time.sleep(0.5)  # simula trabalho
        if crash_before_release:
            # Simula um crash: nunca chama release_lock(). O lock só se
            # libera quando o TTL expira no Redis.
            results.append(f"thread-{thread_id}: crashou segurando o lock")
            return
        release_lock(lock_name, owner, client=client)
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
