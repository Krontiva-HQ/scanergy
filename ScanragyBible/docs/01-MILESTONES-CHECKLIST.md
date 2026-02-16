# Scarnergy — 2-Week Sprint: Milestones & Master Checklist

> **Sprint Duration**: 2 weeks (10 working days)  
> **Team Assumption**: 2–3 engineers + 1 mobile dev + 1 DevOps  
> **Infrastructure**: Docker Compose (dev) → Kubernetes (prod)  
> **Starting Point**: Existing Expo app + ketan/Bosch-GLM50C-Rangefinder codebase

---

## Sprint Overview Map

```
Day   1    2    3    4    5    6    7    8    9    10
      ├────── M1 ──────┤
                ├──────── M2 ────────┤
                     ├──────── M3 ────────┤
                                    ├──────── M4 ────────┤
                                         ├──── M5 ────┤
                                                   ├── M6 ──┤
```

| # | Milestone | Days | Dependencies | Deliverables |
|---|-----------|------|-------------|--------------|
| **M1** | Foundation: Supabase + Schema | Days 1–3 | None | Supabase running, full schema deployed, seed data, auth configured |
| **M2** | BLE Engine: Multi-Device + Real-Time | Days 2–5 | M1 (partial) | Enhanced Python bridge, MQTT broker, WebSocket server, Supabase sync |
| **M3** | Mobile App: Production Rebuild | Days 3–7 | M1, M2 | Expo app with native BLE, offline-first, Supabase integration, all forms |
| **M4** | AI/ML: Measurement Intelligence | Days 5–8 | M1 | Anomaly detection model trained, TFLite exported, FastAPI server, mobile integration |
| **M5** | Dashboards: Metabase + Grafana | Days 7–9 | M1, M2 | 6 Metabase dashboards, 4 Grafana panels, embedded analytics |
| **M6** | Integration, Testing & Deployment | Days 9–10 | All | E2E tests, Docker prod stack, deployment scripts, documentation finalized |

---

## Milestone 1: Foundation — Supabase Backend + Database Schema
**Duration**: Days 1–3 | **Risk**: Low | **Owner**: Backend Engineer

### Objectives
Deploy self-hosted Supabase, create the complete building inspection database schema with TimescaleDB for measurements, configure authentication, and set up edge functions for core business logic.

### Checklist

#### Day 1: Supabase Infrastructure
- [ ] **1.1** Initialize Git repository with full directory structure (see `00-PROJECT-STRUCTURE.md`)
- [ ] **1.2** Create `docker-compose.yml` with Supabase stack (postgres, gotrue, postgrest, realtime, storage, studio)
- [ ] **1.3** Add TimescaleDB extension to PostgreSQL container
- [ ] **1.4** Create `.env.example` with all required variables (JWT secret, API keys, DB credentials)
- [ ] **1.5** Deploy PostgreSQL 15 + TimescaleDB with extensions: `uuid-ossp`, `postgis`, `pg_trgm`, `timescaledb`
- [ ] **1.6** Configure Supabase Studio at `localhost:3000`
- [ ] **1.7** Configure GoTrue auth with email/password + magic link providers
- [ ] **1.8** Verify Supabase REST API: `curl http://localhost:3001/rest/v1/` returns schema
- [ ] **1.9** Configure Supabase Realtime for measurement subscriptions
- [ ] **1.10** Set up Redis for caching and edge function job queues

#### Day 2: Database Schema + Seed Data
- [ ] **1.11** Create migration: `20260201_000_init_schema.sql` — Core tables:
  - `organizations` (multi-tenant root)
  - `users` (inspectors, supervisors, admins)
  - `objects` (buildings: address, postcode, status, schedule)
  - `rekenzones` (calculation zones per building)
  - `gevels` (facades: position, orientation, dimensions, area)
  - `daken` (roofs: type, slope, orientation, area)
  - `vloeren` (floors: insulation, area, perimeter)
  - `installaties` (installations: type, model, location)
  - `transparante_delen` (openings: dimensions, count, material)
  - `dakkapellen` (dormers: attributes, opening area)
  - `inspections` (inspection events: status, inspector, timestamps)
  - `calendar_visits` (scheduled visits: date, time, object, inspector)
- [ ] **1.12** Create migration: `20260201_001_measurements.sql` — Measurement tables:
  - `measurements` (TimescaleDB hypertable: value_mm, raw_hex, source, device_id, timestamp)
  - `measurement_sessions` (grouping: inspection_id, element_type, element_id)
  - `devices` (BLE devices: name, address, firmware, last_seen)
  - `device_assignments` (device → inspector mapping)
