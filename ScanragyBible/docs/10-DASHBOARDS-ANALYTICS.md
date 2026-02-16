# Scarnergy — Dashboards & Analytics

> **BI Platform**: Metabase (open-source, replaces proprietary BI)
> **Real-Time Monitoring**: Grafana (open-source, time-series native)
> **Data Sources**: PostgreSQL (Supabase), TimescaleDB (measurements), MQTT (live)

---

## 1. Metabase BI Dashboards

### Dashboard 1: Inspection Overview
| Widget | Type | Query |
|--------|------|-------|
| Total Objects | Number | COUNT(*) FROM objects |
| Completion Rate | Gauge | COUNT(status='complete') / COUNT(*) |
| Inspections This Week | Line Chart | GROUP BY date, COUNT inspections |
| Inspector Workload | Bar Chart | GROUP BY inspector, COUNT assigned |
| Upcoming Visits | Table | calendar_visits WHERE date >= today ORDER BY date |
| Average Time Per Inspection | Number | AVG(completed_at - started_at) |

### Dashboard 2: Measurement Quality
| Widget | Type | Query |
|--------|------|-------|
| Total Measurements | Number | COUNT(*) FROM measurements WHERE captured_at > interval |
| Anomaly Rate | Gauge | COUNT(anomaly_score < 0) / COUNT(*) * 100 |
| Measurement Distribution | Histogram | value_mm distribution |
| Top Anomaly Reasons | Pie Chart | GROUP BY anomaly_flag |
| Quality Score by Inspector | Bar Chart | 1 - anomaly_rate per inspector |
| Daily Measurement Trend | Line Chart | COUNT per day over 30 days |

### Dashboard 3: Building Portfolio
| Widget | Type | Query |
|--------|------|-------|
| Building Map | Map (PostGIS) | objects with lat/lng |
| Buildings by Type | Pie Chart | GROUP BY building_type |
| Zone Coverage | Stacked Bar | complete/partial/missing zones per building |
| Missing Elements | Table | buildings with incomplete zone data |

### Dashboard 4: Energy Performance
| Widget | Type | Query |
|--------|------|-------|
| Energy Label Distribution | Donut | COUNT per label A-G |
| Average Energy Index | Number | AVG(energy_index) |
| Energy Trend | Line Chart | monthly average energy index |
| Worst Performers | Table | TOP 20 buildings by energy_index DESC |
| Improvement Recommendations | Table | most frequent improvement types |

### Dashboard 5: Inspector Performance
| Widget | Type | Query |
|--------|------|-------|
| Inspections Per Week | Bar Chart | per inspector, per week |
| Measurements Per Inspection | Box Plot | distribution per inspector |
| Quality Score Ranking | Ranked Bar | 1 - anomaly_rate per inspector |
| Calendar Adherence | Gauge | on-time visits / total visits |

### Dashboard 6: Device Fleet
| Widget | Type | Query |
|--------|------|-------|
| Active Devices | Number | COUNT WHERE last_seen > 24h ago |
| Firmware Distribution | Pie | GROUP BY firmware_version |
| Device Uptime | Timeline | connection/disconnection events |
| Assignment Map | Table | device → inspector → current building |

---

## 2. Grafana Real-Time Panels

### Panel 1: Live Measurement Stream
- **Type**: Time-series graph
- **Source**: TimescaleDB `SELECT time_bucket('1s', captured_at), AVG(value_mm) FROM measurements`
- **Refresh**: 1 second
- **Features**: Auto-scroll, device color coding, anomaly markers

### Panel 2: Device Connectivity
- **Type**: State timeline
- **Source**: MQTT `scarnergy/devices/+/status`
- **Features**: Connected/disconnected state per device, RSSI gauge, reconnection events

### Panel 3: Field Activity
- **Type**: Geomap
- **Source**: PostgreSQL `SELECT lat, lng, inspector_name FROM active_inspections`
- **Features**: Real-time inspector positions, measurement count bubbles

### Panel 4: System Health
- **Type**: Multi-stat + Graph
- **Source**: Prometheus metrics
- **Panels**: API latency, MQTT throughput, WebSocket connections, error rate, edge function duration

---

## 3. Deployment

```yaml
# docker-compose section for dashboards
  metabase:
    image: metabase/metabase:v0.48.0
    ports: ["3003:3000"]
    environment:
      MB_DB_TYPE: postgres
      MB_DB_HOST: db
      MB_DB_PORT: 5432
      MB_DB_DBNAME: metabase
      MB_DB_USER: metabase
      MB_DB_PASS: ${METABASE_DB_PASSWORD}
    volumes: [metabase_data:/metabase-data]

  grafana:
    image: grafana/grafana:10.2.0
    ports: ["3030:3000"]
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - ./services/grafana/provisioning:/etc/grafana/provisioning
      - ./services/grafana/dashboards:/var/lib/grafana/dashboards
      - grafana_data:/var/lib/grafana
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
