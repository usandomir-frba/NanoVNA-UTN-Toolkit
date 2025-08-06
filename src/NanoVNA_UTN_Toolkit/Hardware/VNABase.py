import logging
import time
from typing import Optional, Tuple

from .Serial import Interface
from .Version import Version

def drain_serial(serial_port):
    """Drain up to 8KB of outstanding data in the serial incoming buffer"""
    timeout = serial_port.timeout
    serial_port.timeout = 0.05
    for _ in range(64):  # 64 * 128 = 8KB max to drain
        if not serial_port.read(128):
            break
    serial_port.timeout = timeout

logger = logging.getLogger(__name__)

class VNABase:
    """Base class for VNA devices with minimal functionality."""
    
    name = "VNA"
    valid_datapoints = (101, 51, 11)
    serial_number = "UNKNOWN"
    
    def __init__(self, iface: Interface):
        self.serial = iface
        self.version = Version()
        self.datapoints = self.valid_datapoints[0]
        self.timeout = 0.1
        self.is_connected = False
    
    def connect(self) -> bool:
        """Attempt to connect to the VNA and verify it's responding."""
        try:
            if not self.serial.is_open:
                self.serial.open()
            
            # Test connection by getting version
            self.version = self._get_version()
            if self.version.major > 0:  # Valid version number
                self.is_connected = True
                return True
                
        except Exception as e:
            logger.error("Connection failed: %s", str(e))
            
        self.is_connected = False
        return False
    
    def disconnect(self):
        """Close the connection to the VNA."""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_connected = False
    
    def _get_version(self) -> Version:
        """Get the firmware version from the VNA."""
        try:
            with self.serial.lock:
                drain_serial(self.serial)
                self.serial.write(b"version\r")
                response = self.serial.readline().decode('ascii', errors='ignore').strip()
                if response.startswith("version "):
                    return Version(response[8:])  # Remove "version " prefix
        except Exception as e:
            logger.error("Error getting version: %s", str(e))
        
        return Version("0.0.0")  # Return default version on failure
    
    def check_connection(self) -> Tuple[bool, str]:
        """Check if the VNA is connected and responding."""
        try:
            if not self.serial or not self.serial.is_open:
                return False, "Not connected to any device"
                
            # Simple command to check if device is responsive
            with self.serial.lock:
                drain_serial(self.serial)
                self.serial.write(b"help\r")
                response = self.serial.read(10).decode('ascii', errors='ignore')
                if response:
                    return True, f"Connected to {self.name} (v{self.version})"
                
            return False, "Device not responding"
            
        except Exception as e:
            return False, f"Connection error: {str(e)}"
