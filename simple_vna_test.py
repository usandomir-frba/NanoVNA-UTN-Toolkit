#!/usr/bin/env python3
"""
Simple VNA Tester - Basic connectivity test for VNA devices

This script provides minimal functionality to test basic serial communication
with VNA devices without importing problematic modules.
"""

import argparse
import logging
import serial
import serial.tools.list_ports
import sys
from typing import Dict, List, Optional, Tuple, Type, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('vna_tester')

class SimpleVNATester:
    """Simple VNA tester with minimal dependencies."""
    
    # Common VNA device identifiers (VID, PID, name, baudrate)
    KNOWN_DEVICES = [
        # NanoVNA
        (0x0483, 0x5740, 'NanoVNA (DFU Mode)', 115200),
        (0x0483, 0x3748, 'NanoVNA', 115200),
        (0x0483, 0x5740, 'NanoVNA-H', 115200),
        (0x0483, 0x5740, 'NanoVNA-H4', 115200),
        # Original NanoVNA
        (0x0483, 0x5740, 'NanoVNA (Original)', 115200),
        # V2
        (0x0483, 0x5740, 'NanoVNA-V2', 115200),
        # LiteVNA
        (0x0483, 0x5740, 'LiteVNA', 115200),
        # TinySA
        (0x0483, 0x5740, 'TinySA', 115200),
    ]
    
    def __init__(self):
        self.available_ports = self.list_ports()
        self.detected_devices = self.detect_devices()
    
    def list_ports(self) -> List[Dict[str, Any]]:
        """List all available serial ports with detailed information."""
        ports = []
        
        for port in serial.tools.list_ports.comports():
            port_info = {
                'device': port.device,
                'description': getattr(port, 'description', 'N/A'),
                'manufacturer': getattr(port, 'manufacturer', 'N/A'),
                'product': getattr(port, 'product', 'N/A'),
                'vid': port.vid if hasattr(port, 'vid') and port.vid is not None else None,
                'pid': port.pid if hasattr(port, 'pid') and port.pid is not None else None,
                'serial_number': getattr(port, 'serial_number', 'N/A'),
            }
            ports.append(port_info)
            
        return ports
    
    def detect_devices(self) -> List[Dict[str, Any]]:
        """Detect VNA devices from available ports."""
        devices = []
        
        for port in self.available_ports:
            if port['vid'] is None or port['pid'] is None:
                continue
                
            # Check against known devices
            for vid, pid, name, baudrate in self.KNOWN_DEVICES:
                if port['vid'] == vid and port['pid'] == pid:
                    device = port.copy()
                    device['name'] = name
                    device['baudrate'] = baudrate
                    devices.append(device)
                    break
            else:
                # If not in known devices but looks like a VNA
                if any(s in port['description'].lower() 
                      for s in ['vna', 'nanovna', 'vector network', 'tinysa']):
                    port['name'] = f"Possible VNA: {port['description']}"
                    port['baudrate'] = 115200  # Default baudrate
                    devices.append(port)
        
        return devices
    
    def test_connection(self, port_name: str, baudrate: int = 115200, 
                       timeout: float = 1.0) -> Tuple[bool, str]:
        """Test basic serial connection to a device.
        
        Args:
            port_name: Name of the serial port (e.g., 'COM8')
            baudrate: Baud rate to use for the connection
            timeout: Read timeout in seconds
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Try to open the serial port
            with serial.Serial(port_name, baudrate=baudrate, timeout=timeout) as ser:
                # Send a newline to trigger a response
                ser.write(b'\n')
                
                # Try to read a response
                response = ser.readline().decode('ascii', errors='ignore').strip()
                
                if response:
                    return True, f"Device responded: {response}"
                else:
                    # Try sending 'help' command
                    ser.write(b'help\n')
                    response = ser.readline().decode('ascii', errors='ignore').strip()
                    if response:
                        return True, f"Device responded to 'help': {response}"
                    
                    # Try sending 'version' command
                    ser.write(b'version\n')
                    response = ser.readline().decode('ascii', errors='ignore').strip()
                    if response:
                        return True, f"Device version: {response}"
                    
                    # If we get here, the device didn't respond as expected
                    return True, "Device opened successfully but didn't respond to commands"
                    
        except serial.SerialException as e:
            return False, f"Serial error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test connection to VNA devices')
    parser.add_argument('--port', '-p', help='Serial port to use (e.g., COM8)')
    parser.add_argument('--baudrate', '-b', type=int, default=115200,
                       help='Baud rate (default: 115200)')
    parser.add_argument('--list-ports', '-l', action='store_true',
                       help='List all available serial ports')
    parser.add_argument('--list-devices', '-d', action='store_true',
                       help='List detected VNA devices')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = SimpleVNATester()
    
    # List all ports if requested
    if args.list_ports:
        print("\n=== Available Serial Ports ===")
        for port in tester.available_ports:
            print(f"\nPort: {port['device']}")
            print(f"  Description: {port['description']}")
            print(f"  Manufacturer: {port['manufacturer']}")
            print(f"  Product: {port['product']}")
            vid = f"{port['vid']:04x}" if port['vid'] is not None else 'N/A'
            pid = f"{port['pid']:04x}" if port['pid'] is not None else 'N/A'
            print(f"  VID:PID: {vid}:{pid}")
            print(f"  Serial: {port['serial_number']}")
        return 0
    
    # List detected devices if requested
    if args.list_devices or not args.port:
        print("\n=== Detected VNA Devices ===")
        if not tester.detected_devices:
            print("No VNA devices detected.")
            if args.port:
                print("Will attempt to connect to the specified port anyway.")
            else:
                return 1
        else:
            for device in tester.detected_devices:
                print(f"\nPort: {device['device']}")
                print(f"  Type: {device['name']}")
                print(f"  VID:PID: {device['vid']:04x}:{device['pid']:04x}")
                print(f"  Baudrate: {device['baudrate']}")
        
        if not args.port:
            print("\nSpecify a port with --port to test connection")
            return 0
    
    # Test connection to specified port
    port_name = args.port
    baudrate = args.baudrate
    
    print(f"\n=== Testing Connection ===")
    print(f"Port: {port_name}")
    print(f"Baudrate: {baudrate}")
    
    success, message = tester.test_connection(port_name, baudrate)
    
    if success:
        print(f"\n[SUCCESS] {message}")
    else:
        print(f"\n[ERROR] {message}")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
