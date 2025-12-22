"""create users table

Revision ID: 3cd1f73d7395
Revises: 34c18afc8fbc
Create Date: 2025-12-14 12:13:53.426508

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3cd1f73d7395"
down_revision: str | None = "34c18afc8fbc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False, unique=True),
        sa.Column("emailpolicy", sa.String(length=32), nullable=False, server_default="appendonly"),
        sa.Column(
            "createdat", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
