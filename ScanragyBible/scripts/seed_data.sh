#!/usr/bin/env bash
# ============================================
# Scarnergy Seed Data
# ============================================
set -euo pipefail

DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-scarnergy}"

echo "Seeding Scarnergy database..."

docker exec -i scarnergy-db psql -U "$DB_USER" -d "$DB_NAME" << 'SQL'

-- Organizations
INSERT INTO organizations (id, name, slug, subscription_tier) VALUES
  ('org-001', 'Krontiva Africa', 'krontiva', 'enterprise'),
  ('org-002', 'Dutch Energy Assessors', 'dea', 'professional'),
  ('org-003', 'BuildCheck BV', 'buildcheck', 'starter')
ON CONFLICT (id) DO NOTHING;

-- Users (passwords managed by GoTrue auth)
INSERT INTO users (id, org_id, email, full_name, role) VALUES
  ('usr-001', 'org-001', 'solomon@krontiva.africa', 'Solomon', 'admin'),
  ('usr-002', 'org-001', 'inspector1@krontiva.africa', 'Field Inspector 1', 'inspector'),
  ('usr-003', 'org-002', 'jan@dea.nl', 'Jan de Vries', 'admin'),
  ('usr-004', 'org-002', 'emma@dea.nl', 'Emma Bakker', 'inspector'),
  ('usr-005', 'org-003', 'test@buildcheck.nl', 'Test User', 'inspector')
ON CONFLICT (id) DO NOTHING;

-- Devices
INSERT INTO devices (id, org_id, device_type, serial_number, firmware_version, status) VALUES
  ('dev-001', 'org-001', 'glm50c', 'GLM50C-001', '2.3.0', 'active'),
  ('dev-002', 'org-001', 'glm50c', 'GLM50C-002', '2.3.0', 'active'),
  ('dev-003', 'org-001', 'esp32', 'ESP32-BRIDGE-001', '1.0.0', 'active'),
  ('dev-004', 'org-002', 'glm50c', 'GLM50C-003', '2.3.0', 'active'),
  ('dev-005', 'org-002', 'glm50c', 'GLM50C-004', '2.3.0', 'active')
ON CONFLICT (id) DO NOTHING;

-- Sample buildings (objects)
INSERT INTO objects (id, org_id, name, address, city, postal_code, build_year, object_type, status) VALUES
  ('obj-001', 'org-001', 'Krontiva HQ', '15 Independence Ave', 'Accra', '00233', 2018, 'commercial', 'active'),
  ('obj-002', 'org-002', 'Herengracht 100', 'Herengracht 100', 'Amsterdam', '1015BS', 1890, 'residential', 'active'),
  ('obj-003', 'org-002', 'Keizersgracht 200', 'Keizersgracht 200', 'Amsterdam', '1016DT', 1920, 'residential', 'active'),
  ('obj-004', 'org-002', 'Prinsengracht 300', 'Prinsengracht 300', 'Amsterdam', '1016HJ', 1905, 'mixed', 'active'),
  ('obj-005', 'org-003', 'Testgebouw 1', 'Teststraat 1', 'Rotterdam', '3011AA', 2000, 'residential', 'active')
ON CONFLICT (id) DO NOTHING;

SELECT 'Seed data loaded successfully' AS status;
SQL

echo "Seed data complete."
