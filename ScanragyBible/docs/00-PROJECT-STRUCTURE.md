# Scarnergy — Complete Project Structure

> **Codename**: Scarnergy (Smart Construction Assessment & Rangefinder Energy Platform)  
> **Organization**: Krontiva Africa  
> **Base Hardware**: Bosch GLM 50C / GLM 50-27CG Laser Rangefinder  
> **Backend Platform**: Supabase (Open Source — replacing Xano)  
> **Dashboards**: Metabase (BI Analytics) + Grafana (Real-Time IoT)  
> **Mobile Framework**: React Native / Expo (iOS + Android)  
> **Last Updated**: February 2026

---

## Vision

Scarnergy is a production-grade building inspection and energy assessment platform that connects Bosch laser rangefinders (via BLE) to a modern, open-source technology stack. Field inspectors capture precision measurements of building facades (gevels), roofs (daken), floors (vloeren), and installations directly from laser devices, which flow in real-time through an intelligent pipeline that validates, stores, computes derived metrics, and surfaces actionable energy performance insights through analytics dashboards and mobile applications.

The platform is novel in three dimensions: (1) direct BLE-to-cloud measurement capture with on-device AI validation, (2) an open-source backend that eliminates proprietary vendor lock-in, and (3) AI-powered anomaly detection that flags measurement inconsistencies before they become costly inspection errors.

---

## Full Directory Tree

