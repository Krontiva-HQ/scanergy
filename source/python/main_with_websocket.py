#!/usr/bin/env python3
"""
Enhanced main.py that integrates with WebSocket server for real-time web dashboard
"""

import asyncio
import logging
from datetime import datetime
from bleak import BleakScanner, BleakClient
import websockets
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket server details
WEBSOCKET_HOST = "localhost"
WEBSOCKET_PORT = 8765

# Service and characteristic UUIDs for Bosch GLM 50C
SERVICE_UUID = "02A6C0D0-0451-4000-B000-FB3210111989"
CHARACTERISTIC_UUID = "02A6C0D1-0451-4000-B000-FB3210111989"

# Device identification
# Set DEVICE_ADDRESS to an empty string to enable auto-discovery by device name.
DEVICE_ADDRESS = "90:7B:C6:69:18:3C"
DEVICE_NAME_KEYWORDS = ["bosch", "glm", "50c"]

# Global WebSocket connection and last device info
websocket_connection = None
current_device_info = None
CONTROL_FILE = "control.json"

def decode_measurement(hex_data: str) -> int:
    """Decode measurement from hex data using the correct Bosch GLM 50C protocol"""
    try:
        import struct
        
        # Remove any whitespace and convert to lowercase
        clean_hex = hex_data.replace(" ", "").lower()
        
        # Convert hex string to bytes
        bytes_data = bytearray()
        for i in range(0, len(clean_hex), 2):
            bytes_data.append(int(clean_hex[i:i+2], 16))
        
        # Check if data starts with the correct prefix (c0 55 10 06)
        if len(bytes_data) >= 11 and bytes_data.startswith(b'\xc0\x55\x10\x06'):
            # Bytes 7-10 contain the measurement as little-endian 32-bit float
            measurement_float = struct.unpack('<f', bytes_data[7:11])[0]
            # Convert to millimeters (multiply by 1000)
            measurement_mm = int(round(measurement_float * 1000))
            return measurement_mm
        
        return 0
    except Exception as e:
        logger.error(f"Error decoding measurement: {e}")
        return 0

async def send_measurement_to_websocket(value: int, raw_hex: str):
    """Send measurement data to WebSocket server via file"""
    try:
        import json
        
        message = {
            "type": "measurement",
            "value": value,
            "rawHex": raw_hex,
            "timestamp": datetime.now().isoformat()
        }
        
        with open("measurement_data.json", "w") as f:
            json.dump(message, f)
        
        logger.info(f"Sent measurement to WebSocket: {value}mm")
            
    except Exception as e:
        logger.error(f"Error sending to WebSocket: {e}")

async def send_status_to_websocket(connected: bool, error: str = None):
    """Send status update to WebSocket server via file"""
    try:
        import json
        
        # Build status message and include device info if available
        message = {
            "type": "status",
            "connected": connected,
            "error": error,
            "device": current_device_info
        }
        
        with open("measurement_data.json", "w") as f:
            json.dump(message, f)
        
        logger.info(f"Sent status to WebSocket: connected={connected}")
            
    except Exception as e:
        logger.error(f"Error sending status to WebSocket: {e}")

