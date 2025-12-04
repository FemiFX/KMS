import uuid
from datetime import datetime
from app import db


class Content(db.Model):
    """
    Language-neutral identity object for all content types.
    This is the core polymorphic content table.
    """
    __tablename__ = 'content'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = db.Column(db.Enum('article', 'video', 'audio', 'publication', name='content_type'), nullable=False)
    created_by_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    visibility = db.Column(db.Enum('private', 'org', 'public', name='visibility_type'), default='private', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    created_by = db.relationship('User', back_populates='contents')
    translations = db.relationship('ArticleTranslation', back_populates='content', cascade='all, delete-orphan')
    media = db.relationship('MediaContent', back_populates='content', uselist=False, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='content_tag', back_populates='contents')

    def __repr__(self):
        return f'<Content {self.id} type={self.type}>'

    def to_dict(self, include_translations=False, language=None):
        """Serialize content to dictionary"""
        data = {
            'id': self.id,
            'type': self.type,
            'visibility': self.visibility,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'tags': [tag.to_dict() for tag in self.tags],
        }

        if self.type == 'article' and include_translations:
            if language:
                # Get specific language translation
                translation = next((t for t in self.translations if t.language == language), None)
                if translation:
                    data['translation'] = translation.to_dict()
            else:
                # Get all translations
                data['translations'] = [t.to_dict() for t in self.translations]

        elif self.type in ('video', 'audio', 'publication') and self.media:
            data['media'] = self.media.to_dict()

        return data