```
scarnergy/
│
├── README.md                              # Project overview and quick-start
├── LICENSE                                # Proprietary license
├── docker-compose.yml                     # Full-stack local development
├── docker-compose.prod.yml                # Production deployment overrides
├── .env.example                           # Template for environment variables
├── .gitignore
├── Makefile                               # Common commands (build, test, deploy)
│
│
├── ══════════════════════════════════════
├── 📁 docs/                               # ARCHITECTURE & PLANNING DOCS
├── ══════════════════════════════════════
│   ├── 00-PROJECT-STRUCTURE.md            # This document
│   ├── 01-MILESTONES-CHECKLIST.md         # 2-week sprint plan with checklists
│   ├── 02-IMPLEMENTATION-GUIDE.md         # Master implementation guide
│   ├── 03-PLATFORM-OVERVIEW.md            # Vision, architecture, tech stack
│   ├── 04-SUPABASE-BACKEND.md             # Supabase setup, schema, edge functions
│   ├── 05-BLE-MEASUREMENT-ENGINE.md       # BLE protocol, Python bridge, native BLE
│   ├── 06-MOBILE-APP-REACT-NATIVE.md      # Expo app, screens, forms, offline-first
│   ├── 07-AI-MEASUREMENT-INTELLIGENCE.md  # On-device ML, anomaly detection, validation
│   ├── 08-ESP32-IOT-BRIDGE.md             # ESP32 BLE keyboard + MQTT gateway
│   ├── 09-REALTIME-DATA-PIPELINE.md       # WebSocket, MQTT, Supabase Realtime
│   ├── 10-DASHBOARDS-ANALYTICS.md         # Metabase BI + Grafana real-time
│   ├── 11-DOMAIN-DATA-MODEL.md            # Objects, Rekenzones, Gevels, Daken, etc.
│   ├── 12-ENERGY-CALCULATIONS-ENGINE.md   # NTA 8800 compliance, energy metrics
│   ├── 13-INSPECTION-WORKFLOW.md          # Field inspection lifecycle, scheduling
│   ├── 14-INFRASTRUCTURE-DEPLOYMENT.md    # Docker, K8s, Terraform, monitoring
│   ├── 15-SECURITY-COMPLIANCE.md          # Auth, RBAC, encryption, GDPR
│   ├── 16-TESTING-PRODUCTION.md           # Test strategy, load testing, release
│   ├── 17-DATABASE-SCHEMA.md              # Complete SQL schema for all modules
│   ├── 18-API-REFERENCE.md                # REST + Realtime API contracts
│   └── adr/                               # Architecture Decision Records
│       ├── 001-supabase-over-xano.md
│       ├── 002-metabase-for-bi.md
│       ├── 003-grafana-for-iot.md
│       ├── 004-expo-react-native.md
│       ├── 005-tflite-on-device-ml.md
│       └── 006-mqtt-for-iot-mesh.md
│
│
├── ══════════════════════════════════════
├── 📁 services/                           # MICROSERVICES & BACKEND
├── ══════════════════════════════════════
│   │
│   ├── 📁 supabase/                       # SUPABASE (Backend Platform)
│   │   ├── config.toml                    # Supabase local config
│   │   ├── seed.sql                       # Development seed data
│   │   ├── migrations/                    # Database migrations (timestamped)
│   │   │   ├── 20260201_000_init_schema.sql
│   │   │   ├── 20260201_001_rls_policies.sql
│   │   │   ├── 20260201_002_timescale_hypertables.sql
│   │   │   └── 20260201_003_functions_triggers.sql
│   │   ├── functions/                     # Supabase Edge Functions (Deno)
│   │   │   ├── measurement-ingest/        # High-throughput measurement intake
│   │   │   │   └── index.ts
│   │   │   ├── energy-calculator/         # NTA 8800 energy computation
│   │   │   │   └── index.ts
│   │   │   ├── anomaly-detector/          # Server-side measurement validation
│   │   │   │   └── index.ts
│   │   │   ├── report-generator/          # PDF inspection report builder
│   │   │   │   └── index.ts
│   │   │   ├── sync-resolver/             # Offline-online conflict resolution
│   │   │   │   └── index.ts
│   │   │   └── webhook-handler/           # External event processing
│   │   │       └── index.ts
│   │   └── storage/                       # Supabase Storage buckets config
│   │       ├── inspection-photos/
│   │       ├── reports/
│   │       └── building-models/
│   │
│   ├── 📁 ble-bridge/                     # PYTHON BLE BRIDGE SERVICE
│   │   ├── Dockerfile
│   │   ├── docker-compose.ble.yml
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── main.py                    # BLE scanner + connection manager
│   │   │   ├── glm50c_protocol.py         # Bosch GLM50C BLE protocol decoder
│   │   │   ├── websocket_server.py        # WebSocket broadcast server
│   │   │   ├── mqtt_publisher.py          # MQTT measurement publisher
│   │   │   ├── supabase_sync.py           # Direct Supabase write client
│   │   │   ├── device_manager.py          # Multi-device BLE connection pool
│   │   │   ├── measurement_validator.py   # Pre-storage validation rules
│   │   │   └── config.py                  # Environment + device config
│   │   ├── models/
│   │   │   ├── measurement.py             # Measurement data models
│   │   │   ├── device.py                  # BLE device models
│   │   │   └── status.py                  # Connection status models
│   │   └── tests/
│   │       ├── test_protocol.py
│   │       ├── test_validator.py
│   │       └── test_device_manager.py
│   │
│   ├── 📁 mqtt-broker/                    # ECLIPSE MOSQUITTO MQTT
│   │   ├── Dockerfile
│   │   ├── mosquitto.conf
│   │   ├── acl.conf                       # Topic-level access control
│   │   └── certs/                         # TLS certificates
│   │
│   ├── 📁 ai-engine/                      # AI/ML MEASUREMENT INTELLIGENCE
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── models/
│   │   │   ├── anomaly_detector.py        # Isolation Forest anomaly model
│   │   │   ├── measurement_classifier.py  # Measurement type classifier
│   │   │   ├── building_geometry_validator.py  # Physical plausibility checker
│   │   │   └── energy_predictor.py        # Energy performance predictor
│   │   ├── training/
│   │   │   ├── train_anomaly_model.py     # Training pipeline
│   │   │   ├── train_classifier.py
│   │   │   ├── prepare_dataset.py         # Data preprocessing
│   │   │   └── evaluate.py               # Model evaluation
│   │   ├── inference/
│   │   │   ├── server.py                  # FastAPI inference server
│   │   │   └── tflite_converter.py        # Export to TFLite for mobile
│   │   ├── data/
│   │   │   ├── synthetic_measurements.py  # Synthetic training data generator
│   │   │   └── building_standards.json    # Reference building dimensions
│   │   └── exports/
│   │       ├── anomaly_detector.tflite    # Mobile-ready model
│   │       └── measurement_classifier.tflite
│   │
│   ├── 📁 metabase/                       # METABASE BI DASHBOARDS
│   │   ├── Dockerfile
│   │   ├── docker-compose.metabase.yml
│   │   ├── metabase-config.json
│   │   └── dashboards/
│   │       ├── inspection_overview.json   # Inspection pipeline status
│   │       ├── measurement_quality.json   # Measurement accuracy & anomalies
│   │       ├── building_portfolio.json    # Building stock analytics
│   │       ├── energy_performance.json    # Energy label distribution
│   │       ├── inspector_performance.json # Inspector productivity metrics
│   │       └── device_fleet.json          # Rangefinder device health
│   │
│   ├── 📁 grafana/                        # GRAFANA REAL-TIME DASHBOARDS
│   │   ├── Dockerfile
│   │   ├── provisioning/
│   │   │   ├── datasources/
│   │   │   │   ├── supabase-postgres.yml
│   │   │   │   ├── timescaledb.yml
│   │   │   │   └── mqtt.yml
│   │   │   └── dashboards/
│   │   │       └── dashboards.yml
│   │   └── dashboards/
│   │       ├── live_measurements.json      # Real-time measurement stream
│   │       ├── device_connectivity.json    # BLE device status monitor
│   │       ├── field_activity.json         # Live inspector activity map
│   │       └── system_health.json          # Infrastructure monitoring
│   │
│   └── 📁 report-engine/                  # PDF REPORT GENERATOR
│       ├── Dockerfile
│       ├── src/
│       │   ├── generator.py               # Report orchestrator
│       │   ├── templates/
│       │   │   ├── inspection_report.html # Jinja2 inspection template
│       │   │   ├── energy_label.html      # Energy label certificate
│       │   │   └── summary_report.html    # Executive summary
│       │   └── renderers/
│       │       ├── pdf_renderer.py        # WeasyPrint PDF output
│       │       └── chart_renderer.py      # Matplotlib chart generation
│       └── tests/
│           └── test_generator.py
│
│
├── ══════════════════════════════════════
├── 📁 esp32/                              # ESP32 IoT BRIDGE FIRMWARE
├── ══════════════════════════════════════
│   ├── platformio.ini                     # PlatformIO build config
│   ├── src/
│   │   ├── main.cpp                       # Entry point: BLE + WiFi + MQTT
│   │   ├── ble_scanner.cpp                # Multi-device BLE scanner
│   │   ├── glm50c_client.cpp              # Bosch GLM50C BLE client
│   │   ├── mqtt_client.cpp                # MQTT publish client
│   │   ├── wifi_manager.cpp               # WiFi provisioning + reconnect
│   │   ├── ble_keyboard.cpp               # Legacy BLE keyboard output
│   │   ├── ota_updater.cpp                # Over-the-air firmware updates
│   │   ├── led_status.cpp                 # Status LED controller
│   │   └── config.h                       # Pin definitions, UUIDs, endpoints
│   ├── include/
│   │   ├── ble_scanner.h
│   │   ├── glm50c_client.h
│   │   ├── mqtt_client.h
│   │   └── wifi_manager.h
│   ├── lib/                               # PlatformIO libraries
│   ├── test/
│   │   └── test_protocol_decode.cpp
│   └── docs/
│       ├── wiring_diagram.md
│       └── provisioning_guide.md
│
│
├── ══════════════════════════════════════
├── 📁 mobile/                             # MOBILE APPLICATIONS
├── ══════════════════════════════════════
│   │
│   ├── 📁 inspector-app/                  # INSPECTOR MOBILE APP (Expo)
│   │   ├── app.json                       # Expo config (BLE, camera, location)
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── eas.json                       # EAS Build configuration
│   │   ├── index.ts                       # App entry point
│   │   ├── App.tsx                        # Root with providers
│   │   ├── src/
│   │   │   ├── navigation/
│   │   │   │   ├── AppNavigator.tsx       # Tab + stack navigation
│   │   │   │   └── types.ts              # Route type definitions
│   │   │   ├── screens/
│   │   │   │   ├── HomeScreen.tsx         # Object list + search
│   │   │   │   ├── CalendarScreen.tsx     # Visit calendar
│   │   │   │   ├── MeasurementScreen.tsx  # Live measurement dashboard
│   │   │   │   ├── ObjectDetailScreen.tsx # Building detail + zones
│   │   │   │   ├── GevelDetailScreen.tsx  # Facade detail + measurements
│   │   │   │   ├── DakDetailScreen.tsx    # Roof detail + measurements
│   │   │   │   ├── VloerDetailScreen.tsx  # Floor detail + measurements
│   │   │   │   ├── InstallatieScreen.tsx  # Installation equipment
│   │   │   │   ├── PhotoCaptureScreen.tsx # Inspection photo capture
│   │   │   │   ├── ReportScreen.tsx       # Generate/preview reports
│   │   │   │   ├── DeviceManagerScreen.tsx # BLE device pairing
│   │   │   │   ├── SettingsScreen.tsx     # App configuration
│   │   │   │   └── SyncScreen.tsx         # Offline/online sync status
│   │   │   ├── components/
│   │   │   │   ├── forms/
│   │   │   │   │   ├── GevelForm.tsx      # Facade measurement form
│   │   │   │   │   ├── DakForm.tsx        # Roof measurement form
│   │   │   │   │   ├── VloerForm.tsx      # Floor measurement form
│   │   │   │   │   ├── InstallatieForm.tsx # Installation form
│   │   │   │   │   ├── TransparantDeelForm.tsx # Opening form
│   │   │   │   │   └── MeasurementInput.tsx # BLE-linked measurement field
│   │   │   │   ├── ble/
│   │   │   │   │   ├── BLEDeviceList.tsx  # Discovered device list
│   │   │   │   │   ├── BLEStatusBadge.tsx # Connection status indicator
│   │   │   │   │   └── MeasurementStream.tsx # Live measurement ticker
│   │   │   │   ├── charts/
│   │   │   │   │   ├── MeasurementChart.tsx # Measurement trend chart
│   │   │   │   │   ├── EnergyGauge.tsx    # Energy label gauge
│   │   │   │   │   └── AreaBreakdown.tsx  # Building area breakdown
│   │   │   │   ├── maps/
│   │   │   │   │   └── BuildingMap.tsx    # Building location map
│   │   │   │   └── common/
│   │   │   │       ├── Card.tsx
│   │   │   │       ├── Badge.tsx
│   │   │   │       ├── LoadingSpinner.tsx
│   │   │   │       └── ErrorBoundary.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useBLE.ts              # BLE connection hook (react-native-ble-plx)
│   │   │   │   ├── useGLM50C.ts           # Bosch-specific BLE protocol hook
│   │   │   │   ├── useWebSocket.ts        # WebSocket measurement hook
│   │   │   │   ├── useMeasurement.ts      # Measurement state management
│   │   │   │   ├── useOfflineSync.ts      # Offline queue + sync
│   │   │   │   ├── useSupabase.ts         # Supabase client hook
│   │   │   │   └── useAnomalyDetection.ts # On-device TFLite inference
│   │   │   ├── services/
│   │   │   │   ├── supabaseClient.ts      # Supabase JS client init
│   │   │   │   ├── measurementService.ts  # CRUD + real-time subscriptions
│   │   │   │   ├── objectService.ts       # Building objects API
│   │   │   │   ├── inspectionService.ts   # Inspection workflow API
│   │   │   │   ├── syncService.ts         # Offline sync queue manager
│   │   │   │   ├── bleProtocol.ts         # GLM50C BLE protocol decoder
│   │   │   │   ├── energyCalculator.ts    # Client-side energy computation
│   │   │   │   └── reportService.ts       # Report generation trigger
│   │   │   ├── store/
│   │   │   │   ├── index.ts               # Zustand store root
│   │   │   │   ├── measurementStore.ts    # Measurement state
│   │   │   │   ├── objectStore.ts         # Building object state
│   │   │   │   ├── bleStore.ts            # BLE device state
│   │   │   │   ├── syncStore.ts           # Sync queue state
│   │   │   │   └── settingsStore.ts       # User preferences
│   │   │   ├── models/
│   │   │   │   ├── types.ts               # Domain type definitions
│   │   │   │   ├── measurement.ts         # Measurement types
│   │   │   │   ├── ble.ts                 # BLE device types
│   │   │   │   └── enums.ts               # Shared enums
│   │   │   ├── utils/
│   │   │   │   ├── geometry.ts            # Area/perimeter calculations
│   │   │   │   ├── conversion.ts          # Unit conversions
│   │   │   │   ├── validation.ts          # Input validation rules
│   │   │   │   └── formatting.ts          # Display formatters
│   │   │   ├── providers/
│   │   │   │   ├── MeasurementProvider.tsx # Measurement context
│   │   │   │   ├── BLEProvider.tsx        # BLE context
│   │   │   │   ├── AuthProvider.tsx       # Supabase auth context
│   │   │   │   └── SyncProvider.tsx       # Sync status context
│   │   │   ├── ai/
│   │   │   │   ├── AnomalyDetector.ts     # TFLite model runner
│   │   │   │   ├── MeasurementClassifier.ts # Measurement type inference
│   │   │   │   └── models/               # .tflite model files
│   │   │   │       ├── anomaly_detector.tflite
│   │   │   │       └── classifier.tflite
│   │   │   └── data/
│   │   │       ├── sampleData.ts          # Offline demo data
│   │   │       └── referenceValues.ts     # Building standard references
│   │   └── assets/
│   │       ├── icons/
│   │       ├── images/
│   │       └── fonts/
│   │
│   └── 📁 supervisor-app/                 # SUPERVISOR WEB APP (React)
│       ├── package.json
│       ├── src/
│       │   ├── pages/
│       │   │   ├── Dashboard/             # Portfolio overview
│       │   │   ├── Inspections/           # Inspection management
│       │   │   ├── Buildings/             # Building inventory
│       │   │   ├── Reports/               # Report review + export
│       │   │   ├── Devices/               # Device fleet management
│       │   │   ├── Inspectors/            # Inspector management
│       │   │   └── Settings/              # System settings
│       │   ├── components/
│       │   └── lib/
│       └── Dockerfile
│
│
├── ══════════════════════════════════════
├── 📁 deploy/                             # DEPLOYMENT & INFRASTRUCTURE
├── ══════════════════════════════════════
│   ├── docker/
│   │   ├── Dockerfile.ble-bridge
│   │   ├── Dockerfile.ai-engine
│   │   ├── Dockerfile.report-engine
│   │   └── nginx/
│   │       ├── nginx.conf
│   │       └── ssl/
│   ├── kubernetes/
│   │   ├── namespaces/
│   │   ├── supabase/
│   │   ├── metabase/
│   │   ├── grafana/
│   │   ├── mqtt/
│   │   ├── ai-engine/
│   │   └── monitoring/
│   └── terraform/
│       ├── main.tf
│       ├── variables.tf
│       └── gcp/
│
│
├── ══════════════════════════════════════
├── 📁 monitoring/                         # OBSERVABILITY
├── ══════════════════════════════════════
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   └── provisioning/
│   ├── loki/
│   │   └── loki-config.yml
│   └── alertmanager/
│       └── alertmanager.yml
│
│
├── ══════════════════════════════════════
├── 📁 tests/                              # TESTING
├── ══════════════════════════════════════
│   ├── unit/
│   │   ├── ble-protocol/
│   │   ├── energy-calculations/
│   │   ├── measurement-validation/
│   │   └── data-model/
│   ├── integration/
│   │   ├── supabase-sync/
│   │   ├── ble-to-cloud/
│   │   ├── mqtt-pipeline/
│   │   └── offline-sync/
│   ├── e2e/
│   │   ├── inspection_flow.spec.ts
│   │   ├── measurement_capture.spec.ts
│   │   └── report_generation.spec.ts
│   ├── performance/
│   │   ├── measurement_throughput.yml
│   │   └── concurrent_devices.yml
│   └── fixtures/
│       ├── sample_measurements.json
│       ├── sample_buildings.json
│       └── ble_packet_captures.json
│
│
└── ══════════════════════════════════════
    📁 scripts/                            # UTILITY SCRIPTS
    ══════════════════════════════════════
    ├── setup.sh                           # One-command dev environment
    ├── seed_data.sh                       # Seed development data
    ├── migrate.sh                         # Database migrations
    ├── flash_esp32.sh                     # ESP32 firmware flash
    ├── train_models.sh                    # AI model training pipeline
    ├── export_tflite.sh                   # Export models for mobile
    ├── health_check.sh                    # Service health checks
    └── deploy.sh                          # Production deployment
```

