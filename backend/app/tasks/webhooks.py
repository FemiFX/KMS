import requests
import hmac
import hashlib
import json
from datetime import datetime
from app import celery_app, db
from app.models import Webhook, WebhookEvent


@celery_app.task(name='tasks.dispatch_webhook', bind=True, max_retries=3)
def dispatch_webhook(self, webhook_id, event_type, payload):
    """
    Dispatch webhook to external endpoint with retry logic.
    Implements exponential backoff on failure.
    """
    webhook = Webhook.query.get(webhook_id)
    if not webhook or not webhook.is_active:
        return {'error': 'Webhook not found or inactive'}

    # Check if event type is subscribed
    if event_type not in webhook.events:
        return {'error': 'Event type not subscribed'}

    # Create webhook event record
    event = WebhookEvent(
        webhook_id=webhook_id,
        event_type=event_type,
        payload=payload,
        status='pending'
    )
    db.session.add(event)
    db.session.commit()

    try:
        # Prepare payload
        payload_json = json.dumps(payload)

        # Sign payload with webhook secret
        signature = None
        if webhook.secret:
            signature = hmac.new(
                webhook.secret.encode('utf-8'),
                payload_json.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

        # Send webhook
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'KMS-Webhook/1.0'
        }

        if signature:
            headers['X-Webhook-Signature'] = f'sha256={signature}'

        response = requests.post(
            webhook.url,
            data=payload_json,
            headers=headers,
            timeout=30
        )

        # Update event record
        event.status = 'success' if response.status_code < 400 else 'failed'
        event.attempts += 1
        event.last_attempt_at = datetime.utcnow()
        event.response_status = response.status_code
        event.response_body = response.text[:1000]  # Store first 1000 chars

        db.session.commit()

        if response.status_code >= 400:
            # Retry on failure
            raise self.retry(countdown=60 * (2 ** self.request.retries))

        return {
            'status': 'success',
            'webhook_id': webhook_id,
            'event_id': event.id,
            'response_status': response.status_code
        }

    except Exception as e:
        event.status = 'failed'
        event.attempts += 1
        event.last_attempt_at = datetime.utcnow()
        db.session.commit()

        # Retry on exception
        try:
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
        except:
            return {
                'status': 'error',
                'webhook_id': webhook_id,
                'event_id': event.id,
                'error': str(e)
            }
