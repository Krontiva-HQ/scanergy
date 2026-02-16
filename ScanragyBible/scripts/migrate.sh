#!/usr/bin/env bash
# ============================================
# Scarnergy Database Migration
# ============================================
set -euo pipefail

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-scarnergy}"
DB_USER="${DB_USER:-postgres}"

echo "Running Scarnergy migrations on $DB_HOST:$DB_PORT/$DB_NAME"

# Enable extensions
docker exec scarnergy-db psql -U "$DB_USER" -d "$DB_NAME" -c "
  CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
  CREATE EXTENSION IF NOT EXISTS pgcrypto;
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  CREATE EXTENSION IF NOT EXISTS uuid-ossp;
"

# Run migration files in order
MIGRATION_DIR="./services/supabase/migrations"
if [ -d "$MIGRATION_DIR" ]; then
  for f in $(ls "$MIGRATION_DIR"/*.sql 2>/dev/null | sort); do
    echo "  Applying: $(basename $f)"
    docker exec -i scarnergy-db psql -U "$DB_USER" -d "$DB_NAME" < "$f"
  done
  echo "All migrations applied."
else
  echo "No migration files found in $MIGRATION_DIR"
  echo "Create your schema in $MIGRATION_DIR/001_initial_schema.sql"
fi