---

## Service Port Registry

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Supabase Studio | 3000 | HTTP | Database admin UI |
| Supabase API (PostgREST) | 3001 | HTTP | REST API + Realtime |
| Supabase Auth (GoTrue) | 9999 | HTTP | Authentication |
| Supabase Storage | 5000 | HTTP | File storage API |
| Supabase Edge Functions | 54321 | HTTP | Serverless functions |
| PostgreSQL + TimescaleDB | 5432 | TCP | Primary database |
| Inspector App (Expo) | 8081 | HTTP | Metro bundler |
| Supervisor Web App | 3002 | HTTP | React admin app |
| BLE Bridge WebSocket | 8765 | WS | Live measurement stream |
| MQTT Broker (Mosquitto) | 1883 | MQTT | IoT device messaging |
| MQTT Broker (TLS) | 8883 | MQTTS | IoT device messaging (secure) |
| MQTT WebSocket | 9001 | WS | Browser MQTT client |
| AI Engine (FastAPI) | 8500 | HTTP | ML inference API |
| Report Engine | 8600 | HTTP | PDF report generation |
| Metabase | 3003 | HTTP | BI dashboards |
| Grafana | 3030 | HTTP | Real-time IoT dashboards |
| Prometheus | 9090 | HTTP | Metrics collection |
| Redis | 6379 | TCP | Cache + job queues |

