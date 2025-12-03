#!/usr/bin/env python
"""
Main entry point for the KMS Flask application.
"""
import os
from app import create_app, db, celery_app

# Create Flask app
app = create_app()

# Make celery app available
celery = celery_app


@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell"""
    from app.models import (
        Content, ArticleTranslation, MediaContent, Transcript,
        Tag, TagLabel, ContentTag, Embedding, Webhook, WebhookEvent, User
    )

    return {
        'db': db,
        'Content': Content,
        'ArticleTranslation': ArticleTranslation,
        'MediaContent': MediaContent,
        'Transcript': Transcript,
        'Tag': Tag,
        'TagLabel': TagLabel,
        'ContentTag': ContentTag,
        'Embedding': Embedding,
        'Webhook': Webhook,
        'WebhookEvent': WebhookEvent,
        'User': User,
    }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
