"""create user_blacklist_inn

Revision ID: de99d41dff72
Revises: a291dc92b69a
Create Date: 2025-12-14

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

revision: str = "de99d41dff72"
down_revision: str | None = "a291dc92b69a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(conn, name: str) -> bool:
    q = text(
        "select 1 from information_schema.tables "
        "where table_schema='public' and table_name=:name"
    )
    return conn.execute(q, {"name": name}).first() is not None


def _index_exists(conn, name: str) -> bool:
    q = text("select 1 from pg_indexes where schemaname='public' and indexname=:name")
    return conn.execute(q, {"name": name}).first() is not None


def upgrade() -> None:
    conn = op.get_bind()

    if not _table_exists(conn, "user_blacklist_inn"):
        op.create_table(
            "user_blacklist_inn",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("userid", sa.Integer(), nullable=False),
            sa.Column("inn", sa.String(length=12), nullable=False),
            sa.Column("reason", sa.String(length=512), nullable=True),
            sa.Column(
                "createdat",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(["userid"], ["users.id"], ondelete="CASCADE"),
        )

    if not _index_exists(conn, "ux_user_blacklist_inn_userid_inn"):
        op.create_index(
            "ux_user_blacklist_inn_userid_inn", "user_blacklist_inn", ["userid", "inn"], unique=True
        )

    if not _index_exists(conn, "ix_user_blacklist_inn_userid_createdat"):
        op.create_index(
            "ix_user_blacklist_inn_userid_createdat",
            "user_blacklist_inn",
            ["userid", "createdat"],
            unique=False,
        )


def downgrade() -> None:
    conn = op.get_bind()

    if _index_exists(conn, "ix_user_blacklist_inn_userid_createdat"):
        op.drop_index("ix_user_blacklist_inn_userid_createdat", table_name="user_blacklist_inn")
    if _index_exists(conn, "ux_user_blacklist_inn_userid_inn"):
        op.drop_index("ux_user_blacklist_inn_userid_inn", table_name="user_blacklist_inn")
    if _table_exists(conn, "user_blacklist_inn"):
        op.drop_table("user_blacklist_inn")
