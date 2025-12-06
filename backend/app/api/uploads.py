"""File upload endpoints for editor embeds."""
from flask import Blueprint, request, jsonify, current_app, url_for
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from app.utils.api_access import enforce_read_only_in_public_mode

uploads_bp = Blueprint('uploads', __name__)


@uploads_bp.before_request
def _protect_public_mode():
    enforce_read_only_in_public_mode()


# Allowed extensions
ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
ALLOWED_VIDEOS = {'mp4', 'webm', 'mov'}
ALLOWED_DOCUMENTS = {'pdf', 'doc', 'docx', 'txt', 'md'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@uploads_bp.route('/image', methods=['POST'])
def upload_image():
    """
    Upload an image for use in the editor
    POST /api/uploads/image
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename, ALLOWED_IMAGES):
        return jsonify({'error': 'Invalid file type. Allowed: ' + ', '.join(ALLOWED_IMAGES)}), 400

    try:
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'images')
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        # Return URL
        url = url_for('static', filename=f'uploads/images/{filename}')

        return jsonify({'url': url}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@uploads_bp.route('/file', methods=['POST'])
def upload_file():
    """
    Upload a file attachment for use in the editor
    POST /api/uploads/file
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    allowed_all = ALLOWED_IMAGES | ALLOWED_VIDEOS | ALLOWED_DOCUMENTS
    if not allowed_file(file.filename, allowed_all):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Generate unique filename but preserve original name info
        original_name = secure_filename(file.filename)
        ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{original_name.rsplit('.', 1)[0]}_{unique_id}.{ext}" if ext else f"{original_name}_{unique_id}"

        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'files')
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        # Return URL and metadata
        url = url_for('static', filename=f'uploads/files/{filename}')
        file_size = os.path.getsize(filepath)

        return jsonify({
            'url': url,
            'name': original_name,
            'size': file_size,
            'type': ext
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
