from flask import Blueprint

# Admin blueprint for /admin routes
admin_bp = Blueprint('admin', __name__)

from . import routes