- [ ] **1.13** Create migration: `20260201_002_rls_policies.sql` — Row-Level Security:
  - Organization-scoped read/write on all tables
  - Inspector can only see assigned objects
  - Supervisor sees all within organization
- [ ] **1.14** Create migration: `20260201_003_functions_triggers.sql`:
  - `calculate_gross_area()` trigger on gevel/dak/vloer insert/update
  - `calculate_net_area()` trigger subtracting openings
  - `update_measurement_stats()` trigger on measurement insert
  - `resolve_energy_label()` function for NTA 8800 computation
- [ ] **1.15** Create `seed.sql` with sample data:
  - 3 organizations, 10 users (inspectors/supervisors)
  - 25 buildings with full zone/element hierarchies
  - 500 sample measurements across multiple sessions
  - 15 devices with assignment history
- [ ] **1.16** Run migrations and verify: all tables created, RLS active, seed data loaded

#### Day 3: Edge Functions + Storage + API
- [ ] **1.17** Create Edge Function: `measurement-ingest` — High-throughput measurement intake:
  - Accepts batch measurements from BLE bridge / MQTT / mobile
  - Validates format, runs basic range checks
  - Inserts into TimescaleDB hypertable
  - Publishes to Supabase Realtime channel
- [ ] **1.18** Create Edge Function: `energy-calculator` — NTA 8800 computation:
  - Accepts building object ID
  - Fetches all zones, elements, measurements
  - Computes energy performance indicators
  - Returns energy label (A–G) with breakdown
- [ ] **1.19** Create Edge Function: `sync-resolver` — Offline conflict resolution:
  - Accepts offline mutation queue from mobile
  - Resolves conflicts using last-write-wins with vector clocks
  - Returns resolution report
- [ ] **1.20** Configure Supabase Storage buckets:
  - `inspection-photos` (public read, authenticated write, 10MB limit)
  - `reports` (authenticated read/write, 50MB limit)
  - `building-models` (authenticated read/write)
- [ ] **1.21** Verify complete API surface:
  - REST CRUD for all domain tables
  - Realtime subscriptions for measurements
  - Edge functions respond correctly
  - Storage upload/download works
- [ ] **1.22** Create `scripts/setup.sh` for one-command dev environment
- [ ] **1.23** Create `scripts/seed_data.sh` to reset and reload sample data

### Exit Criteria
- [ ] `docker compose up` brings up full Supabase stack + TimescaleDB + Redis
- [ ] All 15+ tables created with RLS policies active
- [ ] REST API returns data for all endpoints with proper auth
- [ ] Realtime subscription delivers measurement events within 100ms
- [ ] Edge functions execute and return correct results
- [ ] Seed data provides realistic demo experience

---

## Milestone 2: BLE Measurement Engine — Multi-Device + Real-Time Pipeline
**Duration**: Days 2–5 | **Risk**: Medium | **Owner**: IoT/Backend Engineer

### Objectives
Enhance the ketan/Bosch-GLM50C-Rangefinder Python bridge for multi-device support, add MQTT broker for ESP32 communication, build WebSocket server for mobile/web clients, and create the real-time measurement pipeline from device to database.

### Checklist

#### Day 2–3: Enhanced Python BLE Bridge
- [ ] **2.1** Fork and restructure ketan/Bosch-GLM50C-Rangefinder Python code into `services/ble-bridge/src/`
- [ ] **2.2** Refactor `glm50c_protocol.py` — Clean protocol decoder:
  - Service UUID: `02A6C0D0-0451-4000-B000-FB3210111989`
  - Characteristic: `02A6C0D1-0451-4000-B000-FB3210111989`
  - Packet validation: prefix `c0 55 10 06`
  - Measurement extraction: bytes 7–10 → little-endian float32 → meters → mm
  - Enable notifications write: `[0xC0, 0x55, 0x02, 0x01, 0x00, 0x1A]`
- [ ] **2.3** Build `device_manager.py` — Multi-device BLE connection pool:
  - Concurrent connections to up to 5 GLM devices
  - Auto-reconnect with exponential backoff
  - Device health monitoring (RSSI, battery, last measurement)
  - Device registration → Supabase `devices` table
