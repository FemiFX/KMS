from flask import Blueprint, request, jsonify
from app import db
from app.models import Webhook, WebhookEvent
import secrets
from app.utils.api_access import enforce_read_only_in_public_mode

webhooks_bp = Blueprint('webhooks', __name__)


@webhooks_bp.before_request
def _protect_public_mode():
    enforce_read_only_in_public_mode()


@webhooks_bp.route('', methods=['GET'])
def list_webhooks():
    """
    List all registered webhooks
    GET /api/webhooks
    """
    webhooks = Webhook.query.order_by(Webhook.created_at.desc()).all()

    return jsonify({
        'webhooks': [w.to_dict() for w in webhooks]
    }), 200


@webhooks_bp.route('', methods=['POST'])
def create_webhook():
    """
    Register a new webhook
    POST /api/webhooks
    Body: {"url": "https://example.com/webhook", "events": ["content.updated", "media.uploaded"]}
    """
    data = request.get_json()

    if not data.get('url') or not data.get('events'):
        return jsonify({'error': 'URL and events are required'}), 400

    # Generate secret for signing
    secret = secrets.token_urlsafe(32)

    webhook = Webhook(
        url=data['url'],
        secret=secret,
        events=data['events'],
        is_active=data.get('is_active', True)
    )

    db.session.add(webhook)
    db.session.commit()

    response = webhook.to_dict()
    response['secret'] = secret  # Return secret once on creation

    return jsonify(response), 201


@webhooks_bp.route('/<webhook_id>', methods=['GET'])
def get_webhook(webhook_id):
    """
    Get specific webhook
    GET /api/webhooks/{id}
    """
    webhook = Webhook.query.get_or_404(webhook_id)
    return jsonify(webhook.to_dict()), 200


@webhooks_bp.route('/<webhook_id>', methods=['PUT'])
def update_webhook(webhook_id):
    """
    Update webhook
    PUT /api/webhooks/{id}
    """
    webhook = Webhook.query.get_or_404(webhook_id)
    data = request.get_json()

    if 'url' in data:
        webhook.url = data['url']

    if 'events' in data:
        webhook.events = data['events']

    if 'is_active' in data:
        webhook.is_active = data['is_active']

    db.session.commit()

    return jsonify(webhook.to_dict()), 200


@webhooks_bp.route('/<webhook_id>', methods=['DELETE'])
def delete_webhook(webhook_id):
    """
    Delete webhook
    DELETE /api/webhooks/{id}
    """
    webhook = Webhook.query.get_or_404(webhook_id)
    db.session.delete(webhook)
    db.session.commit()

    return '', 204


@webhooks_bp.route('/<webhook_id>/events', methods=['GET'])
def get_webhook_events(webhook_id):
    """
    Get webhook delivery history
    GET /api/webhooks/{id}/events?page=1
    """
    webhook = Webhook.query.get_or_404(webhook_id)

    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)

    pagination = WebhookEvent.query.filter_by(webhook_id=webhook_id)\
        .order_by(WebhookEvent.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [e.to_dict() for e in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200
