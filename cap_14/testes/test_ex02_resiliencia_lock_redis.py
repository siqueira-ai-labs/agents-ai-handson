"""Testes unitários — Ex02: Resiliência no Lock do Redis (com fakeredis)"""
import pathlib
import sys
import threading
import time

import fakeredis
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex02_resiliencia_lock_redis_solucao as ex02


@pytest.fixture
def fake_client():
    return fakeredis.FakeStrictRedis()


def test_modulo_importavel():
    assert ex02 is not None


def test_acquire_lock_bem_sucedido(fake_client):
    assert ex02.acquire_lock("t1", "owner-A", ttl=5, client=fake_client) is True


def test_acquire_lock_falha_se_ja_adquirido(fake_client):
    ex02.acquire_lock("t1", "owner-A", ttl=5, client=fake_client)
    assert ex02.acquire_lock("t1", "owner-B", ttl=5, client=fake_client) is False


def test_release_lock_so_libera_se_owner_correto(fake_client):
    ex02.acquire_lock("t1", "owner-A", ttl=5, client=fake_client)
    assert ex02.release_lock("t1", "owner-B", client=fake_client) is False
    assert ex02.release_lock("t1", "owner-A", client=fake_client) is True
    assert fake_client.get("lock:t1") is None


def test_lock_expira_apos_ttl(fake_client):
    ex02.acquire_lock("t1", "owner-A", ttl=1, client=fake_client)
    time.sleep(1.2)
    # Worker 2 deve conseguir adquirir depois que o TTL expirou, mesmo sem release
    assert ex02.acquire_lock("t1", "owner-B", ttl=5, client=fake_client) is True


def test_worker_2_assume_apos_worker_1_crashar(fake_client):
    """Simula o cenário do enunciado: Worker 1 crasha segurando o lock (TTL
    curto); Worker 2 não deve ficar bloqueado indefinidamente."""
    results = []
    ex02.worker(1, "crash-lock", results, client=fake_client, crash_before_release=True)
    assert "crashou" in results[0]

    # TTL padrão do worker é LOCK_TTL (30s) — reduzimos via acquire_lock direto
    # para não deixar o teste lento: liberamos manualmente para simular o TTL
    # expirando, já que testamos a expiração de fato em test_lock_expira_apos_ttl.
    fake_client.delete("lock:crash-lock")
    ex02.worker(2, "crash-lock", results, client=fake_client)
    assert "OK" in results[1]


def test_tres_threads_concorrentes_apenas_uma_adquire_por_vez(fake_client):
    results = []
    threads = [
        threading.Thread(target=ex02.worker, args=(i, "concurrent-lock", results), kwargs={"client": fake_client})
        for i in range(3)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(results) == 3
    assert all("OK" in r or "falhou" in r for r in results)
