#!/usr/bin/env python3
"""
Simple nanoVNA connection checker.

This script attempts to connect to a nanoVNA device and verifies the connection.
"""

import argparse
import logging
import sys
import serial.tools.list_ports
from pynanovna.hardware import NanoVNA, Interface

def find_nanovna_port():
    """Attempt to find a nanoVNA device by checking common USB serial ports."""
    # Common VID:PID pairs for nanoVNA devices
    NANOVNA_VIDPIDS = [
        (0x0483, 0x5740),  # STMicroelectronics in DFU mode
        (0x0483, 0xdf11),  # STMicroelectronics in normal mode
        (0x0483, 0x3748),  # STMicroelectronics
        (0x0483, 0x374b),  # STMicroelectronics
        (0x16c0, 0x0483),  # VOTI/OpenMoko (older devices)
    ]
    
    for port in serial.tools.list_ports.comports():
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            if (port.vid, port.pid) in NANOVNA_VIDPIDS:
                return port.device
    
    # If no device found by VID/PID, try to find by name
    for port in serial.tools.list_ports.comports():
        if 'nanoVNA' in port.description or 'VNA' in port.description:
            return port.device
    
    return None

def main():
    """Main function to check nanoVNA connection."""
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Check nanoVNA connection')
    parser.add_argument('--port', '-p', help='Serial port to use (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger(__name__)
    
    # Find or use the specified port
    port = args.port
    if not port:
        port = find_nanovna_port()
        if not port:
            print("Error: No nanoVNA device found. Please specify the port manually with --port")
            return 1
    
    print(f"Attempting to connect to {port}...")
    
    # Create interface and VNA instances
    try:
        iface = Interface(port=port)
        vna = NanoVNA(iface)
        
        # Attempt to connect
        if vna.connect():
            success, message = vna.check_connection()
            print(f"✓ {message}")
            return 0
        else:
            print(f"✗ Failed to connect to device on {port}")
            return 1
            
    except serial.SerialException as e:
        print(f"Serial port error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1
    finally:
        if 'vna' in locals():
            vna.disconnect()

if __name__ == "__main__":
    sys.exit(main())
