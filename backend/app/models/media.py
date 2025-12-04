import uuid
from datetime import datetime
from app import db


class MediaContent(db.Model):
    """
    Video, audio, and publication content metadata.
    Actual files stored in S3/MinIO.
    """
    __tablename__ = 'media_content'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = db.Column(db.String(36), db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False, unique=True)
    kind = db.Column(db.Enum('video', 'audio', 'publication', name='media_kind'), nullable=False)
    object_key = db.Column(db.String(500), nullable=False)  # S3/MinIO path
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.BigInteger)  # bytes
    duration_seconds = db.Column(db.Float)
    thumbnail_key = db.Column(db.String(500))
    original_language = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    content = db.relationship('Content', back_populates='media')
    transcripts = db.relationship('Transcript', back_populates='media', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<MediaContent {self.id} kind={self.kind}>'

    def to_dict(self, include_transcripts=False):
        """Serialize to dictionary"""
        data = {
            'id': self.id,
            'content_id': self.content_id,
            'kind': self.kind,
            'object_key': self.object_key,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'duration_seconds': self.duration_seconds,
            'thumbnail_key': self.thumbnail_key,
            'original_language': self.original_language,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

        if include_transcripts:
            data['transcripts'] = [t.to_dict() for t in self.transcripts]

        return data


class Transcript(db.Model):
    """
    Per-language transcript for media content.
    Supports original and translated transcripts.
    """
    __tablename__ = 'transcript'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    media_id = db.Column(db.String(36), db.ForeignKey('media_content.id', ondelete='CASCADE'), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    text = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(100))  # STT model used (e.g., "whisper-large-v3")
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    media = db.relationship('MediaContent', back_populates='transcripts')
    embeddings = db.relationship('Embedding',
                                foreign_keys='Embedding.owner_id',
                                primaryjoin='and_(Transcript.id==Embedding.owner_id, Embedding.owner_type=="transcript")',
                                cascade='all, delete-orphan',
                                overlaps='embeddings')

    # Constraints
    __table_args__ = (
        db.UniqueConstraint('media_id', 'language', name='uq_media_language'),
        db.Index('idx_transcript_language', 'language'),
    )

    def __repr__(self):
        return f'<Transcript {self.id} lang={self.language}>'

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'media_id': self.media_id,
            'language': self.language,
            'text': self.text,
            'model': self.model,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
