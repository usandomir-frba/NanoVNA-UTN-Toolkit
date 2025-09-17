"""
Test for device-specific sweep points limits in SweepOptionsWindow.
"""
import sys
import os

# Add the src path to sys.path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from PySide6.QtWidgets import QApplication

# Mock VNA device classes for testing
class MockNanoVNA_H4:
    name = "NanoVNA-H4"
    sweep_points_min = 11
    sweep_points_max = 101

class MockSV4401A:
    name = "SV4401A"
    sweep_points_min = 101
    sweep_points_max = 1001

class MockLiteVNA64:
    name = "LiteVNA64"
    sweep_points_min = 11
    sweep_points_max = 65535

def test_device_limits():
    """Test that sweep points limits are correctly applied for different devices."""
    # Create QApplication for testing
    app = QApplication(sys.argv)
    
    from NanoVNA_UTN_Toolkit.ui.sweep_window.sweep_options_window import SweepOptionsWindow
    
    # Test with different mock devices
    test_devices = [
        MockNanoVNA_H4(),
        MockSV4401A(),
        MockLiteVNA64(),
        None  # No device (should use defaults)
    ]
    
    for device in test_devices:
        print(f"\nTesting with device: {device.name if device else 'No device'}")
        
        # Create window with the mock device
        window = SweepOptionsWindow(vna_device=device)
        
        # Check that limits were applied correctly
        if device:
            expected_min = device.sweep_points_min
            expected_max = device.sweep_points_max
            device_name = device.name
        else:
            expected_min = 11  # Default
            expected_max = 1001  # Default
            device_name = "Default"
        
        actual_min = window.sweep_points_min
        actual_max = window.sweep_points_max
        
        print(f"  Expected limits: {expected_min} - {expected_max}")
        print(f"  Actual limits: {actual_min} - {actual_max}")
        
        # Check spinbox range
        spinbox_min = window.segments_spinbox.minimum()
        spinbox_max = window.segments_spinbox.maximum()
        print(f"  Spinbox range: {spinbox_min} - {spinbox_max}")
        
        # Verify limits match
        assert actual_min == expected_min, f"Min limit mismatch for {device_name}"
        assert actual_max == expected_max, f"Max limit mismatch for {device_name}"
        assert spinbox_min == expected_min, f"Spinbox min mismatch for {device_name}"
        assert spinbox_max == expected_max, f"Spinbox max mismatch for {device_name}"
        
        print(f"  ✅ Limits correctly applied for {device_name}")
        
        # Clean up
        window.close()
    
    print("\n✅ All device limit tests passed!")


if __name__ == "__main__":
    test_device_limits()
