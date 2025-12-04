from flask import render_template, request
from flask_login import login_required
from datetime import datetime
from . import admin_bp


@admin_bp.route('/')
@login_required
def index():
    """Dashboard homepage with recent content and stats"""
    from app.models import Content, ArticleTranslation, MediaContent, Tag
    from app import db

    current_language = request.args.get('lang', 'en')

    # Get recent content (last 6 items)
    recent_query = db.session.query(Content).join(ArticleTranslation).filter(
        ArticleTranslation.language == current_language
    ).order_by(Content.updated_at.desc()).limit(6).all()

    recent_content = []
    for content in recent_query:
        translation = next((t for t in content.translations if t.language == current_language), None)
        if translation:
            recent_content.append({
                'id': content.id,
                'title': translation.title,
                'type': content.type,
                'space_name': 'Content',
                'created_by_initials': 'U',
                'last_edited': f"{(datetime.now() - content.updated_at).days}d ago" if content.updated_at else 'Recently'
            })

    # Calculate stats
    stats = {
        'total_content': Content.query.count(),
        'total_media': MediaContent.query.count(),
        'languages_count': db.session.query(ArticleTranslation.language).distinct().count(),
        'total_tags': Tag.query.count()
    }

    return render_template(
        'dashboard.html',
        current_language=current_language,
        current_year=datetime.now().year,
        recent_content=recent_content,
        stats=stats
    )


@admin_bp.route('/search')
@login_required
def search_page():
    """Search page with results"""
    from app.models import Content, ArticleTranslation
    from app import db

    current_language = request.args.get('lang', 'en')
    query = request.args.get('q', '').strip()
    content_type = request.args.get('type', '')
    page = int(request.args.get('page', 1))
    per_page = 20

    results = []
    total = 0

    if query:
        # Build query
        content_query = db.session.query(Content).join(ArticleTranslation)

        # Filter by content type
        if content_type:
            content_query = content_query.filter(Content.type == content_type)

        # Filter by language
        content_query = content_query.filter(ArticleTranslation.language == current_language)

        # Search in title and markdown
        search_filter = db.or_(
            ArticleTranslation.title.ilike(f'%{query}%'),
            ArticleTranslation.markdown.ilike(f'%{query}%')
        )
        content_query = content_query.filter(search_filter)

        # Get total count
        total = content_query.count()

        # Paginate
        content_items = content_query.offset((page - 1) * per_page).limit(per_page).all()

        # Format results
        for content in content_items:
            translation = next((t for t in content.translations if t.language == current_language), None)
            if translation:
                # Get excerpt from markdown
                excerpt = translation.markdown[:200] + '...' if len(translation.markdown) > 200 else translation.markdown
                excerpt = excerpt.replace('#', '').replace('*', '').strip()

                # Get tags
                tag_labels = [ct.tag.default_label for ct in content.content_tags] if hasattr(content, 'content_tags') else []

                results.append({
                    'id': content.id,
                    'type': content.type,
                    'title': translation.title,
                    'excerpt': excerpt,
                    'language': translation.language,
                    'tags': tag_labels,
                    'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else None,
                    'visibility': content.visibility
                })

    return render_template(
        'search.html',
        current_language=current_language,
        current_year=datetime.now().year,
        query=query,
        content_type=content_type,
        language=current_language,
        results=results,
        total=total,
        page=page,
        per_page=per_page
    )


