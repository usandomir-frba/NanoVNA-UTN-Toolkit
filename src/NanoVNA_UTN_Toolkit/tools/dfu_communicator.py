#!/usr/bin/env python3
"""
nanoVNA DFU Mode Communicator

This script attempts to communicate with a nanoVNA device in DFU (Device Firmware Update) mode.
"""

import argparse
import logging
import sys
import serial
import serial.tools.list_ports
from time import sleep

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class DFUCommunicator:
    """Class to communicate with nanoVNA in DFU mode."""
    
    def __init__(self, port=None, baudrate=115200, timeout=1.0):
        """Initialize the DFU communicator."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
    
    def connect(self):
        """Connect to the DFU device."""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            logger.info(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the DFU device."""
        if self.serial and self.serial.is_open:
            self.serial.close()
            logger.info("Disconnected from device")
    
    def send_command(self, command, expect_response=True, timeout=1.0):
        """Send a command to the DFU device and optionally wait for a response."""
        if not self.serial or not self.serial.is_open:
            logger.error("Not connected to any device")
            return None
        
        try:
            # Clear buffers
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            # Send command
            logger.debug(f"Sending command: {command}")
            self.serial.write((command + '\r\n').encode('ascii'))
            self.serial.flush()
            
            if not expect_response:
                return None
                
            # Read response
            response = b''
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                if self.serial.in_waiting > 0:
                    chunk = self.serial.read(self.serial.in_waiting)
                    response += chunk
                    # If we get a newline, we might have the complete response
                    if b'\n' in chunk:
                        break
                time.sleep(0.01)
            
            if response:
                response_str = response.decode('ascii', errors='replace').strip()
                logger.debug(f"Received response: {response_str}")
                return response_str
            return None
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return None
    
    def get_info(self):
        """Get information from the DFU device."""
        info = {}
        
        # Try common DFU commands
        commands = {
            'version': 'version',
            'help': 'help',
            'info': 'info',
            'get': 'get',
            'dfu_info': '?',
        }
        
        for name, cmd in commands.items():
            response = self.send_command(cmd)
            if response:
                info[name] = response
        
        return info

def find_dfu_device():
    """Find a device in DFU mode."""
    # Common DFU mode VID:PID for STM32
    DFU_VIDPIDS = [
        (0x0483, 0x5740),  # STMicroelectronics in DFU mode
    ]
    
    for port in serial.tools.list_ports.comports():
        if hasattr(port, 'vid') and hasattr(port, 'pid') and port.vid is not None and port.pid is not None:
            if (port.vid, port.pid) in DFU_VIDPIDS:
                logger.info(f"Found DFU device: {port.device} (VID: 0x{port.vid:04x}, PID: 0x{port.pid:04x})")
                return port.device
    
    logger.warning("No DFU device found")
    return None

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Communicate with nanoVNA in DFU mode')
    parser.add_argument('--port', '-p', help='Serial port to use (e.g., COM3 or /dev/ttyUSB0)')
    parser.add_argument('--baudrate', '-b', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Find DFU device if not specified
    port = args.port
    if not port:
        port = find_dfu_device()
        if not port:
            logger.error("No DFU device found. Please specify a port with --port")
            return 1
    
    # Create and connect to DFU device
    dfu = DFUCommunicator(port=port, baudrate=args.baudrate)
    
    try:
        if not dfu.connect():
            return 1
        
        print(f"\n=== Communicating with DFU device on {port} ===\n")
        
        # Try to get device information
        print("Attempting to get device information...")
        info = dfu.get_info()
        
        if info:
            print("\n=== Device Information ===")
            for key, value in info.items():
                print(f"{key}: {value}")
        else:
            print("No information received from device")
        
        # Try to send some common commands
        print("\n=== Testing Commands ===")
        test_commands = [
            'version',
            'help',
            'info',
            '?',
            'get',
            'read 0x08000000 16',  # Try to read first 16 bytes of flash
        ]
        
        for cmd in test_commands:
            print(f"\nCommand: {cmd}")
            response = dfu.send_command(cmd)
            if response:
                print(f"Response: {response}")
            else:
                print("No response or error")
        
        print("\n=== DFU Communication Complete ===")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.debug)
        return 1
    finally:
        dfu.disconnect()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
