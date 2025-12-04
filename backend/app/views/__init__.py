from flask import Blueprint
from flask_login import current_user

# Admin blueprint for /admin routes
admin_bp = Blueprint('admin', __name__)


@admin_bp.context_processor
def inject_nav_context():
    """
    Inject navigation sections, user info, and notifications into all admin templates.
    """
    from .nav_utils import get_nav_sections, get_user_context

    context = {
        'nav_sections': get_nav_sections(),
        'unread_count': 0,  # TODO: Implement notification count
        'notifications': []  # TODO: Implement notifications
    }

    # Add user context
    context.update(get_user_context(current_user))

    return context


from . import routes
