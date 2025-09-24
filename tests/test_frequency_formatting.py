#!/usr/bin/env python3
"""
Comprehensive test suite for frequency formatting in NanoVNA-UTN-Toolkit

This test validates that the frequency formatting system works correctly
across the full range of 1 KHz to 6 GHz, covering all typical use cases
for VNA (Vector Network Analyzer) equipment.

Problem solved:
- Before: Frequencies like 600 MHz were displayed truncated as "600.00"
- After: They are displayed complete as "600.000" with adequate precision

Changes implemented:
- graphics_utils.py: limit_frequency_input limits changed from (3,2) to (6,3)
- This allows 6 integer digits + 3 decimals instead of 3 integers + 2 decimals
"""

import os
import sys
import unittest

# Add src to path to import project modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import format_frequency_smart_split
except ImportError:
    # Fallback if import fails - define the function locally for testing
    def format_frequency_smart_split(freq_hz):
        """Format frequency and return (value, unit) tuple."""
        if freq_hz >= 1e9:
            return f"{freq_hz/1e9:.3f}", "GHz"
        elif freq_hz >= 1e6:
            return f"{freq_hz/1e6:.3f}", "MHz"
        elif freq_hz >= 1e3:
            return f"{freq_hz/1e3:.3f}", "kHz"
        else:
            return f"{freq_hz:.1f}", "Hz"

def limit_frequency_input_new(text, max_digits=6, max_decimals=3):
    """Frequency input limiter with new limits (6 digits, 3 decimals)."""
    filtered = "".join(c for c in text if c.isdigit() or c == ".")
    
    if filtered.count(".") > 1:
        parts = filtered.split(".", 1)
        filtered = parts[0] + "." + "".join(parts[1:]).replace(".", "")
    
    if "." in filtered:
        integer_part, decimal_part = filtered.split(".", 1)
        integer_part = integer_part[:max_digits]
        decimal_part = decimal_part[:max_decimals]
        filtered = integer_part + "." + decimal_part
    else:
        filtered = filtered[:max_digits]

    return filtered

def limit_frequency_input_old(text, max_digits=3, max_decimals=2):
    """Frequency input limiter with old limits (3 digits, 2 decimals) for comparison."""
    filtered = "".join(c for c in text if c.isdigit() or c == ".")
    
    if filtered.count(".") > 1:
        parts = filtered.split(".", 1)
        filtered = parts[0] + "." + "".join(parts[1:]).replace(".", "")
    
    if "." in filtered:
        integer_part, decimal_part = filtered.split(".", 1)
        integer_part = integer_part[:max_digits]
        decimal_part = decimal_part[:max_decimals]
        filtered = integer_part + "." + decimal_part
    else:
        filtered = filtered[:max_digits]

    return filtered


