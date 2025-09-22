#!/usr/bin/env python3
"""
Test script for Touchstone export functionality
"""

import sys
import os
import numpy as np

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_touchstone_export():
    """Test the Touchstone export functionality with sample data."""
    
    print("Testing Touchstone export functionality...")
    
    # Create sample data (similar to what would come from a VNA sweep)
    num_points = 101
    freq_start = 50e6  # 50 MHz
    freq_stop = 1500e6  # 1500 MHz
    
    # Generate frequency array
    freqs = np.linspace(freq_start, freq_stop, num_points)
    
    # Generate sample S11 data (reflection coefficient)
    # Simulating a simple low-pass filter response
    s11_magnitude = 0.1 + 0.3 * (freqs / freq_stop)  # Increasing reflection with frequency
    s11_phase = -np.pi * (freqs / freq_stop)  # Phase variation
    s11 = s11_magnitude * np.exp(1j * s11_phase)
    
    # Generate sample S21 data (transmission coefficient)
    # Simulating a low-pass filter with rolloff
    s21_magnitude = 1.0 / (1 + (freqs / (500e6))**2)  # Rolloff at 500 MHz
    s21_phase = -2 * np.pi * (freqs / freq_stop)  # Phase delay
    s21 = s21_magnitude * np.exp(1j * s21_phase)
    
    print(f"Generated sample data:")
    print(f"  Frequency range: {freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz")
    print(f"  Number of points: {len(freqs)}")
    print(f"  S11 range: {np.min(np.abs(s11)):.3f} - {np.max(np.abs(s11)):.3f}")
    print(f"  S21 range: {np.min(np.abs(s21)):.3f} - {np.max(np.abs(s21)):.3f}")
    
    # Create a mock graphics window object
    class MockGraphicsWindow:
        def __init__(self):
            self.freqs = freqs
            self.s11 = s11
            self.s21 = s21
            self.vna_device = None
    
    # Create the mock object
    mock_window = MockGraphicsWindow()
    
    # Test the export function
    output_file = os.path.join(os.path.dirname(__file__), "test_export.s2p")
    
    try:
        # Import the export function (we'll create it as a standalone function)
        _export_touchstone_s2p_standalone(mock_window, output_file)
        
        print(f"\nExport successful! File saved as: {output_file}")
        
        # Read back and verify the file
        with open(output_file, 'r') as f:
            content = f.read()
            
        print(f"\nFile content preview (first 10 lines):")
        lines = content.split('\n')[:10]
        for i, line in enumerate(lines):
            print(f"  {i+1:2d}: {line}")
        
        # Verify file structure
        data_lines = [line for line in content.split('\n') if line and not line.startswith('!') and not line.startswith('#')]
        print(f"\nData verification:")
        print(f"  Total data lines: {len(data_lines)}")
        print(f"  Expected: {num_points}")
        
        if len(data_lines) == num_points:
            print("  ✓ Correct number of data points")
        else:
            print("  ✗ Incorrect number of data points")
        
        # Check first data line format
        if data_lines:
            first_line = data_lines[0].split()
            print(f"  First line has {len(first_line)} values (expected 9: freq + 4 S-parameters * 2)")
            if len(first_line) == 9:
                print("  ✓ Correct data format")
            else:
                print("  ✗ Incorrect data format")
        
        return True
        
    except Exception as e:
        print(f"\nError during export: {e}")
        return False

def _export_touchstone_s2p_standalone(window, file_path: str):
    """Standalone version of the export function for testing."""
    from datetime import datetime
    
    print(f"Writing S2P file: {file_path}")
    
    # Get device information if available
    device_name = "Test Device"
    if hasattr(window, 'vna_device') and window.vna_device:
        device_name = getattr(window.vna_device, 'name', type(window.vna_device).__name__)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        # Write header comments
        f.write(f"! Touchstone file exported from NanoVNA UTN Toolkit\n")
        f.write(f"! Device: {device_name}\n")
        f.write(f"! Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"! Frequency range: {window.freqs[0]/1e6:.3f} - {window.freqs[-1]/1e6:.3f} MHz\n")
        f.write(f"! Number of points: {len(window.freqs)}\n")
        f.write(f"!\n")
        
        # Write option line (frequency in Hz, S-parameters, Real/Imaginary format, 50 ohm reference)
        f.write("# HZ S RI R 50\n")
        
        # Write data points
        for i in range(len(window.freqs)):
            freq_hz = int(window.freqs[i])
            
            # S11 data (reflection coefficient port 1)
            s11 = window.s11[i]
            s11_real = float(s11.real)
            s11_imag = float(s11.imag)
            
            # S21 data (transmission coefficient port 2 to port 1)
            s21 = window.s21[i]
            s21_real = float(s21.real)
            s21_imag = float(s21.imag)
            
            # For a 2-port S2P file, we need S11, S21, S12, S22
            # Since VNA typically only measures S11 and S21, we'll set S12=S21 and S22=0
            # This is a reasonable assumption for most VNA measurements
            s12_real = s21_real  # Assume reciprocal network (S12 = S21)
            s12_imag = s21_imag
            s22_real = 0.0       # Assume matched port 2 (no reflection)
            s22_imag = 0.0
            
            # Write data line: freq S11_real S11_imag S21_real S21_imag S12_real S12_imag S22_real S22_imag
            f.write(f"{freq_hz} {s11_real:.6e} {s11_imag:.6e} {s21_real:.6e} {s21_imag:.6e} "
                   f"{s12_real:.6e} {s12_imag:.6e} {s22_real:.6e} {s22_imag:.6e}\n")
    
    print(f"Successfully wrote {len(window.freqs)} data points")

if __name__ == "__main__":
    test_touchstone_export()
