# File Viewer Kit

Inline PDF/PNG (and other common docs) preview for backend pages, including a modal viewer and download/scan guards.

## What’s inside
- `templates/backend/partials/file_viewer.html` – document list with inline thumbnails, PDF embeds, and a modal viewer (images, PDFs, DOCX via Mammoth.js). Styles/JS are bundled in the partial for drop-in use.

## Expected context
- `documents`: iterable with fields:
  - `id`
  - `original_filename`
  - `stored_filename` (for download path)
  - `document_type.value` (display label)
  - `file_size_mb`
  - `scan_status.value` in `{'clean','infected','failed','pending'}` (gates preview/download)
  - optional `is_verified`
- `download_endpoint`: Flask endpoint name that serves files (see below).
- Optional `title`: heading override (defaults to “Dokumente”).

## Download/inline endpoint (Flask example)
```python
@bp.route('/documents/<int:document_id>/download')
@login_required
def download_document(document_id):
    doc = Document.query.get_or_404(document_id)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if doc.scan_status != ScanStatus.CLEAN:
        flash('Datei kann erst nach abgeschlossenem Virenscan heruntergeladen werden.', 'warning')
        return redirect(url_for('your.detail_view', application_id=doc.application_id))
    file_path = doc.get_file_path(upload_folder)
    if not os.path.exists(file_path):
        flash('Datei wurde nicht gefunden.', 'danger')
        return redirect(url_for('your.detail_view', application_id=doc.application_id))

    inline = request.args.get('inline') == '1'
    return send_from_directory(
        upload_folder,
        doc.stored_filename,
        as_attachment=not inline,
        download_name=doc.original_filename
    )
```

## Using the partial (Jinja)
```jinja
{% set documents = application.documents %}
{% include 'backend/partials/file_viewer.html' with context %}
```
Make sure `download_endpoint` is in the context (e.g., `download_endpoint='intake.download_document'`).

## Client-side behavior
- Inline previews: images render as `<img>`; PDFs render via `<object>`.
- “Anzeigen” button opens a full-viewport modal for images/PDFs/DOCX.
- Mammoth.js CDN is included for DOCX → HTML rendering; remove if not needed.

## Notes
- Relies on Tailwind palette from this project (indigo, goldamber, etc.); adjust classes to your design system if different.
- The modal uses the `dark` class on `<html>` for dark-mode styling.
- If you don’t need DOCX, delete the Mammoth.js `<script>` and the DOCX branch in the JS.
