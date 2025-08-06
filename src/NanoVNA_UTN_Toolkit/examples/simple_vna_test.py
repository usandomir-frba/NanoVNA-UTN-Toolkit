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
    
    # Common baudrates to try when auto-detecting
    COMMON_BAUDRATES = [
        4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200, 230400, 460800, 
        921600, 1000000, 1152000, 1500000, 1843200, 2000000, 3000000
    ]
    
    # Common VNA device identifiers (VID, PID, name, default_baudrate, commands)
    KNOWN_DEVICES = [
        # NanoVNA SAA2
        (0x0483, 0x5740, 'NanoVNA SAA2', 115200, [b'help\r\n', b'info\r\n', b'version\r\n']),
        # NanoVNA
        (0x0483, 0x5740, 'NanoVNA (DFU Mode)', 115200, [b'\n', b'help\n', b'version\n']),
        (0x0483, 0x3748, 'NanoVNA', 115200, [b'\n', b'help\n', b'version\n']),
        (0x0483, 0x5740, 'NanoVNA-H', 115200, [b'\n', b'help\n', b'version\n']),
        (0x0483, 0x5740, 'NanoVNA-H4', 115200, [b'\n', b'help\n', b'version\n']),
        # Original NanoVNA
        (0x0483, 0x5740, 'NanoVNA (Original)', 115200, [b'\n', b'help\n', b'version\n']),
        # V2
        (0x0483, 0x5740, 'NanoVNA-V2', 115200, [b'\n', b'help\n', b'version\n']),
        # LiteVNA
        (0x0483, 0x5740, 'LiteVNA', 115200, [b'\n', b'help\n', b'version\n']),
        # TinySA
        (0x0483, 0x5740, 'TinySA', 115200, [b'\n', b'help\n', b'version\n']),
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
            for dev_info in self.KNOWN_DEVICES:
                vid, pid, name, baudrate = dev_info[:4]
                if port['vid'] == vid and port['pid'] == pid:
                    device = port.copy()
                    device['name'] = name
                    device['baudrate'] = baudrate
                    if len(dev_info) > 4:  # If commands are specified
                        device['commands'] = dev_info[4]
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
    
    def test_connection_at_baudrate(self, port_name: str, baudrate: int = 115200, 
                                   timeout: float = 1.0, commands: list = None) -> Tuple[bool, str, str]:
        """Test connection at a specific baudrate.
        
        Args:
            port_name: Name of the serial port (e.g., 'COM8')
            baudrate: Baud rate to test
            timeout: Read timeout in seconds
            commands: List of commands to try (bytes)
            
        Returns:
            Tuple of (success, message, response)
        """
        if commands is None:
            commands = [b'\r\n', b'help\r\n', b'info\r\n', b'version\r\n']
            
        try:
            # Try to open the serial port
            with serial.Serial(port_name, baudrate=baudrate, timeout=timeout) as ser:
                # Clear any existing data in the buffer
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                
                # Try each command in sequence
                for cmd in commands:
                    try:
                        # Send the command
                        ser.write(cmd)
                        logger.debug(f"Trying baudrate {baudrate}, command: {cmd!r}")
                        
                        # Try to read a response
                        response = ser.readline().decode('ascii', errors='ignore').strip()
                        
                        if response:
                            return True, f"Device responded to {cmd.decode('ascii', errors='replace').strip()}: {response}", response
                            
                    except Exception as e:
                        logger.debug(f"Error with command {cmd!r} at {baudrate} baud: {e}")
                        continue
                
                # If no response, try to read raw data
                try:
                    response = ser.read(100)  # Try to read up to 100 bytes
                    if response:
                        return True, f"Device sent raw data: {response.decode('ascii', errors='replace')}", response.decode('ascii', errors='replace')
                except Exception as e:
                    logger.debug(f"Error reading raw data at {baudrate} baud: {e}")
                
                # If we get here, the device didn't respond as expected
                return False, "Device opened but didn't respond to any commands", ""
                    
        except serial.SerialException as e:
            return False, f"Serial error at {baudrate} baud: {str(e)}", ""
        except Exception as e:
            return False, f"Error at {baudrate} baud: {str(e)}", ""
    
    def test_connection(self, port_name: str, baudrate: int = None, 
                       timeout: float = 1.0, commands: list = None,
                       auto_detect_baudrate: bool = True) -> Tuple[bool, str]:
        """Test connection to a device, optionally trying multiple baudrates.
        
        Args:
            port_name: Name of the serial port (e.g., 'COM8')
            baudrate: Specific baudrate to try, or None to auto-detect
            timeout: Read timeout in seconds for each attempt
            commands: List of commands to try (bytes)
            auto_detect_baudrate: Whether to try multiple baudrates if the first one fails
            
        Returns:
            Tuple of (success, message)
        """
        if baudrate is None or auto_detect_baudrate:
            baudrates_to_try = [baudrate] if baudrate is not None else self.COMMON_BAUDRATES
            print(f"Trying baudrates: {', '.join(map(str, baudrates_to_try))}")
            
            # Try each baudrate
            for current_baud in baudrates_to_try:
                success, message, response = self.test_connection_at_baudrate(
                    port_name, current_baud, timeout, commands)
                
                if success:
                    # If we got a valid response, return it
                    if response.strip():
                        return True, f"[{current_baud} baud] {message}"
                    # If we opened the port but got no response, continue to next baudrate
                    # unless this is the last one to try
                    elif current_baud == baudrates_to_try[-1]:
                        return True, f"[{current_baud} baud] {message}"
                    else:
                        logger.debug(f"No response at {current_baud} baud, trying next baudrate...")
                else:
                    logger.debug(f"Failed at {current_baud} baud: {message}")
            
            # If we get here, all baudrates failed
            return False, f"Failed to communicate with device at any baudrate. Tried: {', '.join(map(str, baudrates_to_try))}"
        else:
            # Just try the specified baudrate
            success, message, _ = self.test_connection_at_baudrate(
                port_name, baudrate, timeout, commands)
            return success, message

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
    
    # For testing all baudrates, we'll ignore device detection
    device_info = None
    commands = None
    baudrate = None  # Force auto-detect all baudrates
    auto_detect = True  # Enable auto-detection of baudrate
    
    # Extended list of baudrates to test
    tester.COMMON_BAUDRATES = [
        300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 
        57600, 115200, 230400, 460800, 576000, 921600, 1000000, 1152000, 
        1500000, 1843200, 2000000, 3000000
    ]
    
    print(f"\n=== Testing Connection ===")
    print(f"Port: {args.port}")
    print(f"Device: {device_info['name'] if device_info else 'Unknown'}")
    print(f"Initial baudrate: {baudrate if baudrate else 'Auto-detect'}")
    
    # Test the connection with auto-detect if needed
    success, message = tester.test_connection(
        port_name=args.port,
        baudrate=baudrate,
        commands=commands,
        auto_detect_baudrate=auto_detect
    )
    
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
