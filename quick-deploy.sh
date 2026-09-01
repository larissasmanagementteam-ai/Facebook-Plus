#!/bin/bash

# Quick Docker Compose Deploy
# Run: bash quick-deploy.sh

set -e

echo "🚀 Starting Facebook-Plus..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker daemon is not running. Please start Docker first."
    exit 1
fi

echo "📦 Building Docker image..."
docker-compose build --quiet

echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "✅ Deployment started!"
echo ""
echo "📊 Access points:"
echo "   • App:        http://localhost:8000"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "📋 Check status:"
echo "   docker-compose ps"
echo ""
echo "📖 View logs:"
echo "   docker-compose logs -f facebook-system"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""
