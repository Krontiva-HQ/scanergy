# Scarnergy — Step-by-Step Implementation Guide

> This is the master implementation guide. Each topic has its own detailed document (03–18) with exact architectures, code patterns, configurations, and verification steps.

---

## How to Use This Guide

1. **Read `00-PROJECT-STRUCTURE.md`** to understand the full codebase layout
2. **Read `01-MILESTONES-CHECKLIST.md`** for the 2-week sprint plan and checklist
3. **Follow milestones M1–M6 in order**. Each milestone maps to specific documents:
   - Detailed architecture diagrams and data flows
   - Exact configuration files and environment variables
   - Code scaffolding and integration patterns
   - Verification steps after each task
   - Exit criteria before moving on
4. **Do not skip milestones**. Each depends on the previous (see dependency map in checklist)

---

## Implementation Principles

### 1. Supabase is the Backbone
Every data operation flows through Supabase. The mobile app, BLE bridge, ESP32, and dashboards all read/write via Supabase's REST API, Realtime subscriptions, or Edge Functions. This creates a single source of truth with consistent auth and RLS.

### 2. Open-Source Everything
Every component is open-source and self-hostable. No proprietary vendor lock-in. Supabase replaces Xano. Metabase replaces any commercial BI tool. Grafana provides real-time monitoring. Eclipse Mosquitto handles IoT messaging. The entire stack can run on-premises or in any cloud.

### 3. BLE-First, Cloud-Second
Measurements originate from Bosch GLM50C laser rangefinders via BLE. The system supports three BLE-to-cloud paths:
- **Direct**: Mobile app → BLE → Supabase (primary for field inspectors)
- **Bridge**: Python bridge → BLE → WebSocket + Supabase (for desktop/kiosk)
- **IoT**: ESP32 → BLE → MQTT → Python → Supabase (for fixed installations)

### 4. Offline-First Mobile
The inspector mobile app must work without network connectivity. Measurements are captured via BLE locally, stored in Zustand + MMKV, and synced to Supabase when connectivity returns. Conflict resolution uses vector clocks with last-write-wins default.

### 5. AI-Validated Measurements
Every measurement passes through validation: on-device (TFLite) for instant feedback, and server-side (FastAPI) for comprehensive checks. Anomalies are flagged but not blocked — inspectors can override with justification.

### 6. Multi-Tenant from Day One
Every table has `org_id`. Every API query is scoped by organization. Supabase RLS enforces tenant isolation. Inspectors see only their assigned buildings. Supervisors see their organization's full portfolio.

### 7. Docker Always, Kubernetes for Scale
Local development uses `docker compose`. Production deployment targets Kubernetes with Helm charts. All services have health check endpoints and readiness probes.

---

## Document Index

### Foundation Documents
| Document | Content | Milestone |
|----------|---------|-----------|
| **`00-PROJECT-STRUCTURE.md`** | Full directory tree, service registry, port map | Reference |
| **`01-MILESTONES-CHECKLIST.md`** | 2-week sprint plan, dependencies, checklists | Reference |
| **`02-IMPLEMENTATION-GUIDE.md`** | This document — how to use all other docs | Reference |
| **`03-PLATFORM-OVERVIEW.md`** | Vision, architecture, tech stack, component roles | M1 |

### Backend & Data
| Document | Content | Milestone |
|----------|---------|-----------|
| **`04-SUPABASE-BACKEND.md`** | Supabase deployment, schema, edge functions, auth, storage | M1 |
| **`11-DOMAIN-DATA-MODEL.md`** | Objects, Rekenzones, Gevels, Daken, Vloeren, Installaties | M1 |
| **`12-ENERGY-CALCULATIONS-ENGINE.md`** | NTA 8800 compliance, energy metrics, label computation | M1, M4 |
| **`17-DATABASE-SCHEMA.md`** | Complete SQL schema with TimescaleDB hypertables | M1 |
| **`18-API-REFERENCE.md`** | REST + Realtime API contracts with examples | M1 |

