"""
Scarnergy BLE Measurement Bridge
Connects to Bosch GLM 50C rangefinders via BLE,
serves measurements over WebSocket, MQTT, and Supabase.

See docs/05-BLE-MEASUREMENT-ENGINE.md for full implementation details.
"""
import asyncio
import os
import struct
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scarnergy.ble-bridge")

# GLM 50C BLE Constants
GLM_SERVICE_UUID = "02A6C0D0-0451-4000-B000-FB3210111989"
GLM_CHAR_UUID = "02A6C0D1-0451-4000-B000-FB3210111989"
GLM_ENABLE_CMD = bytes([0xC0, 0x55, 0x02, 0x01, 0x00, 0x1A])
VALID_PREFIX = bytes([0xC0, 0x55, 0x10, 0x06])

WEBSOCKET_PORT = int(os.getenv("WEBSOCKET_PORT", "8765"))


def decode_measurement(data: bytes) -> dict | None:
    """Decode Bosch GLM 50C BLE measurement packet."""
    if len(data) < 11 or data[:4] != VALID_PREFIX:
        return None
    meters = struct.unpack_from('<f', data, 7)[0]
    mm = round(meters * 1000, 1)
    if mm < 50 or mm > 50000:
        return None
    return {
        "value_mm": mm,
        "value_m": round(meters, 4),
        "raw_hex": data.hex(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


async def main():
    logger.info(f"Scarnergy BLE Bridge starting on port {WEBSOCKET_PORT}")
    logger.info("See docs/05-BLE-MEASUREMENT-ENGINE.md for full implementation")

    while True:
        await asyncio.sleep(60)
        logger.info("BLE Bridge running... waiting for implementation")


if __name__ == "__main__":
    asyncio.run(main())
