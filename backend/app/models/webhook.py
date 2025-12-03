import uuid
from datetime import datetime
from app import db


class Webhook(db.Model):
    """
    Webhook endpoint registration for external integrations.
    """
    __tablename__ = 'webhook'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(255))  # For signing payloads
    events = db.Column(db.JSON, nullable=False)  # List of event types to subscribe to
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    webhook_events = db.relationship('WebhookEvent', back_populates='webhook', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Webhook {self.id} url={self.url}>'

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'events': self.events,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class WebhookEvent(db.Model):
    """
    Track webhook delivery attempts and status.
    """
    __tablename__ = 'webhook_event'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    webhook_id = db.Column(db.String(36), db.ForeignKey('webhook.id', ondelete='CASCADE'), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    status = db.Column(db.Enum('pending', 'success', 'failed', name='webhook_status'), default='pending', nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    last_attempt_at = db.Column(db.DateTime)
    response_status = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    webhook = db.relationship('Webhook', back_populates='webhook_events')

    # Indexes
    __table_args__ = (
        db.Index('idx_webhook_event_status', 'status'),
        db.Index('idx_webhook_event_type', 'event_type'),
    )

    def __repr__(self):
        return f'<WebhookEvent {self.id} type={self.event_type}>'

    def to_dict(self):
        """Serialize to dictionary"""
        return {
            'id': self.id,
            'webhook_id': self.webhook_id,
            'event_type': self.event_type,
            'status': self.status,
            'attempts': self.attempts,
            'last_attempt_at': self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            'response_status': self.response_status,
            'created_at': self.created_at.isoformat(),
        }
