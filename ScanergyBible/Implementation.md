# Rebuild Guide — End‑to‑End

## Overview

This guide explains how the project’s parts tie together and how to rebuild the entire stack from scratch on a fresh machine. It covers the Expo app (UI), Python BLE/WebSocket bridge, Docker‑hosted WebSocket server, and the optional ESP32 BLE keyboard client, plus future data orchestration with Xano.

## Prerequisites

- macOS with Homebrew recommended
- Node.js (LTS) and npm
- Python 3.12 and virtualenv
- Docker Desktop
- VS Code (optional) with PlatformIO extension (for ESP32)
- Xcode (iOS Simulator) or Android Studio (Android Emulator) if running mobile

## Components and Roles

- UI (Expo app): user interface, lists objects/zones, shows calendar and measurements dashboard  
  Source: [react-native/expo-app](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app)
- WebSocket server: publishes measurements/status to UI clients  
  Source: [python/simple_websocket_server.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/simple_websocket_server.py)
- Python BLE bridge: connects to Bosch GLM 50C, decodes notifications, and writes measurement/status  
  Source: [python/main_with_websocket.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/main_with_websocket.py)
- ESP32 BLE keyboard (optional): types measurement values into the host as keystrokes  
  Source: [esp32/src/main.cpp](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32/src/main.cpp)
- Future orchestrator (Xano): backend for domain data and events  
  Doc: [Bible/Xano.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/Xano.md)

## Step 1 — Clone and Install

```bash
git clone <your-repo-url> /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app
npm install
```

Docs you’ll use:
- UI overview: [Bible/ExpoApp.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/ExpoApp.md)
- Architecture: [Bible/Architecture.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/Architecture.md)
- Data model: [Bible/DataModel.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/DataModel.md)

## Step 2 — Run the UI (Sample Data Mode)

The app loads built‑in sample data at startup via `applyDataOverride`, so no backend is required.

```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app
npm start           # Metro
npm run ios         # iOS simulator
npm run android     # Android emulator
npm run web         # Expo web
```

Key files:
- Home screen: [src/HomeScreen.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/HomeScreen.tsx)
- Sample datasets: [src/sampleData.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/sampleData.ts)
- In‑memory store: [src/queries.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/queries.ts)

## Step 3 — WebSocket Server in Docker

Run the server that broadcasts measurement/status to UI clients:

```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python
docker build -t bosch-glm-ws .
docker run -p 8765:8765 -v /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python:/app bosch-glm-ws
# or
docker compose up -d
```

Files:
- Dockerfile: [python/Dockerfile](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/Dockerfile)
- Compose: [python/docker-compose.yml](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/docker-compose.yml)
- Server: [python/simple_websocket_server.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/simple_websocket_server.py)

Port:
- `ws://localhost:8765` (use machine IP on mobile)

Data/control files shared via the volume:
- [measurement_data.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/measurement_data.json)
- [control.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/control.json)

## Step 4 — Python BLE Bridge

Set up a venv and install dependencies:
```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the BLE bridge:
```bash
python main_with_websocket.py
```

Useful scripts:
- Find device: [find_device.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/find_device.py)
- Direct typing (no WebSocket): [main.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/main.py)

Behavior:
- Connects to Bosch GLM 50C, subscribes to characteristic
- Decodes notifications (prefix `c0 55 10 06`, meters in bytes 7–10)
- Writes measurement/status to `measurement_data.json` for the WebSocket server to broadcast

## Step 5 — Wire the UI to WebSocket

The UI uses a WebSocket hook and provider:
- Hook: [src/hooks/useWebSocket.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/hooks/useWebSocket.ts)
- Provider/dashboard: [src/measurement/MeasurementProvider.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/measurement/MeasurementProvider.tsx), [src/MeasurementDashboard.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/MeasurementDashboard.tsx)

UI connects to `ws://localhost:8765` and shows status, devices, and latest measurements.

## Step 6 — Optional ESP32 BLE Keyboard

If you want measurements typed into the focused app via BLE keyboard:

Build and flash:
```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32
pio run
pio run -t upload
pio device monitor -b 115200
```

Behavior:
- Scans/connects to GLM 50C, decodes measurement, types it as text + RETURN.  
See [esp32/src/main.cpp](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32/src/main.cpp) and config in [esp32/platformio.ini](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32/platformio.ini).

## Step 7 — Data Models and Calculations

Domain types and computed fields:
- Summary: [Bible/DataModel.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/DataModel.md)
- Types: [react-native/expo54/types.ts](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo54/types.ts)
- UI forms for measurements and geometry:
  - Gevel: [src/GevelForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/GevelForm.tsx)
  - Dak: [src/DakForm.tsx](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app/src/DakForm.tsx)

Key computations:
- Gross area (length × width)
- Net area (gross − openings)
- Orientation and slope captured for façade/roof analytics
- Unit conversion between meters and millimeters

## Step 8 — End‑to‑End Run Scenarios

- Web Dashboard:
  - Start Docker WebSocket server
  - Run Python BLE bridge
  - Start Expo web: measurements stream into the dashboard
- Mobile (simulators/emulators):
  - Same as above, but UI runs in iOS or Android simulator
  - Use host machine IP in WebSocket URL for connectivity
- ESP32 mode:
  - Use BLE keyboard client to type measurements into any focused app

## Troubleshooting

- No device found: run [find_device.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/find_device.py), ensure GLM is on and discoverable
- No measurements: confirm notification prefix `c0 55 10 06` and initial write `[0xC0, 0x55, 0x02, 0x01, 0x00, 0x1A]`
- WebSocket not receiving:
  - Check `measurement_data.json` updates
  - Verify Docker port mapping `8765:8765`
  - For mobile, use `ws://<host-ip>:8765`

## Future — Xano Orchestration

- Xano becomes the backend of record:
  - Read domain data (objects, zones, visits)
  - Post measurement/inspection events
- Config via env:
  - `XANO_BASE_URL`, `XANO_API_KEY` (or JWT)
- Migration plan:
  - Implement `xanoApi` in UI, map payloads to local types, inject via `applyDataOverride`
  - Optionally post from Python bridge when BLE decodes measurements
See [Bible/Xano.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/Xano.md).

## Directory Map

- Bible docs:
  - [ExpoApp.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/ExpoApp.md)
  - [Architecture.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/Architecture.md)
  - [DataModel.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/DataModel.md)
  - [Python.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/Python.md)
  - [ESP32.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/ESP32.md)
  - [Xano.md](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/Bible/Xano.md)
