# Scarnergy — Supabase Backend (Replacing Xano)

> **Role**: Central backend platform — REST API, Realtime, Auth, Storage, Edge Functions  
> **Replaces**: Xano (proprietary BaaS)  
> **Why Supabase**: Open-source, PostgreSQL-native, self-hostable, excellent React Native SDK, real-time subscriptions, built-in auth, edge functions for business logic

---

## 1. Architecture Decision: Supabase over Xano

### Why We Replaced Xano

| Concern | Xano | Supabase |
|---------|------|----------|
| Open Source | ❌ Proprietary | ✅ Apache 2.0 / MIT |
| Self-Hosted | ❌ Cloud only | ✅ Full self-hosted Docker |
| Vendor Lock-In | ❌ High | ✅ None — standard PostgreSQL |
| Real-Time | ❌ Polling / webhooks | ✅ Native WebSocket subscriptions |
| PostgreSQL Access | ❌ Abstracted | ✅ Direct SQL + extensions (TimescaleDB, PostGIS) |
| Edge Functions | ❌ Visual function stacks | ✅ Deno TypeScript functions |
| Mobile SDK | ❌ Generic REST | ✅ First-class React Native SDK |
| Cost at Scale | ❌ Per-request pricing | ✅ Self-hosted = infrastructure cost only |
| Row-Level Security | ❌ Manual in API logic | ✅ Native PostgreSQL RLS policies |

### What Supabase Provides

- **PostgREST**: Auto-generated REST API from PostgreSQL schema
- **GoTrue**: Authentication (email, magic link, OAuth, SSO)
- **Realtime**: WebSocket subscriptions for database changes
- **Storage**: S3-compatible object storage for photos and reports
- **Edge Functions**: Serverless Deno functions for business logic
- **Studio**: Web-based database admin UI
- **pg_net**: HTTP requests from PostgreSQL functions
- **TimescaleDB**: Time-series hypertables for measurement data

---

## 2. Self-Hosted Deployment

### Docker Compose Configuration

```yaml
# docker-compose.yml (Supabase stack)
version: '3.8'

services:
  db:
    image: timescale/timescaledb:latest-pg15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: scarnergy
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

  kong:
    image: kong:2.8.1
    environment:
      KONG_DATABASE: "off"
      KONG_DECLARATIVE_CONFIG: /var/lib/kong/kong.yml
    ports:
      - "3001:8000"  # API Gateway
      - "3002:8443"  # API Gateway (SSL)

  auth:
    image: supabase/gotrue:v2.132.3
    environment:
      GOTRUE_DB_DATABASE_URL: postgres://postgres:${POSTGRES_PASSWORD}@db:5432/scarnergy
      GOTRUE_SITE_URL: ${SITE_URL}
      GOTRUE_JWT_SECRET: ${JWT_SECRET}
      GOTRUE_EXTERNAL_EMAIL_ENABLED: "true"
    depends_on:
      db: { condition: service_healthy }

  rest:
    image: postgrest/postgrest:v12.0.1
    environment:
      PGRST_DB_URI: postgres://postgres:${POSTGRES_PASSWORD}@db:5432/scarnergy
      PGRST_DB_ANON_ROLE: anon
      PGRST_JWT_SECRET: ${JWT_SECRET}
    depends_on:
      db: { condition: service_healthy }

  realtime:
    image: supabase/realtime:v2.25.35
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: postgres
      DB_PASSWORD: ${POSTGRES_PASSWORD}
      DB_NAME: scarnergy
      PORT: 4000
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      db: { condition: service_healthy }

  storage:
    image: supabase/storage-api:v0.43.11
    environment:
      DATABASE_URL: postgres://postgres:${POSTGRES_PASSWORD}@db:5432/scarnergy
      STORAGE_BACKEND: file
      FILE_STORAGE_BACKEND_PATH: /var/lib/storage
      JWT_SECRET: ${JWT_SECRET}
    volumes:
      - storage_data:/var/lib/storage

  studio:
    image: supabase/studio:20240101
    environment:
      STUDIO_PG_META_URL: http://meta:8080
      SUPABASE_URL: http://kong:8000
      SUPABASE_REST_URL: http://rest:3000
    ports:
      - "3000:3000"

  meta:
    image: supabase/postgres-meta:v0.68.0
    environment:
      PG_META_DB_HOST: db

volumes:
  pgdata:
  storage_data:
```

### Environment Variables (.env.example)

```env
# PostgreSQL
POSTGRES_PASSWORD=your-secure-password-here

# Supabase
JWT_SECRET=your-jwt-secret-minimum-32-characters
SITE_URL=http://localhost:3000
ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# MQTT
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=scarnergy
MQTT_PASSWORD=your-mqtt-password

# AI Engine
AI_ENGINE_URL=http://localhost:8500
AI_ENGINE_API_KEY=your-ai-api-key

# Redis
REDIS_URL=redis://localhost:6379
```

---

## 3. Edge Functions

