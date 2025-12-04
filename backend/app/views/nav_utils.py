from flask import request


def get_nav_sections():
    """
    Generate navigation sections for the admin sidebar based on current endpoint.
    Returns a list of navigation sections with active states.
    """
    endpoint = request.endpoint or ''

    # Determine which sections and children are active
    is_dashboard = endpoint == 'admin.index'
    is_search = endpoint == 'admin.search_page'
    is_contents = endpoint in ['admin.contents_page', 'admin.new_content_page']
    is_contents_list = endpoint == 'admin.contents_page'
    is_contents_new = endpoint == 'admin.new_content_page'
    is_media = endpoint in ['admin.media_page', 'admin.media_upload_page']
    is_media_list = endpoint == 'admin.media_page'
    is_media_upload = endpoint == 'admin.media_upload_page'
    is_tags = endpoint == 'admin.tags_page'
    is_translations = endpoint == 'admin.translations_page'

    nav_sections = [
        {
            "id": "dashboard",
            "label": "Dashboard",
            "url": "/admin/",
            "icon": "home",
            "single": True,
            "active": is_dashboard
        },
        {
            "id": "search",
            "label": "Suche",
            "url": "/admin/search",
            "icon": "search",
            "single": True,
            "active": is_search
        },
        {
            "id": "contents",
            "label": "Inhalte",
            "icon": "file",
            "single": False,
            "open": is_contents,
            "children": [
                {
                    "label": "Alle Inhalte",
                    "url": "/admin/contents",
                    "active": is_contents_list
                },
                {
                    "label": "Neuer Artikel",
                    "url": "/admin/contents/new",
                    "active": is_contents_new
                }
            ]
        },
        {
            "id": "media",
            "label": "Medien",
            "icon": "photo",
            "single": False,
            "open": is_media,
            "children": [
                {
                    "label": "Alle Medien",
                    "url": "/admin/media",
                    "active": is_media_list
                },
                {
                    "label": "Hochladen",
                    "url": "/admin/media/upload",
                    "active": is_media_upload
                }
            ]
        },
        {
            "id": "tags",
            "label": "Tags",
            "url": "/admin/tags",
            "icon": "tag",
            "single": True,
            "active": is_tags
        },
        {
            "id": "translations",
            "label": "Übersetzungen",
            "url": "/admin/translations",
            "icon": "language",
            "single": True,
            "active": is_translations
        }
    ]

    return nav_sections


def get_user_context(current_user):
    """
    Generate user context for the header user menu.
    """
    if hasattr(current_user, 'email') and current_user.is_authenticated:
        email = current_user.email
        # Generate initials from email
        initials = email[0].upper() if email else 'U'
        return {
            'user_initials': initials,
            'user_name': email,
            'user_role': 'Admin'
        }
    else:
        return {
            'user_initials': 'U',
            'user_name': 'User',
            'user_role': 'Admin'
        }