- [ ] **2.4** Build `measurement_validator.py` — Pre-storage validation:
  - Range checks: 0.05m to 50m (GLM50C spec)
  - Rate limiting: max 2 measurements/second per device
  - Duplicate detection: reject identical values within 500ms window
  - Checksum verification on raw BLE packets
- [ ] **2.5** Build `supabase_sync.py` — Direct database writer:
  - Batch insert measurements (up to 100 per batch)
  - Supabase JS client for auth + real-time
  - Retry logic with dead-letter queue for failed inserts
- [ ] **2.6** Enhance `websocket_server.py`:
  - Multi-client broadcast (up to 50 concurrent clients)
  - Client command handling (connect device, disconnect, request status)
  - Measurement and status message types with JSON schema
  - Heartbeat/keepalive for mobile clients
- [ ] **2.7** Build `mqtt_publisher.py` — MQTT integration:
  - Publish measurements to `scarnergy/measurements/{device_id}`
  - Publish device status to `scarnergy/devices/{device_id}/status`
  - Subscribe to `scarnergy/commands/{device_id}` for remote control
  - QoS 1 for measurements, QoS 0 for status
- [ ] **2.8** Containerize BLE bridge with Dockerfile and docker-compose service

#### Day 4–5: MQTT Broker + ESP32 Enhancement
- [ ] **2.9** Deploy Eclipse Mosquitto MQTT broker:
  - Configure `mosquitto.conf` with persistence
  - Set up ACL: device-level publish, service-level subscribe
  - Enable WebSocket listener on port 9001 (for browser clients)
  - Configure TLS for production (port 8883)
- [ ] **2.10** Enhance ESP32 firmware (extend ketan/Bosch-GLM50C-Rangefinder):
  - Add WiFi manager with captive portal provisioning
  - Add MQTT client: publish measurements to broker
  - Add multi-device BLE scanner (connect to nearest GLM device)
  - Add OTA firmware update support
  - Add status LED controller (BLE connected / WiFi connected / error states)
  - Retain BLE keyboard mode as fallback
- [ ] **2.11** Build ESP32 → MQTT → Supabase pipeline:
  - ESP32 publishes to MQTT broker
  - Python bridge subscribes to MQTT, writes to Supabase
  - Verify end-to-end: ESP32 measurement → MQTT → Python → Supabase → Realtime → Client
- [ ] **2.12** Create `control.json` protocol for remote device management:
  - `reconnect_device` — force reconnect to specific GLM
  - `set_measurement_mode` — single/continuous
  - `request_status` — trigger status report
  - `firmware_update` — trigger OTA
- [ ] **2.13** Write unit tests for protocol decoder and validator
- [ ] **2.14** Write integration tests for BLE → WebSocket → Supabase flow

### Exit Criteria
- [ ] Python bridge maintains connection GLM devices
- [ ] Measurements flow: BLE → Python → WebSocket + MQTT + Supabase in <200ms
- [ ] ESP32 connects to WiFi, publishes measurements via MQTT
- [ ] MQTT broker handles 100+ messages/second with persistence
- [ ] Invalid measurements are rejected with error codes
- [ ] WebSocket broadcasts to 10+ clients simultaneously

---

## Milestone 3: Mobile App — Production Rebuild (iOS + Android)
**Duration**: Days 3–7 | **Risk**: High | **Owner**: Mobile Developer

### Objectives
Rebuild the Expo app for production with native BLE integration, Supabase backend, offline-first architecture, all measurement forms, and real-time dashboard. Target iOS and Android via EAS Build.

### Checklist

#### Day 3–4: App Foundation + Supabase Integration
- [ ] **3.1** Initialize Expo project with EAS Build configuration
- [ ] **3.2** Configure `app.json` with BLE, camera, location, and storage permissions
- [ ] **3.3** Install core dependencies:
  - `@supabase/supabase-js` — Backend client
  - `react-native-ble-plx` — Native BLE (via dev client)
  - `zustand` — State management with persist middleware
  - `@react-navigation/native` + `@react-navigation/bottom-tabs` + `@react-navigation/stack`
  - `react-native-mmkv` — Fast key-value storage for offline
  - `@shopify/react-native-skia` — High-performance charts
  - `react-native-reanimated` — Smooth animations
  - `expo-camera` — Photo capture
  - `expo-location` — Building geolocation
- [ ] **3.4** Set up Supabase client with auth flow:
  - Email/password login
  - JWT token management with refresh
  - Session persistence via MMKV
