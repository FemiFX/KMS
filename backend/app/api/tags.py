from flask import Blueprint, request, jsonify
from app import db
from app.models import Tag, TagLabel

tags_bp = Blueprint('tags', __name__)


@tags_bp.route('', methods=['GET'])
def list_tags():
    """
    List all tags
    GET /api/tags?lang=en&namespace=topic
    """
    language = request.args.get('lang')
    namespace = request.args.get('namespace')

    query = Tag.query

    if namespace:
        query = query.filter_by(namespace=namespace)

    tags = query.order_by(Tag.default_label).all()

    return jsonify({
        'tags': [tag.to_dict(language=language) for tag in tags]
    }), 200


@tags_bp.route('', methods=['POST'])
def create_tag():
    """
    Create a new tag
    POST /api/tags
    Body: {"key": "python", "default_label": "Python", "namespace": "topic", "color": "#3776ab"}
    """
    data = request.get_json()

    if not data.get('key') or not data.get('default_label'):
        return jsonify({'error': 'Key and default_label are required'}), 400

    # Check if key already exists
    if Tag.query.filter_by(key=data['key']).first():
        return jsonify({'error': 'Tag with this key already exists'}), 409

    tag = Tag(
        key=data['key'],
        default_label=data['default_label'],
        namespace=data.get('namespace'),
        color=data.get('color')
    )

    db.session.add(tag)
    db.session.commit()

    return jsonify(tag.to_dict()), 201


@tags_bp.route('/<tag_id>', methods=['GET'])
def get_tag(tag_id):
    """
    Get specific tag
    GET /api/tags/{id}?lang=en
    """
    language = request.args.get('lang')
    tag = Tag.query.get_or_404(tag_id)

    return jsonify(tag.to_dict(language=language)), 200


@tags_bp.route('/<tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """
    Update tag
    PUT /api/tags/{id}
    """
    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json()

    if 'default_label' in data:
        tag.default_label = data['default_label']

    if 'namespace' in data:
        tag.namespace = data['namespace']

    if 'color' in data:
        tag.color = data['color']

    db.session.commit()

    return jsonify(tag.to_dict()), 200


@tags_bp.route('/<tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """
    Delete tag
    DELETE /api/tags/{id}
    """
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return '', 204


@tags_bp.route('/<tag_id>/labels', methods=['POST'])
def create_tag_label(tag_id):
    """
    Create localized label for tag
    POST /api/tags/{id}/labels
    Body: {"language": "de", "label": "Python Programmierung"}
    """
    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json()

    if not data.get('language') or not data.get('label'):
        return jsonify({'error': 'Language and label are required'}), 400

    # Check if label exists
    existing = TagLabel.query.filter_by(tag_id=tag_id, language=data['language']).first()

    if existing:
        existing.label = data['label']
        label = existing
    else:
        label = TagLabel(
            tag_id=tag_id,
            language=data['language'],
            label=data['label']
        )
        db.session.add(label)

    db.session.commit()

    return jsonify(label.to_dict()), 201
