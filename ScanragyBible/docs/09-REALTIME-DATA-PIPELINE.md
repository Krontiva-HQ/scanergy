# Scarnergy — Real-Time Data Pipeline

> **Role**: Move measurements from BLE devices to database, dashboards, and mobile clients in real-time
> **Protocols**: WebSocket, MQTT, Supabase Realtime (PostgreSQL CDC)
> **Latency Target**: <200ms device-to-dashboard

---

## 1. Pipeline Architecture

```
BLE Device ──► [Path A: Mobile BLE] ──► React Native App ──► Supabase REST ──►┐
                                                                                │
BLE Device ──► [Path B: Python Bridge] ──► WebSocket Server ──────────────────►├──► PostgreSQL
              └──► MQTT Publisher ──► Mosquitto Broker ──► MQTT-Supabase ──────┤    (TimescaleDB)
                                                                                │
BLE Device ──► [Path C: ESP32] ──► MQTT ──► Mosquitto ──► Python Subscriber ──►┘         │
                                                                                          │
                                                PostgreSQL CDC ──► Supabase Realtime ─────┤
                                                                      │                    │
                                    Mobile App (WebSocket) ◄──────────┘                    │
                                    Grafana (TimescaleDB)  ◄───────────────────────────────┘
                                    Metabase (PostgreSQL)  ◄───────────────────────────────┘
```

---

## 2. Message Formats

### Measurement Message (All Paths)
```json
{
  "type": "measurement",
  "value_mm": 2450.0,
  "raw_hex": "c055100600000019411a0000000000000000",
  "device_id": "AA:BB:CC:DD:EE:FF",
  "session_id": "uuid-session-123",
  "element_type": "gevel",
  "element_id": "uuid-element-456",
  "source": "ble_mobile",
  "anomaly_score": 0.85,
  "timestamp": "2026-02-11T14:30:00.000Z"
}
```

### Device Status Message
```json
{
  "type": "status",
  "device_id": "AA:BB:CC:DD:EE:FF",
  "connected": true,
  "rssi": -65,
  "firmware": "2.1.0",
  "battery_estimate": 85,
  "measurements_today": 142,
  "last_measurement": "2026-02-11T14:29:55.000Z"
}
```

---

## 3. Supabase Realtime Channels

| Channel | Event | Filter | Consumers |
|---------|-------|--------|-----------|
| `measurement-stream` | INSERT on measurements | `session_id=eq.{id}` | Mobile app (active session) |
| `device-status` | UPDATE on devices | `org_id=eq.{id}` | Grafana, Supervisor app |
| `inspection-events` | ALL on inspections | `inspector_id=eq.{id}` | Mobile app (assigned inspector) |
| `anomaly-alerts` | INSERT on measurements | `anomaly_score.lt.0` | Grafana alerts, Supervisor app |

---

## 4. Performance Targets

| Metric | Target | Measurement Point |
|--------|--------|-------------------|
| BLE → Mobile state | <100ms | BLE notification to React state update |
| BLE → Supabase | <200ms | BLE notification to database INSERT |
| BLE → Grafana | <2s | BLE notification to Grafana panel refresh |
| ESP32 → Supabase | <500ms | MQTT publish to database INSERT |
| Throughput | 100 meas/sec | Concurrent measurements across all devices |
| WebSocket clients | 50 concurrent | Python bridge broadcast capacity |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
