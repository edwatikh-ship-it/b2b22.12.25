"""create user blacklist inn

Revision ID: 34c18afc8fbc
Revises: ea4ad222417f
Create Date: 2025-12-14

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "34c18afc8fbc"
down_revision: str | None = "ea4ad222417f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_blacklist_inn",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("inn", sa.String(length=12), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_user_blacklist_inn_user_id_inn",
        "user_blacklist_inn",
        ["user_id", "inn"],
        unique=True,
    )

    op.create_index(
        "ix_user_blacklist_inn_user_id",
        "user_blacklist_inn",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_blacklist_inn_user_id_inn", table_name="user_blacklist_inn")
    op.drop_index("ix_user_blacklist_inn_user_id", table_name="user_blacklist_inn")
    op.drop_table("user_blacklist_inn")