### Measurement Ingest (High-Throughput)

```typescript
// supabase/functions/measurement-ingest/index.ts
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  const { measurements } = await req.json();

  // Validate batch
  const validated = measurements.filter((m: any) => {
    return m.value_mm > 50 && m.value_mm < 50000 // 5cm to 50m
      && m.device_id && m.timestamp;
  });

  // Batch insert into TimescaleDB hypertable
  const { data, error } = await supabase
    .from("measurements")
    .insert(validated.map((m: any) => ({
      value_mm: m.value_mm,
      raw_hex: m.raw_hex,
      source: m.source, // 'ble_mobile' | 'ble_bridge' | 'mqtt_esp32'
      device_id: m.device_id,
      session_id: m.session_id,
      element_type: m.element_type,
      element_id: m.element_id,
      inspector_id: m.inspector_id,
      org_id: m.org_id,
      anomaly_score: m.anomaly_score || null,
      captured_at: m.timestamp,
    })));

  if (error) return new Response(JSON.stringify({ error }), { status: 500 });

  return new Response(JSON.stringify({
    ingested: validated.length,
    rejected: measurements.length - validated.length,
  }), { status: 200 });
});
```

### Energy Calculator (NTA 8800)

```typescript
// supabase/functions/energy-calculator/index.ts
serve(async (req) => {
  const { object_id } = await req.json();
  const supabase = createClient(/* ... */);

  // Fetch building data
  const { data: object } = await supabase.from("objects").select("*").eq("id", object_id).single();
  const { data: zones } = await supabase.from("rekenzones").select("*").eq("object_id", object_id);
  const { data: gevels } = await supabase.from("gevels").select("*").in("rekenzone_id", zones.map(z => z.id));
  const { data: daken } = await supabase.from("daken").select("*").in("rekenzone_id", zones.map(z => z.id));
  const { data: vloeren } = await supabase.from("vloeren").select("*").in("rekenzone_id", zones.map(z => z.id));
  const { data: installaties } = await supabase.from("installaties").select("*").in("rekenzone_id", zones.map(z => z.id));

  // Compute energy metrics (simplified NTA 8800)
  const totalEnvelopeArea = calculateEnvelopeArea(gevels, daken, vloeren);
  const transmissionLoss = calculateTransmissionLoss(gevels, daken, vloeren);
  const ventilationLoss = calculateVentilationLoss(object);
  const heatingDemand = transmissionLoss + ventilationLoss;
  const systemEfficiency = calculateSystemEfficiency(installaties);
  const energyIndex = heatingDemand / (totalEnvelopeArea * systemEfficiency);
  const energyLabel = resolveLabel(energyIndex);

  return new Response(JSON.stringify({
    object_id,
    energy_index: energyIndex,
    energy_label: energyLabel,
    breakdown: { totalEnvelopeArea, transmissionLoss, ventilationLoss, heatingDemand, systemEfficiency },
  }));
});
```

---

## 4. Real-Time Subscriptions

### Client-Side (React Native)

```typescript
// Mobile app: subscribe to new measurements for current session
const channel = supabase
  .channel('measurement-stream')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'measurements',
    filter: `session_id=eq.${sessionId}`,
  }, (payload) => {
    // Update local state with new measurement
    addMeasurement(payload.new);
  })
  .subscribe();
```

### Server-Side (Python BLE Bridge)

```python
# BLE bridge: publish measurement via Supabase client
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def on_measurement(value_mm, raw_hex, device_id):
    supabase.table("measurements").insert({
        "value_mm": value_mm,
        "raw_hex": raw_hex,
        "source": "ble_bridge",
        "device_id": device_id,
        "captured_at": datetime.utcnow().isoformat(),
    }).execute()
```

---

## 5. Storage Configuration

| Bucket | Access | Max Size | Content |
|--------|--------|----------|---------|
| `inspection-photos` | Public read, auth write | 10MB/file | Building/element photos |
| `reports` | Auth read/write | 50MB/file | Generated PDF reports |
| `building-models` | Auth read/write | 100MB/file | 3D models, floor plans |
| `firmware` | Admin read/write | 10MB/file | ESP32 OTA firmware files |

---

## 6. Verification Steps

```bash
# 1. Start Supabase
docker compose up -d

# 2. Check all services
curl http://localhost:3001/rest/v1/ -H "apikey: $ANON_KEY"
# Should return: list of tables

# 3. Test auth
curl -X POST http://localhost:3001/auth/v1/signup \
  -H "apikey: $ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@krontiva.com","password":"test123456"}'

# 4. Test realtime
wscat -c "ws://localhost:3001/realtime/v1/websocket?apikey=$ANON_KEY"

# 5. Test edge function
curl http://localhost:54321/functions/v1/measurement-ingest \
  -H "Authorization: Bearer $SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"measurements":[{"value_mm":2450,"device_id":"test","timestamp":"2026-02-11T12:00:00Z"}]}'
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
