"""create blacklist domain url items

Revision ID: 5101a0517140
Revises: b21b2a3bb6ee
Create Date: 2025-12-16 13:58:39.001818

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5101a0517140"
down_revision: str | None = "b21b2a3bb6ee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "blacklist_domain_url_items",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "domain_id",
            sa.Integer(),
            sa.ForeignKey("blacklist_domains.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("comment", sa.String(length=1024), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_blacklist_domain_url_items_domain_id_url_unique",
        "blacklist_domain_url_items",
        ["domain_id", "url"],
        unique=True,
    )
    op.create_index(
        "ix_blacklist_domain_url_items_domain_id",
        "blacklist_domain_url_items",
        ["domain_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_blacklist_domain_url_items_domain_id",
        table_name="blacklist_domain_url_items",
    )
    op.drop_index(
        "ix_blacklist_domain_url_items_domain_id_url_unique",
        table_name="blacklist_domain_url_items",
    )
    op.drop_table("blacklist_domain_url_items")
