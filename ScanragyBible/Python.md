# Python — BLE + WebSocket Bridge

## Overview

Python scripts provide two integration paths:
- Direct BLE read and OS keyboard typing ([main.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/main.py)).
- BLE read that publishes measurements/status to a simple WebSocket server via a shared file ([main_with_websocket.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/main_with_websocket.py) + [simple_websocket_server.py](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/simple_websocket_server.py)).

The Expo/web apps subscribe to `ws://localhost:8765` and render live measurements.

## Setup

```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Dependencies (macOS-focused):
- bleak, websockets, pynput, pyobjc CoreBluetooth bridges.

## Run — WebSocket Bridge

Option A: Use npm scripts from the Expo app directory:
```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/react-native/expo-app
npm run py:start-all       # starts simple_websocket_server.py and main_with_websocket.py
npm run web                # starts Expo Web and both Python processes concurrently
```

Option B: Run manually:
```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python
source venv/bin/activate
python simple_websocket_server.py
# in another terminal:
python main_with_websocket.py
```

## Docker

Run the WebSocket server in Docker:
```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python
docker build -t bosch-glm-ws .
docker run -p 8765:8765 -v /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python:/app bosch-glm-ws
```

Or with Compose:
```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python
docker compose up -d
```

Notes:
- The volume mount shares measurement_data.json and control.json between the BLE script and the container.
- Clients should connect to ws://localhost:8765 (or ws://<machine-ip>:8765 for mobile devices).

## How It Works

- WebSocket server: `simple_websocket_server.py`
  - Watches `measurement_data.json` for inbound messages.
  - Broadcasts measurement/status to clients; maintains streaming and heartbeat state.
  - Accepts client commands and writes `control.json` for the BLE script.

- BLE script: `main_with_websocket.py`
  - Connects to Bosch GLM 50C:
    - Service: `02A6C0D0-0451-4000-B000-FB3210111989`
    - Characteristic: `02A6C0D1-0451-4000-B000-FB3210111989`
  - Subscribes to notifications, decodes payloads:
    - Valid packets start with `c0 55 10 06`.
    - Bytes 7–10: little-endian 32-bit float (meters). Converts to mm.
  - Writes messages to `measurement_data.json`:
    - Measurement: `{ "type":"measurement","value":1234,"rawHex":"...", "timestamp":"..." }`
    - Status: `{ "type":"status","connected":true,"error":null,"device":{...} }`
  - Monitors `control.json` for actions (e.g., reconnect_device with optional address/name).

## Direct Typing Mode

- `main.py` reads measurements via BLE and types the value into the focused application using `pynput`.
- Uses fixed device address by default. Update the address string or discover via the scanner.

## Device Scanner

Find your device:
```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python
source venv/bin/activate
python find_device.py
```
Look for entries with names containing "bosch", "glm", or "50c" and note the address.

## Ports and Files

- WebSocket server: `ws://localhost:8765`
- Data file: [measurement_data.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/measurement_data.json)
- Control file: [control.json](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/python/control.json)

## Notes

- macOS BLE stack requires `pyobjc` frameworks provided in requirements.txt.
- If you see “No matching device found”, use `find_device.py` and update address or rely on name discovery.
- For Expo mobile BLE integration, use a development client; otherwise run the Python bridge and consume WebSocket data from the UI.
