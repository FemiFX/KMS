from flask import render_template, request, flash, redirect, url_for, current_app
from werkzeug.routing import BuildError
from flask_login import login_required
from datetime import datetime
from . import admin_bp


@admin_bp.route('/')
@login_required
def index():
    """Dashboard homepage with recent content and stats"""
    from app.models import Content, ArticleTranslation, MediaContent, Tag
    from app import db

    current_language = request.args.get('lang', 'de')

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
    from app.models import Content, ArticleTranslation, Tag, ContentTag
    from app import db

    current_language = request.args.get('lang', 'de')
    query = request.args.get('q', '').strip()
    content_type = request.args.get('type', '')
    tag_filter = request.args.get('tag', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 20

    results = []
    total = 0

    if query or tag_filter:
        # Build query
        content_query = db.session.query(Content).join(ArticleTranslation)

        # Filter by content type
        if content_type:
            content_query = content_query.filter(Content.type == content_type)

        # Filter by language
        content_query = content_query.filter(ArticleTranslation.language == current_language)

        # Filter by tag
        if tag_filter:
            content_query = content_query.join(ContentTag).join(Tag).filter(
                db.or_(
                    Tag.key == tag_filter,
                    Tag.default_label.ilike(f'%{tag_filter}%')
                )
            )

        # Search in title, markdown, or tags
        if query:
            search_filter = db.or_(
                ArticleTranslation.title.ilike(f'%{query}%'),
                ArticleTranslation.markdown.ilike(f'%{query}%'),
                Tag.default_label.ilike(f'%{query}%'),
                Tag.key.ilike(f'%{query}%')
            )
            content_query = content_query.outerjoin(ContentTag).outerjoin(Tag).filter(search_filter)

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
                tag_labels = [tag.default_label for tag in content.tags] if content.tags else []

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
        tag_filter=tag_filter,
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
    from flask import flash

    # Handle flash message from URL parameter
    flash_success = request.args.get('flash_success')
    if flash_success:
        flash(flash_success, 'success')

    current_language = request.args.get('lang', 'de')
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
            tag_labels = [tag.default_label for tag in content.tags] if content.tags else []

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

    current_language = request.args.get('lang', 'de')
    tags = Tag.query.order_by(Tag.default_label).all()

    return render_template(
        'create_content.html',
        current_language=current_language,
        current_year=datetime.now().year,
        tags=tags,
        supported_languages=Config.SUPPORTED_LANGUAGES
    )

@admin_bp.route('/articles')
@login_required
def articles_page():
    """Articles list view (filtered to type=article)"""
    from app.models import Content, ArticleTranslation, Tag
    from app import db

    current_language = request.args.get('lang', 'de')
    visibility = request.args.get('visibility', '')
    tag_filter = request.args.get('tag', '')
    sort_by = request.args.get('sort', 'newest')
    page = int(request.args.get('page', 1))
    per_page = 12

    content_query = db.session.query(Content).join(ArticleTranslation)
    content_query = content_query.filter(Content.type == 'article')
    content_query = content_query.filter(ArticleTranslation.language == current_language)

    if visibility:
        content_query = content_query.filter(Content.visibility == visibility)

    if tag_filter:
        from app.models import ContentTag
        content_query = content_query.join(ContentTag).join(Tag).filter(
            db.or_(Tag.key == tag_filter, Tag.default_label.ilike(f'%{tag_filter}%'))
        )

    if sort_by == 'oldest':
        content_query = content_query.order_by(Content.created_at.asc())
    elif sort_by == 'title':
        content_query = content_query.order_by(ArticleTranslation.title.asc())
    else:
        content_query = content_query.order_by(Content.created_at.desc())

    total = content_query.count()
    content_items = content_query.offset((page - 1) * per_page).limit(per_page).all()

    contents = []
    for content in content_items:
        translation = next((t for t in content.translations if t.language == current_language), None)
        if translation:
            excerpt = translation.markdown[:150] + '...' if len(translation.markdown) > 150 else translation.markdown
            excerpt = excerpt.replace('#', '').replace('*', '').strip()
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

    available_tags = Tag.query.order_by(Tag.default_label).all()
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
        content_type='article',
        visibility=visibility,
        tag_filter=tag_filter,
        sort_by=sort_by,
        available_tags=available_tags,
        page_title="Artikel - Verwaltungsportal",
        page_heading="Artikel verwalten",
        page_subtitle=f"{total} Artikel gefunden",
        nav_new_url='admin.articles_new_page',
        nav_new_label='Neuer Artikel'
    )

@admin_bp.route('/articles/new')
@login_required
def articles_new_page():
    """New article form (reuses content creation view)"""
    return new_content_page()

