"""create parsing tables

Revision ID: 99022bad0a16
Revises: c4b1499dcaf9
Create Date: 2025-12-22 18:16:26.548364

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '99022bad0a16'
down_revision: Union[str, None] = 'c4b1499dcaf9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "parsing_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("raw_keys_json", sa.Text(), nullable=True),
        sa.Column("depth", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "parsing_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column(
            "request_id",
            sa.Integer(),
            sa.ForeignKey("parsing_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("parser_task_id", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
    )

    op.create_index("ix_parsing_runs_run_id", "parsing_runs", ["run_id"])
    op.create_index("ix_parsing_runs_request_id", "parsing_runs", ["request_id"])
    op.create_index("ix_parsing_runs_status", "parsing_runs", ["status"])

    op.create_table(
        "parsing_hits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "run_id",
            sa.Integer(),
            sa.ForeignKey("parsing_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("key_id", sa.Integer(), nullable=True),
        sa.Column("keyword", sa.String(length=500), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index("ix_parsing_hits_run_id", "parsing_hits", ["run_id"])
    op.create_index("ix_parsing_hits_domain", "parsing_hits", ["domain"])


def downgrade() -> None:
    op.drop_index("ix_parsing_hits_domain", table_name="parsing_hits")
    op.drop_index("ix_parsing_hits_run_id", table_name="parsing_hits")
    op.drop_table("parsing_hits")

    op.drop_index("ix_parsing_runs_status", table_name="parsing_runs")
    op.drop_index("ix_parsing_runs_request_id", table_name="parsing_runs")
    op.drop_index("ix_parsing_runs_run_id", table_name="parsing_runs")
    op.drop_table("parsing_runs")

    op.drop_table("parsing_requests")
