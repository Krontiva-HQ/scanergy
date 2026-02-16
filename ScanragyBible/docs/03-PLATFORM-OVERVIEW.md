# Scarnergy — Platform Overview

> **Version**: 2.0 (Production Redesign)  
> **Status**: Active Development  
> **Architecture**: Microservices + Event-Driven + Offline-First Mobile

---

## 1. Executive Summary

Scarnergy is an intelligent building inspection and energy assessment platform that transforms how field inspectors capture, validate, and analyze building measurements. By connecting Bosch GLM 50C laser rangefinders directly to a cloud-native, open-source backend via Bluetooth Low Energy (BLE), Scarnergy eliminates manual data entry errors, provides real-time AI-powered measurement validation, and generates comprehensive energy performance reports compliant with NTA 8800 standards.

### What Makes Scarnergy Novel

1. **Direct BLE-to-Cloud Pipeline**: Laser measurements flow from Bosch GLM50C → BLE → Mobile/ESP32 → Supabase in under 200ms, with zero manual transcription.
2. **AI Measurement Intelligence**: On-device TFLite models validate measurements in real-time, flagging physical impossibilities (e.g., 100m wall height) before they pollute the database.
3. **Three BLE Paths**: Mobile (inspector in field), Python Bridge (desktop/kiosk), ESP32+MQTT (fixed installations) — all converging on the same Supabase backend.
4. **100% Open-Source Stack**: Supabase, Metabase, Grafana, Mosquitto, TFLite, React Native — no vendor lock-in, fully self-hostable.
5. **Offline-First Mobile**: Inspectors capture measurements in basements, rooftops, and rural areas without connectivity, syncing automatically when online.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FIELD LAYER                                │
│                                                                 │
│  ┌──────────┐    BLE    ┌──────────────┐                       │
│  │ Bosch    │◄─────────►│  Inspector   │                       │
│  │ GLM 50C  │           │  Mobile App  │                       │
│  │ (×N)     │           │  (iOS/Android)│                       │
│  └──────────┘           └──────┬───────┘                       │
│                                │                                │
│  ┌──────────┐    BLE    ┌─────┴────────┐                       │
│  │ Bosch    │◄─────────►│   ESP32      │                       │
│  │ GLM 50C  │           │   IoT Bridge │                       │
│  └──────────┘           └──────┬───────┘                       │
│                                │ MQTT                           │
│  ┌──────────┐    BLE    ┌─────┴────────┐                       │
│  │ Bosch    │◄─────────►│   Python     │                       │
│  │ GLM 50C  │           │   BLE Bridge │                       │
│  └──────────┘           └──────┬───────┘                       │
│                                │ WebSocket                      │
└────────────────────────────────┼────────────────────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────┐
│                      CLOUD LAYER                                │
│                                │                                │
│  ┌─────────────────────────────┼─────────────────────────────┐ │
│  │              SUPABASE PLATFORM                             │ │
│  │                             │                              │ │
│  │  ┌──────────┐  ┌───────────┴──┐  ┌───────────────┐       │ │
│  │  │ PostgREST│  │  Realtime    │  │  Edge          │       │ │
│  │  │ REST API │  │  (WebSocket) │  │  Functions     │       │ │
│  │  └────┬─────┘  └──────┬──────┘  └───────┬────────┘       │ │
│  │       │               │                  │                 │ │
│  │  ┌────┴───────────────┴──────────────────┴──────────┐     │ │
│  │  │  PostgreSQL + TimescaleDB                         │     │ │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐│     │ │
│  │  │  │Buildings│ │Measures │ │Devices  │ │Users   ││     │ │
│  │  │  │& Zones  │ │(Hyper-  │ │& Assign │ │& Auth  ││     │ │
│  │  │  │         │ │ table)  │ │         │ │        ││     │ │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └────────┘│     │ │
│  │  └──────────────────────────────────────────────────┘     │ │
│  │                                                            │ │
│  │  ┌──────────┐  ┌──────────┐                               │ │
│  │  │ GoTrue   │  │ Storage  │                               │ │
│  │  │ (Auth)   │  │ (Photos/ │                               │ │
│  │  │          │  │  Reports)│                               │ │
│  │  └──────────┘  └──────────┘                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ AI Engine    │  │ MQTT Broker  │  │ Report Engine │         │
│  │ (FastAPI)    │  │ (Mosquitto)  │  │ (WeasyPrint)  │         │
│  │ - Anomaly    │  │ - IoT msgs   │  │ - PDF reports │         │
│  │ - Classify   │  │ - Device ctl │  │ - Energy certs│         │
│  │ - Energy     │  │ - Status     │  │ - Summaries   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Metabase     │  │ Grafana      │  │ Supervisor   │         │
│  │ (BI Dash)    │  │ (RT Dash)    │  │ Web App      │         │
│  │ - Portfolio  │  │ - Live meas  │  │ - Management │         │
│  │ - Quality    │  │ - Devices    │  │ - Inspections│         │
│  │ - Energy     │  │ - Activity   │  │ - Reports    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow: Measurement Lifecycle

```
1. CAPTURE         2. TRANSMIT          3. VALIDATE         4. STORE           5. ANALYZE
───────────────    ──────────────────   ────────────────    ──────────────    ──────────────
Bosch GLM50C       BLE Notification     On-Device TFLite   Supabase Insert   Metabase Query
  │                  │                    │                   │                 │
  ├─ Laser pulse     ├─ c0 55 10 06...   ├─ Range check     ├─ TimescaleDB    ├─ Portfolio
  ├─ Distance calc   ├─ bytes 7-10       ├─ Anomaly score   ├─ Hypertable     ├─ Quality
  ├─ BLE notify      │  (LE float32)     ├─ Type classify   ├─ RLS enforced   ├─ Energy
  │                  ├─ → meters → mm    ├─ Geometry check  ├─ Realtime pub   ├─ Inspector
  │                  │                    │                   │                 │
  │                  │                    Server-side:        Supabase          Grafana:
  │                  │                    ├─ FastAPI batch    Realtime:         ├─ Live stream
  │                  │                    ├─ Cross-validate   ├─ WebSocket      ├─ Device map
  │                  │                    └─ Flag anomalies   ├─ → Mobile       ├─ Activity
  │                  │                                        ├─ → Dashboard    └─ Alerts
  │                  │                                        └─ → Grafana
```

