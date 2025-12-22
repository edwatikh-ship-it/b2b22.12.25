"""create suppliers tables

Revision ID: 9d40af57b9c5
Revises: be4136aa1c68
Create Date: 2025-12-15 02:58:34.814058

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "9d40af57b9c5"
down_revision: str | None = "be4136aa1c68"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
