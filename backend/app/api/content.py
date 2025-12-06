from flask import Blueprint, request, jsonify
from datetime import datetime

from app import db
from app.models import (
    Content,
    ArticleTranslation,
    ArticleTranslationVersion,
    User,
    Tag,
    MediaContent,
)
from app.utils import render_markdown
from app.utils.api_access import enforce_read_only_in_public_mode
from flask_login import current_user

content_bp = Blueprint('content', __name__)


@content_bp.before_request
def _protect_public_mode():
    enforce_read_only_in_public_mode()


@content_bp.route('', methods=['POST'])
def create_content():
    """
    Create new content (article, video, or audio)
    POST /api/contents
    """
    data = request.get_json()

    # Validate required fields
    if not data.get('type'):
        return jsonify({'error': 'Content type is required'}), 400

    # TODO: Hook into real auth later. For now create or reuse a default user.
    user = User.query.first()
    if not user:
        user = User(email='admin@example.com', name='Admin User')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()

    # Create content
    content = Content(
        type=data['type'],
        created_by_id=user.id,
        visibility=data.get('visibility', 'private')
    )
    db.session.add(content)
    db.session.flush()

    # Handle article translations (multiple allowed)
    translations = data.get('translations', [])
    if not translations and data.get('translation'):
        translations = [data['translation']]
    if data['type'] == 'article':
        if not translations:
            return jsonify({'error': 'At least one translation is required for articles'}), 400

        primary_exists = any(t.get('is_primary') for t in translations)
        for idx, trans_data in enumerate(translations):
            language = trans_data.get('language')
            title = trans_data.get('title')
            markdown = trans_data.get('markdown', '')

            if not language or not title:
                return jsonify({'error': 'Translation language and title are required'}), 400

            translation = ArticleTranslation(
                content_id=content.id,
                language=language,
                title=title,
                markdown=markdown,
                is_primary=trans_data.get('is_primary', False)
            )
            # Ensure one primary translation
            if not primary_exists and idx == 0:
                translation.is_primary = True
            translation.generate_slug()
            translation.rendered_html = render_markdown(markdown)
            db.session.add(translation)
            db.session.flush()
            _snapshot_translation_version(translation, user.id if user else None)

    # Handle media creation for video/audio when metadata is provided
    if data['type'] in ('video', 'audio') and data.get('media'):
        media_data = data['media']
        media = MediaContent(
            content_id=content.id,
            kind=data['type'],
            object_key=media_data.get('object_key'),
            mime_type=media_data.get('mime_type'),
            file_size=media_data.get('file_size'),
            duration_seconds=media_data.get('duration_seconds'),
            thumbnail_key=media_data.get('thumbnail_key'),
            original_language=media_data.get('original_language')
        )
        db.session.add(media)

    # Handle tags: accept list of IDs, keys, or dicts {key, default_label, namespace, color}
    tags_payload = data.get('tags', [])
    for tag_item in tags_payload:
        tag = None

        # If provided as dict
        if isinstance(tag_item, dict):
            tag_id = tag_item.get('id')
            tag_key = tag_item.get('key')
            if tag_id:
                tag = Tag.query.get(tag_id)
            elif tag_key:
                tag = Tag.query.filter_by(key=tag_key).first()
                if not tag:
                    tag = Tag(
                        key=tag_key,
                        default_label=tag_item.get('default_label', tag_key),
                        namespace=tag_item.get('namespace'),
                        color=tag_item.get('color')
                    )
                    db.session.add(tag)
        else:
            # String input treated as key
            tag = Tag.query.filter_by(key=str(tag_item)).first()
            if not tag:
                tag = Tag(
                    key=str(tag_item),
                    default_label=str(tag_item)
                )
                db.session.add(tag)

        if tag:
            content.tags.append(tag)

    db.session.commit()

    return jsonify(content.to_dict(include_translations=True, language=request.args.get('lang'))), 201