---

## 4. Technology Stack Summary

### Infrastructure
| Layer | Technology | Role |
|-------|-----------|------|
| Database | PostgreSQL 15 + TimescaleDB | Domain data + time-series measurements |
| Backend | Supabase (self-hosted) | REST API, Realtime, Auth, Storage, Edge Functions |
| Cache | Redis 7 | Session cache, job queues, rate limiting |
| IoT Messaging | Eclipse Mosquitto 2.x | MQTT broker for ESP32 communication |
| AI Inference | FastAPI + scikit-learn | Server-side measurement validation |
| Reporting | WeasyPrint + Jinja2 | HTML→PDF inspection reports |
| BI Analytics | Metabase | Business intelligence dashboards |
| RT Monitoring | Grafana | Real-time IoT and system dashboards |

### Mobile
| Layer | Technology | Role |
|-------|-----------|------|
| Framework | React Native / Expo | Cross-platform iOS + Android |
| BLE | react-native-ble-plx | Native Bluetooth Low Energy |
| State | Zustand + MMKV | Offline-first state management |
| Navigation | React Navigation 6 | Tab + Stack navigation |
| Charts | @shopify/react-native-skia | High-performance data visualization |
| ML | TensorFlow Lite | On-device anomaly detection |
| Build | EAS Build | Cloud-based iOS/Android builds |

### IoT / Hardware
| Layer | Technology | Role |
|-------|-----------|------|
| Rangefinder | Bosch GLM 50C / GLM 50-27CG | Laser distance measurement (BLE) |
| IoT Bridge | ESP32 (PlatformIO) | BLE → WiFi → MQTT gateway |
| BLE Library | NimBLE-Arduino | ESP32 BLE client stack |
| Desktop Bridge | Python (bleak) | Desktop BLE → WebSocket → Supabase |

### DevOps
| Layer | Technology | Role |
|-------|-----------|------|
| Containers | Docker + Docker Compose | Development environment |
| Orchestration | Kubernetes + Helm | Production deployment |
| IaC | Terraform | Cloud infrastructure provisioning |
| Monitoring | Prometheus + Grafana + Loki | Metrics, dashboards, logs |
| CI/CD | GitHub Actions | Automated build, test, deploy |

---

## 5. Component Responsibilities

### Supabase (Replaces Xano)
- **Authentication**: JWT-based login with email/password, magic links, SSO
- **REST API**: Auto-generated CRUD from PostgreSQL schema via PostgREST
- **Realtime**: WebSocket subscriptions for measurement events
- **Edge Functions**: Server-side business logic (energy calculations, sync resolution)
- **Storage**: Inspection photos, PDF reports, building models
- **RLS**: Row-Level Security for multi-tenant data isolation

### Python BLE Bridge (Extends ketan/Bosch-GLM50C-Rangefinder)
- **Multi-device**: Connect up to 5 GLM devices simultaneously
- **Protocol**: Decode Bosch BLE notifications (c0 55 10 06 prefix)
- **Broadcast**: WebSocket server for real-time clients
- **IoT**: MQTT publisher for broker integration
- **Database**: Direct Supabase write client
- **Validation**: Pre-storage measurement validation

### ESP32 IoT Bridge (Extends ketan/Bosch-GLM50C-Rangefinder)
- **BLE Client**: Connect to Bosch GLM50C via NimBLE
- **WiFi**: Captive portal provisioning + auto-reconnect
- **MQTT**: Publish measurements to broker topics
- **OTA**: Over-the-air firmware updates
- **Keyboard**: Legacy BLE keyboard mode (fallback)
- **Status**: LED indicators for connection states

### AI Engine
- **Anomaly Detection**: Isolation Forest model for measurement outliers
- **Classification**: Measurement type inference (height/width/depth)
- **Geometry Validation**: Physical plausibility cross-checks
- **Energy Prediction**: Energy label estimation from building envelope
- **Mobile Export**: TFLite models for on-device inference

### Metabase (BI Dashboards)
- **Inspection Overview**: Pipeline status, completion rates, workload
- **Measurement Quality**: Anomaly rates, accuracy scores, distribution
- **Building Portfolio**: Geographic distribution, building types, coverage
- **Energy Performance**: Label distribution, trends, compliance
- **Inspector Performance**: Productivity, quality, calendar adherence
- **Device Fleet**: Uptime, firmware, assignments, health

### Grafana (Real-Time Dashboards)
- **Live Measurements**: Real-time measurement stream from MQTT/TimescaleDB
- **Device Connectivity**: BLE connection status, RSSI, reconnections
- **Field Activity**: Active inspectors, live progress, photo uploads
- **System Health**: API latency, MQTT throughput, error rates, alerts

---

## 6. Deployment Environments

| Environment | Infrastructure | Purpose |
|-------------|---------------|---------|
| **Local Dev** | Docker Compose on macOS/Linux | Developer workstation |
| **CI/CD** | GitHub Actions + Docker | Automated testing |
| **Staging** | Kubernetes (2 nodes) | Pre-production validation |
| **Production** | Kubernetes (4–6 nodes) + managed PostgreSQL | Live operations |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
