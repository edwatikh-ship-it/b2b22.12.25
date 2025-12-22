"""create blacklist_domains

Revision ID: b21b2a3bb6ee
Revises: 9d40af57b9c5
Create Date: 2025-12-16 00:42:17.659659

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b21b2a3bb6ee"
down_revision: str | None = "9d40af57b9c5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "blacklist_domains",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("root_domain", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_blacklist_domains_root_domain", "blacklist_domains", ["root_domain"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_blacklist_domains_root_domain", table_name="blacklist_domains")
    op.drop_table("blacklist_domains")
