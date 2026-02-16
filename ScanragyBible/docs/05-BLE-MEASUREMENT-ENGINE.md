# Scarnergy — BLE Measurement Engine

> **Role**: Connect Bosch GLM 50C laser rangefinders via BLE, decode measurements, validate, and publish to cloud  
> **Extends**: github.com/ketan/Bosch-GLM50C-Rangefinder (Python + ESP32)  
> **Three BLE Paths**: Mobile (react-native-ble-plx), Python Bridge (bleak), ESP32 (NimBLE)

---

## 1. Bosch GLM 50C BLE Protocol

### Device Identification
| Property | Value |
|----------|-------|
| Device Name | `Bosch GLM50C` or `GLM 50-27 CG` |
| Service UUID | `02A6C0D0-0451-4000-B000-FB3210111989` |
| Characteristic UUID | `02A6C0D1-0451-4000-B000-FB3210111989` |
| Notification Prefix | `C0 55 10 06` (4 bytes) |
| Measurement Bytes | 7–10 (little-endian IEEE 754 float32, meters) |
| Enable Command | `[0xC0, 0x55, 0x02, 0x01, 0x00, 0x1A]` |

### Packet Decode Sequence

```
Raw BLE Notification (20 bytes):
C0 55 10 06 XX XX XX [B0 B1 B2 B3] XX XX XX XX XX XX XX XX XX

Step 1: Validate prefix → bytes[0:4] == C0 55 10 06
Step 2: Extract measurement → bytes[7:11] as little-endian float32
Step 3: Convert → value_meters * 1000 = value_mm
Step 4: Validate → 50mm ≤ value_mm ≤ 50000mm (device spec range)
```

### Connection Sequence

```
1. SCAN     → Filter by Service UUID 02A6C0D0...
2. CONNECT  → BLE GATT connection
3. DISCOVER → Find Characteristic 02A6C0D1...
4. WRITE    → Send enable command [C0 55 02 01 00 1A]
5. SUBSCRIBE → Enable notifications on characteristic
6. RECEIVE  → Process notification callbacks
7. DECODE   → Extract measurement from payload
```

---

## 2. Python BLE Bridge (Enhanced)

### Architecture

```
┌─────────────┐     BLE      ┌──────────────┐
│ Bosch GLM   │◄────────────►│ device_      │
│ Device 1    │              │ manager.py   │──┐
└─────────────┘              └──────────────┘  │
┌─────────────┐     BLE      ┌──────────────┐  │    ┌──────────────┐
│ Bosch GLM   │◄────────────►│ device_      │──┼───►│ measurement_ │
│ Device 2    │              │ manager.py   │  │    │ validator.py │
└─────────────┘              └──────────────┘  │    └──────┬───────┘
┌─────────────┐     BLE      ┌──────────────┐  │           │
│ Bosch GLM   │◄────────────►│ device_      │──┘           ▼
│ Device N    │              │ manager.py   │    ┌──────────────────┐
└─────────────┘              └──────────────┘    │                  │
                                                 ├─► websocket_     │
                                                 │   server.py      │
                                                 ├─► mqtt_          │
                                                 │   publisher.py   │
                                                 └─► supabase_      │
                                                     sync.py        │
```

### Multi-Device Manager

```python
# services/ble-bridge/src/device_manager.py
import asyncio
from bleak import BleakClient, BleakScanner
from typing import Dict, Callable

GLM_SERVICE_UUID = "02a6c0d0-0451-4000-b000-fb3210111989"
GLM_CHAR_UUID = "02a6c0d1-0451-4000-b000-fb3210111989"
ENABLE_CMD = bytearray([0xC0, 0x55, 0x02, 0x01, 0x00, 0x1A])
VALID_PREFIX = bytes([0xC0, 0x55, 0x10, 0x06])
MAX_DEVICES = 5

class DeviceManager:
    def __init__(self, on_measurement: Callable):
        self.clients: Dict[str, BleakClient] = {}
        self.on_measurement = on_measurement

    async def scan_and_connect(self):
        """Scan for GLM devices and connect to all found."""
        devices = await BleakScanner.discover(timeout=10.0)
        glm_devices = [d for d in devices if GLM_SERVICE_UUID.lower() in
                       [str(s).lower() for s in (d.metadata.get("uuids", []))]]

        for device in glm_devices[:MAX_DEVICES]:
            if device.address not in self.clients:
                asyncio.create_task(self._connect_device(device))

    async def _connect_device(self, device):
        """Connect to a single device with auto-reconnect."""
        client = BleakClient(device.address)
        try:
            await client.connect()
            await client.write_gatt_char(GLM_CHAR_UUID, ENABLE_CMD)
            await client.start_notify(GLM_CHAR_UUID,
                lambda _, data: self._handle_notification(device.address, data))
            self.clients[device.address] = client
        except Exception as e:
            # Exponential backoff reconnect
            await asyncio.sleep(5)
            asyncio.create_task(self._connect_device(device))

    def _handle_notification(self, address: str, data: bytearray):
        """Decode measurement from BLE notification."""
        if len(data) >= 11 and data[:4] == VALID_PREFIX:
            import struct
            value_meters = struct.unpack('<f', data[7:11])[0]
            value_mm = round(value_meters * 1000, 1)
            if 50 <= value_mm <= 50000:
                self.on_measurement({
                    "device_id": address,
                    "value_mm": value_mm,
                    "raw_hex": data.hex(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "ble_bridge"
                })
```

