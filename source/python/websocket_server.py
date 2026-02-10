#!/usr/bin/env python3
"""
WebSocket server for Bosch GLM 50C laser rangefinder
Serves real-time measurement data to web clients
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Set
import sys
import os

# Add the parent directory to the path so we can import from main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main as run_laser_meter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connected WebSocket clients
connected_clients: Set[websockets.WebSocketServerProtocol] = set()

# Global variables to store the latest measurement and device status
latest_measurement = None
device_connected = False
device_error = None

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
    global latest_measurement
    latest_measurement = measurement_data
    
    message = {
        "type": "measurement",
        "data": {
            "value": measurement_data["value"],
            "rawHex": measurement_data["rawHex"],
            "timestamp": measurement_data["timestamp"].isoformat()
        },
        "timestamp": datetime.now().isoformat()
    }
    
    await send_to_all_clients(json.dumps(message))
    logger.info(f"Sent measurement update: {measurement_data['value']}mm")

async def send_status_update(websocket=None):
    """Send device status update to client(s)"""
    message = {
        "type": "status",
        "data": {
            "running": True,
            "connected": device_connected,
            "error": device_error
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

async def handle_client(websocket, path):
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
                        
            except json.JSONDecodeError:
                logger.error("Invalid JSON received from client")
            except Exception as e:
                logger.error(f"Error handling client message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client connection closed")
    finally:
        await unregister_client(websocket)

async def laser_meter_task():
    """Task to run the laser meter and send updates"""
    global device_connected, device_error
    
    try:
        logger.info("Starting laser meter task...")
        
        # Import the measurement callback from main.py
        from main import decode_measurement
        
        # This is a simplified version - in practice, you'd need to modify main.py
        # to accept a callback function for measurements
        device_connected = True
        device_error = None
        
        # Send initial status
        await send_status_update()
        
        # Here you would integrate with the actual laser meter code
        # For now, we'll simulate some measurements
        logger.info("Laser meter task started successfully")
        
    except Exception as e:
        logger.error(f"Error in laser meter task: {e}")
        device_connected = False
        device_error = str(e)
        await send_error_update(str(e))

async def main():
    """Main function to start the WebSocket server"""
    logger.info("Starting Bosch GLM 50C WebSocket server...")
    
    # Start the laser meter task
    laser_task = asyncio.create_task(laser_meter_task())
    
    # Start the WebSocket server
    server = await websockets.serve(
        handle_client,
        "localhost",
        8765,
        ping_interval=20,
        ping_timeout=10
    )
    
    logger.info("WebSocket server started on ws://localhost:8765")
    logger.info("Web dashboard available at http://localhost:3000")
    
    try:
        # Run both tasks concurrently
        await asyncio.gather(server.wait_closed(), laser_task)
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")


