#!/usr/bin/env python3
"""
Simple script to find your Bosch GLM 50C device
"""

import asyncio
import logging
from bleak import BleakScanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scan_for_devices():
    """Scan for all BLE devices and look for Bosch GLM 50C"""
    logger.info("Scanning for BLE devices...")
    logger.info("Make sure your Bosch GLM 50C is turned on and in pairing mode!")
    logger.info("Press Ctrl+C to stop scanning")
    
    try:
        devices = await BleakScanner.discover(timeout=10.0)
        
        logger.info(f"Found {len(devices)} devices:")
        logger.info("=" * 50)
        
        bosch_devices = []
        
        for device in devices:
            name = device.name or "Unknown"
            address = device.address
            rssi = getattr(device, 'rssi', 'N/A')
            
            logger.info(f"Name: {name}")
            logger.info(f"Address: {address}")
            logger.info(f"RSSI: {rssi}")
            logger.info("-" * 30)
            
            # Look for Bosch devices
            if "bosch" in name.lower() or "glm" in name.lower() or "50c" in name.lower():
                bosch_devices.append((name, address))
        
        if bosch_devices:
            logger.info("🎯 BOSCH DEVICES FOUND:")
            for name, address in bosch_devices:
                logger.info(f"  {name}: {address}")
        else:
            logger.info("❌ No Bosch devices found. Make sure your device is on and in pairing mode.")
            
    except KeyboardInterrupt:
        logger.info("Scan stopped by user")
    except Exception as e:
        logger.error(f"Error scanning: {e}")

if __name__ == "__main__":
    asyncio.run(scan_for_devices())
