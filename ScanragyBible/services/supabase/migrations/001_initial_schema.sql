-- ============================================
-- Scarnergy v2.0 — Initial Schema
-- ============================================
-- See docs/17-DATABASE-SCHEMA.md for full documentation

-- Extensions
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enums
CREATE TYPE user_role AS ENUM ('admin', 'supervisor', 'inspector', 'viewer');
CREATE TYPE object_type AS ENUM ('residential', 'commercial', 'industrial', 'mixed');
CREATE TYPE object_status AS ENUM ('active', 'archived', 'pending');
CREATE TYPE device_type AS ENUM ('glm50c', 'esp32', 'other');
CREATE TYPE device_status AS ENUM ('active', 'inactive', 'maintenance');
CREATE TYPE inspection_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
CREATE TYPE measurement_source AS ENUM ('ble_mobile', 'ble_bridge', 'esp32_mqtt', 'manual');
CREATE TYPE energy_label AS ENUM ('A++++', 'A+++', 'A++', 'A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G');

-- Organizations
CREATE TABLE organizations (
    id TEXT PRIMARY KEY DEFAULT 'org-' || gen_random_uuid()::text,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    subscription_tier TEXT DEFAULT 'starter',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id TEXT PRIMARY KEY DEFAULT 'usr-' || gen_random_uuid()::text,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    role user_role DEFAULT 'inspector',
    phone TEXT,
    avatar_url TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_users_org ON users(org_id);

-- Devices
CREATE TABLE devices (
    id TEXT PRIMARY KEY DEFAULT 'dev-' || gen_random_uuid()::text,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    device_type device_type NOT NULL,
    serial_number TEXT,
    firmware_version TEXT,
    status device_status DEFAULT 'active',
    last_seen TIMESTAMPTZ,
    battery_level INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_devices_org ON devices(org_id);

-- Objects (Buildings)
CREATE TABLE objects (
    id TEXT PRIMARY KEY DEFAULT 'obj-' || gen_random_uuid()::text,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT,
    postal_code TEXT,
    build_year INTEGER,
    object_type object_type DEFAULT 'residential',
    status object_status DEFAULT 'active',
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_objects_org ON objects(org_id);

-- Rekenzones (Calculation Zones)
CREATE TABLE rekenzones (
    id TEXT PRIMARY KEY DEFAULT 'rz-' || gen_random_uuid()::text,
    object_id TEXT NOT NULL REFERENCES objects(id) ON DELETE CASCADE,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    zone_type TEXT DEFAULT 'heated',
    floor_area DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_rekenzones_object ON rekenzones(object_id);

-- Gevels (Facades/Walls)
CREATE TABLE gevels (
    id TEXT PRIMARY KEY DEFAULT 'gvl-' || gen_random_uuid()::text,
    rekenzone_id TEXT NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    orientation TEXT,
    hoogte DOUBLE PRECISION,
    breedte DOUBLE PRECISION,
    bruto_oppervlakte DOUBLE PRECISION GENERATED ALWAYS AS (hoogte * breedte) STORED,
    u_waarde DOUBLE PRECISION,
    isolatie_type TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_gevels_rekenzone ON gevels(rekenzone_id);

-- Daken (Roofs)
CREATE TABLE daken (
    id TEXT PRIMARY KEY DEFAULT 'dak-' || gen_random_uuid()::text,
    rekenzone_id TEXT NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    dak_type TEXT,
    oppervlakte DOUBLE PRECISION,
    u_waarde DOUBLE PRECISION,
    isolatie_dikte DOUBLE PRECISION,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vloeren (Floors)
CREATE TABLE vloeren (
    id TEXT PRIMARY KEY DEFAULT 'vlr-' || gen_random_uuid()::text,
    rekenzone_id TEXT NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    vloer_type TEXT,
    oppervlakte DOUBLE PRECISION,
    u_waarde DOUBLE PRECISION,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Installaties (Installations/HVAC)
CREATE TABLE installaties (
    id TEXT PRIMARY KEY DEFAULT 'inst-' || gen_random_uuid()::text,
    rekenzone_id TEXT NOT NULL REFERENCES rekenzones(id) ON DELETE CASCADE,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    installatie_type TEXT NOT NULL,
    merk TEXT,
    model TEXT,
    bouwjaar INTEGER,
    rendement DOUBLE PRECISION,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transparante Delen (Windows/Openings)
CREATE TABLE transparante_delen (
    id TEXT PRIMARY KEY DEFAULT 'td-' || gen_random_uuid()::text,
    gevel_id TEXT REFERENCES gevels(id) ON DELETE CASCADE,
    dak_id TEXT REFERENCES daken(id) ON DELETE CASCADE,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    deel_type TEXT DEFAULT 'raam',
    hoogte DOUBLE PRECISION,
    breedte DOUBLE PRECISION,
    oppervlakte DOUBLE PRECISION GENERATED ALWAYS AS (hoogte * breedte) STORED,
    u_waarde DOUBLE PRECISION,
    g_waarde DOUBLE PRECISION,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CHECK (gevel_id IS NOT NULL OR dak_id IS NOT NULL)
);

-- Inspections
CREATE TABLE inspections (
    id TEXT PRIMARY KEY DEFAULT 'insp-' || gen_random_uuid()::text,
    org_id TEXT NOT NULL REFERENCES organizations(id),
    object_id TEXT NOT NULL REFERENCES objects(id),
    inspector_id TEXT NOT NULL REFERENCES users(id),
    status inspection_status DEFAULT 'scheduled',
    scheduled_date DATE,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    notes TEXT,
    energy_label energy_label,
    energy_index DOUBLE PRECISION,
    report_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_inspections_org ON inspections(org_id);
CREATE INDEX idx_inspections_object ON inspections(object_id);
CREATE INDEX idx_inspections_inspector ON inspections(inspector_id);

-- Measurements (TimescaleDB Hypertable)
CREATE TABLE measurements (
    id TEXT DEFAULT 'msr-' || gen_random_uuid()::text,
    org_id TEXT NOT NULL,
    inspection_id TEXT REFERENCES inspections(id),
    device_id TEXT REFERENCES devices(id),
    user_id TEXT REFERENCES users(id),
    source measurement_source DEFAULT 'ble_mobile',
    value_mm DOUBLE PRECISION NOT NULL,
    raw_hex TEXT,
    measurement_type TEXT,
    target_entity TEXT,
    target_id TEXT,
    anomaly_score DOUBLE PRECISION DEFAULT 0,
    is_anomaly BOOLEAN DEFAULT FALSE,
    ai_classification JSONB DEFAULT '{}',
    session_id TEXT,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    synced_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (id, captured_at)
);

SELECT create_hypertable('measurements', 'captured_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

CREATE INDEX idx_measurements_org_time ON measurements(org_id, captured_at DESC);
CREATE INDEX idx_measurements_device ON measurements(device_id, captured_at DESC);
CREATE INDEX idx_measurements_inspection ON measurements(inspection_id, captured_at DESC);

-- Continuous Aggregate: Hourly measurement stats
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
    COUNT(*) FILTER (WHERE is_anomaly) AS anomaly_count
FROM measurements
GROUP BY bucket, org_id, device_id
WITH NO DATA;

-- Sync Queue (offline-first support)
CREATE TABLE sync_queue (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    org_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    payload JSONB NOT NULL,
    client_timestamp TIMESTAMPTZ NOT NULL,
    server_timestamp TIMESTAMPTZ,
    status TEXT DEFAULT 'pending',
    conflict_resolution JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════
-- ROW LEVEL SECURITY
-- ═══════════════════════════════════════════

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE objects ENABLE ROW LEVEL SECURITY;
ALTER TABLE rekenzones ENABLE ROW LEVEL SECURITY;
ALTER TABLE gevels ENABLE ROW LEVEL SECURITY;
ALTER TABLE daken ENABLE ROW LEVEL SECURITY;
ALTER TABLE vloeren ENABLE ROW LEVEL SECURITY;
ALTER TABLE installaties ENABLE ROW LEVEL SECURITY;
ALTER TABLE transparante_delen ENABLE ROW LEVEL SECURITY;
ALTER TABLE inspections ENABLE ROW LEVEL SECURITY;
ALTER TABLE measurements ENABLE ROW LEVEL SECURITY;

-- Helper function: get user's org_id from JWT
CREATE OR REPLACE FUNCTION auth.user_org_id()
RETURNS TEXT AS $$
  SELECT org_id FROM users WHERE id = auth.uid()::text;
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- RLS Policies (org-scoped access)
CREATE POLICY "org_isolation" ON organizations
    FOR ALL USING (id = auth.user_org_id());

CREATE POLICY "org_isolation" ON users
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON devices
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON objects
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON rekenzones
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON gevels
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON daken
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON vloeren
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON installaties
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON transparante_delen
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON inspections
    FOR ALL USING (org_id = auth.user_org_id());

CREATE POLICY "org_isolation" ON measurements
    FOR ALL USING (org_id = auth.user_org_id());

-- Service role bypass for server-side operations
CREATE POLICY "service_role_all" ON measurements
    FOR ALL TO service_role USING (true);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON objects FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON inspections FOR EACH ROW EXECUTE FUNCTION update_updated_at();
