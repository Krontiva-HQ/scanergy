# Scarnergy — Complete Database Schema

> **Engine**: PostgreSQL 15 + TimescaleDB
> **Extensions**: uuid-ossp, postgis, pg_trgm, timescaledb

---

## Schema Overview

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ============================================
-- ORGANIZATIONS & USERS
-- ============================================

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  settings JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id),
  org_id UUID NOT NULL REFERENCES organizations(id),
  full_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'supervisor', 'inspector')),
  phone TEXT,
  avatar_url TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- BUILDINGS & ZONES
-- ============================================

CREATE TABLE objects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  adres TEXT NOT NULL,
  postcode TEXT,
  plaats TEXT,
  geom GEOMETRY(Point, 4326),
  building_type TEXT DEFAULT 'residential',
  bouwjaar INTEGER,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending','in_progress','complete','review')),
  opname_datum DATE,
  inspecteur_id UUID REFERENCES users(id),
  energy_label TEXT,
  energy_index NUMERIC(6,3),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_objects_org ON objects(org_id);
CREATE INDEX idx_objects_status ON objects(status);
CREATE INDEX idx_objects_geom ON objects USING GIST(geom);

CREATE TABLE rekenzones (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  object_id UUID NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
  naam TEXT NOT NULL,
  verdieping INTEGER DEFAULT 0,
  oppervlakte NUMERIC(12,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- BUILDING ELEMENTS
-- ============================================

CREATE TABLE gevels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rekenzone_id UUID NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
  positie TEXT,
  berekende_orientatie TEXT,
  orientatie_code TEXT,
  hoogte NUMERIC(10,1),          -- mm
  breedte NUMERIC(10,1),         -- mm
  bruto_oppervlakte NUMERIC(14,2) GENERATED ALWAYS AS (hoogte * breedte) STORED,
  netto_oppervlakte NUMERIC(14,2),
  grenst_aan_code TEXT,
  is_perimeter BOOLEAN DEFAULT false,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE daken (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rekenzone_id UUID NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
  type_dak TEXT DEFAULT 'plat' CHECK (type_dak IN ('plat','schuin','zadel','mansarde','shed')),
  hoek NUMERIC(5,1),             -- degrees
  orientatie TEXT,
  lengte NUMERIC(10,1),          -- mm
  breedte NUMERIC(10,1),         -- mm
  bruto_oppervlakte NUMERIC(14,2) GENERATED ALWAYS AS (lengte * breedte) STORED,
  netto_oppervlakte NUMERIC(14,2),
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE vloeren (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rekenzone_id UUID NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
  isolatie BOOLEAN DEFAULT false,
  isolatie_dikte NUMERIC(8,1),   -- mm
  oppervlakte NUMERIC(14,2),     -- mm²
  perimeter NUMERIC(10,1),       -- mm
  grenst_aan_code TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE installaties (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rekenzone_id UUID NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
  type_installatie TEXT NOT NULL,
  merk_model TEXT,
  locatie TEXT,
  bouwjaar INTEGER,
  photo_urls TEXT[] DEFAULT '{}',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE transparante_delen (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  parent_type TEXT NOT NULL CHECK (parent_type IN ('gevel','dak','vloer')),
  parent_id UUID NOT NULL,
  hoogte NUMERIC(10,1),
  breedte NUMERIC(10,1),
  aantal INTEGER DEFAULT 1,
  bruto_oppervlakte NUMERIC(14,2) GENERATED ALWAYS AS (hoogte * breedte * aantal) STORED,
  materiaal TEXT,
  glas_type TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE dakkapellen (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  dak_id UUID NOT NULL REFERENCES daken(id) ON DELETE CASCADE,
  hoogte NUMERIC(10,1),
  breedte NUMERIC(10,1),
  oppervlakte NUMERIC(14,2) GENERATED ALWAYS AS (hoogte * breedte) STORED,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- MEASUREMENTS (TimescaleDB Hypertable)
-- ============================================

CREATE TABLE measurements (
  id UUID DEFAULT uuid_generate_v4(),
  value_mm NUMERIC(10,1) NOT NULL,
  raw_hex TEXT,
  source TEXT NOT NULL CHECK (source IN ('ble_mobile','ble_bridge','mqtt_esp32','manual')),
  device_id UUID REFERENCES devices(id),
  session_id UUID REFERENCES measurement_sessions(id),
  element_type TEXT,
  element_id UUID,
  inspector_id UUID REFERENCES users(id),
  org_id UUID NOT NULL REFERENCES organizations(id),
  anomaly_score NUMERIC(8,4),
  anomaly_flags TEXT[],
  captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (id, captured_at)
);

SELECT create_hypertable('measurements', 'captured_at',
  chunk_time_interval => INTERVAL '1 day');

CREATE INDEX idx_measurements_session ON measurements(session_id, captured_at DESC);
CREATE INDEX idx_measurements_device ON measurements(device_id, captured_at DESC);
CREATE INDEX idx_measurements_org ON measurements(org_id, captured_at DESC);

-- ============================================
-- DEVICES & SESSIONS
-- ============================================

CREATE TABLE devices (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  org_id UUID NOT NULL REFERENCES organizations(id),
  name TEXT,
  address TEXT NOT NULL,
  firmware_version TEXT,
  last_seen TIMESTAMPTZ,
  assigned_to UUID REFERENCES users(id),
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE measurement_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  inspection_id UUID REFERENCES inspections(id),
  element_type TEXT,
  element_id UUID,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  measurement_count INTEGER DEFAULT 0
);

-- ============================================
-- INSPECTIONS & CALENDAR
-- ============================================

CREATE TABLE inspections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  object_id UUID NOT NULL REFERENCES objects(id),
  inspector_id UUID NOT NULL REFERENCES users(id),
  org_id UUID NOT NULL REFERENCES organizations(id),
  status TEXT DEFAULT 'scheduled',
  scheduled_date DATE,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  report_url TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE calendar_visits (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  object_id UUID NOT NULL REFERENCES objects(id),
  inspector_id UUID NOT NULL REFERENCES users(id),
  org_id UUID NOT NULL REFERENCES organizations(id),
  visit_date DATE NOT NULL,
  visit_time TIME,
  duration_minutes INTEGER DEFAULT 60,
  status TEXT DEFAULT 'scheduled',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- CONTINUOUS AGGREGATES (TimescaleDB)
-- ============================================

CREATE MATERIALIZED VIEW measurements_hourly
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 hour', captured_at) AS bucket,
  org_id,
  device_id,
  COUNT(*) AS measurement_count,
  AVG(value_mm) AS avg_value,
  MIN(value_mm) AS min_value,
  MAX(value_mm) AS max_value,
  STDDEV(value_mm) AS stddev_value,
  COUNT(*) FILTER (WHERE anomaly_score < 0) AS anomaly_count
FROM measurements
GROUP BY bucket, org_id, device_id;
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
