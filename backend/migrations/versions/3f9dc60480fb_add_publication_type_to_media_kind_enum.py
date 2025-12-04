"""Add publication type to media_kind enum

Revision ID: 3f9dc60480fb
Revises: f289631eb476
Create Date: 2025-12-04 16:46:27.559966

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f9dc60480fb'
down_revision = 'f289631eb476'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'publication' value to media_kind enum
    op.execute("ALTER TYPE media_kind ADD VALUE IF NOT EXISTS 'publication'")


def downgrade():
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type and updating all references
    # For simplicity, we'll leave the enum value in place on downgrade
    pass
