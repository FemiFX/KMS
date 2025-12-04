"""Add publication type to content_type enum

Revision ID: f289631eb476
Revises: 9a7da5e88c32
Create Date: 2025-12-04 16:22:08.478935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f289631eb476'
down_revision = '9a7da5e88c32'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'publication' value to content_type enum
    op.execute("ALTER TYPE content_type ADD VALUE IF NOT EXISTS 'publication'")


def downgrade():
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type and updating all references
    # For simplicity, we'll leave the enum value in place on downgrade
    pass
