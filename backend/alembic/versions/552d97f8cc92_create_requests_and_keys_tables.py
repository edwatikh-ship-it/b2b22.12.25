"""create requests and keys tables

Revision ID: 552d97f8cc92
Revises: 3315ed698ecb
Create Date: 2025-12-13 22:59:57.084306
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "552d97f8cc92"
down_revision: str | None = "3315ed698ecb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "request_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "request_id",
            sa.Integer(),
            sa.ForeignKey("requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("pos", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("qty", sa.Numeric(), nullable=True),
        sa.Column("unit", sa.String(length=64), nullable=True),
    )

    op.create_index("ix_request_keys_request_id", "request_keys", ["request_id"])


def downgrade() -> None:
    op.drop_index("ix_request_keys_request_id", table_name="request_keys")
    op.drop_table("request_keys")
    op.drop_table("requests")
