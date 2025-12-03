#!/bin/bash
# Quick start script for KMS

echo "🚀 Starting KMS Knowledge Management System"
echo "=========================================="
echo ""

# Build images
echo "📦 Building Docker images..."
docker compose build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Start services
echo ""
echo "🔧 Starting services..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start services!"
    exit 1
fi

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

# Initialize database
echo ""
echo "🗄️  Initializing database..."
docker compose exec flask flask db init 2>/dev/null || echo "Migrations already initialized"
docker compose exec flask flask db migrate -m "Initial migration" 2>/dev/null || echo "Migration already exists"
docker compose exec flask flask db upgrade

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed!"
    exit 1
fi

# Show status
echo ""
echo "✅ KMS is ready!"
echo ""
echo "📍 Services:"
echo "   Flask API:      http://localhost:5000"
echo "   MinIO Console:  http://localhost:9001 (minioadmin/minioadmin)"
echo "   PostgreSQL:     localhost:5432 (kms_user/kms_password)"
echo "   Redis:          localhost:6379"
echo ""
echo "📖 Useful commands:"
echo "   make logs       - View logs"
echo "   make shell      - Open Flask shell"
echo "   make down       - Stop services"
echo "   make restart    - Restart services"
echo ""
echo "🔗 Test the API:"
echo "   curl http://localhost:5000/health"
echo ""