### BLE & IoT
| Document | Content | Milestone |
|----------|---------|-----------|
| **`05-BLE-MEASUREMENT-ENGINE.md`** | BLE protocol, Python bridge, device manager, validation | M2 |
| **`08-ESP32-IOT-BRIDGE.md`** | ESP32 firmware, MQTT, WiFi, OTA, multi-device | M2 |
| **`09-REALTIME-DATA-PIPELINE.md`** | WebSocket, MQTT, Supabase Realtime, data flow | M2 |

### Mobile
| Document | Content | Milestone |
|----------|---------|-----------|
| **`06-MOBILE-APP-REACT-NATIVE.md`** | Expo app, screens, forms, BLE hooks, offline-first | M3 |

### AI/ML
| Document | Content | Milestone |
|----------|---------|-----------|
| **`07-AI-MEASUREMENT-INTELLIGENCE.md`** | Anomaly detection, TFLite, FastAPI, training pipeline | M4 |

### Dashboards & Analytics
| Document | Content | Milestone |
|----------|---------|-----------|
| **`10-DASHBOARDS-ANALYTICS.md`** | Metabase BI dashboards + Grafana real-time panels | M5 |

### Infrastructure & Operations
| Document | Content | Milestone |
|----------|---------|-----------|
| **`13-INSPECTION-WORKFLOW.md`** | Field inspection lifecycle, scheduling, reports | M3, M6 |
| **`14-INFRASTRUCTURE-DEPLOYMENT.md`** | Docker, Kubernetes, Terraform, monitoring | M1, M6 |
| **`15-SECURITY-COMPLIANCE.md`** | Auth, RBAC, encryption, GDPR, RLS | M1, M6 |
| **`16-TESTING-PRODUCTION.md`** | Test strategy, E2E, performance, release process | M6 |

---

## Milestone → Document Mapping

```
M1 (Foundation)           → 03, 04, 11, 12, 14, 15, 17, 18
M2 (BLE Engine)           → 05, 08, 09
M3 (Mobile App)           → 06, 13
M4 (AI/ML)                → 07
M5 (Dashboards)           → 10
M6 (Testing & Deploy)     → 14, 15, 16
```

---

## Quick Start (Development Environment)

```bash
# 1. Clone repository
git clone https://github.com/krontiva/scarnergy.git
cd scarnergy

# 2. Copy environment template
cp .env.example .env
# Edit .env with your Supabase secrets, MQTT credentials, etc.

# 3. Start the full stack
docker compose up -d

# 4. Run database migrations
./scripts/migrate.sh

# 5. Seed development data
./scripts/seed_data.sh

# 6. Verify all services
./scripts/health_check.sh

# 7. Access services
open http://localhost:3000   # Supabase Studio
open http://localhost:3003   # Metabase (BI Dashboards)
open http://localhost:3030   # Grafana (Real-Time Monitoring)
open http://localhost:8500   # AI Engine (Swagger Docs)

# 8. Start the mobile app
cd mobile/inspector-app
npm install
npx expo start

# 9. Start the BLE bridge (requires Bosch GLM device)
cd services/ble-bridge
source venv/bin/activate
python src/main.py
```

---

## Architecture Decision Records

| ADR | Decision | Status |
|-----|----------|--------|
| [ADR-001](adr/001-supabase-over-xano.md) | Supabase over Xano | Accepted |
| [ADR-002](adr/002-metabase-for-bi.md) | Metabase for BI dashboards | Accepted |
| [ADR-003](adr/003-grafana-for-iot.md) | Grafana for real-time IoT monitoring | Accepted |
| [ADR-004](adr/004-expo-react-native.md) | Expo/React Native for mobile (iOS + Android) | Accepted |
| [ADR-005](adr/005-tflite-on-device-ml.md) | TFLite for on-device measurement AI | Accepted |
| [ADR-006](adr/006-mqtt-for-iot-mesh.md) | MQTT (Mosquitto) for ESP32 IoT messaging | Accepted |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
