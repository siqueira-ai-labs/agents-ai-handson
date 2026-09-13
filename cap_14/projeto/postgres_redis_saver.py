"""
cap_14 — PostgresRedisSaver: checkpointing híbrido PostgreSQL + Redis
Módulo 15: Gerenciamento de Estado Distribuído em Produção

Em vez de reimplementar a serialização/armazenamento de checkpoints do zero,
este saver estende o AsyncPostgresSaver oficial do LangGraph (que já resolve
schema, migrations e serialização corretamente) e adiciona uma camada de
locking distribuído via Redis para coordenar escritas concorrentes de
múltiplos workers no mesmo thread_id — o PostgreSQL continua sendo a fonte
da verdade (ACID); o Redis só coordena o acesso.
"""
import uuid
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as redis
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


class LockAcquisitionError(RuntimeError):
    """Levantada quando não foi possível adquirir o lock distribuído a tempo."""


class PostgresRedisSaver(AsyncPostgresSaver):
    def __init__(self, conn, redis_client: "redis.Redis", lock_ttl: int = 30, **kwargs):
        super().__init__(conn, **kwargs)
        self.redis = redis_client
        self.lock_ttl = lock_ttl

    @classmethod
    @asynccontextmanager
    async def from_conn_strings(cls, postgres_conn_string: str, redis_url: str, lock_ttl: int = 30):
        """Context manager assíncrono: cria as conexões, garante o schema
        (setup()) e libera tudo ao sair."""
        redis_client = redis.from_url(redis_url)
        try:
            async with AsyncPostgresSaver.from_conn_string(postgres_conn_string) as pg_saver:
                await pg_saver.setup()
                saver = cls(pg_saver.conn, redis_client=redis_client, lock_ttl=lock_ttl)
                yield saver
        finally:
            await redis_client.aclose()

    def _lock_key(self, thread_id: str) -> str:
        return f"lock:thread:{thread_id}"

    async def _acquire_lock(self, thread_id: str, owner: str) -> None:
        acquired = await self.redis.set(self._lock_key(thread_id), owner, nx=True, ex=self.lock_ttl)
        if not acquired:
            raise LockAcquisitionError(f"Não foi possível adquirir o lock para thread_id={thread_id}")

    async def _release_lock(self, thread_id: str, owner: str) -> None:
        """Libera o lock só se ainda pertencer a este owner (evita liberar um
        lock que já expirou e foi adquirido por outro worker)."""
        key = self._lock_key(thread_id)
        current = await self.redis.get(key)
        if current and current.decode() == owner:
            await self.redis.delete(key)

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict[str, Any],
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        owner = str(uuid.uuid4())
        await self._acquire_lock(thread_id, owner)
        try:
            return await super().aput(config, checkpoint, metadata, new_versions)
        finally:
            await self._release_lock(thread_id, owner)