### Measurement Validator

```python
# services/ble-bridge/src/measurement_validator.py
from dataclasses import dataclass
from typing import Optional, List
import time

@dataclass
class ValidationResult:
    valid: bool
    value_mm: float
    flags: List[str]
    anomaly_score: Optional[float] = None

class MeasurementValidator:
    def __init__(self):
        self.recent: dict = {}  # device_id → (value, timestamp)

    def validate(self, measurement: dict) -> ValidationResult:
        flags = []
        value = measurement["value_mm"]
        device = measurement["device_id"]
        ts = time.time()

        # Range check (GLM 50C: 0.05m to 50m)
        if value < 50 or value > 50000:
            flags.append("OUT_OF_RANGE")

        # Rate limiting (max 2/sec per device)
        if device in self.recent:
            last_val, last_ts = self.recent[device]
            if ts - last_ts < 0.5:
                flags.append("TOO_FAST")
            if abs(value - last_val) < 0.1 and ts - last_ts < 0.5:
                flags.append("DUPLICATE")

        self.recent[device] = (value, ts)

        return ValidationResult(
            valid=len(flags) == 0,
            value_mm=value,
            flags=flags
        )
```

---

## 3. React Native BLE Integration

### useBLE Hook

```typescript
// mobile/inspector-app/src/hooks/useBLE.ts
import { BleManager, Device, Characteristic } from 'react-native-ble-plx';
import { useState, useEffect, useRef, useCallback } from 'react';

const GLM_SERVICE = '02A6C0D0-0451-4000-B000-FB3210111989';
const GLM_CHAR = '02A6C0D1-0451-4000-B000-FB3210111989';
const ENABLE_CMD = 'wFUCAQAa'; // base64 of [0xC0, 0x55, 0x02, 0x01, 0x00, 0x1A]

export function useBLE() {
  const manager = useRef(new BleManager()).current;
  const [devices, setDevices] = useState<Device[]>([]);
  const [connected, setConnected] = useState<Device | null>(null);
  const [measurement, setMeasurement] = useState<number | null>(null);

  const scan = useCallback(() => {
    manager.startDeviceScan([GLM_SERVICE], null, (error, device) => {
      if (device) {
        setDevices(prev => {
          if (prev.find(d => d.id === device.id)) return prev;
          return [...prev, device];
        });
      }
    });
    setTimeout(() => manager.stopDeviceScan(), 10000);
  }, []);

  const connect = useCallback(async (device: Device) => {
    const d = await device.connect();
    await d.discoverAllServicesAndCharacteristics();
    await d.writeCharacteristicWithResponseForService(GLM_SERVICE, GLM_CHAR, ENABLE_CMD);
    d.monitorCharacteristicForService(GLM_SERVICE, GLM_CHAR, (err, char) => {
      if (char?.value) {
        const decoded = decodeMeasurement(char.value);
        if (decoded) setMeasurement(decoded);
      }
    });
    setConnected(d);
  }, []);

  return { devices, connected, measurement, scan, connect };
}

function decodeMeasurement(base64: string): number | null {
  const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
  if (bytes.length >= 11 && bytes[0] === 0xC0 && bytes[1] === 0x55
      && bytes[2] === 0x10 && bytes[3] === 0x06) {
    const buffer = new ArrayBuffer(4);
    const view = new DataView(buffer);
    view.setUint8(0, bytes[7]);
    view.setUint8(1, bytes[8]);
    view.setUint8(2, bytes[9]);
    view.setUint8(3, bytes[10]);
    const meters = view.getFloat32(0, true); // little-endian
    return Math.round(meters * 1000 * 10) / 10; // mm with 1 decimal
  }
  return null;
}
```

---

## 4. Verification

```bash
# Test Python BLE bridge
cd services/ble-bridge
source venv/bin/activate

# 1. Find devices
python src/main.py --scan-only
# Expected: "Found: Bosch GLM50C at XX:XX:XX:XX:XX:XX"

# 2. Connect and capture
python src/main.py
# Expected: "Connected to Bosch GLM50C"
# Take a measurement on the GLM device
# Expected: "Measurement: 2450.0mm from XX:XX:XX:XX:XX:XX"

# 3. Verify WebSocket broadcast
wscat -c ws://localhost:8765
# Expected: {"type":"measurement","value":2450,"device_id":"..."}

# 4. Verify Supabase insert
curl "http://localhost:3001/rest/v1/measurements?order=captured_at.desc&limit=1" \
  -H "apikey: $ANON_KEY"
# Expected: latest measurement record
```

---

*This document is confidential and intended for Krontiva Africa internal use only.*
