from app import celery_app, db
from app.models import MediaContent, Transcript


@celery_app.task(name='tasks.transcribe_media')
def transcribe_media(media_id):
    """
    Transcribe video or audio using Whisper STT.
    This is a placeholder - full implementation requires Whisper setup.
    """
    media = MediaContent.query.get(media_id)
    if not media:
        return {'error': 'Media not found'}

    try:
        # TODO: Implement actual transcription
        # 1. Download media from S3/MinIO
        # 2. Run Whisper STT
        # 3. Save transcript
        # 4. Enqueue embedding generation

        # Placeholder response
        return {
            'status': 'success',
            'media_id': media_id,
            'message': 'Transcription not yet implemented'
        }

    except Exception as e:
        return {
            'status': 'error',
            'media_id': media_id,
            'error': str(e)
        }
