#!/usr/bin/env python3
"""
Simple nanoVNA Connection Tester

This script provides basic functionality to detect and test connections to various VNA devices.
It dynamically imports and uses all device classes from the pynanovna.hardware package.
"""

import argparse
import importlib
import inspect
import logging
import os
import pkgutil
import sys
import serial.tools.list_ports
from typing import Optional, Tuple, Dict, Any, Type, List

# Add the src directory to the path so we can import our modules
sys.path.insert(0, 'src')

# Import base classes first
from pynanovna.hardware import Interface, VNABase

# Dictionary to store device classes by their names
device_classes: Dict[str, Type[VNABase]] = {}

# Dynamically import all modules in the hardware package
hardware_dir = os.path.join('src', 'pynanovna', 'hardware')
for _, module_name, _ in pkgutil.iter_modules([hardware_dir]):
    try:
        module = importlib.import_module(f'pynanovna.hardware.{module_name}')
        # Find all classes that inherit from VNABase (except VNABase itself)
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (issubclass(obj, VNABase) and obj is not VNABase and 
                    obj.__module__ == f'pynanovna.hardware.{module_name}'):
                device_classes[name] = obj
    except ImportError as e:
        logging.warning(f"Could not import {module_name}: {e}")

if not device_classes:
    logging.error("No device classes found in hardware directory!")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class DeviceFinder:
    """Helper class to find and identify VNA devices."""
    
    # Known device identifiers (VID, PID, device_class_name, is_dfu)
    KNOWN_DEVICES = [
        # Format: (vid, pid, device_class_name, is_dfu, friendly_name)
        # DFU Mode
        (0x0483, 0x5740, None, True, 'DFU Mode'),
        # NanoVNA Devices
        (0x0483, 0xdf11, 'NanoVNA', False, 'NanoVNA'),
        (0x0483, 0x3748, 'NanoVNA', False, 'NanoVNA'),
        (0x16c0, 0x0483, 'NanoVNA', False, 'NanoVNA (Legacy)'),
        # NanoVNA V2
        (0x0483, 0x5740, 'NanoVNA_V2', False, 'NanoVNA V2'),  # Same VID:PID as DFU!
        # NanoVNA-H
        (0x0483, 0x5740, 'NanoVNA_H', False, 'NanoVNA-H'),    # Same VID:PID as DFU!
        # NanoVNA-H4
        (0x0483, 0x5740, 'NanoVNA_H4', False, 'NanoVNA-H4'),  # Same VID:PID as DFU!
        # LiteVNA64
        (0x0483, 0x5740, 'LiteVNA64', False, 'LiteVNA64'),    # Same VID:PID as DFU!
        # TinySA
        (0x0483, 0x5740, 'TinySA', False, 'TinySA'),          # Same VID:PID as DFU!
        # Add more devices as needed
    ]
    
    @classmethod
    def find_devices(cls) -> List[Dict[str, Any]]:
        """Find all connected VNA devices.
        
        Returns:
            List of dictionaries with device information.
        """
        devices = []
        
        for port in serial.tools.list_ports.comports():
            if not hasattr(port, 'vid') or not hasattr(port, 'pid'):
                continue
                
            port_info = {
                'port': port.device,
                'vid': port.vid if port.vid else 0,
                'pid': port.pid if port.pid else 0,
                'serial_number': getattr(port, 'serial_number', ''),
                'manufacturer': getattr(port, 'manufacturer', ''),
                'product': getattr(port, 'product', ''),
                'description': getattr(port, 'description', ''),
                'device_class': None,
                'device_name': 'Unknown VNA',
                'is_dfu': False,
                'port_obj': port
            }
            
            # Check against known devices
            device_found = False
            for vid, pid, dev_class_name, is_dfu, friendly_name in cls.KNOWN_DEVICES:
                if (port_info['vid'] == vid and port_info['pid'] == pid):
                    port_info['is_dfu'] = is_dfu
                    port_info['device_name'] = friendly_name
                    
                    # Try to find the appropriate device class
                    if dev_class_name and dev_class_name in device_classes:
                        port_info['device_class'] = device_classes[dev_class_name]
                    
                    devices.append(port_info)
                    device_found = True
                    break
            
            # If not in our known devices list but looks like a VNA
            if not device_found and any(s in port_info['description'].lower() 
                                      for s in ['vna', 'nanovna', 'vector network', 'tinySA']):
                port_info['device_name'] = f"Possible VNA: {port_info['description']}"
                devices.append(port_info)
                    
        return devices


def test_connection(port: str, device_class: Optional[Type[VNABase]] = None, 
                   is_dfu: bool = False) -> Tuple[bool, str]:
    """Test connection to a VNA device.
    
    Args:
        port: Serial port to connect to
        device_class: The VNA device class to use (None for auto-detect)
        is_dfu: Whether the device is in DFU mode
        
    Returns:
        Tuple of (success, message)
    """
    if is_dfu:
        return False, "DFU mode detected. Device needs to be in normal mode for testing."
    
    try:
        interface = Interface(port)
        
        # If no specific device class provided, try to auto-detect
        if device_class is None:
            # Try each device class until one works
            for name, dev_class in device_classes.items():
                try:
                    vna = dev_class(interface)
                    # Try to get version to verify connection
                    version = vna._get_version()
                    return True, f"Connected to {name} (v{version})"
                except Exception as e:
                    logger.debug(f"Not a {name}: {e}")
                    continue
            
            return False, "Could not determine device type. Try specifying the device class."
        else:
            # Use the specified device class
            vna = device_class(interface)
            version = vna._get_version()
            return True, f"Connected to {device_class.__name__} (v{version})"
        
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description='Test connection to nanoVNA devices')
    parser.add_argument('--port', '-p', help='Serial port to use (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    parser.add_argument('--list', '-l', action='store_true', help='List all available serial ports')
    parser.add_argument('--force', '-f', action='store_true', help='Force connection attempt even if in DFU mode')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # List all ports if requested
    if args.list:
        print("\n=== Available Serial Ports ===")
        for port in serial.tools.list_ports.comports():
            print(f"\nPort: {port.device}")
            if hasattr(port, 'description'):
                print(f"  Description: {port.description}")
            if hasattr(port, 'manufacturer'):
                print(f"  Manufacturer: {port.manufacturer}")
            if hasattr(port, 'product'):
                print(f"  Product: {port.product}")
            if hasattr(port, 'vid') and port.vid is not None:
                print(f"  VID: 0x{port.vid:04x}")
            if hasattr(port, 'pid') and port.pid is not None:
                print(f"  PID: 0x{port.pid:04x}")
        return 0
    
    # Find VNA devices
    devices = DeviceFinder.find_devices()
    
    if not devices:
        print("\n[ERROR] No VNA devices found.")
        return 1
    
    print(f"\n=== Found {len(devices)} VNA device(s) ===")
    
    # If port is specified, use it; otherwise use the first found device
    target_port = args.port
    if not target_port:
        target_port = devices[0]['port']
    
    # Find the selected device
    selected_device = None
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
    print(f"VID: 0x{selected_device['vid']:04x}")
    print(f"PID: 0x{selected_device['pid']:04x}")
    print(f"Manufacturer: {selected_device['manufacturer']}")
    print(f"Product: {selected_device['product']}")
    print(f"Serial: {selected_device['serial_number']}")
    
    # Test connection
    print("\n=== Testing Connection ===")
    
    # If force flag is set, ignore DFU detection
    is_dfu = False if args.force else selected_device['is_dfu']
    
    success, message = test_connection(
        selected_device['port'],
        selected_device['device_class'],
        is_dfu
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
