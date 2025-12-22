"""add_request_recipients

Revision ID: fbb98b9e9fc9
Revises: 687ead051921
Create Date: 2025-12-14 16:12:14.902702

"""

from collections.abc import Sequence

from alembic import op

revision: str = "fbb98b9e9fc9"
down_revision: str | None = "687ead051921"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Idempotent: in case revision was applied when upgrade() was empty.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS request_recipients (
            id SERIAL PRIMARY KEY,
            request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
            supplier_id INTEGER NOT NULL,
            selected BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_request_recipients_request_supplier
        ON request_recipients (request_id, supplier_id);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_request_recipients_request_id
        ON request_recipients (request_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS request_recipients;")
