# ADR-003: Grafana for Real-Time IoT Monitoring

**Status**: Accepted  
**Date**: 2026-02-11

## Context
Scarnergy needs real-time visualization of BLE device connectivity, live measurement streams, MQTT broker metrics, and system health — all time-series data with sub-second update requirements.

## Decision
Use **Grafana** for all real-time IoT dashboards, complementing Metabase's BI analytics.

## Rationale
- Native time-series visualization with auto-refresh as low as 1 second
- MQTT datasource plugin for direct broker monitoring
- TimescaleDB datasource for measurement stream visualization
- Prometheus integration for infrastructure metrics
- Alerting engine for device disconnection and anomaly rate thresholds
- Industry standard for IoT monitoring with proven scale
