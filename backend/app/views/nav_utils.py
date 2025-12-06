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
    is_articles = endpoint in ['admin.articles_page', 'admin.articles_new_page', 'admin.articles_drafts_page', 'admin.articles_reviews_page']
    is_articles_list = endpoint == 'admin.articles_page'
    is_articles_new = endpoint == 'admin.articles_new_page'
    is_articles_drafts = endpoint == 'admin.articles_drafts_page'
    is_articles_reviews = endpoint == 'admin.articles_reviews_page'
    is_media = endpoint in ['admin.media_page', 'admin.media_upload_page']
    is_media_list = endpoint == 'admin.media_page'
    is_media_upload = endpoint == 'admin.media_upload_page'
    is_publications = endpoint in ['admin.publications_page', 'admin.publications_upload_page']
    is_publications_list = endpoint == 'admin.publications_page'
    is_publications_upload = endpoint == 'admin.publications_upload_page'
    is_tags = endpoint in ['admin.tags_page', 'admin.tags_new_page', 'admin.tags_edit_page']
    is_tags_list = endpoint == 'admin.tags_page'
    is_tags_new = endpoint == 'admin.tags_new_page'
    is_tags_edit = endpoint == 'admin.tags_edit_page'
    is_translations = endpoint == 'admin.translations_page'
    is_users = endpoint in ['admin.users_page', 'admin.users_new_page', 'admin.users_edit_page']
    is_users_list = endpoint == 'admin.users_page'
    is_users_new = endpoint == 'admin.users_new_page'
    is_users_edit = endpoint == 'admin.users_edit_page'
    is_settings = endpoint == 'admin.settings_general_page'

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
            "id": "articles",
            "label": "Artikel",
            "icon": "document",
            "single": False,
            "open": is_articles,
            "children": [
                {
                    "label": "Alle Artikel",
                    "url": "/admin/articles",
                    "active": is_articles_list
                },
                {
                    "label": "Neuer Artikel",
                    "url": "/admin/articles/new",
                    "active": is_articles_new
                },
                {
                    "label": "Entwürfe",
                    "url": "/admin/articles/drafts",
                    "active": is_articles_drafts
                },
                {
                    "label": "Meine Reviews",
                    "url": "/admin/articles/reviews",
                    "active": is_articles_reviews
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
            "id": "publications",
            "label": "Publikationen",
            "icon": "book",
            "single": False,
            "open": is_publications,
            "children": [
                {
                    "label": "Alle Publikationen",
                    "url": "/admin/publications",
                    "active": is_publications_list
                },
                {
                    "label": "Hochladen",
                    "url": "/admin/publications/upload",
                    "active": is_publications_upload
                }
            ]
        },
        {
            "id": "tags",
            "label": "Tags",
            "icon": "tag",
            "single": False,
            "open": is_tags,
            "children": [
                {
                    "label": "Alle Tags",
                    "url": "/admin/tags",
                    "active": is_tags_list
                },
                {
                    "label": "Neuer Tag",
                    "url": "/admin/tags/new",
                    "active": is_tags_new
                }
            ]
        },
        {
            "id": "users",
            "label": "Benutzer",
            "icon": "users",
            "single": False,
            "open": is_users,
            "children": [
                {
                    "label": "Alle Benutzer",
                    "url": "/admin/users",
                    "active": is_users_list
                },
                {
                    "label": "Neuer Benutzer",
                    "url": "/admin/users/new",
                    "active": is_users_new
                }
            ]
        },
        {
            "id": "translations",
            "label": "Übersetzungen",
            "url": "/admin/translations",
            "icon": "language",
            "single": True,
            "active": is_translations
        },
        {
            "id": "settings",
            "label": "Einstellungen",
            "url": "/admin/settings/general",
            "icon": "settings",
            "single": True,
            "active": is_settings
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
