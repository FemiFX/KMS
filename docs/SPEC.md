Below is a **single consolidated Markdown specification file** that captures the architecture, data model, i18n strategy, editor strategy, content types, tagging, semantic search, media pipeline, and collaboration model we have developed so far.

You can drop this into your repository as `SPEC.md` or `docs/architecture.md`.

---

# Knowledge Platform Specification

*(Forking Outline’s Editor; Full Backend in Flask)*

## Overview

This specification describes a custom Knowledge Management Platform that:

* **Uses only Outline’s rich-markdown-editor** for article editing and rendering.
* Replaces **all of Outline’s backend** with a Python/Flask backend.
* Introduces **multiple content types** (articles, videos, audio, more in the future).
* Supports **i18n** for both UI and content (articles + transcripts).
* Provides **advanced tagging**, **semantic search**, **video/audio transcripts**, and **embeddings**.
* Implements optional **real-time collaboration** using Yjs/WebSockets.
* Supports **webhooks** for external system integrations.

The goal is a modern, extensible, multimodal knowledge platform with strong metadata, search, and multilingual capabilities.

---

# 1. System Architecture

## 1.1 High-Level Components

### Frontend (React)

* Uses **Outline’s rich-markdown-editor** for article editing.
* Implements:

  * Article CRUD screens.
  * Mediathek (video/audio library) with filtering.
  * Per-language variant creation and switching.
  * Tag management UI.
  * Search UI (keyword + semantic).
  * Optional Yjs client for real-time collaborative editing.

### Backend (Flask)

* Source of truth for:

  * Content items (all types)
  * Translations (article + transcript)
  * Tags
  * Media metadata
  * Embeddings
  * Search queries
  * Permissions/visibility
  * Webhooks
* Exposes REST API.

### Async Processing

* Celery/RQ workers for:

  * Video/audio transcription.
  * Embedding generation for:

    * Articles
    * Transcripts
    * Tags (optional)
  * Webhook dispatch.

### Storage

* PostgreSQL:

  * All structured data.
  * `pgvector` for embeddings.
* Object storage (S3/minio):

  * Video and audio files.
  * Thumbnails.
* Redis:

  * Celery/RQ queues.
  * Caching.

### Optional Collaboration Service

* Yjs WebSocket server (Node or Python) for multi-user live editing.
* Flask periodically snapshots synced content.

---

# 2. Content Model

The system uses a **polymorphic content model**.

## 2.1 Core Content Table

```python
Content
--------
id: UUID (PK)
type: ENUM(article, video, audio, ...)
created_by_id: UUID (FK -> User)
visibility: private | org | public
created_at
updated_at
```

This is the **language-neutral identity object** for all content.

## 2.2 Article Translations

```python
ArticleTranslation
-------------------
id: UUID (PK)
content_id: UUID (FK -> Content)
language: "en" | "de" | ...
title
slug
markdown (Outline editor source)
rendered_html (optional)
is_primary: bool

Uniqueness:
(content_id, language)
(slug, language)
```

Each article translation is a **distinct piece of editable text**.

## 2.3 Media Content (Video & Audio)

```python
MediaContent
-------------
id: UUID (PK)
content_id: UUID (FK -> Content)
kind: ENUM(video, audio)
object_key: S3/minio path
mime_type
duration_seconds
thumbnail_key
original_language
```

## 2.4 Transcript (Per Language)

```python
Transcript
-----------
id: UUID (PK)
media_id: UUID (FK -> MediaContent)
language: "en" | "de" | ...
text: full transcript
model: STT model used
is_primary: bool
created_at

Uniqueness:
(media_id, language)
```

Supports:

* Original transcript (primary)
* Additional translated transcripts

---

# 3. Tagging System

Tags are language-neutral semantic units.

## 3.1 Canonical Tags

```python
Tag
----
id: UUID (PK)
key: unique internal identifier
default_label: canonical label
namespace: topic | department | audience | ...
color (optional)
```

## 3.2 Localized Tag Labels (Optional)

```python
TagLabel
---------
id
tag_id
language
label

Uniqueness:
(tag_id, language)
```

## 3.3 Tag Assignments

```python
ContentTag
------------
content_id: UUID (FK -> Content)
tag_id: UUID (FK -> Tag)
PRIMARY KEY(content_id, tag_id)
```

Tags attach to **Content**, not translations.

---

# 4. Semantic Search Architecture

Semantic search covers:

* Article translations (per language)
* Transcripts (per language)
* Tags (optional)
* Future content types (images, datasets, etc.)

## 4.1 Embedding Table

```python
Embedding
-----------
id
owner_type: article_translation | transcript | tag
owner_id
language
model
dim
chunk_index
vector (pgvector)
created_at
```

### Owner types:

* `article_translation` → markdown chunk embeddings
* `transcript` → segmented transcript embeddings
* `tag` (optional) → tag semantic vector

## 4.2 Search Pipeline

1. Compute query embedding in user’s language (`lang`).
2. Query embeddings:

   * default: `WHERE language = :lang`
   * optional: “cross-language mode”
3. Map embedding → owner:

   * `article_translation → content_id`
   * `transcript → media_id → content_id`
4. Group and rank results by `content_id`.
5. Apply filters:

   * tags
   * content type
   * visibility