@content_bp.route('', methods=['GET'])
def list_contents():
    """
    List contents with optional filters
    GET /api/contents?type=article&lang=en&tags=python,flask&page=1&per_page=20
    """
    # Parse query parameters
    content_type = request.args.get('type')
    language = request.args.get('lang', 'en')
    tags_param = request.args.get('tags')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)

    # Build query
    query = Content.query

    if content_type:
        query = query.filter_by(type=content_type)

    # TODO: Add tag filtering
    if tags_param:
        tag_keys = tags_param.split(',')
        # Will implement after tags are set up

    # Paginate
    pagination = query.order_by(Content.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'items': [c.to_dict(include_translations=True, language=language) for c in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@content_bp.route('/<content_id>', methods=['GET'])
def get_content(content_id):
    """
    Get specific content by ID
    GET /api/contents/{id}?lang=en
    """
    language = request.args.get('lang', 'en')

    content = Content.query.get_or_404(content_id)
    return jsonify(content.to_dict(include_translations=True, language=language)), 200


@content_bp.route('/<content_id>', methods=['PUT'])
def update_content(content_id):
    """
    Update content metadata (visibility, tags, etc.)
    PUT /api/contents/{id}
    """
    content = Content.query.get_or_404(content_id)
    data = request.get_json()

    # Update visibility if provided
    if 'visibility' in data:
        content.visibility = data['visibility']

    # Update tags if provided
    if 'tags' in data:
        # Clear existing tags
        content.tags = []

        # Add new tags
        tags_payload = data.get('tags', [])
        for tag_item in tags_payload:
            tag = None

            # If provided as dict
            if isinstance(tag_item, dict):
                tag_id = tag_item.get('id')
                tag_key = tag_item.get('key')
                if tag_id:
                    tag = Tag.query.get(tag_id)
                elif tag_key:
                    tag = Tag.query.filter_by(key=tag_key).first()
                    if not tag:
                        tag = Tag(
                            key=tag_key,
                            default_label=tag_item.get('default_label', tag_key),
                            namespace=tag_item.get('namespace'),
                            color=tag_item.get('color')
                        )
                        db.session.add(tag)
            else:
                # String input treated as key
                tag = Tag.query.filter_by(key=str(tag_item)).first()
                if not tag:
                    tag = Tag(
                        key=str(tag_item),
                        default_label=str(tag_item)
                    )
                    db.session.add(tag)

            if tag:
                content.tags.append(tag)

    content.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(content.to_dict(include_translations=True)), 200


@content_bp.route('/<content_id>', methods=['DELETE'])
def delete_content(content_id):
    """
    Delete content
    DELETE /api/contents/{id}
    """
    content = Content.query.get_or_404(content_id)
    db.session.delete(content)
    db.session.commit()

    return '', 204


@content_bp.route('/<content_id>/translations', methods=['POST'])
def create_translation(content_id):
    """
    Create a new translation for article content
    POST /api/contents/{id}/translations
    """
    content = Content.query.get_or_404(content_id)

    if content.type != 'article':
        return jsonify({'error': 'Translations only supported for articles'}), 400

    data = request.get_json()

    # Validate required fields
    if not data.get('language') or not data.get('title'):
        return jsonify({'error': 'Language and title are required'}), 400

    # Check if translation already exists
    existing = ArticleTranslation.query.filter_by(
        content_id=content_id,
        language=data['language']
    ).first()

    if existing:
        return jsonify({'error': 'Translation already exists for this language'}), 409

    translation = ArticleTranslation(
        content_id=content_id,
        language=data['language'],
        title=data['title'],
        markdown=data.get('markdown', ''),
        is_primary=data.get('is_primary', False)
    )
    translation.generate_slug()

    db.session.add(translation)
    db.session.flush()
    _snapshot_translation_version(translation, current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None)
    db.session.commit()

    # TODO: Enqueue embedding generation task

    return jsonify(translation.to_dict()), 201


@content_bp.route('/<content_id>/translations/<language>', methods=['PUT'])
def update_translation(content_id, language):
    """
    Update an existing translation
    PUT /api/contents/{id}/translations/{lang}
    """
    content = Content.query.get_or_404(content_id)

    if content.type != 'article':
        return jsonify({'error': 'Translations only supported for articles'}), 400

    translation = ArticleTranslation.query.filter_by(
        content_id=content_id,
        language=language
    ).first_or_404()

    data = request.get_json()

    # Update fields
    if 'title' in data:
        translation.title = data['title']
        translation.generate_slug()

    if 'markdown' in data:
        translation.markdown = data['markdown']
        translation.rendered_html = render_markdown(data['markdown'])

    if 'is_primary' in data:
        translation.is_primary = data['is_primary']

    translation.updated_at = datetime.utcnow()

    _snapshot_translation_version(translation, current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None)

    db.session.commit()

    # TODO: Enqueue re-embedding task

    return jsonify(translation.to_dict()), 200


@content_bp.route('/<content_id>/tags', methods=['POST'])
def manage_content_tags(content_id):
    """
    Assign or unassign tags to content
    POST /api/contents/{id}/tags
    Body: {"tag_ids": ["id1", "id2"], "action": "add" | "remove"}
    """
    content = Content.query.get_or_404(content_id)
    data = request.get_json()

    tag_ids = data.get('tag_ids', [])
    action = data.get('action', 'add')

    from app.models import Tag

    if action == 'add':
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag and tag not in content.tags:
                content.tags.append(tag)
    elif action == 'remove':
        for tag_id in tag_ids:
            tag = Tag.query.get(tag_id)
            if tag and tag in content.tags:
                content.tags.remove(tag)

    db.session.commit()

    return jsonify(content.to_dict(include_translations=True)), 200


@content_bp.route('/render_markdown', methods=['POST'])
def render_markdown_api():
    """
    Render markdown to HTML (utility for previews)
    """
    data = request.get_json() or {}
    markdown = data.get('markdown', '')
    if markdown is None:
        markdown = ''
    html = render_markdown(markdown)
    return jsonify({'rendered_html': html})


@content_bp.route('/<content_id>/translations/<language>/versions', methods=['GET'])
def list_translation_versions(content_id, language):
    """
    List versions for a translation (language-specific)
    """
    translation = ArticleTranslation.query.filter_by(content_id=content_id, language=language).first_or_404()
    versions = ArticleTranslationVersion.query.filter_by(translation_id=translation.id).order_by(ArticleTranslationVersion.version_number.desc()).all()
    return jsonify({
        "translation_id": translation.id,
        "versions": [
            {
                "id": v.id,
                "version_number": v.version_number,
                "title": v.title,
                "language": v.language,
                "created_at": v.created_at.isoformat(),
                "created_by_id": v.created_by_id,
            }
            for v in versions
        ]
    }), 200


@content_bp.route('/<content_id>/translations/<language>/versions/<version_id>', methods=['GET'])
def get_translation_version(content_id, language, version_id):
    """
    Get a specific version (for preview)
    """
    translation = ArticleTranslation.query.filter_by(content_id=content_id, language=language).first_or_404()
    version = ArticleTranslationVersion.query.filter_by(id=version_id, translation_id=translation.id).first_or_404()
    return jsonify({
        "id": version.id,
        "version_number": version.version_number,
        "title": version.title,
        "markdown": version.markdown,
        "rendered_html": version.rendered_html,
        "language": version.language,
        "created_at": version.created_at.isoformat(),
        "created_by_id": version.created_by_id,
    }), 200


@content_bp.route('/<content_id>/translations/<language>/versions/<version_id>/revert', methods=['POST'])
def revert_translation_version(content_id, language, version_id):
    """
    Revert a translation to a given version (creates a new version entry representing the reverted state)
    """
    translation = ArticleTranslation.query.filter_by(content_id=content_id, language=language).first_or_404()
    version = ArticleTranslationVersion.query.filter_by(id=version_id, translation_id=translation.id).first_or_404()

    translation.title = version.title
    translation.markdown = version.markdown
    translation.rendered_html = version.rendered_html
    translation.updated_at = datetime.utcnow()

    actor_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None
    _snapshot_translation_version(translation, actor_id)
    db.session.commit()

    return jsonify({"status": "reverted", "translation_id": translation.id, "version_applied": version.version_number}), 200


def _snapshot_translation_version(translation, user_id=None):
    """Create a version snapshot of a translation"""
    next_version = ArticleTranslationVersion.next_version_number(translation.id)
    version = ArticleTranslationVersion(
        translation_id=translation.id,
        content_id=translation.content_id,
        language=translation.language,
        version_number=next_version,
        title=translation.title,
        markdown=translation.markdown,
        rendered_html=translation.rendered_html,
        created_by_id=user_id
    )
    db.session.add(version)
    return version