@admin_bp.route('/articles/drafts')
@login_required
def articles_drafts_page():
    """Draft articles (placeholder)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'articles_drafts.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/articles/reviews')
@login_required
def articles_reviews_page():
    """My review assignments (placeholder)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'articles_reviews.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/contents/<content_id>/edit')
@login_required
def edit_content(content_id):
    """Edit content page"""
    from app.models import Content, ArticleTranslation, Tag
    from app.config import Config

    current_language = request.args.get('lang', 'de')

    # Get the content
    content = Content.query.get_or_404(content_id)

    # Redirect non-articles to publication detail
    if content.type != 'article':
        return redirect(url_for('admin.publication_detail', content_id=content_id, lang=current_language))

    # Get translation for the requested language
    translation = next(
        (t for t in content.translations if t.language == current_language),
        None
    )

    # If no translation exists for this language, try to get the primary translation
    if not translation:
        translation = next(
            (t for t in content.translations if t.is_primary),
            content.translations[0] if content.translations else None
        )
        if translation:
            current_language = translation.language
            flash(f'Keine Übersetzung für die gewünschte Sprache gefunden. Zeige {translation.language}', 'info')

    # Get all tags
    all_tags = Tag.query.order_by(Tag.default_label).all()

    # Prepare existing tags as dictionaries for JavaScript
    existing_tags = [tag.to_dict(current_language) for tag in content.tags]

    return render_template(
        'edit_content.html',
        content=content,
        translation=translation,
        current_language=current_language,
        current_year=datetime.now().year,
        tags=all_tags,
        existing_tags=existing_tags,
        supported_languages=Config.SUPPORTED_LANGUAGES
    )

@admin_bp.route('/publications/<content_id>')
@login_required
def publication_detail(content_id):
    """View publication details in admin"""
    from app.models import Content

    current_language = request.args.get('lang', 'de')
    content = Content.query.get_or_404(content_id)
    if content.type != 'publication':
        return redirect(url_for('admin.edit_content', content_id=content_id, lang=current_language))

    return render_template(
        'publication_detail.html',
        current_language=current_language,
        current_year=datetime.now().year,
        content=content
    )

