from flask import Blueprint, request, jsonify
from app import db
from app.models import Content, ArticleTranslation, Embedding

search_bp = Blueprint('search', __name__)


@search_bp.route('', methods=['GET'])
def search():
    """
    Search content (keyword and semantic)
    GET /api/search?q=python&lang=en&type=article&tags=backend&page=1
    """
    query_text = request.args.get('q', '')
    language = request.args.get('lang', 'en')
    content_type = request.args.get('type')
    tags_param = request.args.get('tags')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 20)), 100)

    if not query_text:
        return jsonify({'error': 'Query parameter q is required'}), 400

    # For now, implement simple keyword search
    # TODO: Implement semantic search with embeddings

    # Build query
    query = Content.query

    if content_type:
        query = query.filter_by(type=content_type)

    # For articles, search in translations
    if not content_type or content_type == 'article':
        query = query.join(ArticleTranslation).filter(
            db.or_(
                ArticleTranslation.title.ilike(f'%{query_text}%'),
                ArticleTranslation.markdown.ilike(f'%{query_text}%')
            ),
            ArticleTranslation.language == language
        )

    # TODO: Add tag filtering
    if tags_param:
        tag_keys = tags_param.split(',')
        # Implement tag filtering

    # Paginate
    pagination = query.distinct().order_by(Content.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'items': [c.to_dict(include_translations=True, language=language) for c in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        'query': query_text
    }), 200


@search_bp.route('/semantic', methods=['POST'])
def semantic_search():
    """
    Semantic search using vector embeddings
    POST /api/search/semantic
    Body: {"query": "machine learning tutorial", "lang": "en", "limit": 10}
    """
    data = request.get_json()
    query_text = data.get('query')
    language = data.get('lang', 'en')
    limit = min(int(data.get('limit', 10)), 50)

    if not query_text:
        return jsonify({'error': 'Query is required'}), 400

    # TODO: Implement semantic search
    # 1. Generate embedding for query
    # 2. Search using pgvector similarity
    # 3. Group by content_id and rank

    return jsonify({
        'message': 'Semantic search not yet implemented',
        'items': []
    }), 200
