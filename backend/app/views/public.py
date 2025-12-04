from flask import Blueprint, render_template, request
from datetime import datetime

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    """Public homepage"""
    current_language = request.args.get('lang', 'en')

    return render_template(
        'public_home.html',
        current_language=current_language,
        current_year=datetime.now().year
    )


@public_bp.route('/contents/<content_id>')
def content_detail(content_id):
    """Display individual content item - publicly accessible"""
    from app.models import Content, ArticleTranslation
    from app.utils import render_markdown
    from app import db

    current_language = request.args.get('lang', 'en')

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
        return "Content not found", 404

    # Get available languages
    available_languages = [t.language for t in content.translations]

    # Get tags
    tag_labels = [ct.tag.default_label for ct in content.content_tags] if hasattr(content, 'content_tags') else []

    # Render markdown to HTML
    markdown_html = render_markdown(translation.markdown)

    # Prepare content data
    content_data = {
        'id': content.id,
        'type': content.type,
        'title': translation.title,
        'markdown': translation.markdown,
        'markdown_html': markdown_html,
        'language': translation.language,
        'created_at': content.created_at.strftime('%B %d, %Y') if content.created_at else None,
        'visibility': content.visibility,
        'tags': tag_labels
    }

    return render_template(
        'content_detail.html',
        current_language=current_language,
        current_year=datetime.now().year,
        content=content_data,
        available_languages=available_languages
    )


@public_bp.route('/search')
def search_page():
    """Public search page with results (no authentication)"""
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
