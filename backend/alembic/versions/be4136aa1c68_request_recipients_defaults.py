"""request_recipients_defaults

Revision ID: be4136aa1c68
Revises: fbb98b9e9fc9
Create Date: 2025-12-14 16:19:20.472990

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "be4136aa1c68"
down_revision: str | None = "fbb98b9e9fc9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Backfill first (idempotent)
    op.execute("UPDATE request_recipients SET created_at = now() WHERE created_at IS NULL")
    op.execute("UPDATE request_recipients SET updated_at = now() WHERE updated_at IS NULL")

    # Ensure defaults exist (idempotent)
    op.execute("ALTER TABLE request_recipients ALTER COLUMN created_at SET DEFAULT now()")
    op.execute("ALTER TABLE request_recipients ALTER COLUMN updated_at SET DEFAULT now()")


def downgrade() -> None:
    # Keep data, only remove defaults
    op.execute("ALTER TABLE request_recipients ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE request_recipients ALTER COLUMN updated_at DROP DEFAULT")
