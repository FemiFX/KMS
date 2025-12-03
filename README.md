# Knowledge Management System (KMS)

A modern, multilingual knowledge management platform with semantic search, media transcription, and rich markdown editing.

## Features

- **Multimodal Content**: Articles, videos, and audio
- **Multilingual Support**: Content translations and UI internationalization
- **Semantic Search**: Vector embeddings with pgvector
- **Rich Markdown Editing**: Powered by Outline's rich-markdown-editor
- **Media Transcription**: Automatic transcription with Whisper
- **Advanced Tagging**: Language-neutral tags with localized labels
- **Webhooks**: External integrations with event notifications
- **Real-time Collaboration**: Optional Yjs integration (planned)

## Tech Stack

**Backend:**
- Flask (Python web framework)
- PostgreSQL with pgvector (database + vector search)
- Redis (caching + task queue)
- Celery (async task processing)
- MinIO (S3-compatible object storage)

**Frontend (Planned):**
- React
- rich-markdown-editor (Outline's editor)
- TypeScript

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend, when implemented)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd kms
   ```

2. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL (with pgvector) on port 5432
   - Redis on port 6379
   - MinIO on ports 9000 (API) and 9001 (Console)
   - Flask API on port 5000
   - Celery worker and beat scheduler

3. **Initialize the database**
   ```bash
   docker-compose exec flask flask db init
   docker-compose exec flask flask db migrate -m "Initial migration"
   docker-compose exec flask flask db upgrade
   ```

4. **Access the services**
   - Flask API: http://localhost:5000
   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
   - PostgreSQL: localhost:5432 (kms_user/kms_password)

### API Endpoints

**Content Management:**
- `POST /api/contents` - Create content
- `GET /api/contents` - List contents
- `GET /api/contents/{id}` - Get content
- `DELETE /api/contents/{id}` - Delete content
- `POST /api/contents/{id}/translations` - Add translation
- `PUT /api/contents/{id}/translations/{lang}` - Update translation
- `POST /api/contents/{id}/tags` - Manage tags

**Media:**
- `POST /api/media` - Upload media
- `GET /api/media/{id}` - Get media with transcripts
- `POST /api/media/{id}/transcripts` - Add/update transcript

**Tags:**
- `GET /api/tags` - List tags
- `POST /api/tags` - Create tag
- `GET /api/tags/{id}` - Get tag
- `PUT /api/tags/{id}` - Update tag
- `DELETE /api/tags/{id}` - Delete tag
- `POST /api/tags/{id}/labels` - Add localized label

**Search:**
- `GET /api/search?q=query&lang=en` - Keyword search
- `POST /api/search/semantic` - Semantic search (TODO)

**Webhooks:**
- `GET /api/webhooks` - List webhooks
- `POST /api/webhooks` - Register webhook
- `GET /api/webhooks/{id}` - Get webhook
- `PUT /api/webhooks/{id}` - Update webhook
- `DELETE /api/webhooks/{id}` - Delete webhook

### Environment Variables

See `backend/.env.example` for configuration options.

## Development

### Running locally (without Docker)

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL with pgvector**
   - Install PostgreSQL 16+
   - Install pgvector extension
   - Create database: `createdb kms`

4. **Run migrations**
   ```bash
   flask db upgrade
   ```

5. **Start Flask**
   ```bash
   flask run
   ```

6. **Start Celery worker (separate terminal)**
   ```bash
   celery -A run.celery worker --loglevel=info
   ```

### Database Migrations

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## Architecture

See [docs/SPEC.md](docs/SPEC.md) for detailed architecture specification.

### Data Model

- **Content**: Language-neutral content identity (polymorphic)
- **ArticleTranslation**: Per-language article text
- **MediaContent**: Video/audio metadata and files
- **Transcript**: Per-language media transcripts
- **Tag**: Language-neutral semantic tags
- **TagLabel**: Localized tag labels
- **Embedding**: Vector embeddings for semantic search
- **Webhook**: External integration endpoints
- **User**: Authentication and content ownership

## TODO

- [ ] Implement embedding generation with OpenAI
- [ ] Implement semantic search with pgvector
- [ ] Set up media transcription with Whisper
- [ ] Implement object storage integration (MinIO/S3)
- [ ] Add authentication/authorization with JWT
- [ ] Build React frontend with rich-markdown-editor
- [ ] Add real-time collaboration with Yjs
- [ ] Implement auto-tagging with LLMs
- [ ] Add comprehensive tests
- [ ] Set up CI/CD pipeline

## License

MIT
