"""blacklist domains comment urls

Revision ID: 9a051d01a91c
Revises: 5101a0517140
Create Date: 2025-12-16 20:27:57.213277

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a051d01a91c"
down_revision: str | None = "5101a0517140"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add optional comment to domains
    op.add_column("blacklist_domains", sa.Column("comment", sa.Text(), nullable=True))

    # Store URL-level blacklist items per domain (optional)
    op.create_table(
        "blacklist_domain_urls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "domain_id",
            sa.Integer(),
            sa.ForeignKey("blacklist_domains.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("domain_id", "url", name="uq_blacklist_domain_urls_domain_id_url"),
    )


def downgrade() -> None:
    op.drop_table("blacklist_domain_urls")
    op.drop_column("blacklist_domains", "comment")