@admin_bp.route('/translations')
@login_required
def translations_page():
    """Translations management page"""
    from app.models import Content, ArticleTranslation
    from app.config import Config
    from app import db

    current_language = request.args.get('lang', 'de')
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

    current_language = request.args.get('lang', 'de')  # Default to 'de' for consistency
    media_type = request.args.get('type', '')  # video, audio
    has_transcript = request.args.get('transcript', '')
    page = int(request.args.get('page', 1))
    per_page = 12

    # Build query - only show videos and audio, not publications
    media_query = MediaContent.query.filter(MediaContent.kind.in_(['video', 'audio']))

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

        # Get tags from associated content
        tag_labels = []
        if media.content and media.content.tags:
            tag_labels = [tag.default_label for tag in media.content.tags]

        # Build public detail URL when routes are available
        detail_url = None
        if media.content_id and 'public' in current_app.blueprints:
            try:
                detail_url = url_for(f'public.{media.kind}_detail', content_id=media.content_id, lang=current_language)
            except BuildError:
                detail_url = None

        media_data.append({
            'id': media.id,
            'content_id': media.content_id,
            'filename': filename,
            'media_type': media.kind,
            'mime_type': media.mime_type,
            'duration': duration_str,
            'file_size_mb': round(media.file_size / (1024 * 1024), 2) if media.file_size else None,
            'has_transcript': transcript is not None,
            'transcript_count': len(media.transcripts),
            'storage_path': media.object_key,
            'created_at': media.created_at.strftime('%B %d, %Y') if media.created_at else None,
            'tags': tag_labels,
            'detail_url': detail_url
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
    current_language = request.args.get('lang', 'de')
    return render_template(
        'media_upload.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/publications')
@login_required
def publications_page():
    """Publications management page"""
    from app.models import Content, ArticleTranslation, MediaContent
    from app import db

    current_language = request.args.get('lang', 'de')  # Default to 'de' to match upload form
    mime_filter = request.args.get('format', '')  # PDF, DOCX, etc.
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, title
    page = int(request.args.get('page', 1))
    per_page = 12

    # Build query for publications
    publications_query = db.session.query(Content).join(MediaContent).filter(
        Content.type == 'publication',
        MediaContent.kind == 'publication'
    ).join(ArticleTranslation).filter(
        ArticleTranslation.language == current_language
    )

    # Filter by MIME type/format
    if mime_filter:
        if mime_filter.lower() == 'pdf':
            publications_query = publications_query.filter(MediaContent.mime_type == 'application/pdf')
        elif mime_filter.lower() == 'docx':
            publications_query = publications_query.filter(
                MediaContent.mime_type.in_(['application/vnd.openxmlformats-officedocument.wordprocessingml.document'])
            )

    # Apply sorting
    if sort_by == 'oldest':
        publications_query = publications_query.order_by(Content.created_at.asc())
    elif sort_by == 'title':
        publications_query = publications_query.order_by(ArticleTranslation.title.asc())
    else:  # newest
        publications_query = publications_query.order_by(Content.created_at.desc())

    # Get total count
    total = publications_query.count()

    # Paginate
    publication_items = publications_query.offset((page - 1) * per_page).limit(per_page).all()

    # Format results
    publications = []
    for content in publication_items:
        translation = next((t for t in content.translations if t.language == current_language), None)
        if translation and content.media:
            # Get excerpt from markdown
            excerpt = translation.markdown[:200] + '...' if len(translation.markdown) > 200 else translation.markdown
            excerpt = excerpt.replace('#', '').replace('*', '').strip()

            # Get tags
            tag_labels = [tag.default_label for tag in content.tags] if content.tags else []

            # Determine file format
            format_display = 'PDF'
            if content.media.mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                format_display = 'DOCX'
            elif content.media.mime_type == 'application/epub+zip':
                format_display = 'EPUB'

            publications.append({
                'id': content.id,
                'title': translation.title,
                'excerpt': excerpt,
                'language': translation.language,
                'tags': tag_labels,
                'format': format_display,
                'mime_type': content.media.mime_type,
                'file_size_mb': round(content.media.file_size / (1024 * 1024), 2) if content.media.file_size else None,
                'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else None,
                'visibility': content.visibility
            })

    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'publications.html',
        current_language=current_language,
        current_year=datetime.now().year,
        publications=publications,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
        mime_filter=mime_filter,
        sort_by=sort_by
    )

@admin_bp.route('/publications/upload', methods=['GET', 'POST'])
@login_required
def publications_upload_page():
    """Publications upload page"""
    from app.models import Content, ArticleTranslation, MediaContent, Tag, User
    from app import db
    from werkzeug.utils import secure_filename
    import os
    import uuid

    current_language = request.values.get('lang', request.args.get('lang', 'en'))

    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            pub_type = request.form.get('pub_type')
            language = request.form.get('language', 'de')
            visibility = request.form.get('visibility', 'org')
            description = request.form.get('description', '')

            # Get files
            publication_file = request.files.get('publication_file')
            thumbnail_file = request.files.get('thumbnail_file')

            # Validate required fields
            if not title or not publication_file or not pub_type:
                flash('Bitte füllen Sie alle erforderlichen Felder aus.', 'error')
                return redirect(url_for('admin.publications_upload_page', lang=current_language))

            # Validate file types
            allowed_publications = {'pdf', 'docx', 'epub'}
            pub_ext = publication_file.filename.rsplit('.', 1)[1].lower() if '.' in publication_file.filename else ''
            if pub_ext not in allowed_publications:
                flash('Ungültiger Dateityp. Erlaubt: PDF, DOCX, EPUB', 'error')
                return redirect(url_for('admin.publications_upload_page', lang=current_language))

            # Upload publication file
            original_name = secure_filename(publication_file.filename)
            unique_id = str(uuid.uuid4())[:12]
            pub_filename = f"{unique_id}_{original_name}"

            # Use Flask app's static folder path
            from flask import current_app
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'publications')
            os.makedirs(upload_dir, exist_ok=True)

            pub_filepath = os.path.join(upload_dir, pub_filename)
            publication_file.save(pub_filepath)

            # Get file size and MIME type
            file_size = os.path.getsize(pub_filepath)
            mime_types = {
                'pdf': 'application/pdf',
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'epub': 'application/epub+zip'
            }
            mime_type = mime_types.get(pub_ext, 'application/octet-stream')

            # Upload thumbnail if provided
            thumbnail_key = None
            if thumbnail_file and thumbnail_file.filename:
                thumb_ext = thumbnail_file.filename.rsplit('.', 1)[1].lower() if '.' in thumbnail_file.filename else ''
                if thumb_ext in {'png', 'jpg', 'jpeg', 'webp'}:
                    thumb_filename = f"{unique_id}_thumb.{thumb_ext}"
                    thumb_dir = os.path.join(current_app.static_folder, 'uploads', 'thumbnails')
                    os.makedirs(thumb_dir, exist_ok=True)
                    thumb_filepath = os.path.join(thumb_dir, thumb_filename)
                    thumbnail_file.save(thumb_filepath)
                    thumbnail_key = f"/static/uploads/thumbnails/{thumb_filename}"

            # Get or create user
            user = User.query.first()
            if not user:
                user = User(email='admin@example.com', name='Admin User')
                user.set_password('admin123')
                db.session.add(user)
                db.session.commit()

            # Create Content entry
            content = Content(
                type='publication',
                created_by_id=user.id,
                visibility=visibility
            )
            db.session.add(content)
            db.session.flush()

            # Create ArticleTranslation with metadata
            translation = ArticleTranslation(
                content_id=content.id,
                language=language,
                title=title,
                markdown=f"**Typ:** {pub_type}\n\n{description}" if description else f"**Typ:** {pub_type}",
                is_primary=True
            )
            translation.generate_slug()
            db.session.add(translation)

            # Create MediaContent entry
            media = MediaContent(
                content_id=content.id,
                kind='publication',
                object_key=f"/static/uploads/publications/{pub_filename}",
                mime_type=mime_type,
                file_size=file_size,
                thumbnail_key=thumbnail_key,
                original_language=language
            )
            db.session.add(media)

            # Handle tags from form (they should be submitted as JSON in the form)
            # For now, we'll parse them from hidden inputs added by JS
            tag_keys = request.form.getlist('tags[]')
            for tag_key in tag_keys:
                tag = Tag.query.filter_by(key=tag_key).first()
                if not tag:
                    # Create new tag if it doesn't exist
                    tag = Tag(
                        key=tag_key,
                        default_label=tag_key.replace('-', ' ').title()
                    )
                    db.session.add(tag)
                content.tags.append(tag)

            db.session.commit()

            flash(f'Publikation "{title}" erfolgreich hochgeladen!', 'success')
            return redirect(url_for('admin.publications_page', lang=current_language))

        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Hochladen: {str(e)}', 'error')
            return redirect(url_for('admin.publications_upload_page', lang=current_language))

    return render_template(
        'publications_upload.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/tags')