async def connect_to_websocket():
    """Connect to the WebSocket server"""
    global websocket_connection
    
    try:
        websocket_connection = await websockets.connect(f"ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        logger.info("Connected to WebSocket server")
        
        # Send initial status
        status_message = {
            "type": "status",
            "data": {
                "running": True,
                "connected": False,
                "error": None
            },
            "timestamp": datetime.now().isoformat()
        }
        await websocket_connection.send(json.dumps(status_message))
        
        return True
    except Exception as e:
        logger.error(f"Failed to connect to WebSocket server: {e}")
        websocket_connection = None
        return False

async def characteristic_notification_handler(sender, data):
    """Handle characteristic notifications from the laser meter"""
    try:
        hex_data = data.hex()
        logger.info(f"Received data: {hex_data}")
        
        measurement = decode_measurement(hex_data)
        if measurement > 0:
            logger.info(f"Decoded measurement: {measurement}mm")
            
            # Send to WebSocket server
            await send_measurement_to_websocket(measurement, hex_data)
            
            # Also print to console for debugging
            print(f"Measurement: {measurement}mm ({hex_data})")
        
    except Exception as e:
        logger.error(f"Error handling characteristic notification: {e}")

async def connect_to_device(target_address: str = None):
    """Connect to the Bosch GLM 50C device"""
    try:
        logger.info("Scanning for device...")

        device = None

        # Try by explicit address first (if provided)
        effective_address = target_address if target_address else DEVICE_ADDRESS
        if effective_address:
            try:
                device = await BleakScanner.find_device_by_address(
                    effective_address,
                    timeout=10,
                    cb=dict(use_bdaddr=True)
                )
            except Exception as e:
                logger.warning(f"Address lookup failed: {e}")

            if not device:
                logger.warning(f"Device with address {effective_address} not found. Falling back to name discovery...")
        else:
            logger.info("No device address set. Using name discovery...")

        # Fallback: scan and pick by name keywords
        if device is None:
            devices = await BleakScanner.discover(timeout=10.0)
            candidates = []
            for d in devices:
                name = (d.name or "").lower()
                if any(k in name for k in DEVICE_NAME_KEYWORDS):
                    candidates.append(d)

            if not candidates:
                logger.error("No Bosch GLM 50C-like device found during name discovery.")
                await send_status_to_websocket(False, "No matching device found")
                return None

            # Prefer strongest signal
            candidates.sort(key=lambda x: getattr(x, 'rssi', -9999), reverse=True)
            device = candidates[0]
            logger.info(f"Selected device by name: {device.name} ({device.address}), RSSI={getattr(device, 'rssi', 'N/A')}")

        logger.info(f"Using device: {device.name} ({device.address})")
        # Track device info for WebSocket status propagation
        global current_device_info
        current_device_info = {
            "name": device.name,
            "address": device.address,
            "lastSeen": datetime.now().isoformat()
        }

        # Connect to the device
        client = BleakClient(device)

        # Register disconnected callback so UI is updated when device powers off
        def _on_disconnected(_client):
            logger.info("BLE device disconnected (callback)")
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.call_soon_threadsafe(asyncio.create_task, send_status_to_websocket(False, "Device disconnected"))
                else:
                    raise RuntimeError("Loop not running")
            except Exception:
                # Fallback: synchronous file write
                try:
                    status_message = {
                        "type": "status",
                        "connected": False,
                        "error": "Device disconnected",
                        "device": current_device_info,
                    }
                    with open("measurement_data.json", "w") as f:
                        json.dump(status_message, f)
                except Exception as e:
                    logger.warning(f"Failed to write disconnect status: {e}")

        try:
            client.set_disconnected_callback(_on_disconnected)
        except Exception as e:
            logger.warning(f"Could not set disconnected callback: {e}")

        await client.connect()
        logger.info("Connected to device")

        # Discover services and characteristics
        await client.start_notify(CHARACTERISTIC_UUID, characteristic_notification_handler)
        logger.info("Started notifications")

        # Send initial command to start measurement
        initial_command = bytes([0xC0, 0x55, 0x02, 0x01, 0x00, 0x1A])
        await client.write_gatt_char(CHARACTERISTIC_UUID, initial_command)
        logger.info("Sent initial command")

        # Update WebSocket status (now includes device info)
        await send_status_to_websocket(True, None)

        return client

    except Exception as e:
        logger.error(f"Error connecting to device: {e}")

        # Update WebSocket status with error (device info may be present)
        await send_status_to_websocket(False, str(e))

        return None

async def main():
    """Main function"""
    logger.info("Starting Bosch GLM 50C with WebSocket integration...")
    
    # Connect to the laser meter device
    client = await connect_to_device()
    
    if not client:
        logger.error("Failed to connect to laser meter device")
        return
    
    try:
        logger.info("Laser meter connected successfully!")
        logger.info("Take measurements with your device to see them in the web dashboard")
        logger.info("Press Ctrl+C to stop")
        
        # Keep the connection alive and respond to control commands
        last_control_mtime = 0
        last_status_heartbeat = time.monotonic()
        while True:
            # Check for control commands (e.g., reconnect requests)
            try:
                import os
                if os.path.exists(CONTROL_FILE):
                    current_mtime = os.path.getmtime(CONTROL_FILE)
                    if current_mtime > last_control_mtime:
                        last_control_mtime = current_mtime
                        with open(CONTROL_FILE, 'r') as f:
                            control = json.load(f)
                        action = control.get('action')
                        if action == 'reconnect_device':
                            target_address = control.get('address')
                            target_name = control.get('name')
                            logger.info(f"Reconnect requested for device {target_name or ''} {target_address or ''}")
                            try:
                                # Disconnect current client if connected
                                if client:
                                    await client.disconnect()
                                    logger.info("Disconnected current device before reconnect")
                                    client = None
                                    await send_status_to_websocket(False, None)
                                # Attempt reconnect (address preferred if provided)
                                client = await connect_to_device(target_address)
                                if client:
                                    logger.info("Reconnect successful")
                                else:
                                    logger.error("Reconnect failed")
                            except Exception as e:
                                logger.error(f"Error during reconnect: {e}")
                                await send_status_to_websocket(False, str(e))
                
            except Exception as e:
                logger.warning(f"Control file check failed: {e}")
            
            # Periodic status heartbeat while connected to avoid false disconnects
            try:
                if client and (time.monotonic() - last_status_heartbeat > 3.0):
                    await send_status_to_websocket(True, None)
                    last_status_heartbeat = time.monotonic()
            except Exception as e:
                logger.warning(f"Status heartbeat failed: {e}")

            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping...")
    finally:
        if client:
            await client.disconnect()
            logger.info("Disconnected from device")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program stopped by user")
    except Exception as e:
        logger.error(f"Program error: {e}")