- [ ] **3.5** Build `AuthProvider.tsx` — Authentication context:
  - Login/logout/register flows
  - Role-based access (inspector/supervisor/admin)
  - Supabase auth state listener
- [ ] **3.6** Build `AppNavigator.tsx` — Tab + Stack navigation:
  - Bottom tabs: Home, Calendar, Measure, Devices, Settings
  - Stack screens: ObjectDetail, GevelDetail, DakDetail, VloerDetail, etc.
- [ ] **3.7** Build `SyncProvider.tsx` — Offline-first sync engine:
  - Queue mutations in MMKV when offline
  - Sync on reconnect with conflict resolution
  - Visual sync status indicator

#### Day 5–6: Screens + BLE Integration
- [ ] **3.8** Rebuild `HomeScreen.tsx` — Object list:
  - Supabase query with real-time subscription
  - Pull-to-refresh + infinite scroll
  - Search/filter by address, status, inspector
  - Offline: reads from Zustand persisted store
- [ ] **3.9** Rebuild `ObjectDetailScreen.tsx` — Building detail:
  - Related rekenzones, gevels, daken, vloeren, installaties
  - Inline add/edit for each element type
  - Photo gallery from Supabase Storage
  - Map view of building location
- [ ] **3.10** Rebuild all measurement forms (connecting to BLE):
  - `GevelForm.tsx` — Facade: position, orientation, height/width (BLE fill), area computation
  - `DakForm.tsx` — Roof: type, slope angle, orientation, dimensions (BLE fill)
  - `VloerForm.tsx` — Floor: insulation flags, area, perimeter (BLE fill)
  - `InstallatieForm.tsx` — Installation: type, model, location, photo
  - `TransparantDeelForm.tsx` — Opening: dimensions, count, material
  - `MeasurementInput.tsx` — Universal BLE-linked input field component:
    - Tap to capture next BLE measurement into this field
    - Visual feedback: pulsing when waiting, green flash on capture
    - Manual override entry
    - Unit conversion (mm/cm/m)
- [ ] **3.11** Build `useBLE.ts` hook — React Native BLE integration:
  - Scan for Bosch GLM devices (service UUID filter)
  - Connect/disconnect management
  - Subscribe to measurement notifications
  - Decode GLM50C protocol (port from Python)
  - Permission handling (iOS/Android differences)
- [ ] **3.12** Build `useGLM50C.ts` hook — Bosch-specific protocol:
  - Write enable notification command
  - Parse measurement packets
  - Extract distance value (bytes 7-10, LE float32)
  - Emit measurement events with metadata
- [ ] **3.13** Build `MeasurementScreen.tsx` — Live measurement dashboard:
  - Active device connection status
  - Live measurement stream with history
  - Statistics: count, average, min, max, std dev
  - Measurement session management (assign to building element)

#### Day 7: Calendar, Reports, Offline Sync
- [ ] **3.14** Build `CalendarScreen.tsx` — Visit calendar:
  - Monthly/weekly view with scheduled inspections
  - Supabase query for `calendar_visits`
  - Tap to navigate to building detail
  - Color coding by status (pending/in-progress/complete)
- [ ] **3.15** Build `DeviceManagerScreen.tsx` — BLE device pairing:
  - Scan for nearby GLM devices
  - Pair/unpair management
  - Device health display (RSSI, battery estimate, firmware)
  - Multi-device list with active connection indicators
- [ ] **3.16** Build `ReportScreen.tsx` — Report generation:
  - Trigger report generation via Edge Function
  - Preview report in-app via WebView
  - Download/share PDF via Supabase Storage
- [ ] **3.17** Build `SyncScreen.tsx` — Offline sync status:
  - Pending mutations queue display
  - Sync progress indicator
  - Conflict resolution UI
  - Force sync button
- [ ] **3.18** Build `PhotoCaptureScreen.tsx` — Inspection photos:
  - Camera capture with metadata (GPS, timestamp, element ID)
  - Upload to Supabase Storage
  - Thumbnail gallery on element detail screens
- [ ] **3.19** Configure EAS Build for iOS and Android:
  - Development client with native BLE module
  - iOS provisioning profile configuration
  - Android signing key configuration
- [ ] **3.20** Test complete flow: Login → Select building → Open facade → Capture BLE measurement → Save → Sync

