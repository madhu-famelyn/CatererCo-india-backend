#!/bin/bash
# Start the CatererCo FastAPI backend
# Usage: bash start.sh

cd "$(dirname "$0")"

# Create venv if not present
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip --quiet
  pip install -r requirements.txt --quiet
  pip install bcrypt==4.0.1 --quiet
  echo "✅ Dependencies installed"
else
  source venv/bin/activate
fi

# Seed if DB doesn't exist
if [ ! -f "catererco.db" ]; then
  echo "🌱 Seeding database..."
  python seed.py
fi

echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000"
echo "📚 API docs at http://localhost:8000/docs"
echo ""
uvicorn main:app --reload --reload-exclude venv --port 8000 --host 0.0.0.0
