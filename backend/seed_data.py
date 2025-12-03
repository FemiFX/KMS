#!/usr/bin/env python3
"""
Seed the database with test content for demonstration purposes.
"""
from app import create_app, db
from app.models import Content, ArticleTranslation, Tag, TagLabel, ContentTag, User
import uuid
from datetime import datetime


def seed_database():
    """Add test content to the database"""
    app = create_app()

    with app.app_context():
        print("🌱 Seeding database with test content...")

        # Create a test user first
        test_user = User.query.filter_by(email="test@kms.local").first()
        if not test_user:
            test_user = User(
                id=str(uuid.uuid4()),
                email="test@kms.local",
                name="Test User",
                preferred_language="en",
                created_at=datetime.utcnow()
            )
            test_user.set_password("testpassword")
            db.session.add(test_user)
            db.session.commit()
            print(f"  ✓ Created test user: {test_user.email}")
        else:
            print(f"  ℹ Test user already exists: {test_user.email}")

        # Create tags first
        tags_data = [
            {"key": "python", "default_label": "Python", "namespace": "topic", "color": "#3776AB"},
            {"key": "javascript", "default_label": "JavaScript", "namespace": "topic", "color": "#F7DF1E"},
            {"key": "machine-learning", "default_label": "Machine Learning", "namespace": "topic", "color": "#FF6F00"},
            {"key": "web-development", "default_label": "Web Development", "namespace": "topic", "color": "#00BCD4"},
            {"key": "tutorial", "default_label": "Tutorial", "namespace": "type", "color": "#4CAF50"},
            {"key": "guide", "default_label": "Guide", "namespace": "type", "color": "#2196F3"},
            {"key": "beginner", "default_label": "Beginner", "namespace": "level", "color": "#8BC34A"},
            {"key": "advanced", "default_label": "Advanced", "namespace": "level", "color": "#F44336"},
        ]

        tags = {}
        for tag_data in tags_data:
            tag = Tag.query.filter_by(key=tag_data["key"]).first()
            if not tag:
                tag = Tag(
                    id=str(uuid.uuid4()),
                    key=tag_data["key"],
                    default_label=tag_data["default_label"],
                    namespace=tag_data["namespace"],
                    color=tag_data["color"]
                )
                db.session.add(tag)
                print(f"  ✓ Created tag: {tag_data['default_label']}")

                # Add German labels for some tags
                if tag_data["key"] == "python":
                    label = TagLabel(id=str(uuid.uuid4()), tag_id=tag.id, language="de", label="Python Programmierung")
                    db.session.add(label)
                elif tag_data["key"] == "tutorial":
                    label = TagLabel(id=str(uuid.uuid4()), tag_id=tag.id, language="de", label="Anleitung")
                    db.session.add(label)

            tags[tag_data["key"]] = tag

        db.session.commit()

        # Sample articles with rich content
        articles = [
            {
                "type": "article",
                "visibility": "public",
                "translations": [
                    {
                        "language": "en",
                        "title": "Getting Started with Python Programming",
                        "markdown": """# Getting Started with Python Programming

Python is a versatile, high-level programming language that's perfect for beginners and powerful enough for experts. In this comprehensive guide, we'll explore the fundamentals of Python programming.

## Why Choose Python?

Python has become one of the most popular programming languages for several compelling reasons:

- **Easy to Learn**: Python's syntax is clear and intuitive, making it an excellent first language
- **Versatile**: Use Python for web development, data science, automation, AI, and more
- **Large Community**: Extensive libraries and frameworks, plus a helpful community
- **High Demand**: Python developers are in high demand across industries

## Installation

To get started, download Python from python.org and install it on your system. Make sure to add Python to your PATH during installation.

## Your First Program

The classic "Hello, World!" program in Python is beautifully simple:

\`\`\`python
print("Hello, World!")
\`\`\`

## Basic Concepts

### Variables and Data Types
Python supports various data types including integers, floats, strings, lists, and dictionaries.

### Control Flow
Learn about if statements, loops, and functions to control your program's logic.

### Next Steps
Once you master the basics, explore Python's rich ecosystem of libraries like NumPy, Pandas, and Django.
""",
                        "is_primary": True
                    },
                    {
                        "language": "de",
                        "title": "Erste Schritte mit Python Programmierung",
                        "markdown": """# Erste Schritte mit Python Programmierung

Python ist eine vielseitige, hochrangige Programmiersprache, die perfekt für Anfänger ist und leistungsstark genug für Experten. In diesem umfassenden Leitfaden werden wir die Grundlagen der Python-Programmierung erkunden.

## Warum Python wählen?

Python ist aus mehreren überzeugenden Gründen zu einer der beliebtesten Programmiersprachen geworden:

- **Einfach zu lernen**: Die Syntax von Python ist klar und intuitiv
- **Vielseitig**: Verwenden Sie Python für Webentwicklung, Data Science, Automatisierung und mehr
- **Große Community**: Umfangreiche Bibliotheken und eine hilfsbereite Community
- **Hohe Nachfrage**: Python-Entwickler sind branchenübergreifend sehr gefragt
""",
                        "is_primary": False
                    }
                ],
                "tags": ["python", "tutorial", "beginner"]
            },
            {
                "type": "article",
                "visibility": "public",
                "translations": [
                    {
                        "language": "en",
                        "title": "Introduction to Machine Learning",
                        "markdown": """# Introduction to Machine Learning

Machine Learning (ML) is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

## What is Machine Learning?

Machine learning algorithms build mathematical models based on sample data, known as training data, to make predictions or decisions without being explicitly programmed to do so.

## Types of Machine Learning

1. **Supervised Learning**: Learn from labeled training data
2. **Unsupervised Learning**: Find patterns in unlabeled data
3. **Reinforcement Learning**: Learn through trial and error

## Popular ML Libraries

- **scikit-learn**: General-purpose ML library
- **TensorFlow**: Deep learning framework by Google
- **PyTorch**: Deep learning framework preferred by researchers
- **Keras**: High-level neural networks API

## Getting Started

Start with basic concepts like linear regression and classification, then progress to more advanced topics like neural networks and deep learning.
""",
                        "is_primary": True
                    }
                ],
                "tags": ["machine-learning", "python", "tutorial"]
            },
            {
                "type": "article",
                "visibility": "public",
                "translations": [
                    {
                        "language": "en",
                        "title": "Modern JavaScript: ES6+ Features You Should Know",
                        "markdown": """# Modern JavaScript: ES6+ Features You Should Know

JavaScript has evolved significantly with ES6 (ES2015) and subsequent releases. Let's explore the most important modern JavaScript features.

## Arrow Functions

Arrow functions provide a concise syntax and lexical `this` binding:

\`\`\`javascript
const greet = (name) => `Hello, ${name}!`;
\`\`\`

## Destructuring

Extract values from arrays and objects elegantly:

\`\`\`javascript
const { name, age } = person;
const [first, second] = array;
\`\`\`

## Template Literals

Create multi-line strings and embed expressions:

\`\`\`javascript
const message = `Welcome, ${username}!
Your account status: ${status}`;
\`\`\`

## Promises and Async/Await

Handle asynchronous operations more cleanly:

\`\`\`javascript
async function fetchData() {
  const response = await fetch(url);
  const data = await response.json();
  return data;
}
\`\`\`

## Modules

Organize code with import/export:

\`\`\`javascript
export const helper = () => { /* ... */ };
import { helper } from './utils.js';
\`\`\`
""",
                        "is_primary": True
                    }
                ],
                "tags": ["javascript", "web-development", "guide"]
            },
            {
                "type": "article",
                "visibility": "public",
                "translations": [
                    {
                        "language": "en",
                        "title": "Building RESTful APIs with Flask",
                        "markdown": """# Building RESTful APIs with Flask

Flask is a lightweight Python web framework perfect for building RESTful APIs. This guide covers best practices and patterns.

## What is Flask?

Flask is a micro web framework written in Python. It's designed to be simple and extensible, making it ideal for API development.

## Setting Up

Install Flask and create a basic application:

\`\`\`python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/hello')
def hello():
    return jsonify({'message': 'Hello, World!'})
\`\`\`

## REST Principles

- **Stateless**: Each request contains all necessary information
- **Cacheable**: Responses should define themselves as cacheable or not
- **Uniform Interface**: Use standard HTTP methods (GET, POST, PUT, DELETE)

## Database Integration

Use SQLAlchemy for database operations:

\`\`\`python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
\`\`\`

## Authentication

Implement JWT tokens for secure API access.

## Best Practices

1. Use blueprints to organize your code
2. Implement proper error handling
3. Version your API (e.g., /api/v1/)
4. Use CORS for cross-origin requests
5. Document your API with OpenAPI/Swagger
""",
                        "is_primary": True
                    }
                ],
                "tags": ["python", "web-development", "advanced"]
            },
            {
                "type": "article",
                "visibility": "public",
                "translations": [
                    {
                        "language": "en",
                        "title": "Understanding Docker Containers",
                        "markdown": """# Understanding Docker Containers

Docker has revolutionized how we develop, ship, and run applications. Learn the fundamentals of containerization.

## What is Docker?

Docker is a platform for developing, shipping, and running applications in containers. Containers package software with all dependencies, ensuring consistency across environments.

## Key Concepts

### Images
An image is a lightweight, standalone, executable package that includes everything needed to run software.

### Containers
A container is a running instance of an image. It's isolated from other containers and the host system.

### Dockerfile
A Dockerfile is a text document containing instructions to build a Docker image.

## Basic Commands

\`\`\`bash
docker build -t myapp .
docker run -p 8080:80 myapp
docker ps
docker stop container_id
\`\`\`

## Docker Compose

Manage multi-container applications with docker-compose.yml:

\`\`\`yaml
version: '3'
services:
  web:
    build: .
    ports:
      - "5000:5000"
  db:
    image: postgres
\`\`\`

## Benefits

- Consistency across development, testing, and production
- Faster deployment and scaling
- Resource efficiency
- Isolation and security
""",
                        "is_primary": True
                    }
                ],
                "tags": ["tutorial", "guide"]
            },
        ]

        # Create articles
        for article_data in articles:
            content = Content(
                id=str(uuid.uuid4()),
                type=article_data["type"],
                created_by_id=test_user.id,
                visibility=article_data["visibility"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(content)

            # Add translations
            for trans_data in article_data["translations"]:
                translation = ArticleTranslation(
                    id=str(uuid.uuid4()),
                    content_id=content.id,
                    language=trans_data["language"],
                    title=trans_data["title"],
                    markdown=trans_data["markdown"],
                    is_primary=trans_data["is_primary"]
                )
                translation.generate_slug()
                db.session.add(translation)

            # Add tags
            for tag_key in article_data["tags"]:
                if tag_key in tags:
                    content_tag = ContentTag(
                        content_id=content.id,
                        tag_id=tags[tag_key].id
                    )
                    db.session.add(content_tag)

            print(f"  ✓ Created article: {article_data['translations'][0]['title']}")

        db.session.commit()

        print("\n✅ Database seeded successfully!")
        print(f"   - Created {len(tags_data)} tags")
        print(f"   - Created {len(articles)} articles with translations")
        print("\n🔍 Test the search at: http://localhost:5000/search")
        print("   Try searching for: python, machine learning, javascript, flask, docker")


if __name__ == "__main__":
    seed_database()
