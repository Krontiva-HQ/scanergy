# ADR-006: MQTT (Eclipse Mosquitto) for ESP32 IoT Messaging

**Status**: Accepted  
**Date**: 2026-02-11

## Context
ESP32 IoT bridges need a lightweight, reliable messaging protocol to publish measurements from fixed installations to the cloud backend. The device operates on WiFi with intermittent connectivity.

## Decision
Use **MQTT** via **Eclipse Mosquitto** broker for all ESP32 ↔ cloud communication.

## Rationale
- MQTT is the industry standard for IoT device messaging
- QoS levels ensure measurement delivery (QoS 1 for measurements)
- Last Will and Testament (LWT) for automatic offline detection
- Lightweight protocol suitable for ESP32's limited resources
- Eclipse Mosquitto is the most widely deployed open-source MQTT broker
- WebSocket bridge (port 9001) enables browser-based MQTT clients
- Topic-based ACLs provide device-level security

## Topic Structure
- `scarnergy/measurements/{device_id}` — Measurement data (QoS 1)
- `scarnergy/devices/{device_id}/status` — Device health (QoS 0)
- `scarnergy/commands/{device_id}` — Remote control (QoS 1)
- `scarnergy/devices/{device_id}/lwt` — Last Will (offline detection)
