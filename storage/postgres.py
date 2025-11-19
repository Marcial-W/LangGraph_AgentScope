import asyncio
import os
from pathlib import Path
from typing import Any, Iterable, List, Optional

import psycopg
from psycopg.rows import dict_row

DEFAULT_DSN = "postgresql://app:app@localhost:5432/appdb"
MIGRATIONS_DIR = Path(__file__).with_suffix("").parent / "migrations"


class PostgresClient:
    def __init__(self, dsn: Optional[str] = None) -> None:
        self.dsn = dsn or os.getenv("POSTGRES_DSN", DEFAULT_DSN)

    async def execute(self, query: str, params: Iterable[Any] | None = None) -> None:
        conn = await psycopg.AsyncConnection.connect(self.dsn)
        try:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
            await conn.commit()
        finally:
            await conn.close()

    async def fetch(self, query: str, params: Iterable[Any] | None = None) -> List[dict]:
        conn = await psycopg.AsyncConnection.connect(self.dsn)
        try:
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(query, params or ())
                rows = await cur.fetchall()
            await conn.commit()
            return rows
        finally:
            await conn.close()


async def run_migrations(dsn: Optional[str] = None) -> None:
    target_dsn = dsn or os.getenv("POSTGRES_DSN", DEFAULT_DSN)
    if not MIGRATIONS_DIR.exists():
        return
    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not sql_files:
        return
    conn = await psycopg.AsyncConnection.connect(target_dsn)
    try:
        async with conn.cursor() as cur:
            for file in sql_files:
                sql = file.read_text(encoding="utf-8").strip()
                if not sql:
                    continue
                await cur.execute(sql)
        await conn.commit()
    finally:
        await conn.close()


def run_migrations_sync(dsn: Optional[str] = None) -> None:
    asyncio.run(run_migrations(dsn))


