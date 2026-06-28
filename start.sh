#!/bin/bash
# Startup script cho Analytics Service

set -e

echo "🚀 Starting Analytics Service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please update it with your configuration."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Setup database (if needed)
if [ "$1" = "--with-db" ]; then
    echo "💾 Setting up database..."
    python setup_db.py
fi

# Run server
echo ""
echo "✨ Analytics Service is ready!"
echo ""
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🔍 ReDoc: http://localhost:8000/redoc"
echo "❤️  Health Check: http://localhost:8000/api/analytics/health"
echo ""
echo "🎯 Starting server..."
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
