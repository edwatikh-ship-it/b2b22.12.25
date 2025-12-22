"""rename userid/createdat columns in user_blacklist_inn

Revision ID: 6fdf6afd7f77
Revises: de99d41dff72
Create Date: 2025-12-14 14:57:50.089833

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "6fdf6afd7f77"
down_revision: str | None = "de99d41dff72"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
