#!/usr/bin/env python3
"""
Simple nanoVNA connection checker.

This script attempts to connect to a nanoVNA device and verifies the connection.
"""

import argparse
import logging
import sys
import serial
import serial.tools.list_ports

# Add the src directory to the path so we can import our modules
sys.path.insert(0, 'src')

from pynanovna.hardware import NanoVNA, Interface, drain_serial

def list_serial_ports():
    """List all available serial ports with detailed information."""
    ports = []
    for port in serial.tools.list_ports.comports():
        port_info = {
            'device': port.device,
            'name': port.name,
            'description': getattr(port, 'description', 'N/A'),
            'hwid': getattr(port, 'hwid', 'N/A'),
            'vid': f"0x{port.vid:04x}" if hasattr(port, 'vid') and port.vid is not None else 'N/A',
            'pid': f"0x{port.pid:04x}" if hasattr(port, 'pid') and port.pid is not None else 'N/A',
            'serial_number': getattr(port, 'serial_number', 'N/A'),
            'manufacturer': getattr(port, 'manufacturer', 'N/A'),
            'product': getattr(port, 'product', 'N/A'),
        }
        ports.append(port_info)
    return ports

def list_all_ports():
    """List all available serial ports with detailed information."""
    ports = []
    for port in serial.tools.list_ports.comports():
        port_info = {
            'device': port.device,
            'name': port.name,
            'description': getattr(port, 'description', 'N/A'),
            'hwid': getattr(port, 'hwid', 'N/A'),
            'vid': f"0x{port.vid:04x}" if hasattr(port, 'vid') and port.vid is not None else 'N/A',
            'pid': f"0x{port.pid:04x}" if hasattr(port, 'pid') and port.pid is not None else 'N/A',
            'serial_number': getattr(port, 'serial_number', 'N/A'),
            'manufacturer': getattr(port, 'manufacturer', 'N/A'),
            'product': getattr(port, 'product', 'N/A'),
        }
        ports.append(port_info)
    return ports

def find_nanovna_port():
    """Attempt to find a nanoVNA device by checking common USB serial ports."""
    logger = logging.getLogger(__name__)
    
    # Common VID:PID pairs for nanoVNA devices
    NANOVNA_VIDPIDS = {
        (0x0483, 0x5740): 'DFU Mode',        # STM32 DFU Mode (Linux/Windows)
        (0x0483, 0xdf11): 'Normal Mode',     # STM32 Normal Mode
        (0x0483, 0x3748): 'Normal Mode',     # STM32 Normal Mode (alternative)
        (0x0483, 0x374b): 'Normal Mode',     # STM32 Normal Mode (alternative)
        (0x16c0, 0x0483): 'Legacy Mode',    # VOTI/OpenMoko (older devices)
    }
    
    # Special cases where we need to check manufacturer/product
    SPECIAL_CASES = [
        # (VID, PID, manufacturer, product, mode)
        (0x0483, 0x5740, 'Microsoft', None, 'Normal Mode'),  # Windows driver in normal mode
        (0x0483, 0x5740, None, None, 'DFU Mode'),           # Default for this VID:PID
    ]
    
    # First, list all ports for debugging
    all_ports = list(serial.tools.list_ports.comports())
    logger.debug(f"Found {len(all_ports)} serial port(s)")
    
    for port in all_ports:
        port_info = {
            'device': port.device,
            'vid': getattr(port, 'vid', None),
            'pid': getattr(port, 'pid', None),
            'description': getattr(port, 'description', ''),
            'manufacturer': getattr(port, 'manufacturer', '')
        }
        
        # Log port info for debugging
        logger.debug(f"Checking port: {port_info}")
        
        # Check by special cases first (manufacturer/product specific)
        if hasattr(port, 'vid') and hasattr(port, 'pid') and port.vid is not None and port.pid is not None:
            port_manufacturer = getattr(port, 'manufacturer', None)
            port_product = getattr(port, 'product', None)
            
            # Check special cases
            for vid, pid, manufacturer, product, mode in SPECIAL_CASES:
                if (port.vid == vid and 
                    port.pid == pid and 
                    (manufacturer is None or port_manufacturer == manufacturer) and
                    (product is None or port_product == product)):
                    logger.info(f"Found nanoVNA device in {mode} at {port.device} "
                              f"(VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}, "
                              f"Manufacturer: {port_manufacturer or 'N/A'}, Product: {port_product or 'N/A'})")
                    return port.device, mode
            
            # Fall back to standard VID:PID lookup
            mode = NANOVNA_VIDPIDS.get((port.vid, port.pid))
            if mode:
                logger.info(f"Found nanoVNA device in {mode} at {port.device} "
                          f"(VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x}, "
                          f"Manufacturer: {port_manufacturer or 'N/A'}, Product: {port_product or 'N/A'})")
                return port.device, mode
        
        # Then check by description
        desc = getattr(port, 'description', '').lower()
        if 'nanovna' in desc or 'vna' in desc:
            logger.info(f"Found VNA device by description at {port.device}: {port.description}")
            return port.device, 'Normal Mode (by description)'
    
    logger.warning("No nanoVNA device found by VID:PID or description")
    return None, None