6. Return unified results.

---

# 5. Internationalization (i18n)

## 5.1 UI-layer i18n

* Frontend: i18next/react-intl.
* Backend: Flask-Babel for emails/system messages.
* Languages selectable per user.

## 5.2 Content i18n (Strategy B – “One content, many translations”)

### Articles

* Stored per language in `ArticleTranslation`.
* Fallback to primary language if translation missing.
* User-flow:

  * Create content → choose primary language.
  * Later “Add Translation” → prefill with auto-translation (optional).

### Media (Video/Audio)

* Media is not language-specific.
* Transcripts are per language.
* Primary transcript = original audio language.
* Optional translated transcripts.

### Tags

* Conceptually language-neutral.
* Optional localized labels.

### Semantic Search

* Embeddings stored with `language`.
* Default: only return same-language results.
* Optional cross-language mode when desired.

---

# 6. Outline Editor Integration

You adopt only Outline’s editor:

* React package: `rich-markdown-editor`.
* Used for **editing and displaying** articles.

## 6.1 Editing Flow

1. Fetch translation:

   * `GET /api/contents/{id}?lang=de`.
2. Render editor with `defaultValue = markdown`.
3. On change:

   * `PUT /api/contents/{id}/translations/de` with new markdown.
4. Backend:

   * Save markdown.
   * Regenerate rendered HTML (optional).
   * Enqueue “re-embed article” worker task.

## 6.2 Rendering

* Either editor in read-only mode.
* Or server-render markdown to HTML.

---

# 7. Media Pipeline (Video & Audio)

## 7.1 Upload

Frontend → `POST /api/media` (multipart):

* Flask streams to S3/minio.
* Creates `Content(type=VIDEO)` + `MediaContent`.

## 7.2 Transcription Worker

Worker:

* Downloads media.
* Runs Whisper or external STT.
* Saves `Transcript`.
* Enqueues `embed_transcript(transcript_id)`.

## 7.3 Mediathek UI

Features:

* List all media.
* Filter by tags.
* Filter by language availability (transcript languages).
* Search (semantic + keyword).
* Video player + transcript viewer.

---

# 8. Collaboration & Webhooks

## 8.1 Real-Time Collaboration (Optional)

Powered by Yjs.

### Model:

* Yjs WebSocket server handles CRDT.
* Editor integrates a Yjs provider.
* Flask persists snapshots periodically.

### Benefits:

* Google-Docs-style multi-cursor editing.
* Independent subsystem; Flask stays clean.

## 8.2 Webhooks (Outbound)

Flask emits events to external URLs:

* `content.updated`
* `article.translation.created`
* `media.uploaded`
* `media.transcribed`
* `tags.updated`

Webhook dispatcher:

* Queued (Celery).
* Retries with exponential backoff.
* Signed payloads.

---

# 9. API Surface Overview (High-Level)

## 9.1 Content

```
POST   /api/contents                              → create content (type + primary language)
GET    /api/contents?type=&tags=&q=&lang=         → list (with filters)
GET    /api/contents/{id}?lang=                   → fetch translation or language fallback
DELETE /api/contents/{id}                         → delete
```

## 9.2 Article Translations

```
POST   /api/contents/{id}/translations            → create translation
PUT    /api/contents/{id}/translations/{lang}     → update translation
```

## 9.3 Media

```
POST   /api/media                                 → upload media
GET    /api/media/{id}?lang=                      → fetch media + transcript(s)
```

## 9.4 Tags

```
GET    /api/tags                                  → list
POST   /api/tags                                  → create
PUT    /api/tags/{id}                             → update
POST   /api/contents/{id}/tags                    → assign/unassign
```

## 9.5 Search

```
GET    /api/search?q=&lang=&type=&tags=           → semantic + keyword search
```

## 9.6 Webhooks

```
POST   /api/webhooks                              → register endpoint
DELETE /api/webhooks/{id}                         → remove
```

---

# 10. Worker Tasks

| Task                                          | Purpose                       |
| --------------------------------------------- | ----------------------------- |
| `transcribe_media(media_id)`                  | Run STT on video/audio        |
| `embed_article_translation(content_id, lang)` | Embed markdown chunks         |
| `embed_transcript(transcript_id)`             | Embed transcript chunks       |
| `dispatch_webhook(event_id)`                  | Send webhook payloads         |
| `auto_tag_content(content_id)` (optional)     | Suggest tags using embeddings |

---

# 11. Future Extensions

* **Image content type**:

  * EXIF metadata extraction.
  * Vision embeddings for semantic discovery.
* **Dataset content type** (CSV, XLSX):

  * Column-level metadata.
  * Auto-generated summaries.
* **Permission model**:

  * Collections/spaces.
  * Per-language permissions.
* **Version history**:

  * Store each translation’s versions individually.

---

# 12. Summary

This system:

* Reuses only the best part of Outline: **rich-markdown-editor**.
* Replaces Outline’s Node backend entirely.
* Supports multiple content types (articles/videos/audio).
* Provides **true multilingual content** using translations per content item.
* Implements **modern semantic search** across text and media transcripts.
* Uses a **clean, future-proof data model**.
* Supports **collaboration** via Yjs/WebSockets.
* Provides external integrations via **webhooks**.

---

