"""Create user model

Revision ID: 001_create_user_model
Revises:
Create Date: 2024-12-28 14:30:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_create_user_model"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create users table with all required fields and constraints."""
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("google_id", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("picture_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("snowflake_config", sa.JSON(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )

    # Create indexes for performance
    op.create_index(op.f("ix_users_email"), "users", ["email"])
    op.create_index(op.f("ix_users_google_id"), "users", ["google_id"])

    # Add table comment
    op.execute(
        "COMMENT ON TABLE users IS 'User accounts with Google OAuth authentication and Snowflake configuration'"
    )

    # Add column comments
    op.execute("COMMENT ON COLUMN users.id IS 'Unique user identifier'")
    op.execute("COMMENT ON COLUMN users.email IS 'User email address (unique)'")
    op.execute("COMMENT ON COLUMN users.google_id IS 'Google OAuth user ID (unique)'")
    op.execute("COMMENT ON COLUMN users.name IS 'User display name'")
    op.execute("COMMENT ON COLUMN users.picture_url IS 'User profile picture URL'")
    op.execute("COMMENT ON COLUMN users.is_active IS 'Whether user account is active'")
    op.execute(
        "COMMENT ON COLUMN users.snowflake_config IS 'User Snowflake connection configuration'"
    )
    op.execute("COMMENT ON COLUMN users.created_at IS 'Record creation timestamp'")
    op.execute("COMMENT ON COLUMN users.updated_at IS 'Record last update timestamp'")


def downgrade() -> None:
    """Drop users table and all related objects."""
    op.drop_index(op.f("ix_users_google_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
