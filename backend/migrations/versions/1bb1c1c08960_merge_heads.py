"""merge heads

Revision ID: 1bb1c1c08960
Revises: 3f9dc60480fb, 9858d0f8eae2
Create Date: 2025-12-04 17:06:46.817171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bb1c1c08960'
down_revision = ('3f9dc60480fb', '9858d0f8eae2')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
