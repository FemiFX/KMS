"""add article translation versions

Revision ID: 7d4a2b8c4c51
Revises: 1bb1c1c08960
Create Date: 2025-12-04 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d4a2b8c4c51'
down_revision = '1bb1c1c08960'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'article_translation_version',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('translation_id', sa.String(length=36), nullable=False),
        sa.Column('content_id', sa.String(length=36), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('markdown', sa.Text(), nullable=False),
        sa.Column('rendered_html', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by_id', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id']),
        sa.ForeignKeyConstraint(['translation_id'], ['article_translation.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('translation_id', 'version_number', name='uq_translation_version_number')
    )
    op.create_index('idx_article_translation_version_translation', 'article_translation_version', ['translation_id'], unique=False)


def downgrade():
    op.drop_index('idx_article_translation_version_translation', table_name='article_translation_version')
    op.drop_table('article_translation_version')
