import asyncio

from sqlalchemy import text

from app.adapters.db.session import engine


async def main() -> None:
    async with engine.begin() as conn:
        # backfill existing nulls (на всякий случай)
        await conn.execute(
            text("UPDATE request_recipients SET created_at = now() WHERE created_at IS NULL")
        )
        await conn.execute(
            text("UPDATE request_recipients SET updated_at = now() WHERE updated_at IS NULL")
        )

        # ensure defaults exist
        await conn.execute(
            text("ALTER TABLE request_recipients ALTER COLUMN created_at SET DEFAULT now()")
        )
        await conn.execute(
            text("ALTER TABLE request_recipients ALTER COLUMN updated_at SET DEFAULT now()")
        )

        # verify defaults
        q = text("""
        SELECT column_name, column_default, is_nullable
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name='request_recipients'
          AND column_name IN ('created_at','updated_at')
        ORDER BY column_name;
        """)
        rows = (await conn.execute(q)).all()
        for r in rows:
            print(r[0], r[1], r[2])


asyncio.run(main())
