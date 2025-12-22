import asyncio

from sqlalchemy import text

from app.adapters.db.session import engine

SQL = """
CREATE TABLE IF NOT EXISTS request_recipients (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    supplier_id INTEGER NOT NULL,
    selected BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_request_recipients_request_supplier
ON request_recipients (request_id, supplier_id);

CREATE INDEX IF NOT EXISTS ix_request_recipients_request_id
ON request_recipients (request_id);
"""


async def main() -> None:
    async with engine.begin() as conn:
        # execute each statement separately (psycopg/asyncpg don't like multi-statement in one execute)
        for stmt in [s.strip() for s in SQL.split(";") if s.strip()]:
            await conn.execute(text(stmt))
        res = await conn.execute(text("SELECT to_regclass('public.request_recipients')"))
        print("table:", res.scalar())


if __name__ == "__main__":
    asyncio.run(main())