### Exit Criteria
- [ ] App runs on both iOS and Android via EAS development client
- [ ] BLE connects to Bosch GLM50C and captures measurements in <100ms
- [ ] All forms save to Supabase with real-time sync
- [ ] Offline mode: capture measurements and queue mutations without network
- [ ] Sync resolves offline queue when network returns
- [ ] Calendar displays scheduled visits from Supabase
- [ ] Photos upload to Supabase Storage and display in element detail

---

## Milestone 4: AI/ML — Measurement Intelligence
**Duration**: Days 5–8 | **Risk**: Medium | **Owner**: ML Engineer / Backend Engineer

### Objectives
Train an anomaly detection model on building measurement data, export to TFLite for on-device mobile inference, build a FastAPI inference server for server-side validation, and integrate into the measurement pipeline.

### Checklist

#### Day 5–6: Training Pipeline + Models
- [ ] **4.1** Build `synthetic_measurements.py` — Training data generator:
  - Generate 50,000+ realistic building measurements:
    - Facade heights: 2.4–15m (normal distribution, σ=2.5)
    - Facade widths: 1.5–20m
    - Roof slopes: 15–60° (common Dutch roof types)
    - Floor areas: 10–500m²
    - Window dimensions: 0.4–3m
  - Inject anomalies (5% of data):
    - Out-of-range values (negative, >50m)
    - Physically impossible combinations (height > 30m for residential)
    - Duplicate rapid-fire readings
    - Corrupted hex values
  - Label: normal=0, anomaly=1 with anomaly type
- [ ] **4.2** Build `building_standards.json` — Reference data:
  - Dutch building dimension standards (NEN norms)
  - Typical ranges by building type (residential, commercial, industrial)
  - Material-specific constraints
- [ ] **4.3** Train `anomaly_detector.py` — Isolation Forest model:
  - Features: value_mm, measurement_rate, time_since_last, element_type, session_stats
  - Isolation Forest with contamination=0.05
  - Cross-validation with F1-score optimization
  - Export: scikit-learn joblib + TFLite conversion
  - Target: >95% precision, >85% recall on test set
- [ ] **4.4** Train `measurement_classifier.py` — Measurement type classifier:
  - Classify measurement intent: height, width, depth, diagonal, perimeter segment
  - Features: value range, sequence position, preceding measurements
  - Random Forest with feature importance analysis
  - Export to TFLite
- [ ] **4.5** Build `building_geometry_validator.py` — Physical plausibility:
  - Rule-based + ML hybrid validator
  - Cross-check: wall height × width ≈ reported gross area
  - Cross-check: sum of opening areas < gross facade area
  - Cross-check: roof area ≥ floor area (for top floor)
  - Flag inconsistencies with confidence scores
- [ ] **4.6** Build `energy_predictor.py` — Energy performance estimator:
  - Input: building envelope measurements + installation types
  - Output: predicted energy label (A-G) with confidence
  - Training on public Dutch energy label dataset (EP-Online)
  - Gradient Boosting with SHAP explanations

#### Day 7–8: Inference Server + Mobile Integration
- [ ] **4.7** Build FastAPI inference server (`ai-engine/inference/server.py`):
  - `POST /validate` — Validate single measurement
  - `POST /validate-batch` — Validate batch measurements
  - `POST /classify` — Classify measurement type
  - `POST /check-geometry` — Cross-validate building geometry
  - `POST /predict-energy` — Predict energy label
  - Prometheus metrics endpoint
  - Health check endpoint
- [ ] **4.8** Build `tflite_converter.py` — Export models for mobile:
  - Convert anomaly detector to TFLite (quantized INT8)
  - Convert classifier to TFLite
  - Validate: TFLite output matches scikit-learn output
  - Target model size: <2MB each
- [ ] **4.9** Integrate TFLite into mobile app:
  - `AnomalyDetector.ts` — Run anomaly detection on each measurement
  - `MeasurementClassifier.ts` — Suggest measurement type
  - Visual feedback: green (normal), yellow (warning), red (anomaly)
  - Confidence score display
- [ ] **4.10** Integrate AI engine into measurement pipeline:
  - BLE bridge calls AI engine for server-side validation
  - Edge Function calls AI engine for batch validation on sync
  - Anomaly flags stored in `measurements` table
  - Dashboard shows anomaly rate metrics
- [ ] **4.11** Write model evaluation report:
  - Confusion matrix, ROC curves, precision-recall
  - Feature importance analysis
  - Latency benchmarks (server + mobile)
