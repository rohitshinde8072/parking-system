#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing Python backend dependencies..."
pip install -r requirements.txt

echo "Building React production frontend..."
cd frontend
npm ci || npm install
npm run build
cd ..

echo "Running database migrations..."
python -c "from backend.app.migrate import migrate_db; from backend.app.services.seed_data import seed_database; migrate_db(); seed_database()"

echo "Build complete! Ready for 24/7 cloud serving."
