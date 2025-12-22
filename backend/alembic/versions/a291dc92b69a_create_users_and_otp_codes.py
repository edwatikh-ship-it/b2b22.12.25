"""create users and otp_codes

Revision ID: a291dc92b69a
Revises: 3cd1f73d7395
Create Date: 2025-12-14

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a291dc92b69a"
down_revision: str | None = "3cd1f73d7395"
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

    if not _table_exists(conn, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column(
                "emailpolicy", sa.String(length=32), nullable=False, server_default="appendonly"
            ),
            sa.Column(
                "createdat",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )

    if not _index_exists(conn, "ix_users_email"):
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if not _table_exists(conn, "otp_codes"):
        op.create_table(
            "otp_codes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("codehash", sa.String(length=128), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("maxattempts", sa.Integer(), nullable=False, server_default="5"),
            sa.Column("expiresat", sa.DateTime(timezone=True), nullable=False),
            sa.Column(
                "createdat",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )

    if not _index_exists(conn, "ix_otp_codes_email_createdat"):
        op.create_index(
            "ix_otp_codes_email_createdat", "otp_codes", ["email", "createdat"], unique=False
        )


def downgrade() -> None:
    conn = op.get_bind()

    if _index_exists(conn, "ix_otp_codes_email_createdat"):
        op.drop_index("ix_otp_codes_email_createdat", table_name="otp_codes")
    if _table_exists(conn, "otp_codes"):
        op.drop_table("otp_codes")

    if _index_exists(conn, "ix_users_email"):
        op.drop_index("ix_users_email", table_name="users")
    # users may pre-exist in some environments; do not drop it blindly on downgrade.
