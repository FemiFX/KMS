import uuid
from datetime import datetime
from app import db


class Tag(db.Model):
    """
    Language-neutral semantic tags.
    Used for categorizing and filtering content.
    """
    __tablename__ = 'tag'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = db.Column(db.String(200), unique=True, nullable=False)  # Internal identifier
    default_label = db.Column(db.String(200), nullable=False)  # Canonical label
    namespace = db.Column(db.String(100))  # e.g., topic, department, audience
    color = db.Column(db.String(7))  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    labels = db.relationship('TagLabel', back_populates='tag', cascade='all, delete-orphan')
    contents = db.relationship('Content', secondary='content_tag', back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.key}>'

    def to_dict(self, language=None):
        """Serialize to dictionary"""
        data = {
            'id': self.id,
            'key': self.key,
            'default_label': self.default_label,
            'namespace': self.namespace,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

        # Include localized label if language specified
        if language:
            label = next((l for l in self.labels if l.language == language), None)
            data['label'] = label.label if label else self.default_label

        return data


class TagLabel(db.Model):
    """
    Localized tag labels for i18n support.
    """
    __tablename__ = 'tag_label'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tag_id = db.Column(db.String(36), db.ForeignKey('tag.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    label = db.Column(db.String(200), nullable=False)

    # Relationships
    tag = db.relationship('Tag', back_populates='labels')

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('tag_id', 'language', name='uq_tag_language'),
        db.Index('idx_tag_label_language', 'language'),
    )

    def __repr__(self):
        return f'<TagLabel {self.label} lang={self.language}>'

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'tag_id': self.tag_id,
            'language': self.language,
            'label': self.label,
        }


class ContentTag(db.Model):
    """
    Many-to-many relationship between Content and Tag.
    """
    __tablename__ = 'content_tag'

    content_id = db.Column(db.String(36), db.ForeignKey('content.id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.String(36), db.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<ContentTag content={self.content_id} tag={self.tag_id}>'
