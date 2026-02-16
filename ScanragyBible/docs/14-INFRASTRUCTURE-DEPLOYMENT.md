# Scarnergy — Infrastructure & Deployment

> **Dev**: Docker Compose (single machine)
> **Staging**: Docker Compose on VM
> **Production**: Kubernetes (4-6 nodes) or Docker Compose with managed PostgreSQL

---

## 1. Docker Compose (Full Stack)

```yaml
version: '3.8'
services:
  # === DATABASE ===
  db:
    image: timescale/timescaledb:latest-pg15
    ports: ["5432:5432"]
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: scarnergy
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  # === SUPABASE ===
  # (See 04-SUPABASE-BACKEND.md for full configuration)

  # === IOT ===
  mqtt:
    image: eclipse-mosquitto:2
    ports: ["1883:1883", "9001:9001"]
    volumes:
      - ./services/mqtt-broker/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mqtt_data:/mosquitto/data

  ble-bridge:
    build: ./services/ble-bridge
    depends_on: [db, mqtt]
    environment:
      SUPABASE_URL: http://rest:3000
      MQTT_BROKER: mqtt
    # Note: BLE requires host network mode or USB passthrough
    network_mode: host

  # === AI ===
  ai-engine:
    build: ./services/ai-engine
    ports: ["8500:8500"]
    environment:
      MODEL_PATH: /app/models

  # === DASHBOARDS ===
  metabase:
    image: metabase/metabase:v0.48.0
    ports: ["3003:3000"]
    environment:
      MB_DB_TYPE: postgres
      MB_DB_HOST: db
      MB_DB_DBNAME: metabase

  grafana:
    image: grafana/grafana:10.2.0
    ports: ["3030:3000"]
    volumes:
      - ./services/grafana/provisioning:/etc/grafana/provisioning

  # === REPORTING ===
  report-engine:
    build: ./services/report-engine
    ports: ["8600:8600"]
    environment:
      SUPABASE_URL: http://rest:3000

  # === REVERSE PROXY ===
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./deploy/docker/nginx/nginx.conf:/etc/nginx/nginx.conf

volumes:
  pgdata:
  mqtt_data:
  metabase_data:
  grafana_data:
```

## 2. Production Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8 GB | 16 GB |
| Storage | 100 GB SSD | 500 GB SSD |
| Network | 100 Mbps | 1 Gbps |
| PostgreSQL | Self-hosted | Managed (Cloud SQL / RDS) |

## 3. Backup Strategy

| Component | Method | Frequency | Retention |
|-----------|--------|-----------|-----------|
| PostgreSQL | pg_dump → S3 | Every 6 hours | 30 days |
| Supabase Storage | rsync → S3 | Daily | 90 days |
| MQTT persistence | Volume backup | Daily | 7 days |
| Metabase config | Export → Git | On change | Infinite |
| Grafana dashboards | Export → Git | On change | Infinite |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
