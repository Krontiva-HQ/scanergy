#!/usr/bin/env python3
"""
Simple WebSocket server for Bosch GLM 50C laser rangefinder
Accepts WebSocket connections from web clients and reads data from a shared file
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Set
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connected WebSocket clients
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

# Global variables to store the latest measurement and device status
latest_measurement = None
device_connected = False
device_error = None
last_device_info = None
last_measurement_monotonic = None

# File to communicate with Python script
DATA_FILE = "measurement_data.json"
# Control file to send commands to the BLE script
CONTROL_FILE = "control.json"
# Heartbeat timeout to mark device disconnected if no updates arrive
HEARTBEAT_TIMEOUT_SECONDS = 6.0
STREAMING_TIMEOUT_SECONDS = 5.0  # if no measurements within this window, consider not streaming

async def register_client(websocket):
    """Register a new WebSocket client"""
    connected_clients.add(websocket)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")
    
    # Send current status to the new client
    await send_status_update(websocket)

async def unregister_client(websocket):
    """Unregister a WebSocket client"""
    connected_clients.discard(websocket)
    logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")

async def send_to_all_clients(message):
    """Send a message to all connected clients"""
    if connected_clients:
        # Create a list of tasks for sending to all clients
        tasks = []
        for client in connected_clients.copy():
            try:
                tasks.append(client.send(message))
            except websockets.exceptions.ConnectionClosed:
                # Remove disconnected clients
                connected_clients.discard(client)
        
        # Send to all clients concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

async def send_measurement_update(measurement_data):
    """Send measurement update to all clients"""
    global latest_measurement, last_measurement_monotonic
    latest_measurement = measurement_data
    last_measurement_monotonic = time.monotonic()
    
    message = {
        "type": "measurement",
        "data": {
            "value": measurement_data["value"],
            "rawHex": measurement_data["rawHex"],
            "timestamp": measurement_data["timestamp"]
        },
        "timestamp": datetime.now().isoformat()
    }
    
    await send_to_all_clients(json.dumps(message))
    logger.info(f"Sent measurement update: {measurement_data['value']}mm")

async def send_status_update(websocket=None):
    """Send device status update to client(s)"""
    # Include devices list if we have device info
    devices_payload = []
    if last_device_info:
        devices_payload = [{
            "name": last_device_info.get("name"),
            "address": last_device_info.get("address"),
            "connected": device_connected,  # will be overridden by effective status below if needed
            "lastSeen": last_device_info.get("lastSeen")
        }]

    # Compute streaming state: connected + recent measurement
    streaming = False
    try:
        if device_connected and last_measurement_monotonic is not None:
            streaming = (time.monotonic() - last_measurement_monotonic) <= STREAMING_TIMEOUT_SECONDS
    except Exception:
        streaming = False

    # Effective connection: treat as disconnected when not streaming
    effective_connected = bool(device_connected and streaming)

    # If we have a devices payload, reflect effective connection there too
    if devices_payload:
        try:
            devices_payload[0]["connected"] = effective_connected
        except Exception:
            pass

    message = {
        "type": "status",
        "data": {
            "running": True,
            "connected": effective_connected,
            "streaming": streaming,
            "error": device_error,
            "devices": devices_payload
        },
        "timestamp": datetime.now().isoformat()
    }
    
    if websocket:
        # Send to specific client
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            connected_clients.discard(websocket)
    else:
        # Send to all clients
        await send_to_all_clients(json.dumps(message))

async def send_error_update(error_message):
    """Send error update to all clients"""
    global device_error
    device_error = error_message
    
    message = {
        "type": "error",
        "data": {
            "message": error_message
        },
        "timestamp": datetime.now().isoformat()
    }
    
    await send_to_all_clients(json.dumps(message))
    logger.error(f"Sent error update: {error_message}")

async def handle_websocket_client(websocket):
    """Handle WebSocket client connections"""
    await register_client(websocket)
    
    try:
        # Keep the connection alive and handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.info(f"Received message from client: {data}")
                
                # Handle different message types from clients
                if data.get("type") == "ping":
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                elif data.get("type") == "get_status":
                    await send_status_update(websocket)
                elif data.get("type") == "get_latest_measurement":
                    if latest_measurement:
                        await send_measurement_update(latest_measurement)
                elif data.get("type") == "reconnect_device":
                    # Write a control command for the BLE process to consume
                    try:
                        payload = data.get("payload") or {}
                        address = payload.get("address")
                        name = payload.get("name")
                        control_message = {
                            "action": "reconnect_device",
                            "address": address,
                            "name": name,
                            "timestamp": datetime.now().isoformat()
                        }
                        with open(CONTROL_FILE, "w") as f:
                            json.dump(control_message, f)

                        # Optionally notify clients that a reconnect was requested
                        # Compute effective connected here too for consistency
                        streaming = False
                        try:
                            if device_connected and last_measurement_monotonic is not None:
                                streaming = (time.monotonic() - last_measurement_monotonic) <= STREAMING_TIMEOUT_SECONDS
                        except Exception:
                            streaming = False
                        effective_connected = bool(device_connected and streaming)

                        await send_to_all_clients(json.dumps({
                            "type": "status",
                            "data": {
                                "running": True,
                                "connected": effective_connected,
                                "error": None,
                                "devices": [{
                                    "name": (name or (last_device_info or {}).get("name")),
                                    "address": (address or (last_device_info or {}).get("address")),
                                    "connected": effective_connected,
                                    "lastSeen": (last_device_info or {}).get("lastSeen")
                                }]
                            },
                            "timestamp": datetime.now().isoformat()
                        }))
                        logger.info(f"Wrote reconnect control command for device {name or ''} {address or ''}")
                    except Exception as e:
                        logger.error(f"Failed to write reconnect control command: {e}")
                        
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from client")
            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client connection closed")
    finally:
        await unregister_client(websocket)

async def monitor_data_file():
    """Monitor the data file for new measurements from Python script"""
    global device_connected, device_error
    
    last_modified = 0
    last_update_monotonic = time.monotonic()
    
    while True:
        try:
            if os.path.exists(DATA_FILE):
                current_modified = os.path.getmtime(DATA_FILE)
                
                if current_modified > last_modified:
                    last_modified = current_modified
                    
                    with open(DATA_FILE, 'r') as f:
                        data = json.load(f)
                    
                    # Any new data counts as a heartbeat
                    last_update_monotonic = time.monotonic()

                    if data.get("type") == "measurement":
                        await send_measurement_update(data)
                        device_connected = True
                        device_error = None
                    elif data.get("type") == "status":
                        device_connected = data.get("connected", False)
                        device_error = data.get("error", None)
                        # Capture device info if provided by writer
                        global last_device_info
                        if "device" in data and data["device"]:
                            last_device_info = data["device"]
                        await send_status_update()
                    elif data.get("type") == "error":
                        await send_error_update(data.get("message", "Unknown error"))
            
            # Heartbeat timeout: if we haven't seen updates for a while and were connected, mark disconnected
            now_mono = time.monotonic()
            if device_connected and (now_mono - last_update_monotonic > HEARTBEAT_TIMEOUT_SECONDS):
                device_connected = False
                device_error = "No heartbeat"
                await send_status_update()
                # Avoid repeated sends; keep last_update_monotonic so we don't re-trigger
            
            await asyncio.sleep(0.1)  # Check every 100ms
            
        except Exception as e:
            logger.error(f"Error monitoring data file: {e}")
            await asyncio.sleep(1)

async def main():
    """Main function to start the server"""
    logger.info("Starting Bosch GLM 50C WebSocket server...")
    
    # Start the file monitoring task
    monitor_task = asyncio.create_task(monitor_data_file())
    
    # Start WebSocket server
    ws_server = await websockets.serve(
        handle_websocket_client,
        "localhost",
        8765,
        ping_interval=20,
        ping_timeout=10
    )
    
    logger.info("WebSocket server started on ws://localhost:8765")
    logger.info("Web dashboard available at http://localhost:3000")
    logger.info("Python script should write to measurement_data.json")
    
    try:
        # Run both tasks concurrently
        await asyncio.gather(ws_server.wait_closed(), monitor_task)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        ws_server.close()
        await ws_server.wait_closed()
        monitor_task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")