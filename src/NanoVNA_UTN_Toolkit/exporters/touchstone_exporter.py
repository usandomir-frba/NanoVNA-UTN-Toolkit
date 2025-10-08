"""
Touchstone Exporter for NanoVNA measurement data.

This module provides functionality to export S-parameter data to Touchstone format (.s2p files).
"""

import os
import logging
from datetime import datetime
from PySide6.QtWidgets import QMessageBox, QFileDialog


class TouchstoneExporter:
    """
    Exports NanoVNA measurement data to Touchstone format (.s2p files).
    
    Supports exporting S11 and S21 parameter data in standard Touchstone format
    for use with other RF analysis tools.
    """
    
    def __init__(self, parent_widget=None):
        """
        Initialize the Touchstone exporter.
        
        Args:
            parent_widget: Parent widget for dialog boxes (optional)
        """
        self.parent_widget = parent_widget
        self.logger = logging.getLogger(__name__)
    
    def export_to_s2p(self, freqs, s11_data, s21_data, device_name=None):
        """
        Export S-parameter data to Touchstone S2P format.
        
        Args:
            freqs: Frequency array in Hz
            s11_data: S11 parameter data (complex array)
            s21_data: S21 parameter data (complex array)
            device_name: Optional device name for the file header
            
        Returns:
            bool: True if export successful, False otherwise
        """
        self.logger.info("Starting Touchstone export")
        
        # Validate input data
        if not self._validate_data(freqs, s11_data, s21_data):
            return False
        
        # Get save file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent_widget,
            "Export Touchstone Data",
            "",
            "Touchstone S2P Files (*.s2p);;All Files (*)"
        )
        
        if not file_path:
            self.logger.info("Export cancelled by user")
            return False
        
        # Ensure file has .s2p extension
        if not file_path.lower().endswith('.s2p'):
            file_path += '.s2p'
        
        try:
            # Export the data
            self._write_s2p_file(file_path, freqs, s11_data, s21_data, device_name or "Unknown")
            
            # Success message
            self._show_success_message(file_path, freqs)
            self.logger.info(f"Successfully exported {len(freqs)} points to {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error exporting Touchstone data:\\n{str(e)}"
            self._show_error("Export Error", error_msg)
            self.logger.error(f"Export error: {e}")
            self.logger.error(f"Exception details: {type(e).__name__}")
            return False
    
    def _validate_data(self, freqs, s11_data, s21_data):
        """
        Validate input data for export.
        
        Args:
            freqs: Frequency array
            s11_data: S11 data array
            s21_data: S21 data array
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        # Check if we have sweep data available
        if freqs is None:
            self._show_warning("No Data", "No sweep data available for export.\\nPlease run a sweep first.")
            self.logger.warning("No frequency data available")
            return False
        
        if s11_data is None:
            self._show_warning("No Data", "No S11 data available for export.\\nPlease run a sweep first.")
            self.logger.warning("No S11 data available")
            return False
            
        if s21_data is None:
            self._show_warning("No Data", "No S21 data available for export.\\nPlease run a sweep first.")
            self.logger.warning("No S21 data available")
            return False
        
        # Check data consistency
        if len(freqs) != len(s11_data) or len(freqs) != len(s21_data):
            error_msg = f"Data length mismatch detected.\\nFreqs: {len(freqs)}, S11: {len(s11_data)}, S21: {len(s21_data)}"
            self._show_error("Data Error", error_msg)
            self.logger.error(error_msg)
            return False
        
        return True
    
    def _write_s2p_file(self, file_path, freqs, s11_data, s21_data, device_name):
        """
        Write data to Touchstone S2P format file.
        
        Args:
            file_path: Path where to save the S2P file
            freqs: Frequency array in Hz
            s11_data: S11 parameter data
            s21_data: S21 parameter data
            device_name: Name of the measurement device
        """
        self.logger.info(f"Writing S2P file: {file_path}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Write header comments
            f.write(f"! Touchstone file exported from NanoVNA UTN Toolkit\\n")
            f.write(f"! Device: {device_name}\\n")
            f.write(f"! Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
            f.write(f"! Frequency range: {freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz\\n")
            f.write(f"! Number of points: {len(freqs)}\\n")
            f.write(f"!\\n")
            
            # Write option line (frequency in Hz, S-parameters, Real/Imaginary format, 50 ohm reference)
            f.write("# HZ S RI R 50\\n")
            
            # Write data points
            for i in range(len(freqs)):
                freq_hz = int(freqs[i])
                
                # S11 data (reflection coefficient port 1)
                s11 = s11_data[i]
                s11_real = float(s11.real)
                s11_imag = float(s11.imag)
                
                # S21 data (transmission coefficient port 2 to port 1)
                s21 = s21_data[i]
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
                       f"{s12_real:.6e} {s12_imag:.6e} {s22_real:.6e} {s22_imag:.6e}\\n")
        
        self.logger.info(f"Successfully wrote {len(freqs)} data points")
    
    def _show_success_message(self, file_path, freqs):
        """Show success message to user."""
        num_points = len(freqs)
        freq_range = f"{freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz"
        success_msg = (f"Touchstone data exported successfully!\\n\\n"
                      f"File: {file_path}\\n"
                      f"Points: {num_points}\\n"
                      f"Frequency range: {freq_range}")
        self._show_info("Export Successful", success_msg)
    
    def _show_warning(self, title, message):
        """Show warning message box."""
        if self.parent_widget:
            QMessageBox.warning(self.parent_widget, title, message)
    
    def _show_info(self, title, message):
        """Show information message box."""
        if self.parent_widget:
            QMessageBox.information(self.parent_widget, title, message)
    
    def _show_error(self, title, message):
        """Show error message box."""
        if self.parent_widget:
            QMessageBox.critical(self.parent_widget, title, message)