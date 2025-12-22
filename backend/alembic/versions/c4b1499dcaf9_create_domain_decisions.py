"""create_domain_decisions

Revision ID: c4b1499dcaf9
Revises: 9a051d01a91c
Create Date: 2025-12-17

"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "c4b1499dcaf9"
down_revision = "9a051d01a91c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "domain_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("domain", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        # Raw carddata snapshot (suppliers service not implemented yet)
        sa.Column("card_inn", sa.String(length=12), nullable=True),
        sa.Column("card_name", sa.String(length=500), nullable=True),
        sa.Column("card_email", sa.String(length=320), nullable=True),
        sa.Column("card_emails", sa.Text(), nullable=True),  # JSON string
        sa.Column("card_phone", sa.String(length=64), nullable=True),
        sa.Column("card_comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("domain_decisions")
