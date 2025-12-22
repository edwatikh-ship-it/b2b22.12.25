"""create request_recipients table

Revision ID: 687ead051921
Revises: 4a17327d9f63
Create Date: 2025-12-14 15:32:37

"""

import sqlalchemy as sa

from alembic import op

revision = "687ead051921"
down_revision = "4a17327d9f63"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "request_recipients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "request_id", "supplier_id", name="uq_request_recipients_request_supplier"
        ),
    )
    op.create_index(
        "ix_request_recipients_request_id", "request_recipients", ["request_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_request_recipients_request_id", table_name="request_recipients")
    op.drop_table("request_recipients")
