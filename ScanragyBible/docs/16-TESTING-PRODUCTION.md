# Scarnergy — Testing & Production Readiness

> **Strategy**: Unit → Integration → E2E → Performance → Security
> **Tools**: Jest (TS), pytest (Python), Detox (mobile E2E), k6 (load)

---

## 1. Test Pyramid

```
                    ┌─────┐
                    │ E2E │  5 tests (critical flows)
                   ┌┴─────┴┐
                   │ Integ │  15 tests (service interactions)
                  ┌┴───────┴┐
                  │  Unit   │  50+ tests (functions, validators, decoders)
                  └─────────┘
```

## 2. Unit Tests

| Module | Framework | Key Tests |
|--------|-----------|-----------|
| BLE Protocol Decoder | pytest | Packet decode, invalid prefix, out-of-range, endianness |
| Measurement Validator | pytest | Range check, rate limit, duplicate detection |
| Energy Calculator | Jest | Area computation, U-values, label resolution |
| Geometry Utils | Jest | Gross/net area, perimeter, unit conversion |
| Zustand Stores | Jest | State mutations, persistence, offline queue |
| AI Models | pytest | Prediction accuracy, TFLite vs sklearn parity |

## 3. Integration Tests

| Flow | Test |
|------|------|
| BLE → WebSocket | Python bridge receives BLE packet → WebSocket client receives JSON |
| BLE → Supabase | Measurement captured → appears in database within 1s |
| MQTT → Supabase | ESP32 publishes → Python subscribes → database INSERT |
| Mobile → Supabase | App creates object → API returns → realtime notification |
| Offline → Sync | App queues 10 mutations offline → reconnect → all synced |
| AI → Pipeline | Anomalous measurement → flagged in database → Grafana alert |

## 4. E2E Tests (Critical Paths)

| # | Test | Steps | Assertion |
|---|------|-------|-----------|
| E1 | Full Inspection | Login → Select building → Measure facade → Save → View dashboard | Measurement in Metabase |
| E2 | Offline Sync | Disconnect → Capture 10 → Reconnect → Verify | All 10 in database |
| E3 | Multi-Device | Connect 3 GLMs → Capture from each → Verify attribution | Correct device_id per measurement |
| E4 | Anomaly Flag | Send 100m wall measurement → Check flag | anomaly_score < 0, Grafana alert |
| E5 | Report Generation | Complete inspection → Generate PDF → Download | Valid PDF with correct data |

## 5. Performance Targets

| Metric | Target | Tool |
|--------|--------|------|
| Measurement throughput | 100/sec sustained | k6 |
| API response time (p95) | <200ms | k6 |
| Mobile app startup | <3 seconds | Detox |
| BLE connection time | <5 seconds | Manual |
| Offline sync (100 mutations) | <10 seconds | Manual |
| Report generation | <30 seconds | k6 |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
