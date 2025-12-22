"""create request_recipients table

Revision ID: ea4ad222417f
Revises: bbff04c57403
Create Date: 2025-12-14 09:33:37.835684

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "ea4ad222417f"
down_revision: str | None = "bbff04c57403"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