---

## Key Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Platform | **Supabase** (self-hosted) | Open-source PostgreSQL BaaS; replaces Xano with real-time, auth, edge functions, storage; no vendor lock-in |
| BI Dashboards | **Metabase** | Open-source, intuitive no-SQL-required BI; ideal for inspection analytics and building portfolio views |
| Real-Time Dashboards | **Grafana** | Best-in-class time-series visualization; MQTT + PostgreSQL sources for live measurement monitoring |
| Mobile Framework | **React Native / Expo** | Cross-platform iOS + Android; EAS Build for native BLE; existing codebase continuity |
| Native BLE | **react-native-ble-plx** | Production-grade BLE library for direct Bosch GLM50C connection from mobile |
| BLE Bridge | **Python (bleak)** | Desktop/server BLE connectivity; extends ketan/Bosch-GLM50C-Rangefinder |
| IoT Messaging | **Eclipse Mosquitto** | Lightweight MQTT broker for ESP32 ↔ cloud communication |
| Time-Series DB | **TimescaleDB** | PostgreSQL extension for hypertable measurement storage; seamless with Supabase |
| AI/ML | **scikit-learn + TFLite** | Anomaly detection + measurement classification; TFLite for on-device mobile inference |
| State Management | **Zustand** | Lightweight, React-hooks-based state; offline-first with persistence |
| Report Generation | **WeasyPrint** | Open-source HTML→PDF; Jinja2 templates for inspection reports |
| Auth | **Supabase Auth (GoTrue)** | JWT-based, supports email/password, magic links, SSO |
| ESP32 Platform | **PlatformIO + NimBLE** | Production firmware toolchain; extends ketan/Bosch-GLM50C-Rangefinder ESP32 code |

---

## Open-Source Projects Extended

| Project | Source | What We Extend |
|---------|--------|----------------|
| Bosch-GLM50C-Rangefinder | github.com/ketan/Bosch-GLM50C-Rangefinder | BLE protocol, Python bridge, ESP32 client — enhanced with multi-device, MQTT, WebSocket, Supabase sync |
| Supabase | github.com/supabase/supabase | Self-hosted backend — customized with TimescaleDB, custom edge functions, building inspection schema |
| Metabase | github.com/metabase/metabase | BI platform — configured with inspection-specific dashboards and embedded analytics |
| Grafana | github.com/grafana/grafana | Monitoring — configured with MQTT + TimescaleDB datasources for real-time IoT |
| Eclipse Mosquitto | github.com/eclipse/mosquitto | MQTT broker — configured with ACLs for device-level topic security |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
