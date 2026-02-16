#!/usr/bin/env bash
# ============================================
# Scarnergy Deploy Script
# ============================================
set -euo pipefail

ENV="${1:-dev}"
echo "Deploying Scarnergy v2.0 — Environment: $ENV"

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose required"; exit 1; }

# Check .env
if [ ! -f .env ]; then
  echo "No .env file found. Copying from .env.example..."
  cp .env.example .env
  echo "⚠  Please edit .env with your actual secrets before production use."
fi

# Pull latest images
echo "Pulling images..."
docker compose pull

# Build custom services
echo "Building custom services..."
docker compose build --parallel

# Start
echo "Starting services..."
if [ "$ENV" = "prod" ]; then
  docker compose -f docker-compose.yml up -d
else
  docker compose up -d
fi

# Wait for database
echo "Waiting for database..."
for i in {1..30}; do
  if docker exec scarnergy-db pg_isready -U postgres > /dev/null 2>&1; then
    echo "Database ready."
    break
  fi
  sleep 2
done

# Run migrations
echo "Running migrations..."
./scripts/migrate.sh

# Health check
echo "Running health check..."
sleep 5
./scripts/health_check.sh

echo ""
echo "═══════════════════════════════════════"
echo " Scarnergy v2.0 deployed successfully!"
echo "═══════════════════════════════════════"
echo " Supabase Studio: http://localhost:3000"
echo " Metabase:        http://localhost:3003"
echo " Grafana:         http://localhost:3030"
echo " AI Engine:       http://localhost:8500/docs"
echo "═══════════════════════════════════════"
