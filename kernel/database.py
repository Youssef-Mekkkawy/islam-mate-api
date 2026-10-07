"""
kernel/database.py — Async database layer
SQLite by default (zero setup), PostgreSQL in production.
Switch via config/config.yaml [database.backend].
"""
from __future__ import annotations
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """All ORM models inherit from this."""
    pass


class DatabaseService:
    def __init__(self) -> None:
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._backend: str = "sqlite"

    async def connect(self, config: dict) -> None:
        """Initialize engine + create tables. Called once at startup."""
        db_cfg = config.get("database", {})
        if not db_cfg.get("enabled", True):
            return
        self._backend = db_cfg.get("backend", "sqlite").lower()
        if self._backend == "postgresql":
            host = db_cfg.get("host", "localhost")
            port = db_cfg.get("port", 5432)
            name = db_cfg.get("name", "islammate")
            user = db_cfg.get("user", "postgres")
            password = db_cfg.get("password", "")
            url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
            self._engine = create_async_engine(
                url, echo=db_cfg.get("echo", False),
                pool_size=db_cfg.get("pool_size", 5),
                max_overflow=10, pool_pre_ping=True,
            )
        else:
            path = db_cfg.get("path", "data/islammate.db")
            url = f"sqlite+aiosqlite:///{path}"
            self._engine = create_async_engine(
                url, echo=db_cfg.get("echo", False),
                connect_args={"check_same_thread": False},
            )
        self._session_factory = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False,
        )
        await self.create_tables()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise RuntimeError("Database not initialized. Check config/config.yaml [database] section.")
        async with self._session_factory() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    async def create_tables(self) -> None:
        if self._engine is None:
            return
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()

    @property
    def ready(self) -> bool:
        return self._engine is not None

    @property
    def backend(self) -> str:
        return self._backend