- [ ] **4.12** Containerize AI engine with Dockerfile

### Exit Criteria
- [ ] Anomaly detector achieves >95% precision, >85% recall
- [ ] TFLite models run on mobile in <50ms per inference
- [ ] FastAPI server responds in <100ms for single validation
- [ ] Measurement pipeline flags anomalies in real-time
- [ ] Energy predictor provides label estimate within ±1 class
- [ ] Models are <2MB each (suitable for mobile distribution)

---

## Milestone 5: Dashboards — Metabase BI + Grafana Real-Time
**Duration**: Days 7–9 | **Risk**: Low | **Owner**: Backend / Data Engineer

### Objectives
Deploy Metabase for business intelligence dashboards (inspection portfolio, measurement quality, energy performance) and Grafana for real-time IoT monitoring (live measurements, device connectivity, field activity).

### Checklist

#### Day 7–8: Metabase BI Dashboards
- [ ] **5.1** Deploy Metabase with Docker:
  - PostgreSQL metadata database
  - Connect to Supabase PostgreSQL as data source
  - Configure admin account and organization
- [ ] **5.2** Build Dashboard: **Inspection Overview**
  - Total objects by status (pending/in-progress/complete)
  - Inspection completion rate over time
  - Average time per inspection
  - Upcoming visits calendar heatmap
  - Inspector workload distribution
- [ ] **5.3** Build Dashboard: **Measurement Quality**
  - Total measurements captured (daily/weekly/monthly)
  - Anomaly rate trend
  - Measurement distribution by type (height/width/area)
  - Top anomaly reasons breakdown
  - Measurement accuracy score per inspector
- [ ] **5.4** Build Dashboard: **Building Portfolio**
  - Building count by type, region, status
  - Geographic distribution map (PostGIS)
  - Average building dimensions by type
  - Zone coverage completeness
  - Missing element tracking
- [ ] **5.5** Build Dashboard: **Energy Performance**
  - Energy label distribution (A–G pie chart)
  - Energy score trend over time
  - Building comparison matrix
  - Improvement recommendation frequency
  - NTA 8800 compliance status
- [ ] **5.6** Build Dashboard: **Inspector Performance**
  - Inspections per inspector per week
  - Average measurement count per inspection
  - Quality score (anomaly rate, completeness)
  - Calendar adherence (on-time vs late)
  - Comparative leaderboard
- [ ] **5.7** Build Dashboard: **Device Fleet**
  - Active devices count
  - Device uptime and connectivity history
  - Firmware version distribution
  - Battery health estimates
  - Assignment coverage

#### Day 8–9: Grafana Real-Time Dashboards
- [ ] **5.8** Deploy Grafana with Docker:
  - Provision PostgreSQL (TimescaleDB) datasource
  - Provision MQTT datasource (via mqtt-datasource plugin)
  - Configure auto-provisioned dashboards
- [ ] **5.9** Build Panel: **Live Measurements**
  - Real-time measurement stream (time-series graph)
  - Current active devices with last measurement
  - Measurement rate (measurements/minute)
  - Value distribution histogram (rolling 5 minutes)
- [ ] **5.10** Build Panel: **Device Connectivity**
  - Device connection status map (connected/disconnected/error)
  - RSSI signal strength over time
  - Reconnection events timeline
  - MQTT message throughput
- [ ] **5.11** Build Panel: **Field Activity**
  - Active inspectors map (GPS from mobile)
  - Live inspection progress bars
  - Measurement capture events timeline
  - Photo upload activity
- [ ] **5.12** Build Panel: **System Health**
  - Supabase API response times
  - MQTT broker metrics
  - WebSocket connection count
  - Edge function execution times
  - Error rate by service
- [ ] **5.13** Configure Grafana alerts:
  - Device disconnected > 5 minutes → Slack notification
  - Anomaly rate > 10% in 1 hour → Email alert
  - MQTT broker > 80% capacity → PagerDuty
  - Supabase API latency > 500ms → Slack
- [ ] **5.14** Embed Metabase dashboards in Supervisor Web App (iframe)

### Exit Criteria
- [ ] 6 Metabase dashboards accessible and populated with seed data
- [ ] Grafana shows real-time measurement stream with <2s latency
- [ ] Grafana alerts fire correctly for configured conditions
- [ ] Dashboards render correctly on desktop and tablet
- [ ] Embedded analytics work in Supervisor Web App
- [ ] All dashboards have documented data sources and refresh rates

