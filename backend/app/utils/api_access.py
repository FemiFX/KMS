from flask import current_app, request, abort

# Methods that are always allowed regardless of mode (safe/readonly)
ALLOWED_METHODS = {'GET', 'HEAD', 'OPTIONS'}


def enforce_read_only_in_public_mode():
    """Block write operations when running in public mode or when explicitly configured."""
    method = request.method.upper()
    if method in ALLOWED_METHODS:
        return

    app_mode = current_app.config.get('APP_MODE', 'full')
    public_read_only = current_app.config.get('PUBLIC_API_READ_ONLY', False)

    if app_mode == 'public' or public_read_only:
        abort(403, description='Write operations are disabled on the public service')
