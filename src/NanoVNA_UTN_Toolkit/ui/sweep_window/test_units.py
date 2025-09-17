"""
Quick test for unit conversion functionality in SweepOptionsWindow.
"""
import sys
import os

# Add the src path to sys.path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from PySide6.QtWidgets import QApplication

def test_unit_conversions():
    """Test unit conversion methods."""
    # Create QApplication for testing
    app = QApplication(sys.argv)
    
    from NanoVNA_UTN_Toolkit.ui.sweep_window.sweep_options_window import SweepOptionsWindow
    
    # Create a minimal window instance to test methods
    window = SweepOptionsWindow()
    
    # Test frequency_to_hz conversions
    assert window.frequency_to_hz(1, "Hz") == 1
    assert window.frequency_to_hz(1, "kHz") == 1000
    assert window.frequency_to_hz(1, "MHz") == 1000000
    assert window.frequency_to_hz(1, "GHz") == 1000000000
    
    # Test hz_to_frequency conversions
    assert window.hz_to_frequency(1000, "kHz") == 1.0
    assert window.hz_to_frequency(1000000, "MHz") == 1.0
    assert window.hz_to_frequency(1000000000, "GHz") == 1.0
    
    # Test default values and max frequency
    print("Testing default range:")
    print(f"50 kHz = {window.frequency_to_hz(50, 'kHz')} Hz")
    print(f"1.5 GHz = {window.frequency_to_hz(1.5, 'GHz')} Hz")
    print(f"Max frequency limit: {window.max_frequency_hz / 1e9:.1f} GHz")
    
    # Test max frequency validation
    max_freq_ghz = window.max_frequency_hz / 1e9
    print(f"Maximum allowed frequency: {max_freq_ghz:.1f} GHz")
    
    print("✅ All unit conversion tests passed!")
    
    # Clean up
    window.close()


if __name__ == "__main__":
    test_unit_conversions()