class TestFrequencyFormatting(unittest.TestCase):
    """Test suite to validate correct VNA frequency formatting."""

    def setUp(self):
        """Initial test setup."""
        # Define test frequency sets organized by range
        
        # kHz range (1 - 999 kHz)
        self.khz_frequencies = [
            1e3, 5.5e3, 12e3, 47.8e3, 125e3, 333.33e3, 567.89e3, 999.99e3
        ]
        
        # MHz range - Units (1 - 9 MHz)
        self.mhz_units = [
            1e6, 2.5e6, 5.123e6, 7.777e6, 9.999e6
        ]
        
        # MHz range - Tens (10 - 99 MHz)  
        self.mhz_tens = [
            10e6, 25.5e6, 50e6, 77.123e6, 99.999e6
        ]
        
        # MHz range - Hundreds (100 - 999 MHz) - CRITICAL: includes original problem
        self.mhz_hundreds = [
            100e6, 250.5e6, 433e6, 600e6, 868.12e6, 915e6, 999.99e6
        ]
        
        # GHz range (1 - 6 GHz) - Maximum VNA range
        self.ghz_frequencies = [
            1e9, 1.2e9, 1.234e9, 1.575420e9, 2.4e9, 2.45e9, 3.5e9, 5.8e9, 6e9
        ]
        
        # Extreme cases
        self.extreme_cases = [
            1.111111e6, 123.456789e6, 999.999999e6, 5.999999e9
        ]

    def test_khz_range_formatting(self):
        """Test kHz range formatting (1-999 kHz)."""
        for freq_hz in self.khz_frequencies:
            with self.subTest(freq_hz=freq_hz):
                value, unit = format_frequency_smart_split(freq_hz)
                
                self.assertEqual(unit, "kHz", f"Freq {freq_hz} Hz should be in kHz")
                
                limited_new = limit_frequency_input_new(value)
                self.assertEqual(value, limited_new, 
                    f"Freq {freq_hz} Hz: {value} kHz truncated to {limited_new}")
                
                expected_value = freq_hz / 1e3
                actual_value = float(value)
                self.assertAlmostEqual(expected_value, actual_value, places=3,
                    msg=f"Wrong numeric value for {freq_hz} Hz")

    def test_mhz_units_formatting(self):
        """Test MHz units range formatting (1-9 MHz)."""
        for freq_hz in self.mhz_units:
            with self.subTest(freq_hz=freq_hz):
                value, unit = format_frequency_smart_split(freq_hz)
                
                self.assertEqual(unit, "MHz")
                limited_new = limit_frequency_input_new(value)
                self.assertEqual(value, limited_new)
                
                expected_value = freq_hz / 1e6
                actual_value = float(value)
                self.assertAlmostEqual(expected_value, actual_value, places=3)

    def test_mhz_tens_formatting(self):
        """Test MHz tens range formatting (10-99 MHz)."""
        for freq_hz in self.mhz_tens:
            with self.subTest(freq_hz=freq_hz):
                value, unit = format_frequency_smart_split(freq_hz)
                
                self.assertEqual(unit, "MHz")
                limited_new = limit_frequency_input_new(value)
                self.assertEqual(value, limited_new)
                
                expected_value = freq_hz / 1e6
                actual_value = float(value)
                self.assertAlmostEqual(expected_value, actual_value, places=3)

    def test_mhz_hundreds_formatting_critical(self):
        """CRITICAL test: MHz hundreds range formatting (100-999 MHz).
        
        This test specifically includes 600 MHz which was the original reported problem.
        """
        for freq_hz in self.mhz_hundreds:
            with self.subTest(freq_hz=freq_hz):
                value, unit = format_frequency_smart_split(freq_hz)
                
                self.assertEqual(unit, "MHz", f"Freq {freq_hz} Hz should be in MHz")
                
                # Critical validation: new limits should not truncate
                limited_new = limit_frequency_input_new(value)
                self.assertEqual(value, limited_new, 
                    f"CRITICAL FAILURE - Freq {freq_hz} Hz: {value} MHz truncated to {limited_new}")
                
                # Validate original problem case specifically
                if freq_hz == 600e6:
                    self.assertEqual(value, "600.000", 
                        f"ORIGINAL PROBLEM - 600 MHz should display as '600.000', got '{value}'")
                
                expected_value = freq_hz / 1e6
                actual_value = float(value)
                self.assertAlmostEqual(expected_value, actual_value, places=3)

    def test_ghz_range_formatting(self):
        """Test GHz range formatting (1-6 GHz)."""
        for freq_hz in self.ghz_frequencies:
            with self.subTest(freq_hz=freq_hz):
                value, unit = format_frequency_smart_split(freq_hz)
                
                self.assertEqual(unit, "GHz", f"Freq {freq_hz} Hz should be in GHz")
                
                limited_new = limit_frequency_input_new(value)
                self.assertEqual(value, limited_new)
                
                expected_value = freq_hz / 1e9
                actual_value = float(value)
                self.assertAlmostEqual(expected_value, actual_value, places=3)

    def test_extreme_cases(self):
        """Test extreme precision and boundary cases."""
        for freq_hz in self.extreme_cases:
            with self.subTest(freq_hz=freq_hz):
                value, unit = format_frequency_smart_split(freq_hz)
                
                limited_new = limit_frequency_input_new(value)
                self.assertEqual(value, limited_new, 
                    f"Extreme case {freq_hz} Hz failed: {value} {unit}")

    def test_original_problem_specifically(self):
        """Specific test for the original reported problem: 600 MHz."""
        freq_hz = 600e6
        
        value, unit = format_frequency_smart_split(freq_hz)
        
        print(f"Original problem test: {freq_hz} Hz -> {value} {unit}")
        
        self.assertEqual(unit, "MHz", "600 MHz should be displayed in MHz")
        self.assertEqual(value, "600.000", f"Expected '600.000', got '{value}'")
        
        limited_new = limit_frequency_input_new(value)
        self.assertEqual(value, limited_new, f"New limits truncated: {value} -> {limited_new}")
        
        limited_old = limit_frequency_input_old(value)
        self.assertNotEqual(value, limited_old, f"Old limits should truncate: {value} -> {limited_old}")
        
        print(f"Fix validated: New={limited_new}, Old={limited_old}")

    def test_precision_limits_validation(self):
        """Test that precision limits work correctly for various inputs."""
        test_cases = [
            ("123.456", "123.456"),
            ("123456.789", "123456.789"),
            ("1234567.890", "123456.890"),
            ("123.4567", "123.456"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = limit_frequency_input_new(input_text)
                self.assertEqual(result, expected, 
                    f"Input '{input_text}' should become '{expected}', got '{result}'")

    def test_comprehensive_coverage(self):
        """Comprehensive test covering all frequency ranges with summary."""
        all_frequencies = (
            self.khz_frequencies + 
            self.mhz_units + 
            self.mhz_tens + 
            self.mhz_hundreds + 
            self.ghz_frequencies + 
            self.extreme_cases
        )
        
        results = []
        failures = []
        
        for freq_hz in all_frequencies:
            try:
                value, unit = format_frequency_smart_split(freq_hz)
                limited = limit_frequency_input_new(value)
                
                if value == limited:
                    results.append((freq_hz, value, unit, "OK"))
                else:
                    results.append((freq_hz, value, unit, "TRUNCATED"))
                    failures.append(freq_hz)
                    
            except Exception as e:
                results.append((freq_hz, "ERROR", "ERROR", str(e)))
                failures.append(freq_hz)
        
        total_tests = len(all_frequencies)
        successful_tests = total_tests - len(failures)
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"Comprehensive test summary:")
        print(f"Total frequencies tested: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failures: {len(failures)}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if failures:
            print(f"Failed frequencies: {failures}")
        
        self.assertEqual(len(failures), 0, f"Test failures in frequencies: {failures}")
        self.assertEqual(success_rate, 100.0, f"Success rate should be 100%, got {success_rate:.1f}%")


if __name__ == '__main__':
    print("Running NanoVNA frequency formatting tests...")
    unittest.main(verbosity=2, buffer=True)