"""attachments

Revision ID: 0dc050e5c206
Revises: 552d97f8cc92
Create Date: 2025-12-14 00:05:21.321590

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0dc050e5c206"
down_revision: str | None = "552d97f8cc92"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
