"""rename userid/createdat columns in user_blacklist_inn (safe)"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "c56fcd5c76e3"
down_revision = "de99d41dff72"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old indexes (names taken from \d output)
    op.drop_index("ix_user_blacklist_inn_userid_createdat", table_name="user_blacklist_inn")
    op.drop_index("ux_user_blacklist_inn_userid_inn", table_name="user_blacklist_inn")

    # Rename columns
    op.alter_column("user_blacklist_inn", "userid", new_column_name="user_id")
    op.alter_column("user_blacklist_inn", "createdat", new_column_name="created_at")

    # Recreate indexes with new names/columns
    op.create_index(
        "ix_user_blacklist_inn_user_id_created_at",
        "user_blacklist_inn",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ux_user_blacklist_inn_user_id_inn",
        "user_blacklist_inn",
        ["user_id", "inn"],
        unique=True,
    )


def downgrade() -> None:
    # Drop new indexes
    op.drop_index("ix_user_blacklist_inn_user_id_created_at", table_name="user_blacklist_inn")
    op.drop_index("ux_user_blacklist_inn_user_id_inn", table_name="user_blacklist_inn")

    # Rename columns back
    op.alter_column("user_blacklist_inn", "created_at", new_column_name="createdat")
    op.alter_column("user_blacklist_inn", "user_id", new_column_name="userid")

    # Recreate old indexes
    op.create_index(
        "ix_user_blacklist_inn_userid_createdat",
        "user_blacklist_inn",
        ["userid", "createdat"],
        unique=False,
    )
    op.create_index(
        "ux_user_blacklist_inn_userid_inn",
        "user_blacklist_inn",
        ["userid", "inn"],
        unique=True,
    )
