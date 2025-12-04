from flask import Blueprint, request, jsonify
from app import db
from app.models import Content, MediaContent, Transcript, User
from app.utils.api_access import enforce_read_only_in_public_mode

media_bp = Blueprint('media', __name__)


@media_bp.before_request
def _protect_public_mode():
    enforce_read_only_in_public_mode()


@media_bp.route('', methods=['POST'])
def upload_media():
    """
    Upload media (video or audio)
    POST /api/media
    Multipart form with file
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    kind = request.form.get('kind', 'video')  # video or audio
    visibility = request.form.get('visibility', 'private')

    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    # TODO: Validate file type
    # TODO: Upload to MinIO/S3
    # For now, return placeholder

    # Get or create user
    user = User.query.first()
    if not user:
        user = User(email='admin@example.com', name='Admin User')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()

    # Create content
    content = Content(
        type=kind,
        created_by_id=user.id,
        visibility=visibility
    )
    db.session.add(content)
    db.session.flush()

    # Create media record
    media = MediaContent(
        content_id=content.id,
        kind=kind,
        object_key=f'media/{content.id}/{file.filename}',  # Placeholder
        mime_type=file.content_type,
        original_language=request.form.get('language', 'en')
    )
    db.session.add(media)
    db.session.commit()

    # TODO: Enqueue transcription task

    return jsonify(content.to_dict(include_translations=True)), 201


@media_bp.route('/<media_id>', methods=['GET'])
def get_media(media_id):
    """
    Get media with transcripts
    GET /api/media/{id}?lang=en
    """
    language = request.args.get('lang')

    media = MediaContent.query.get_or_404(media_id)

    data = media.to_dict(include_transcripts=True)

    # Filter transcripts by language if specified
    if language and 'transcripts' in data:
        data['transcripts'] = [t for t in data['transcripts'] if t['language'] == language]

    return jsonify(data), 200


@media_bp.route('/<media_id>/transcripts', methods=['POST'])
def create_transcript(media_id):
    """
    Create or update transcript for media
    POST /api/media/{id}/transcripts
    Body: {"language": "en", "text": "...", "model": "whisper-large-v3"}
    """
    media = MediaContent.query.get_or_404(media_id)
    data = request.get_json()

    if not data.get('language') or not data.get('text'):
        return jsonify({'error': 'Language and text are required'}), 400

    # Check if transcript exists
    transcript = Transcript.query.filter_by(
        media_id=media_id,
        language=data['language']
    ).first()

    if transcript:
        # Update existing
        transcript.text = data['text']
        transcript.model = data.get('model', transcript.model)
    else:
        # Create new
        transcript = Transcript(
            media_id=media_id,
            language=data['language'],
            text=data['text'],
            model=data.get('model'),
            is_primary=data.get('is_primary', False)
        )
        db.session.add(transcript)

    db.session.commit()

    # TODO: Enqueue embedding generation task

    return jsonify(transcript.to_dict()), 201
