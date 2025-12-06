from flask import Blueprint, render_template, request, redirect, url_for
import math
from datetime import datetime
from app.models import Content, ArticleTranslation, Tag, ContentTag
from app import db

public_bp = Blueprint('public', __name__)


def get_content_metadata(content_type):
    """Get icon, label, and gradient for content type"""
    metadata = {
        'article': {
            'icon': 'fa-file-lines',
            'label': 'Artikel',
            'gradient': 'from-emerald'
        },
        'video': {
            'icon': 'fa-video',
            'label': 'Video',
            'gradient': 'from-terracotta'
        },
        'audio': {
            'icon': 'fa-microphone',
            'label': 'Audio',
            'gradient': 'from-heritage'
        },
        'publication': {
            'icon': 'fa-book',
            'label': 'Publikation',
            'gradient': 'from-inkblue'
        }
    }
    return metadata.get(content_type, {'icon': 'fa-file', 'label': content_type.capitalize(), 'gradient': 'from-emerald'})


@public_bp.route('/')
def index():
    """Public homepage with featured content"""
    current_language = request.args.get('lang', 'de')

    # Get featured content (latest 6 items, publicly visible)
    featured_query = db.session.query(Content).join(ArticleTranslation).filter(
        ArticleTranslation.language == current_language,
        Content.visibility == 'public'
    ).order_by(Content.created_at.desc()).limit(6).all()

    featured_content = []
    for content in featured_query:
        translation = next((t for t in content.translations if t.language == current_language), None)
        if translation:
            # Get excerpt
            excerpt = translation.markdown[:150] + '...' if len(translation.markdown) > 150 else translation.markdown
            excerpt = excerpt.replace('#', '').replace('*', '').strip()

            # Get tags
            tag_labels = [tag.default_label for tag in content.tags] if content.tags else []

            # Get metadata for type
            metadata = get_content_metadata(content.type)

            featured_content.append({
                'id': content.id,
                'type': content.type,
                'type_label': metadata['label'],
                'icon': metadata['icon'],
                'gradient': metadata['gradient'],
                'title': translation.title,
                'excerpt': excerpt,
                'tags': tag_labels[:3],
                'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else 'Kürzlich'
            })

    return render_template(
        'public_home.html',
        current_language=current_language,
        current_year=datetime.now().year,
        featured_content=featured_content
    )


def _get_content_data(content_id, current_language):
    """Helper function to fetch and prepare content data"""
    from app.utils import render_markdown
    from app.models import MediaContent

    # Get content
    content = Content.query.get_or_404(content_id)

    # Get translation for requested language
    translation = next(
        (t for t in content.translations if t.language == current_language),
        None
    )

    # Fallback to primary translation if requested language not available
    if not translation:
        translation = next(
            (t for t in content.translations if t.is_primary),
            content.translations[0] if content.translations else None
        )

    if not translation:
        return None, None, None

    # Get available languages
    available_languages = [t.language for t in content.translations]

    # Get tags
    tag_labels = [tag.default_label for tag in content.tags] if content.tags else []

    # Render markdown to HTML
    markdown_html = render_markdown(translation.markdown)

    # Check if there's associated media
    media_content = MediaContent.query.filter_by(content_id=content.id).first()

    # Prepare content data
    word_count = len(translation.markdown.split()) if translation and translation.markdown else 0
    read_time_minutes = max(1, math.ceil(word_count / 200)) if word_count else 0
    content_data = {
        'id': content.id,
        'type': content.type,
        'title': translation.title,
        'markdown': translation.markdown,
        'markdown_html': markdown_html,
        'language': translation.language,
        'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else None,
        'visibility': content.visibility,
        'tags': tag_labels,
        'media_content': media_content,
        'read_time_minutes': read_time_minutes
    }

    return content, content_data, available_languages


@public_bp.route('/contents/<content_id>')
def content_detail(content_id):
    """Legacy route - redirects to type-specific route"""
    content = Content.query.get_or_404(content_id)
    current_language = request.args.get('lang', 'de')

    # Redirect to type-specific route
    route_map = {
        'article': 'public.article_detail',
        'publication': 'public.publication_detail',
        'video': 'public.video_detail',
        'audio': 'public.audio_detail'
    }

    route_name = route_map.get(content.type, 'public.article_detail')
    return redirect(url_for(route_name, content_id=content_id, lang=current_language))


@public_bp.route('/contents/article/<content_id>')
def article_detail(content_id):
    """Display article content"""
    current_language = request.args.get('lang', 'de')
    content, content_data, available_languages = _get_content_data(content_id, current_language)

    if not content_data:
        return "Content not found", 404

    # Verify it's actually an article
    if content.type != 'article':
        route_map = {
            'publication': 'public.publication_detail',
            'video': 'public.video_detail',
            'audio': 'public.audio_detail'
        }
        return redirect(url_for(route_map.get(content.type, 'public.article_detail'), content_id=content_id, lang=current_language))

    return render_template(
        'content_article.html',
        current_language=current_language,
        current_year=datetime.now().year,
        content=content_data,
        available_languages=available_languages
    )


