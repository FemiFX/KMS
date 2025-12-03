import uuid
from datetime import datetime
from app import db
from pgvector.sqlalchemy import Vector


class Embedding(db.Model):
    """
    Vector embeddings for semantic search.
    Supports articles, transcripts, and tags.
    """
    __tablename__ = 'embedding'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_type = db.Column(db.Enum('article_translation', 'transcript', 'tag', name='embedding_owner_type'), nullable=False)
    owner_id = db.Column(db.String(36), nullable=False)  # Foreign key to owner
    language = db.Column(db.String(10), nullable=False)
    model = db.Column(db.String(100), nullable=False)  # e.g., "text-embedding-3-small"
    dim = db.Column(db.Integer, nullable=False)  # Embedding dimensions
    chunk_index = db.Column(db.Integer, default=0, nullable=False)  # For chunked content
    vector = db.Column(Vector(1536))  # pgvector column - adjust dimension as needed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Indexes for efficient querying
    __table_args__ = (
        db.Index('idx_embedding_owner', 'owner_type', 'owner_id'),
        db.Index('idx_embedding_language', 'language'),
    )

    def __repr__(self):
        return f'<Embedding {self.id} type={self.owner_type}>'

    def to_dict(self):
        """Serialize to dictionary (without vector for size)"""
        return {
            'id': self.id,
            'owner_type': self.owner_type,
            'owner_id': self.owner_id,
            'language': self.language,
            'model': self.model,
            'dim': self.dim,
            'chunk_index': self.chunk_index,
            'created_at': self.created_at.isoformat(),
        }
