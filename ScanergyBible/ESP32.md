# ESP32 — BLE Client (PlatformIO)

## Overview

This module implements an ESP32 BLE client that:
- Scans for a device advertising the Bosch GLM 50C service.
- Connects, subscribes to the measurement characteristic.
- Decodes the measurement from the notification payload.
- Types the value over BLE Keyboard as text plus RETURN.

Key references:
- Board/env config: [platformio.ini](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32/platformio.ini)
- Entrypoint: [src/main.cpp](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32/src/main.cpp)

## Dependencies

Configured in platformio.ini:
- NimBLE-Arduino (h2zero/NimBLE-Arduino@1.4.1)
- ESP32 BLE Keyboard (t-vk/ESP32 BLE Keyboard@0.3.2)

Build flags:
- `-DUSE_NIMBLE`

Serial monitor:
- Speed 115200, with filters for time, log2file, esp32_exception_decoder.

## Build and Flash (CLI)

```bash
cd /Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32
pio run                 # build
pio run -t upload       # flash to connected ESP32
pio device monitor -b 115200
```

You can also use the VS Code PlatformIO extension for one-click build/flash/monitor.

## Behavior Details

- BLE Keyboard name: "Bosch keyboard"
- Service UUID: `02a6c0d0-0451-4000-b000-fb3210111989`
- Characteristic UUID: `02a6c0d1-0451-4000-b000-fb3210111989`
- Subscription callback:
  - Valid packets start with hex prefix `c0 55 10 06`.
  - Bytes 7–10 in the payload contain a little-endian 32-bit float of the length in meters.
  - The code prints and types the value as a decimal string (meters) and sends RETURN.
  - Initial write enables measurement notifications: `c0 55 02 01 00 1a`.

## File Layout

- [src/main.cpp](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32/src/main.cpp): BLE scan/connect/subscribe, payload decode, BLE keyboard output.
- [platformio.ini](file:///Users/dibelaba/Documents/GitHub/Bosch-GLM50C-Rangefinder/esp32/platformio.ini): board, framework, libraries, monitor config.
- include/, lib/, test/: standard PlatformIO scaffolding.

## Notes

- Pair the ESP32 BLE Keyboard with the host where you want measurements typed.
- If you need to change the advertised service/characteristic UUIDs, update the UUID constants in main.cpp.
- For advanced logging, uncomment or tune log levels in platformio.ini and code.
