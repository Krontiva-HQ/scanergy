# Scarnergy v2.0

> **Smart Construction Assessment & Rangefinder Energy Platform**  
> Built by **Krontiva Africa** | Open-Source Stack | Production-Grade

---

## What is Scarnergy?

Scarnergy connects **Bosch GLM 50C laser rangefinders** directly to a cloud-native backend via Bluetooth Low Energy (BLE), enabling field inspectors to capture precision building measurements that flow in real-time through an AI-validated pipeline to analytics dashboards.

### Key Features

- **Direct BLE-to-Cloud**: Laser → BLE → Mobile/ESP32 → Supabase in <200ms
- **AI Validation**: On-device TFLite + server-side anomaly detection
- **Three BLE Paths**: Mobile (field), Python Bridge (desktop), ESP32+MQTT (fixed)
- **Offline-First Mobile**: Capture measurements without connectivity, sync when online
- **100% Open-Source**: Supabase, Metabase, Grafana, Mosquitto, TFLite — no vendor lock-in
- **iOS + Android**: React Native/Expo with native BLE support
- **Energy Assessment**: NTA 8800 energy label computation from building measurements
- **Real-Time Dashboards**: Metabase (BI) + Grafana (IoT monitoring)

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/krontiva/scarnergy.git
cd scarnergy

# 2. Configure
cp .env.example .env
# Edit .env with your secrets

# 3. Launch
docker compose up -d

# 4. Setup
./scripts/migrate.sh
./scripts/seed_data.sh

# 5. Verify
./scripts/health_check.sh

# 6. Access
open http://localhost:3000   # Supabase Studio
open http://localhost:3003   # Metabase Dashboards
open http://localhost:3030   # Grafana Real-Time
open http://localhost:8500/docs  # AI Engine API
```

### Mobile App

```bash
cd mobile/inspector-app
npm install
npx expo start
```

### BLE Bridge (requires Bosch GLM device)

```bash
cd services/ble-bridge
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

---

## Architecture

```
Bosch GLM 50C ──BLE──► Mobile App ──────► Supabase ──► Metabase
                                              │
Bosch GLM 50C ──BLE──► Python Bridge ────────►├──────► Grafana
                                              │
Bosch GLM 50C ──BLE──► ESP32 ──MQTT──► Mosquitto ──► Python ──►┘
                                                        │
                                              AI Engine ◄┘
                                              (Anomaly Detection)
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Supabase (self-hosted) | REST API, Auth, Realtime, Storage |
| Database | PostgreSQL + TimescaleDB | Domain data + time-series measurements |
| BI Dashboards | Metabase | Inspection analytics, building portfolio |
| RT Dashboards | Grafana | Live measurements, device monitoring |
| Mobile | React Native / Expo | iOS + Android inspector app |
| IoT Bridge | ESP32 (NimBLE) | BLE → WiFi → MQTT gateway |
| BLE Bridge | Python (bleak) | Desktop BLE → WebSocket → Supabase |
| IoT Messaging | Eclipse Mosquitto | MQTT broker for ESP32 devices |
| AI/ML | scikit-learn + TFLite | Anomaly detection, measurement validation |
| Reports | WeasyPrint + Jinja2 | PDF inspection reports |

## Documentation

All documentation is in the `docs/` folder:

| Doc | Content |
|-----|---------|
| [00-PROJECT-STRUCTURE](docs/00-PROJECT-STRUCTURE.md) | Full directory tree, ports, tech decisions |
| [01-MILESTONES-CHECKLIST](docs/01-MILESTONES-CHECKLIST.md) | 2-week sprint plan with checklists |
| [02-IMPLEMENTATION-GUIDE](docs/02-IMPLEMENTATION-GUIDE.md) | How to use all documentation |
| [03-PLATFORM-OVERVIEW](docs/03-PLATFORM-OVERVIEW.md) | Vision, architecture, data flow |
| [04-SUPABASE-BACKEND](docs/04-SUPABASE-BACKEND.md) | Supabase setup, edge functions, realtime |
| [05-BLE-MEASUREMENT-ENGINE](docs/05-BLE-MEASUREMENT-ENGINE.md) | BLE protocol, Python bridge, native BLE |
| [06-MOBILE-APP-REACT-NATIVE](docs/06-MOBILE-APP-REACT-NATIVE.md) | Expo app, screens, offline-first |
| [07-AI-MEASUREMENT-INTELLIGENCE](docs/07-AI-MEASUREMENT-INTELLIGENCE.md) | Anomaly detection, TFLite, training |
| [08-ESP32-IOT-BRIDGE](docs/08-ESP32-IOT-BRIDGE.md) | ESP32 firmware, MQTT, OTA |
| [09-REALTIME-DATA-PIPELINE](docs/09-REALTIME-DATA-PIPELINE.md) | WebSocket, MQTT, Supabase Realtime |
| [10-DASHBOARDS-ANALYTICS](docs/10-DASHBOARDS-ANALYTICS.md) | Metabase + Grafana dashboards |
| [11-DOMAIN-DATA-MODEL](docs/11-DOMAIN-DATA-MODEL.md) | TypeScript types, entities, computed fields |
| [12-ENERGY-CALCULATIONS-ENGINE](docs/12-ENERGY-CALCULATIONS-ENGINE.md) | NTA 8800 energy metrics |
| [13-INSPECTION-WORKFLOW](docs/13-INSPECTION-WORKFLOW.md) | Field inspection lifecycle |
| [14-INFRASTRUCTURE-DEPLOYMENT](docs/14-INFRASTRUCTURE-DEPLOYMENT.md) | Docker, K8s, backups |
| [15-SECURITY-COMPLIANCE](docs/15-SECURITY-COMPLIANCE.md) | Auth, RLS, encryption |
| [16-TESTING-PRODUCTION](docs/16-TESTING-PRODUCTION.md) | Test strategy, performance targets |
| [17-DATABASE-SCHEMA](docs/17-DATABASE-SCHEMA.md) | Complete SQL schema |
| [18-API-REFERENCE](docs/18-API-REFERENCE.md) | REST + Realtime API contracts |

## Extended Open-Source Projects

| Project | What We Extend |
|---------|----------------|
| [ketan/Bosch-GLM50C-Rangefinder](https://github.com/ketan/Bosch-GLM50C-Rangefinder) | BLE protocol, Python bridge, ESP32 — enhanced with multi-device, MQTT, Supabase |
| [Supabase](https://github.com/supabase/supabase) | Backend platform — customized with TimescaleDB, building inspection schema |
| [Metabase](https://github.com/metabase/metabase) | BI dashboards — configured with inspection-specific analytics |
| [Grafana](https://github.com/grafana/grafana) | Real-time monitoring — MQTT + TimescaleDB for IoT |
| [Eclipse Mosquitto](https://github.com/eclipse/mosquitto) | MQTT broker — ACLs for device-level security |

---

## License

Proprietary — Krontiva Africa. All rights reserved.
