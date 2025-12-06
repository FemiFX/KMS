import uuid
from datetime import datetime
from slugify import slugify
from app import db
from sqlalchemy import func


class ArticleTranslation(db.Model):
    """
    Per-language article content.
    Each translation is a distinct piece of editable text.
    """
    __tablename__ = 'article_translation'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = db.Column(db.String(36), db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(600), nullable=False)
    markdown = db.Column(db.Text, nullable=False)
    rendered_html = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    content = db.relationship('Content', back_populates='translations')
    embeddings = db.relationship('Embedding',
                                foreign_keys='Embedding.owner_id',
                                primaryjoin='and_(ArticleTranslation.id==Embedding.owner_id, Embedding.owner_type=="article_translation")',
                                cascade='all, delete-orphan',
                                overlaps='embeddings')

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('content_id', 'language', name='uq_content_language'),
        db.UniqueConstraint('slug', 'language', name='uq_slug_language'),
        db.Index('idx_article_slug', 'slug'),
        db.Index('idx_article_language', 'language'),
    )

    def __repr__(self):
        return f'<ArticleTranslation {self.id} lang={self.language}>'

    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        if not self.slug and self.title:
            base_slug = slugify(self.title, max_length=100)
            # Ensure uniqueness
            counter = 1
            slug = base_slug
            while ArticleTranslation.query.filter_by(slug=slug, language=self.language).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'language': self.language,
            'title': self.title,
            'slug': self.slug,
            'markdown': self.markdown,
            'rendered_html': self.rendered_html,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class ArticleTranslationVersion(db.Model):
    """
    Point-in-time snapshot of an article translation for versioning/revert/preview.
    """
    __tablename__ = 'article_translation_version'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    translation_id = db.Column(db.String(36), db.ForeignKey('article_translation.id', ondelete='CASCADE'), nullable=False)
    content_id = db.Column(db.String(36), db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    markdown = db.Column(db.Text, nullable=False)
    rendered_html = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_by_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True)

    translation = db.relationship('ArticleTranslation', backref='versions')

    __table_args__ = (
        db.UniqueConstraint('translation_id', 'version_number', name='uq_translation_version_number'),
        db.Index('idx_article_translation_version_translation', 'translation_id'),
    )

    @classmethod
    def next_version_number(cls, translation_id):
        current_max = db.session.query(func.max(cls.version_number)).filter_by(translation_id=translation_id).scalar()
        return (current_max or 0) + 1
