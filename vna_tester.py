#!/usr/bin/env python3
"""
VNA Tester - A simple tool to test connection to various VNA devices

This script uses the original hardware files without modifying them.
"""

import argparse
import importlib
import inspect
import logging
import os
import sys
import serial.tools.list_ports
from typing import Dict, List, Optional, Type, Any

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class VNATester:
    """Main class for VNA testing functionality."""
    
    def __init__(self):
        self.device_classes = self._discover_device_classes()
        logger.info(f"Discovered {len(self.device_classes)} VNA device classes")
    
    def _discover_device_classes(self) -> Dict[str, Type]:
        """Discover all available VNA device classes, handling missing dependencies."""
        device_classes = {}
        hardware_dir = os.path.join('src', 'pynanovna', 'hardware')
        
        # First, try to import VNABase
        try:
            from pynanovna.hardware import VNABase
        except ImportError as e:
            logger.warning(f"Could not import VNABase: {e}")
            return {}
        
        # Known problematic modules that require external dependencies
        SKIP_MODULES = {
            'AVNA', 'Convert', 'Hardware', 'JNCRadio_VNA_3G', 'LiteVNA64',
            'NanoVNA_F_V2', 'NanoVNA_F_V3', 'NanoVNA_V2', 'SV4401A', 'SV6301A',
            'TinySA', 'VNA'
        }
        
        # Get all .py files in the hardware directory
        for filename in os.listdir(hardware_dir):
            if not filename.endswith('.py') or filename == '__init__.py':
                continue
                
            module_name = filename[:-3]  # Remove .py extension
            
            # Skip known problematic modules
            if module_name in SKIP_MODULES:
                logger.debug(f"Skipping module with external dependencies: {module_name}")
                continue
                
            try:
                # Try to import the module
                module = importlib.import_module(f'pynanovna.hardware.{module_name}')
                
                # Find all classes that inherit from VNABase
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, VNABase) and 
                        obj is not VNABase and 
                        obj.__module__ == f'pynanovna.hardware.{module_name}'):
                        device_classes[name] = obj
                        logger.debug(f"Found device class: {name}")
                        
            except ImportError as e:
                logger.warning(f"Could not import module {module_name} (missing dependencies): {e}")
            except Exception as e:
                logger.warning(f"Error processing module {module_name}: {e}")
                
        return device_classes
    
    def list_ports(self) -> List[Dict[str, Any]]:
        """List all available serial ports with detailed information."""
        ports = []
        
        for port in serial.tools.list_ports.comports():
            port_info = {
                'device': port.device,
                'description': getattr(port, 'description', 'N/A'),
                'manufacturer': getattr(port, 'manufacturer', 'N/A'),
                'product': getattr(port, 'product', 'N/A'),
                'vid': f"{port.vid:04x}" if hasattr(port, 'vid') and port.vid is not None else 'N/A',
                'pid': f"{port.pid:04x}" if hasattr(port, 'pid') and port.pid is not None else 'N/A',
                'serial_number': getattr(port, 'serial_number', 'N/A'),
            }
            ports.append(port_info)
            
        return ports
    
    def find_devices(self) -> List[Dict[str, Any]]:
        """Find all connected VNA devices."""
        from pynanovna.hardware import Interface
        
        devices = []
        
        for port in serial.tools.list_ports.comports():
            if not hasattr(port, 'vid') or not hasattr(port, 'pid') or not port.vid or not port.pid:
                continue
                
            port_info = {
                'port': port.device,
                'vid': port.vid,
                'pid': port.pid,
                'manufacturer': getattr(port, 'manufacturer', ''),
                'product': getattr(port, 'product', ''),
                'description': getattr(port, 'description', ''),
                'serial_number': getattr(port, 'serial_number', ''),
                'device_class': None,
                'device_name': 'Unknown VNA',
            }
            
            # Try to match with known device classes
            for name, dev_class in self.device_classes.items():
                try:
                    # Some devices might have specific detection methods
                    if hasattr(dev_class, 'detect'):
                        if dev_class.detect(port):
                            port_info['device_class'] = dev_class
                            port_info['device_name'] = name
                            break
                    # Fallback to VID/PID matching
                    elif (port.vid, port.pid) in getattr(dev_class, 'USB_PID_LIST', []):
                        port_info['device_class'] = dev_class
                        port_info['device_name'] = name
                        break
                        
                except Exception as e:
                    logger.debug(f"Error detecting device {name}: {e}")
                    continue
            
            # If no specific class matched but it looks like a VNA
            if not port_info['device_class'] and any(s in port_info['description'].lower() 
                                                   for s in ['vna', 'nanovna', 'vector network']):
                port_info['device_name'] = f"Possible VNA: {port_info['description']}"
                
            devices.append(port_info)
            
        return devices
    
    def test_connection(self, port: str, device_class: Optional[Type] = None) -> tuple[bool, str]:
        """Test connection to a VNA device.
        
        Args:
            port: Serial port to connect to
            device_class: Optional specific device class to use
            
        Returns:
            Tuple of (success, message)
        """
        try:
            from pynanovna.hardware import Interface
            from pynanovna.hardware.Serial import Interface as SerialInterface
            
            # Create interface with increased timeout
            interface = Interface(port)
            if hasattr(interface, 'serial'):
                interface.serial.timeout = 1.0  # Increase timeout for slow devices
            
            # If no specific device class, try to auto-detect
            if device_class is None:
                # First try basic serial communication
                try:
                    # Send a simple command to check if device responds
                    if hasattr(interface, 'write'):
                        interface.write(b"\r\n")
                        response = interface.readline().strip()
                        if response:
                            return True, f"Device responded to basic serial test: {response.decode('utf-8', errors='ignore')}"
                except Exception as e:
                    logger.debug(f"Basic serial test failed: {e}")
                
                # Try each device class
                for name, dev_class in self.device_classes.items():
                    try:
                        logger.debug(f"Trying device class: {name}")
                        vna = dev_class(interface)
                        if hasattr(vna, '_get_version'):
                            version = vna._get_version()
                            return True, f"Connected to {name} (v{version})"
                        else:
                            return True, f"Connected to {name} (version unknown)"
                    except Exception as e:
                        logger.debug(f"Not a {name}: {e}")
                        continue
                
                return False, "Could not determine device type. Device may not be supported or in an unexpected mode."
            else:
                # Use the specified device class
                vna = device_class(interface)
                if hasattr(vna, '_get_version'):
                    version = vna._get_version()
                    return True, f"Connected to {device_class.__name__} (v{version})"
                return True, f"Connected to {device_class.__name__} (version unknown)"
                
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test connection to VNA devices')
    parser.add_argument('--port', '-p', help='Serial port to use (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('--list-ports', '-l', action='store_true', help='List all available serial ports')
    parser.add_argument('--list-devices', '-d', action='store_true', help='List all detected VNA devices')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = VNATester()
    
    # List all ports if requested
    if args.list_ports:
        print("\n=== Available Serial Ports ===")
        for port in tester.list_ports():
            print(f"\nPort: {port['device']}")
            print(f"  Description: {port['description']}")
            print(f"  Manufacturer: {port['manufacturer']}")
            print(f"  Product: {port['product']}")
            print(f"  VID:PID: {port['vid']}:{port['pid']}")
            print(f"  Serial: {port['serial_number']}")
        return 0
    
    # Find VNA devices
    devices = tester.find_devices()
    
    # List devices if requested
    if args.list_devices or not args.port:
        print("\n=== Detected VNA Devices ===")
        if not devices:
            print("No VNA devices found.")
            return 1
            
        for device in devices:
            print(f"\nPort: {device['port']}")
            print(f"  Type: {device['device_name']}")
            print(f"  VID:PID: {device['vid']:04x}:{device['pid']:04x}")
            print(f"  Manufacturer: {device['manufacturer']}")
            print(f"  Product: {device['product']}")
            print(f"  Serial: {device['serial_number']}")
        
        if not args.port:
            print("\nSpecify a port with --port to test connection")
            return 0
    
    # Test connection to specified port
    target_port = args.port
    selected_device = None
    
    # Find the selected device
    for device in devices:
        if device['port'] == target_port:
            selected_device = device
            break
    
    if not selected_device:
        print(f"\n[ERROR] Device not found on port {target_port}")
        return 1
    
    # Print device info
    print(f"\n=== Device Information ===")
    print(f"Port: {selected_device['port']}")
    print(f"Type: {selected_device['device_name']}")
    print(f"VID:PID: {selected_device['vid']:04x}:{selected_device['pid']:04x}")
    print(f"Manufacturer: {selected_device['manufacturer']}")
    print(f"Product: {selected_device['product']}")
    
    # Test connection
    print("\n=== Testing Connection ===")
    success, message = tester.test_connection(
        selected_device['port'],
        selected_device.get('device_class')
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
