"""Add user table with OAuth fields

Revision ID: 001
Revises:
Create Date: 2025-07-04 15:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create user table with OAuth fields and preferences."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.Column(
            "google_id",
            sa.String(length=255),
            nullable=False,
            comment="Google OAuth user ID",
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
            comment="User email address from Google",
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
            comment="User display name from Google",
        ),
        sa.Column(
            "picture",
            sa.Text(),
            nullable=True,
            comment="User profile picture URL from Google",
        ),
        sa.Column(
            "auto_run_queries",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
            comment="Whether to auto-run queries without confirmation",
        ),
        sa.Column(
            "default_row_limit",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("500"),
            comment="Default row limit for query results",
        ),
        sa.Column(
            "default_output_format",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'table'"),
            comment="Default output format: table, natural, or both",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
            comment="Whether the user account is active",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_google_id", "users", ["google_id"])
    op.create_index("ix_users_id", "users", ["id"])


def downgrade() -> None:
    """Drop user table."""
    op.drop_index("ix_users_id", table_name="users")
    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
