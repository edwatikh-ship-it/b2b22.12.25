"""add_moderator_suppliers_and_parsing_logs

Revision ID: 99235fd52ce6
Revises: 99022bad0a16
Create Date: 2025-12-22 19:48:47.296716

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '99235fd52ce6'
down_revision: Union[str, None] = '99022bad0a16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create moderator_suppliers table
    op.create_table(
        'moderator_suppliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('inn', sa.String(length=12), nullable=True),
        sa.Column('email', sa.String(length=320), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=32), nullable=False, server_default='supplier'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moderator_suppliers_inn'), 'moderator_suppliers', ['inn'], unique=False)
    op.create_index(op.f('ix_moderator_suppliers_domain'), 'moderator_suppliers', ['domain'], unique=False)

    # Create parsing_run_logs table
    op.create_table(
        'parsing_run_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('run_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('level', sa.String(length=16), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('context', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['run_id'], ['parsing_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parsing_run_logs_run_id'), 'parsing_run_logs', ['run_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_parsing_run_logs_run_id'), table_name='parsing_run_logs')
    op.drop_table('parsing_run_logs')
    op.drop_index(op.f('ix_moderator_suppliers_domain'), table_name='moderator_suppliers')
    op.drop_index(op.f('ix_moderator_suppliers_inn'), table_name='moderator_suppliers')
    op.drop_table('moderator_suppliers')
