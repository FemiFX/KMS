# API Examples

Quick reference for testing the KMS API endpoints.

## Health Check

```bash
curl http://localhost:5000/health
```

## Content Management

### Create Article Content

```bash
curl -X POST http://localhost:5000/api/contents \
  -H "Content-Type: application/json" \
  -d '{
    "type": "article",
    "visibility": "public",
    "translation": {
      "language": "en",
      "title": "Getting Started with Python",
      "markdown": "# Introduction\n\nPython is a versatile programming language..."
    }
  }'
```

### List All Contents

```bash
curl "http://localhost:5000/api/contents?type=article&lang=en&page=1&per_page=20"
```

### Get Specific Content

```bash
# Replace {content_id} with actual ID
curl "http://localhost:5000/api/contents/{content_id}?lang=en"
```

### Update Translation

```bash
# Replace {content_id} with actual ID
curl -X PUT http://localhost:5000/api/contents/{content_id}/translations/en \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "markdown": "# Updated Content\n\nThis is the updated markdown content..."
  }'
```

### Add New Translation

```bash
# Replace {content_id} with actual ID
curl -X POST http://localhost:5000/api/contents/{content_id}/translations \
  -H "Content-Type: application/json" \
  -d '{
    "language": "de",
    "title": "Erste Schritte mit Python",
    "markdown": "# Einführung\n\nPython ist eine vielseitige Programmiersprache..."
  }'
```

### Delete Content

```bash
# Replace {content_id} with actual ID
curl -X DELETE http://localhost:5000/api/contents/{content_id}
```

## Tags

### Create Tag

```bash
curl -X POST http://localhost:5000/api/tags \
  -H "Content-Type: application/json" \
  -d '{
    "key": "python",
    "default_label": "Python",
    "namespace": "topic",
    "color": "#3776ab"
  }'
```

### List Tags

```bash
curl "http://localhost:5000/api/tags?lang=en"
```

### Add Localized Tag Label

```bash
# Replace {tag_id} with actual ID
curl -X POST http://localhost:5000/api/tags/{tag_id}/labels \
  -H "Content-Type: application/json" \
  -d '{
    "language": "de",
    "label": "Python Programmierung"
  }'
```

### Assign Tags to Content

```bash
# Replace {content_id} and {tag_id} with actual IDs
curl -X POST http://localhost:5000/api/contents/{content_id}/tags \
  -H "Content-Type: application/json" \
  -d '{
    "tag_ids": ["{tag_id}"],
    "action": "add"
  }'
```

## Search

### Keyword Search

```bash
curl "http://localhost:5000/api/search?q=python&lang=en&type=article&page=1"
```

### Semantic Search (TODO)

```bash
curl -X POST http://localhost:5000/api/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning tutorials",
    "lang": "en",
    "limit": 10
  }'
```

## Media

### Upload Media (Placeholder - file upload via form)

```bash
curl -X POST http://localhost:5000/api/media \
  -F "file=@/path/to/video.mp4" \
  -F "kind=video" \
  -F "visibility=public" \
  -F "language=en"
```

### Get Media with Transcripts

```bash
# Replace {media_id} with actual ID
curl "http://localhost:5000/api/media/{media_id}?lang=en"
```

### Add Transcript

```bash
# Replace {media_id} with actual ID
curl -X POST http://localhost:5000/api/media/{media_id}/transcripts \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "text": "Full transcript text here...",
    "model": "whisper-large-v3",
    "is_primary": true
  }'
```

## Webhooks

### Register Webhook

```bash
curl -X POST http://localhost:5000/api/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["content.updated", "media.uploaded", "article.translation.created"]
  }'
```

### List Webhooks

```bash
curl http://localhost:5000/api/webhooks
```

### Get Webhook Delivery History

```bash
# Replace {webhook_id} with actual ID
curl "http://localhost:5000/api/webhooks/{webhook_id}/events?page=1"
```

## Testing Workflow

Here's a complete workflow to test the system:

```bash
# 1. Check health
curl http://localhost:5000/health

# 2. Create a tag
TAG_RESPONSE=$(curl -s -X POST http://localhost:5000/api/tags \
  -H "Content-Type: application/json" \
  -d '{"key": "python", "default_label": "Python", "namespace": "topic", "color": "#3776ab"}')
TAG_ID=$(echo $TAG_RESPONSE | jq -r '.id')

# 3. Create article content
CONTENT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/contents \
  -H "Content-Type: application/json" \
  -d '{
    "type": "article",
    "visibility": "public",
    "translation": {
      "language": "en",
      "title": "Python Tutorial",
      "markdown": "# Python Basics\n\nLearn Python programming..."
    }
  }')
CONTENT_ID=$(echo $CONTENT_RESPONSE | jq -r '.id')

# 4. Assign tag to content
curl -X POST http://localhost:5000/api/contents/$CONTENT_ID/tags \
  -H "Content-Type: application/json" \
  -d "{\"tag_ids\": [\"$TAG_ID\"], \"action\": \"add\"}"

# 5. Add German translation
curl -X POST http://localhost:5000/api/contents/$CONTENT_ID/translations \
  -H "Content-Type: application/json" \
  -d '{
    "language": "de",
    "title": "Python Tutorial",
    "markdown": "# Python Grundlagen\n\nLerne Python Programmierung..."
  }'

# 6. Search for content
curl "http://localhost:5000/api/search?q=python&lang=en"

# 7. List all content
curl "http://localhost:5000/api/contents?lang=en"

echo "Testing complete! Content ID: $CONTENT_ID, Tag ID: $TAG_ID"
```