---

## Milestone 6: Integration Testing, Deployment & Documentation
**Duration**: Days 9–10 | **Risk**: Medium | **Owner**: Full Team

### Objectives
Run end-to-end integration tests, finalize Docker production stack, write deployment scripts, and complete all documentation.

### Checklist

#### Day 9: Integration Testing
- [ ] **6.1** E2E Test: **Full Inspection Flow**
  - Login → Select building → Navigate to facade → Capture BLE measurement → Save → View in dashboard
  - Verify: measurement appears in Supabase, Metabase, and Grafana within 5 seconds
- [ ] **6.2** E2E Test: **Offline + Sync**
  - Disconnect network → Capture 10 measurements → Reconnect → Verify sync
  - Confirm: all measurements appear in database with correct timestamps
- [ ] **6.3** E2E Test: **Multi-Device**
  - Connect 3 GLM devices → Capture from each → Verify all measurements attributed correctly
- [ ] **6.4** E2E Test: **Anomaly Detection**
  - Send normal measurements → Verify green status
  - Send anomalous measurement (100m wall height) → Verify red flag
  - Check: anomaly flag in database, alert in Grafana
- [ ] **6.5** E2E Test: **ESP32 Pipeline**
  - ESP32 captures measurement → MQTT → Python bridge → Supabase → Mobile app display
  - Measure end-to-end latency (<500ms target)
- [ ] **6.6** E2E Test: **Report Generation**
  - Complete inspection → Trigger report → Verify PDF generated with correct data
- [ ] **6.7** Performance Test: **Measurement Throughput**
  - Simulate 100 concurrent measurements/second
  - Verify: no data loss, <200ms processing time
- [ ] **6.8** Security Test: **Auth + RLS**
  - Verify: Inspector A cannot see Inspector B's data
  - Verify: Unauthenticated requests are rejected
  - Verify: API keys are not exposed in mobile bundle

#### Day 10: Production Deployment + Documentation
- [ ] **6.9** Create `docker-compose.prod.yml`:
  - Production Supabase with proper secrets
  - Metabase with persistent volume
  - Grafana with provisioned dashboards
  - MQTT broker with TLS
  - AI engine with GPU support (optional)
  - Nginx reverse proxy with SSL
- [ ] **6.10** Create deployment scripts:
  - `scripts/deploy.sh` — Production deployment
  - `scripts/backup.sh` — Database backup to S3/GCS
  - `scripts/health_check.sh` — All-service health check
  - `scripts/migrate.sh` — Run pending migrations
- [ ] **6.11** Create EAS Build profiles:
  - Development: internal distribution, debug mode
  - Preview: internal distribution, release mode
  - Production: app store submission ready
- [ ] **6.12** Finalize all documentation (docs/ folder):
  - Verify all 18 doc files are complete and cross-referenced
  - API reference with curl examples
  - Mobile developer onboarding guide
  - ESP32 provisioning guide
- [ ] **6.13** Create `README.md` — Project overview + quick-start
- [ ] **6.14** Tag release: `v2.0.0-alpha`

### Exit Criteria
- [ ] All E2E tests pass with documented evidence
- [ ] Production Docker stack starts cleanly with one command
- [ ] EAS Build produces installable iOS and Android builds
- [ ] All 18 documentation files are complete
- [ ] Deployment scripts execute without errors
- [ ] Health check script confirms all services are green

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| BLE connectivity issues on iOS | High | High | Use `react-native-ble-plx` with Expo dev client; extensive iOS BLE testing |
| TimescaleDB performance at scale | Low | High | Chunk interval tuning; continuous aggregates for dashboard queries |
| Offline sync conflicts | Medium | Medium | Last-write-wins with vector clocks; manual conflict resolution UI |
| TFLite model size for mobile | Medium | Low | Quantization (INT8); model pruning; lazy loading |
| ESP32 WiFi reliability | Medium | Medium | Auto-reconnect; offline buffering; heartbeat monitoring |
| Supabase self-hosted complexity | Medium | Medium | Use official Docker images; automated health checks; fallback to Supabase Cloud |

---

## Definition of Done

A milestone is "done" when:
1. All checklist items are marked complete
2. All exit criteria are verified
3. Code is committed to the repository with passing CI
4. Documentation is updated to reflect implementation
5. No critical or high-severity bugs remain open

---

*This document is confidential and intended for Krontiva Africa internal use only.*