@login_required
def tags_page():
    """Tags management page"""
    from app.models import Tag, TagLabel
    from app import db

    current_language = request.args.get('lang', 'de')
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

@admin_bp.route('/tags/new')
@login_required
def tags_new_page():
    """Create a new tag form"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'tags_new.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/tags/create', methods=['POST'])
@login_required
def tags_create():
    """Create a new tag"""
    from app.models import Tag
    from app import db
    from flask import flash, redirect, url_for

    current_language = request.form.get('lang', 'en')
    key = request.form.get('key', '').strip()
    default_label = request.form.get('default_label', '').strip()
    namespace = request.form.get('namespace', '').strip() or None
    color = request.form.get('color', '').strip() or None

    # Validate required fields
    if not key or not default_label:
        flash('Schlüssel und Standard-Label sind erforderlich.', 'error')
        return redirect(url_for('admin.tags_new_page', lang=current_language))

    # Check if key already exists
    existing_tag = Tag.query.filter_by(key=key).first()
    if existing_tag:
        flash(f'Ein Tag mit dem Schlüssel "{key}" existiert bereits.', 'error')
        return redirect(url_for('admin.tags_new_page', lang=current_language))

    # Create new tag
    try:
        new_tag = Tag(
            key=key,
            default_label=default_label,
            namespace=namespace,
            color=color
        )
        db.session.add(new_tag)
        db.session.commit()

        flash(f'Tag "{default_label}" erfolgreich erstellt.', 'success')
        return redirect(url_for('admin.tags_page', lang=current_language))
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Erstellen des Tags: {str(e)}', 'error')
        return redirect(url_for('admin.tags_new_page', lang=current_language))

@admin_bp.route('/tags/<tag_id>/edit')
@login_required
def tags_edit_page(tag_id):
    """Edit an existing tag (placeholder form)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'tags_edit.html',
        current_language=current_language,
        current_year=datetime.now().year,
        tag_id=tag_id
    )

@admin_bp.route('/users')
@login_required
def users_page():
    """Users list (placeholder)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'users.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/users/new')
@login_required
def users_new_page():
    """Create a new user (placeholder form)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'users_new.html',
        current_language=current_language,
        current_year=datetime.now().year
    )

@admin_bp.route('/users/<user_id>/edit')
@login_required
def users_edit_page(user_id):
    """Edit existing user (placeholder form)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'users_edit.html',
        current_language=current_language,
        current_year=datetime.now().year,
        user_id=user_id
    )

@admin_bp.route('/settings/general')
@login_required
def settings_general_page():
    """General settings (placeholder)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'settings_general.html',
        current_language=current_language,
        current_year=datetime.now().year
    )


@admin_bp.route('/about')
def about_page():
    """About page (to be implemented)"""
    current_language = request.args.get('lang', 'de')
    return render_template(
        'about.html',
        current_language=current_language,
        current_year=datetime.now().year
    )


# NOTE: Content detail route moved to public.py
# to allow public access to content without authentication
