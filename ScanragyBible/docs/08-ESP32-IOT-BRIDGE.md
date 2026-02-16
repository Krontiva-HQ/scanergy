# Scarnergy — ESP32 IoT Bridge

> **Role**: BLE-to-WiFi-to-MQTT gateway for fixed installations
> **Extends**: github.com/ketan/Bosch-GLM50C-Rangefinder ESP32 code
> **Platform**: ESP32-WROOM-32 via PlatformIO + NimBLE + PubSubClient

---

## 1. Enhanced ESP32 Architecture

```
┌─────────────────────────────────────────────────┐
│                  ESP32 FIRMWARE                   │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐│
│  │ BLE      │   │ WiFi     │   │ MQTT Client  ││
│  │ Scanner  │──►│ Manager  │──►│ (PubSub)     ││
│  │ (NimBLE) │   │ (Captive │   │              ││
│  │          │   │  Portal) │   │ Topics:      ││
│  │ ┌──────┐ │   └──────────┘   │ measurements/││
│  │ │GLM50C│ │                   │ devices/     ││
│  │ │Client│ │                   │ commands/    ││
│  │ └──────┘ │                   └──────────────┘│
│  └──────────┘                                    │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐│
│  │ BLE      │   │ OTA      │   │ LED Status   ││
│  │ Keyboard │   │ Updater  │   │ Controller   ││
│  │ (Legacy) │   │ (HTTP)   │   │              ││
│  └──────────┘   └──────────┘   └──────────────┘│
└─────────────────────────────────────────────────┘
```

---

## 2. PlatformIO Configuration

```ini
; esp32/platformio.ini
[env:esp32]
platform = espressif32
board = esp32dev
framework = arduino
lib_deps =
    h2zero/NimBLE-Arduino@1.4.1
    t-vk/ESP32 BLE Keyboard@0.3.2
    knolleary/PubSubClient@2.8
    tzapu/WiFiManager@2.0.16-rc.2
build_flags = -DUSE_NIMBLE
monitor_speed = 115200
monitor_filters = esp32_exception_decoder, time, log2file
```

---

## 3. MQTT Topic Structure

| Topic | Direction | QoS | Payload |
|-------|-----------|-----|---------|
| `scarnergy/measurements/{device_id}` | ESP32 → Broker | 1 | `{"value_mm":2450,"raw_hex":"...","ts":"..."}` |
| `scarnergy/devices/{device_id}/status` | ESP32 → Broker | 0 | `{"connected":true,"rssi":-65,"battery":85}` |
| `scarnergy/commands/{device_id}` | Broker → ESP32 | 1 | `{"cmd":"reconnect"}` or `{"cmd":"ota","url":"..."}` |
| `scarnergy/devices/{device_id}/lwt` | Broker (LWT) | 1 | `{"status":"offline"}` |

---

## 4. OTA Firmware Update

```cpp
// esp32/src/ota_updater.cpp
#include <HTTPUpdate.h>

void checkForUpdate(const char* firmwareUrl) {
    WiFiClient client;
    t_httpUpdate_return ret = httpUpdate.update(client, firmwareUrl);
    switch (ret) {
        case HTTP_UPDATE_OK: Serial.println("OTA Success"); ESP.restart(); break;
        case HTTP_UPDATE_FAILED: Serial.printf("OTA Failed: %s\n", httpUpdate.getLastErrorString().c_str()); break;
        case HTTP_UPDATE_NO_UPDATES: Serial.println("No update available"); break;
    }
}
```

---

## 5. LED Status Indicators

| State | LED Pattern | Meaning |
|-------|------------|---------|
| Solid Blue | ━━━━━━━ | BLE connected to GLM |
| Blinking Blue | ━ ━ ━ ━ | BLE scanning |
| Solid Green | ━━━━━━━ | WiFi + MQTT connected |
| Blinking Green | ━ ━ ━ ━ | WiFi connecting |
| Solid Red | ━━━━━━━ | Error state |
| Flash White | ⚡ | Measurement published |

---

*This document is confidential and intended for Krontiva Africa internal use only.*
