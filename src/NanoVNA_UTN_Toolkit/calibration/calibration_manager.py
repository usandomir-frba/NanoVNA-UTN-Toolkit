"""
Enhanced calibration manager module for NanoVNA-UTN-Toolkit.
Handles OSM calibrations with persistent state and Touchstone export.
"""
import numpy as np
import logging
import os
import pickle
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import skrf as rf


class OSMCalibrationManager:
    """
    Enhanced OSM calibration manager with persistent state and Touchstone export.
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            # Default to calibration directory in project
            base_path = os.path.join(os.path.dirname(__file__))
        
        self.base_path = base_path
        self.osm_results_path = os.path.join(base_path, "osm_results")
        self.config_path = os.path.join(base_path, "config")
        
        # Ensure directories exist
        os.makedirs(self.osm_results_path, exist_ok=True)
        os.makedirs(self.config_path, exist_ok=True)
        
        # Calibration data storage
        self.measurements = {
            'open': {'freqs': None, 's11': None, 'measured': False},
            'short': {'freqs': None, 's11': None, 'measured': False},
            'match': {'freqs': None, 's11': None, 'measured': False}
        }
        
        self.device_name = None
        self.calibration_date = None
        self.is_complete = False
        
        logging.info(f"[OSMCalibrationManager] Initialized with base path: {base_path}")
        
    def set_measurement(self, standard_name: str, freqs: np.ndarray, s11: np.ndarray) -> bool:
        """Store measurement for given standard and save as Touchstone file."""
        try:
            standard_name = standard_name.lower()
            if standard_name not in self.measurements:
                logging.error(f"[OSMCalibrationManager] Unknown standard: {standard_name}")
                return False
            
            # Store in memory
            self.measurements[standard_name]['freqs'] = np.array(freqs)
            self.measurements[standard_name]['s11'] = np.array(s11)
            self.measurements[standard_name]['measured'] = True
            
            # Save as Touchstone file
            touchstone_path = os.path.join(self.osm_results_path, f"{standard_name}.s1p")
            self._save_as_touchstone(freqs, s11, touchstone_path)
            
            # Check if calibration is complete
            self._check_completion()
            
            logging.info(f"[OSMCalibrationManager] {standard_name.upper()} measurement saved")
            logging.info(f"[OSMCalibrationManager] Touchstone saved: {touchstone_path}")
            
            return True
            
        except Exception as e:
            logging.error(f"[OSMCalibrationManager] Error saving {standard_name}: {e}")
            return False
    
    def _save_as_touchstone(self, freqs: np.ndarray, s11: np.ndarray, filepath: str):
        """Save measurement as Touchstone .s1p file."""
        try:
            # Create scikit-rf Network
            s_data = s11.reshape(-1, 1, 1)  # Reshape for 1-port
            network = rf.Network(frequency=freqs, s=s_data, z0=50)
            
            # Write Touchstone file
            network.write_touchstone(filepath)
            
            logging.info(f"[OSMCalibrationManager] Touchstone file saved: {filepath}")
            
        except Exception as e:
            logging.error(f"[OSMCalibrationManager] Error saving Touchstone file: {e}")
    
    def get_measurement(self, standard_name: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """Get measurement data for given standard."""
        standard_name = standard_name.lower()
        if standard_name not in self.measurements:
            return None
        
        data = self.measurements[standard_name]
        if not data['measured']:
            return None
            
        return data['freqs'], data['s11']
    
    def is_standard_measured(self, standard_name: str) -> bool:
        """Check if a standard has been measured."""
        standard_name = standard_name.lower()
        return self.measurements.get(standard_name, {}).get('measured', False)
    
    def _check_completion(self):
        """Check if all standards have been measured."""
        all_measured = all(
            data['measured'] for data in self.measurements.values()
        )
        
        if all_measured and not self.is_complete:
            self.is_complete = True
            self.calibration_date = datetime.now()
            logging.info("[OSMCalibrationManager] OSM calibration is now COMPLETE")
    
    def get_completion_status(self) -> Dict[str, bool]:
        """Return completion status for all standards."""
        return {
            'open': self.measurements['open']['measured'],
            'short': self.measurements['short']['measured'],
            'match': self.measurements['match']['measured'],
            'complete': self.is_complete
        }
    
    def save_calibration_file(self, filename: str) -> bool:
        """Save complete calibration as .cal file compatible with NanoVNA-Saver format."""
        try:
            if not self.is_complete:
                logging.warning("[OSMCalibrationManager] Cannot save incomplete calibration")
                return False
            
            # Prepare path
            if not filename.endswith('.cal'):
                filename += '.cal'
            cal_path = os.path.join(self.config_path, filename)
            
            # Get frequency data (should be same for all standards)
            freqs = self.measurements['open']['freqs']
            
            # Get S11 data for each standard
            open_s11 = self.measurements['open']['s11']
            short_s11 = self.measurements['short']['s11']
            match_s11 = self.measurements['match']['s11']
            
            # Write .cal file in NanoVNA-Saver format
            with open(cal_path, 'w') as f:
                f.write("# Calibration data for NanoVNA-UTN-Toolkit\n")
                f.write("# Generated on: {}\n".format(self.calibration_date.strftime("%Y-%m-%d %H:%M:%S")))
                if self.device_name:
                    f.write(f"# Device: {self.device_name}\n")
                f.write("\n")
                f.write("# Hz ShortR ShortI OpenR OpenI LoadR LoadI\n")
                
                for i in range(len(freqs)):
                    freq = freqs[i]
                    short_r, short_i = short_s11[i].real, short_s11[i].imag
                    open_r, open_i = open_s11[i].real, open_s11[i].imag
                    load_r, load_i = match_s11[i].real, match_s11[i].imag
                    
                    f.write(f"{freq} {short_r} {short_i} {open_r} {open_i} {load_r} {load_i}\n")
            
            logging.info(f"[OSMCalibrationManager] Calibration file saved: {cal_path}")
            return True
            
        except Exception as e:
            logging.error(f"[OSMCalibrationManager] Error saving calibration file: {e}")
            return False
    
    def load_calibration_file(self, filename: str) -> bool:
        """Load calibration from .cal file."""
        try:
            if not filename.endswith('.cal'):
                filename += '.cal'
            cal_path = os.path.join(self.config_path, filename)
            
            if not os.path.exists(cal_path):
                logging.warning(f"[OSMCalibrationManager] Calibration file not found: {cal_path}")
                return False
            
            freqs = []
            short_data = []
            open_data = []
            load_data = []
            
            with open(cal_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('#') or not line:
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 7:
                        freq = float(parts[0])
                        short_r, short_i = float(parts[1]), float(parts[2])
                        open_r, open_i = float(parts[3]), float(parts[4])
                        load_r, load_i = float(parts[5]), float(parts[6])
                        
                        freqs.append(freq)
                        short_data.append(complex(short_r, short_i))
                        open_data.append(complex(open_r, open_i))
                        load_data.append(complex(load_r, load_i))
            
            if freqs:
                # Store loaded data
                freqs = np.array(freqs)
                self.measurements['open']['freqs'] = freqs
                self.measurements['open']['s11'] = np.array(open_data)
                self.measurements['open']['measured'] = True
                
                self.measurements['short']['freqs'] = freqs
                self.measurements['short']['s11'] = np.array(short_data)
                self.measurements['short']['measured'] = True
                
                self.measurements['match']['freqs'] = freqs
                self.measurements['match']['s11'] = np.array(load_data)
                self.measurements['match']['measured'] = True
                
                self._check_completion()
                
                logging.info(f"[OSMCalibrationManager] Calibration loaded from: {cal_path}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"[OSMCalibrationManager] Error loading calibration file: {e}")
            return False
    
    def list_available_calibrations(self) -> List[str]:
        """List all available .cal files."""
        try:
            cal_files = []
            for file in os.listdir(self.config_path):
                if file.endswith('.cal'):
                    cal_files.append(file[:-4])  # Remove .cal extension
            return sorted(cal_files)
        except Exception as e:
            logging.error(f"[OSMCalibrationManager] Error listing calibrations: {e}")
            return []
    
    def clear_all_measurements(self):
        """Clear all measurement data."""
        for standard in self.measurements:
            self.measurements[standard] = {'freqs': None, 's11': None, 'measured': False}
        
        self.is_complete = False
        self.calibration_date = None
        logging.info("[OSMCalibrationManager] All measurements cleared")
    
    def apply_calibration(self, freqs: np.ndarray, s11_raw: np.ndarray) -> np.ndarray:
        """
        Apply OSM calibration to raw S11 measurements.
        
        For now this is a placeholder - real OSM correction would use
        error correction formulas involving all three standards.
        """
        if not self.is_complete:
            logging.warning("[OSMCalibrationManager] Cannot apply incomplete calibration")
            return s11_raw
        
        logging.info(f"[OSMCalibrationManager] Applying OSM calibration to {len(s11_raw)} points")
        
        # TODO: Implement actual OSM error correction mathematics
        # This would involve calculating error terms and applying correction
        
        return s11_raw


def get_current_calibration_info(config_path: str = None) -> Optional[Dict[str, str]]:
    """Get information about currently selected calibration."""
    try:
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config")
        
        # Check for active calibration info
        from PySide6.QtCore import QSettings
        config_file = os.path.join(config_path, "calibration_config.ini")
        
        if os.path.exists(config_file):
            settings = QSettings(config_file, QSettings.Format.IniFormat)
            
            method = settings.value("Calibration/Method", "---")
            name = settings.value("Calibration/Name", None)
            
            if method and method != "---":
                return {
                    'method': method,
                    'name': name or "Unnamed",
                    'type': 'OSM' if 'OSM' in method else 'Other'
                }
        
        return None
        
    except Exception as e:
        logging.error(f"[get_current_calibration_info] Error: {e}")
        return None
