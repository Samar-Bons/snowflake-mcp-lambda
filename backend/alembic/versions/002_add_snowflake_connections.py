"""Add snowflake_connections table

Revision ID: 002
Revises: 001
Create Date: 2025-07-10 12:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create snowflake_connections table
    op.create_table(
        "snowflake_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("encrypted_account", sa.Text(), nullable=False),
        sa.Column("encrypted_user", sa.Text(), nullable=False),
        sa.Column("encrypted_password", sa.Text(), nullable=False),
        sa.Column("encrypted_warehouse", sa.Text(), nullable=False),
        sa.Column("encrypted_database", sa.Text(), nullable=False),
        sa.Column("encrypted_schema", sa.Text(), nullable=False),
        sa.Column("encrypted_role", sa.Text(), nullable=True),
        sa.Column("query_timeout", sa.Integer(), nullable=False),
        sa.Column("max_rows", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_tested_at", sa.DateTime(), nullable=True),
        sa.Column("last_test_success", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_snowflake_connections_user_id"),
        "snowflake_connections",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(
        op.f("ix_snowflake_connections_user_id"), table_name="snowflake_connections"
    )

    # Drop table
    op.drop_table("snowflake_connections")
