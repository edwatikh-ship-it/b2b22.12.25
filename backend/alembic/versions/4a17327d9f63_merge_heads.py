"""merge heads

Revision ID: 4a17327d9f63
Revises: 9458942023a4
Create Date: 2025-12-14 15:23:55.318380

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "4a17327d9f63"
down_revision: str | None = "9458942023a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
