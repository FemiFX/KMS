# Frontend Style Kit

Navigation header (with language selector, dark-mode toggle), global base layout, and homepage hero section extracted for reuse.

## Contents
- `templates/base.html` – full public layout with nav, translation dropdown (desktop/mobile), dark-mode toggle, footer, flash message JS helper.
- `templates/frontend/hero_section.html` – homepage hero (headline, CTAs, geometric art block).
- `tailwind.config.js`, `static/src/tailwind.css`, `static/css/tailwind.css` – theme tokens and compiled CSS for immediate drop-in.

## Integration
1) Copy `templates/base.html` into your project and extend it from your pages:
   ```jinja
   {% extends "base.html" %}
   {% block title %}Home{% endblock %}
   {% block content %}
     {% include "frontend/hero_section.html" %}
     <!-- page sections... -->
   {% endblock %}
   ```
2) Ensure Tailwind CSS is served (via `static/css/tailwind.css`) and that the Tailwind config is picked up by your build if you regenerate.
3) Language selector:
   - Requires `current_locale` in template context for `<html lang>`.
   - `setLanguage(lang)` updates URL query `?lang=...` and reloads; hook your backend to read it.
   - Dropdowns exist for desktop and mobile; both use `.language-option[-mobile]` buttons with `data-lang`.
4) Dark mode:
   - Toggles `dark` on `<html>` and persists `localStorage.theme` (`light|dark`).
   - Tailwind is configured with `darkMode: 'class'` and custom palette (indigo, skyblue, rosequartz, goldamber, teal, ivory).
5) Flash messages:
   - JS helpers `window.showFlashMessage(message, category, duration)` and `window.dismissFlashMessage(id)` are available; they render into `#flashMessagesContainer`.

## Tailwind build (if you regenerate CSS)
Use the same scripts from `package.json`:
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
If you don’t want to rebuild, keep `static/css/tailwind.css` as-is.

## Notes
- Fonts are loaded from Google (Inter, Outfit) in `base.html`; adjust if you need self-hosting.
- Hero artwork uses `/static/images/btf-image.svg`; replace the asset as needed.
- Navigation links/CTA URLs are placeholders; swap to your project routes.