def main():
    """Main function to check nanoVNA connection."""
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Check nanoVNA connection')
    parser.add_argument('--port', '-p', help='Serial port to use (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    parser.add_argument('--list', '-l', action='store_true', help='List all available serial ports and exit')
    parser.add_argument('--force', '-f', action='store_true', help='Force connection even if in DFU mode')
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger(__name__)
    
    # List all available serial ports if requested
    if args.list:
        print("\n=== Available Serial Ports ===")
        ports = list_serial_ports()
        if not ports:
            print("No serial ports found!")
            return 1
            
        for i, port in enumerate(ports, 1):
            print(f"\nPort {i}:")
            for key, value in port.items():
                print(f"  {key}: {value}")
        print("\nUse --port COMx to specify a port (replace COMx with the actual port name)")
        return 0
    
    # List all ports if requested
    if args.list:
        print("\n=== Available Serial Ports ===")
        ports = list_all_ports()
        if not ports:
            print("No serial ports found!")
            return 1
            
        for i, port in enumerate(ports, 1):
            print(f"\nPort {i}:")
            for key, value in port.items():
                print(f"  {key}: {value}")
        print("\nUse --port COMx to specify a port (replace COMx with the actual port name)")
        return 0
    
    # Find or use the specified port
    port = args.port
    mode = None
    
    if not port:
        port, mode = find_nanovna_port()
        if not port:
            print("\n[ERROR] No nanoVNA device found. Please specify the port manually with --port")
            print("Available ports:")
            for p in list_all_ports():
                print(f"  {p['device']} - {p.get('description', 'N/A')}")
            return 1
    
    print(f"\n=== Connection Attempt ===")
    print(f"Port: {port}")
    if mode:
        print(f"Detected mode: {mode}")
    
    # Check if device is in DFU mode
    is_dfu = False
    port_manufacturer = None
    
    for port_info in serial.tools.list_ports.comports():
        if port_info.device == port and hasattr(port_info, 'vid') and hasattr(port_info, 'pid'):
            port_manufacturer = getattr(port_info, 'manufacturer', '')
            
            # Special case: Microsoft driver in normal mode
            if port_manufacturer == 'Microsoft' and (port_info.vid, port_info.pid) == (0x0483, 0x5740):
                print("\n[INFO] Detected Microsoft driver in normal mode")
                is_dfu = False
                break
                
            # Standard DFU detection
            if (port_info.vid, port_info.pid) == (0x0483, 0x5740):  # DFU mode
                is_dfu = True
                print("\n[WARNING] Device is in DFU (firmware update) mode.")
                if not args.force:
                    print("To use the device normally, please:")
                    print("1. Disconnect the device")
                    print("2. Connect it normally (without pressing any buttons)")
                    print("3. If it still enters DFU mode, check for a physical DFU button")
                    print("\nTo force connection in DFU mode, use --force")
                    return 1
    
    try:
        # Try to connect to the device
        print(f"\nAttempting to connect to {port}...")
        
        # Set appropriate timeout for the mode
        timeout = 5.0 if is_dfu else 2.0
        
        interface = Interface(port, timeout=timeout)
        vna = NanoVNA(interface)
        
        # Try to connect and check version
        print("Checking connection and version...")
        connected, message = vna.check_connection()
        
        if connected:
            print(f"\n[SUCCESS] {message}")
            print("\n=== Connection Successful ===")
            print(f"Port: {port}")
            print(f"Mode: {'DFU' if is_dfu else 'Normal'}")
            print(f"Message: {message}")
            return 0
        else:
            print(f"\n[ERROR] Connection failed: {message}")
            if is_dfu:
                print("\nNote: The device is in DFU mode. To use normal VNA features:")
                print("1. Disconnect the device")
                print("2. Connect it without pressing any buttons")
                print("3. If it still enters DFU mode, check for a physical DFU button")
            return 1
            
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the device is properly connected")
        print("2. Check if another program is using the port")
        print("3. Try disconnecting and reconnecting the device")
        if 'Access is denied' in str(e):
            print("4. Close any other programs that might be using this port")
        return 1
        
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
        
    finally:
        if 'vna' in locals():
            try:
                vna.disconnect()
            except:
                pass  # Ignore errors during disconnect

if __name__ == "__main__":
    sys.exit(main())