@admin_bp.route('/contents')
@login_required
def contents_page():
    """Browse content page with filtering and pagination"""
    from app.models import Content, ArticleTranslation, Tag
    from app import db

    current_language = request.args.get('lang', 'en')
    content_type = request.args.get('type', '')
    visibility = request.args.get('visibility', '')
    tag_filter = request.args.get('tag', '')
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, title
    page = int(request.args.get('page', 1))
    per_page = 12

    # Build query
    content_query = db.session.query(Content).join(ArticleTranslation)

    # Filter by content type
    if content_type:
        content_query = content_query.filter(Content.type == content_type)

    # Filter by visibility
    if visibility:
        content_query = content_query.filter(Content.visibility == visibility)

    # Filter by language
    content_query = content_query.filter(ArticleTranslation.language == current_language)

    # Filter by tag
    if tag_filter:
        from app.models import ContentTag
        content_query = content_query.join(ContentTag).join(Tag).filter(
            db.or_(Tag.key == tag_filter, Tag.default_label.ilike(f'%{tag_filter}%'))
        )

    # Apply sorting
    if sort_by == 'oldest':
        content_query = content_query.order_by(Content.created_at.asc())
    elif sort_by == 'title':
        content_query = content_query.order_by(ArticleTranslation.title.asc())
    else:  # newest
        content_query = content_query.order_by(Content.created_at.desc())

    # Get total count
    total = content_query.count()

    # Paginate
    content_items = content_query.offset((page - 1) * per_page).limit(per_page).all()

    # Format results
    contents = []
    for content in content_items:
        translation = next((t for t in content.translations if t.language == current_language), None)
        if translation:
            # Get excerpt from markdown
            excerpt = translation.markdown[:150] + '...' if len(translation.markdown) > 150 else translation.markdown
            excerpt = excerpt.replace('#', '').replace('*', '').strip()

            # Get tags
            tag_labels = [ct.tag.default_label for ct in content.content_tags] if hasattr(content, 'content_tags') else []

            contents.append({
                'id': content.id,
                'type': content.type,
                'title': translation.title,
                'excerpt': excerpt,
                'language': translation.language,
                'tags': tag_labels,
                'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else None,
                'visibility': content.visibility
            })

    # Get available tags for filter
    available_tags = Tag.query.order_by(Tag.default_label).all()

    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'contents.html',
        current_language=current_language,
        current_year=datetime.now().year,
        contents=contents,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        content_type=content_type,
        visibility=visibility,
        tag_filter=tag_filter,
        sort_by=sort_by,
        available_tags=available_tags
    )


@admin_bp.route('/contents/new')
@login_required
def new_content_page():
    """Content creation page"""
    from app.models import Tag
    from app.config import Config

    current_language = request.args.get('lang', 'en')
    tags = Tag.query.order_by(Tag.default_label).all()

    return render_template(
        'create_content.html',
        current_language=current_language,
        current_year=datetime.now().year,
        tags=tags,
        supported_languages=Config.SUPPORTED_LANGUAGES
    )

@admin_bp.route('/translations')
@login_required
def translations_page():
    """Translations management page"""
    from app.models import Content, ArticleTranslation
    from app.config import Config
    from app import db

    current_language = request.args.get('lang', 'en')
    content_type = request.args.get('type', '')
    show_incomplete = request.args.get('incomplete', '') == 'true'

    # Build query for all content
    content_query = Content.query

    # Filter by type if specified
    if content_type:
        content_query = content_query.filter(Content.type == content_type)

    # Order by most recent
    content_items = content_query.order_by(Content.created_at.desc()).all()

    # Format content with translation status
    contents_data = []
    supported_languages = Config.SUPPORTED_LANGUAGES

    for content in content_items:
        # Get all translations
        translations = {t.language: t for t in content.translations}

        # Find primary translation
        primary_translation = next((t for t in content.translations if t.is_primary), None)
        if not primary_translation and content.translations:
            primary_translation = content.translations[0]

        # Calculate translation coverage
        available_languages = list(translations.keys())
        missing_languages = [lang for lang in supported_languages if lang not in available_languages]

        # Filter if showing only incomplete
        if show_incomplete and len(missing_languages) == 0:
            continue

        # Get the title (prefer primary, fallback to first available)
        title = primary_translation.title if primary_translation else "Untitled"

        contents_data.append({
            'id': content.id,
            'type': content.type,
            'title': title,
            'primary_language': primary_translation.language if primary_translation else None,
            'available_languages': available_languages,
            'missing_languages': missing_languages,
            'translation_count': len(translations),
            'total_languages': len(supported_languages),
            'completion_percentage': int((len(available_languages) / len(supported_languages)) * 100),
            'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else None
        })

    return render_template(
        'translations.html',
        current_language=current_language,
        current_year=datetime.now().year,
        contents=contents_data,
        supported_languages=supported_languages,
        content_type=content_type,
        show_incomplete=show_incomplete
    )