@public_bp.route('/contents/publication/<content_id>')
def publication_detail(content_id):
    """Display publication content"""
    current_language = request.args.get('lang', 'de')
    content, content_data, available_languages = _get_content_data(content_id, current_language)

    if not content_data:
        return "Content not found", 404

    # Verify it's actually a publication
    if content.type != 'publication':
        route_map = {
            'article': 'public.article_detail',
            'video': 'public.video_detail',
            'audio': 'public.audio_detail'
        }
        return redirect(url_for(route_map.get(content.type, 'public.publication_detail'), content_id=content_id, lang=current_language))

    return render_template(
        'content_publication.html',
        current_language=current_language,
        current_year=datetime.now().year,
        content=content_data,
        available_languages=available_languages
    )


@public_bp.route('/contents/video/<content_id>')
def video_detail(content_id):
    """Display video content"""
    current_language = request.args.get('lang', 'de')
    content, content_data, available_languages = _get_content_data(content_id, current_language)

    if not content_data:
        return "Content not found", 404

    # Verify it's actually a video
    if content.type != 'video':
        route_map = {
            'article': 'public.article_detail',
            'publication': 'public.publication_detail',
            'audio': 'public.audio_detail'
        }
        return redirect(url_for(route_map.get(content.type, 'public.video_detail'), content_id=content_id, lang=current_language))

    return render_template(
        'content_video.html',
        current_language=current_language,
        current_year=datetime.now().year,
        content=content_data,
        available_languages=available_languages
    )


@public_bp.route('/contents/audio/<content_id>')
def audio_detail(content_id):
    """Display audio content"""
    current_language = request.args.get('lang', 'de')
    content, content_data, available_languages = _get_content_data(content_id, current_language)

    if not content_data:
        return "Content not found", 404

    # Verify it's actually audio
    if content.type != 'audio':
        route_map = {
            'article': 'public.article_detail',
            'publication': 'public.publication_detail',
            'video': 'public.video_detail'
        }
        return redirect(url_for(route_map.get(content.type, 'public.audio_detail'), content_id=content_id, lang=current_language))

    return render_template(
        'content_audio.html',
        current_language=current_language,
        current_year=datetime.now().year,
        content=content_data,
        available_languages=available_languages
    )


@public_bp.route('/search')
def search_page():
    """Public search page with results and category breakdown"""
    current_language = request.args.get('lang', 'de')
    query = request.args.get('q', '').strip()
    content_type = request.args.get('type', '')
    tag_filters = request.args.getlist('tags')  # Get multiple tag parameters
    page = int(request.args.get('page', 1))
    per_page = 12

    results = []
    total = 0
    category_counts = {
        'article': 0,
        'video': 0,
        'audio': 0,
        'publication': 0
    }

    if query or tag_filters:
        # Base query for public content (include tags for search)
        base_query = (
            db.session.query(Content)
            .join(ArticleTranslation)
            .outerjoin(ContentTag)
            .outerjoin(Tag)
            .filter(
                ArticleTranslation.language == current_language,
                Content.visibility == 'public'
            )
        )

        # Search filter (title, markdown, tags) - only if query exists
        if query:
            search_filter = db.or_(
                ArticleTranslation.title.ilike(f'%{query}%'),
                ArticleTranslation.markdown.ilike(f'%{query}%'),
                Tag.default_label.ilike(f'%{query}%'),
                Tag.key.ilike(f'%{query}%')
            )
            base_query = base_query.filter(search_filter)

        # Filter by selected tags
        if tag_filters:
            for tag_key in tag_filters:
                base_query = base_query.filter(
                    Content.tags.any(Tag.key == tag_key)
                )

        # Get category counts for all types
        for c_type in ['article', 'video', 'audio', 'publication']:
            count_query = base_query.filter(Content.type == c_type).distinct()
            category_counts[c_type] = count_query.count()

        # Build filtered query
        content_query = base_query
        if content_type:
            content_query = content_query.filter(Content.type == content_type)

        # Get total count
        total = content_query.distinct().count()

        # Paginate
        content_items = (
            content_query
            .order_by(Content.created_at.desc())
            .distinct()
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        # Format results
        for content in content_items:
            translation = next((t for t in content.translations if t.language == current_language), None)
            if translation:
                # Get excerpt from markdown
                excerpt = translation.markdown[:150] + '...' if len(translation.markdown) > 150 else translation.markdown
                excerpt = excerpt.replace('#', '').replace('*', '').strip()

                # Get tags
                tag_labels = [tag.default_label for tag in content.tags] if content.tags else []

                # Get metadata for type
                metadata = get_content_metadata(content.type)

                results.append({
                    'id': content.id,
                    'type': content.type,
                    'type_label': metadata['label'],
                    'icon': metadata['icon'],
                    'gradient': metadata['gradient'],
                    'title': translation.title,
                    'excerpt': excerpt,
                    'language': translation.language,
                    'tags': tag_labels[:3],
                    'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else 'Kürzlich',
                    'visibility': content.visibility
                })

    return render_template(
        'public_search.html',
        current_language=current_language,
        current_year=datetime.now().year,
        query=query,
        content_type=content_type,
        language=current_language,
        results=results,
        total=total,
        page=page,
        per_page=per_page,
        category_counts=category_counts
    )
