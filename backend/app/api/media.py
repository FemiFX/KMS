from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Content, MediaContent, Transcript, User, ArticleTranslation, Tag
from app.utils.api_access import enforce_read_only_in_public_mode
from flask_login import current_user
import os
import uuid
import json

media_bp = Blueprint('media', __name__)


@media_bp.before_request
def _protect_public_mode():
    enforce_read_only_in_public_mode()


@media_bp.route('', methods=['POST'])
def upload_media():
    """
    Upload media (video or audio)
    POST /api/media
    Multipart form with file, title, summary, tags, etc.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    kind = request.form.get('kind', 'video')  # video or audio
    visibility = request.form.get('visibility', 'private')
    title = request.form.get('title', '')
    summary = request.form.get('summary', '')
    language = request.form.get('language', 'de')
    transcript_text = request.form.get('transcript', '')
    auto_transcript = request.form.get('auto_transcript', 'false').lower() == 'true'

    if not file.filename:
        return jsonify({'error': 'Empty filename'}), 400

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    if not summary:
        return jsonify({'error': 'Summary is required'}), 400

    # Validate file type
    allowed_video = {'mp4', 'webm', 'mov', 'avi', 'mkv'}
    allowed_audio = {'mp3', 'wav', 'ogg', 'm4a', 'flac'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

    if kind == 'video' and file_ext not in allowed_video:
        return jsonify({'error': f'Invalid video format. Allowed: {", ".join(allowed_video)}'}), 400
    elif kind == 'audio' and file_ext not in allowed_audio:
        return jsonify({'error': f'Invalid audio format. Allowed: {", ".join(allowed_audio)}'}), 400

    # Get current user
    user = current_user if current_user.is_authenticated else User.query.first()
    if not user:
        return jsonify({'error': 'No user available'}), 500

    try:
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{unique_id}_{original_filename}"

        # Create upload directory
        upload_dir = os.path.join(current_app.static_folder, 'uploads', kind + 's')
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        # Get file size
        file_size = os.path.getsize(filepath)

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
            object_key=f'/static/uploads/{kind}s/{filename}',
            mime_type=file.content_type,
            original_language=language,
            file_size=file_size
        )
        db.session.add(media)
        db.session.flush()

        # Create translation
        translation = ArticleTranslation(
            content_id=content.id,
            language=language,
            title=title,
            markdown=summary,
            is_primary=True
        )
        translation.generate_slug()
        db.session.add(translation)

        # Handle tags
        tags_json = request.form.get('tags', '[]')
        try:
            tags_data = json.loads(tags_json)
            for tag_data in tags_data:
                if isinstance(tag_data, dict):
                    tag_key = tag_data.get('key')
                    tag_label = tag_data.get('label', tag_key)
                else:
                    tag_key = tag_data
                    tag_label = tag_data

                # Get or create tag
                tag = Tag.query.filter_by(key=tag_key).first()
                if not tag:
                    tag = Tag(key=tag_key, default_label=tag_label)
                    db.session.add(tag)
                    db.session.flush()

                if tag not in content.tags:
                    content.tags.append(tag)
        except json.JSONDecodeError:
            pass  # Ignore tag errors

        # Handle transcript
        if transcript_text:
            transcript = Transcript(
                media_id=media.id,
                language=language,
                text=transcript_text,
                is_primary=True
            )
            db.session.add(transcript)

        db.session.commit()

        # TODO: If auto_transcript is True, enqueue transcription task

        return jsonify({
            'message': 'Media uploaded successfully',
            'content_id': content.id,
            'media_id': media.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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