@admin_bp.route('/media')
@login_required
def media_page():
    """Media library page"""
    from app.models import MediaContent, Transcript
    from app import db

    current_language = request.args.get('lang', 'en')
    media_type = request.args.get('type', '')  # video, audio
    has_transcript = request.args.get('transcript', '')
    page = int(request.args.get('page', 1))
    per_page = 12

    # Build query
    media_query = MediaContent.query

    # Filter by type (kind in the model)
    if media_type:
        media_query = media_query.filter(MediaContent.kind == media_type)

    # Filter by transcript availability
    if has_transcript == 'yes':
        media_query = media_query.join(Transcript).filter(Transcript.language == current_language)
    elif has_transcript == 'no':
        # Get media without transcripts
        media_with_transcripts = db.session.query(MediaContent.id).join(Transcript).filter(Transcript.language == current_language)
        media_query = media_query.filter(~MediaContent.id.in_(media_with_transcripts))

    # Order by most recent
    media_query = media_query.order_by(MediaContent.created_at.desc())

    # Get total
    total = media_query.count()

    # Paginate
    media_items = media_query.offset((page - 1) * per_page).limit(per_page).all()

    # Format media data
    media_data = []
    for media in media_items:
        # Get transcript for current language
        transcript = next((t for t in media.transcripts if t.language == current_language), None)

        # Extract filename from object_key
        filename = media.object_key.split('/')[-1] if media.object_key else 'Unknown'

        # Calculate duration in readable format
        duration_str = None
        if media.duration_seconds:
            minutes = int(media.duration_seconds // 60)
            seconds = int(media.duration_seconds % 60)
            duration_str = f"{minutes:02d}:{seconds:02d}"

        media_data.append({
            'id': media.id,
            'filename': filename,
            'media_type': media.kind,
            'mime_type': media.mime_type,
            'duration': duration_str,
            'file_size_mb': round(media.file_size / (1024 * 1024), 2) if media.file_size else None,
            'has_transcript': transcript is not None,
            'transcript_count': len(media.transcripts),
            'storage_path': media.object_key,
            'created_at': media.created_at.strftime('%B %d, %Y') if media.created_at else None
        })

    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'media.html',
        current_language=current_language,
        current_year=datetime.now().year,
        media_items=media_data,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        media_type=media_type,
        has_transcript=has_transcript
    )

@admin_bp.route('/media/upload')
@login_required
def media_upload_page():
    """Media upload page (placeholder)"""
    current_language = request.args.get('lang', 'en')
    return render_template(
        'media_upload.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/tags')
@login_required
def tags_page():
    """Tags management page"""
    from app.models import Tag, TagLabel
    from app import db

    current_language = request.args.get('lang', 'en')
    namespace = request.args.get('namespace', '')

    # Build query
    query = Tag.query

    # Filter by namespace if provided
    if namespace:
        query = query.filter(Tag.namespace == namespace)

    # Get all tags
    tags = query.order_by(Tag.namespace, Tag.default_label).all()

    # Format tags with localized labels
    tags_data = []
    for tag in tags:
        # Get localized label
        label = tag.default_label
        tag_label = next((tl for tl in tag.labels if tl.language == current_language), None)
        if tag_label:
            label = tag_label.label

        # Count content using this tag
        content_count = len(tag.contents) if hasattr(tag, 'contents') else 0

        tags_data.append({
            'id': tag.id,
            'key': tag.key,
            'label': label,
            'default_label': tag.default_label,
            'namespace': tag.namespace,
            'color': tag.color,
            'content_count': content_count,
            'created_at': tag.created_at.strftime('%B %d, %Y') if tag.created_at else None
        })

    # Get unique namespaces for filter
    namespaces = db.session.query(Tag.namespace).distinct().order_by(Tag.namespace).all()
    namespaces = [n[0] for n in namespaces if n[0]]

    return render_template(
        'tags.html',
        current_language=current_language,
        current_year=datetime.now().year,
        tags=tags_data,
        namespaces=namespaces,
        current_namespace=namespace
    )


@admin_bp.route('/about')
def about_page():
    """About page (to be implemented)"""
    current_language = request.args.get('lang', 'en')
    return render_template(
        'about.html',
        current_language=current_language,
        current_year=datetime.now().year
    )


# NOTE: Content detail route moved to public.py
# to allow public access to content without authentication
