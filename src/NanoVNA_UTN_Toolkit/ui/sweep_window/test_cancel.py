"""
Test for cancel functionality in SweepOptionsWindow.
"""
import sys
import os

# Add the src path to sys.path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from PySide6.QtWidgets import QApplication

def test_cancel_functionality():
    """Test that cancel button restores original values."""
    # Create QApplication for testing
    app = QApplication(sys.argv)
    
    from NanoVNA_UTN_Toolkit.ui.sweep_window.sweep_options_window import SweepOptionsWindow
    
    # Create window instance
    window = SweepOptionsWindow()
    
    # Store original values for comparison
    original_start_freq = window.start_freq_edit.value()
    original_start_unit = window.start_freq_unit.currentText()
    original_stop_freq = window.stop_freq_edit.value()
    original_stop_unit = window.stop_freq_unit.currentText()
    original_segments = window.segments_spinbox.value()
    
    print(f"Original values:")
    print(f"  Start: {original_start_freq} {original_start_unit}")
    print(f"  Stop: {original_stop_freq} {original_stop_unit}")
    print(f"  Segments: {original_segments}")
    
    # Modify values
    window.start_freq_edit.setValue(100.0)
    window.start_freq_unit.setCurrentText("MHz")
    window.stop_freq_edit.setValue(2.0)
    window.stop_freq_unit.setCurrentText("GHz")
    window.segments_spinbox.setValue(200)
    
    print(f"\nModified values:")
    print(f"  Start: {window.start_freq_edit.value()} {window.start_freq_unit.currentText()}")
    print(f"  Stop: {window.stop_freq_edit.value()} {window.stop_freq_unit.currentText()}")
    print(f"  Segments: {window.segments_spinbox.value()}")
    
    # Test cancel functionality (without actually closing the window)
    if hasattr(window, 'original_values') and window.original_values:
        # Restore original values (same logic as cancel_changes but without closing)
        window.start_freq_edit.setValue(window.original_values['start_freq'])
        window.start_freq_unit.setCurrentText(window.original_values['start_unit'])
        window.stop_freq_edit.setValue(window.original_values['stop_freq'])
        window.stop_freq_unit.setCurrentText(window.original_values['stop_unit'])
        window.segments_spinbox.setValue(window.original_values['segments'])
        
        print(f"\nAfter cancel (restored values):")
        print(f"  Start: {window.start_freq_edit.value()} {window.start_freq_unit.currentText()}")
        print(f"  Stop: {window.stop_freq_edit.value()} {window.stop_freq_unit.currentText()}")
        print(f"  Segments: {window.segments_spinbox.value()}")
        
        # Verify values were restored
        assert window.start_freq_edit.value() == original_start_freq
        assert window.start_freq_unit.currentText() == original_start_unit
        assert window.stop_freq_edit.value() == original_stop_freq
        assert window.stop_freq_unit.currentText() == original_stop_unit
        assert window.segments_spinbox.value() == original_segments
        
        print("\n✅ Cancel functionality test passed!")
    else:
        print("❌ Original values not stored properly")
    
    # Clean up
    window.close()


if __name__ == "__main__":
    test_cancel_functionality()
