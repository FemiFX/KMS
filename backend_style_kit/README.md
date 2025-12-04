# Backend Style Kit (Admin)

This folder packages the admin layout, sidebar, header, notifications, flash messages, and Tailwind theme from the Black Trans+ Fund project so you can drop them into a new codebase.

## Contents
- `templates/backend/base_admin.html` – main layout with sidebar, header, notification dropdown, theme toggle, and embedded JS.
- `templates/backend/partials/flash_messages.html` – flash/alert rendering.
- `static/src/tailwind.css` – Tailwind source.
- `static/css/tailwind.css` – prebuilt CSS output.
- `tailwind.config.js` – theme (colors, fonts, dark mode config).

## How to integrate
1) Copy `templates/backend` and `static` from this kit into the new project.
2) Ensure your base template loads the compiled CSS and Font Awesome:
   ```html
   <link rel="stylesheet" href="{{ url_for('static', filename='css/tailwind.css') }}">
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
   ```
   If you want hosted fonts, add Google Fonts for Inter/Outfit or self-host them in `static/`.
3) Render pages by extending `templates/backend/base_admin.html` and filling blocks:
   ```jinja
   {% extends 'backend/base_admin.html' %}
   {% block title %}Dashboard{% endblock %}
   {% block page_title %}Dashboard{% endblock %}
   {% block page_subtitle %}Backend{% endblock %}
   {% block content %}...{% endblock %}
   ```
4) Provide template context variables (see below) and include a CSRF meta tag in `<head>`:
   ```html
   <meta name="csrf-token" content="{{ csrf_token() }}">
   ```

## Expected context data
- `nav_sections`: list of sections. Each section:
  - `single` (bool) for single-link vs expandable.
  - `label`, `url`, `icon` (one of `home, table, users, credit-card, user, settings` → mapped to Font Awesome in the macro).
  - `active` (bool) to highlight.
  - `open` (bool) to expand submenus.
  - `children` (list) if not single; each child has `label`, `url`, `active`.
- `user_initials`, `user_name`, `user_role`: shown in the header user menu.
- Notifications:
  - `unread_count`: number for the badge.
  - `notifications`: list with fields `id`, `title`, `message`, `time_ago`, optional `link`, and `status.value` in `{'unread','read'}`.
- Flash messages: categories `success`, `danger`, `warning`, anything else defaults to neutral styling.

## Notification endpoints expected by the JS
- `POST /admin/notifications/mark-read/<id>`
- `POST /admin/notifications/mark-all-read`
Both should return 200 OK. The JS sends `Content-Type: application/json` and `X-CSRFToken` using the meta tag above.

## Dark mode behavior
- `darkMode: 'class'` in Tailwind; JS toggles `dark` on `<html>` and stores preference in `localStorage` (`theme` key).
- The palette is defined in `tailwind.config.js` (primary indigo, cocoa, skyblue, rosequartz, goldamber, teal, ivory).

## Tailwind build setup
- Dev dependencies needed: `tailwindcss@^3`, `postcss`, `autoprefixer`.
- Example `package.json` scripts to add/merge:
  ```json
  {
    "scripts": {
      "build:css": "TAILWIND_DISABLE_OXIDE=1 node node_modules/tailwindcss/lib/cli.js -c tailwind.config.js -i ./static/src/tailwind.css -o ./static/css/tailwind.css --minify",
      "dev:css": "TAILWIND_DISABLE_OXIDE=1 node node_modules/tailwindcss/lib/cli.js -c tailwind.config.js -i ./static/src/tailwind.css -o ./static/css/tailwind.css --watch"
    },
    "devDependencies": {
      "tailwindcss": "^3.4.15",
      "postcss": "^8.5.6",
      "autoprefixer": "^10.4.22"
    }
  }
  ```
- First-time setup: `npm install` (or `npm install -D tailwindcss postcss autoprefixer`), then `npm run build:css` to regenerate `static/css/tailwind.css` after edits.

## Quick sample (Python/Flask style)
```python
nav_sections = [
    {"id": "dashboard", "label": "Dashboard", "url": "/admin", "icon": "home", "single": True, "active": True},
    {"id": "users", "label": "Users", "icon": "users", "single": False, "open": True, "children": [
        {"label": "All users", "url": "/admin/users", "active": False},
        {"label": "Invitations", "url": "/admin/invitations", "active": False},
    ]},
]

notifications = [
    {"id": 1, "title": "New request", "message": "A form was submitted", "time_ago": "5m", "link": "/admin/requests/1", "status": type("s", (), {"value": "unread"})()},
]

return render_template(
    'backend/dashboard.html',
    nav_sections=nav_sections,
    user_initials='JD',
    user_name='Jordan Doe',
    user_role='Admin',
    unread_count=len([n for n in notifications if n["status"].value == "unread"]),
    notifications=notifications,
)
```

## Notes
- The sidebar/search box are optional; remove or replace in the template if unused.
- Keep `templates/backend/partials/flash_messages.html` included so messages render uniformly.
- If you prefer not to ship the prebuilt CSS, delete `static/css/tailwind.css` and rely on `npm run build:css`.
