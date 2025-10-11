import os
import logging
import numpy as np
import skrf as rf

class CalibrationErrors:
    """General calibration error handler supporting different calibration methods."""

    def __init__(self, calibration_dir):
        """
        Initialize the error calculator with the folder containing calibration S1P files.

        Parameters
        ----------
        calibration_dir : str
            Path to the folder containing the OSM calibration S1P files (open, short, match).
        """
        self.calibration_dir = calibration_dir
        logging.info(f"[CalibrationErrors] Initialized with calibration directory: {calibration_dir}")

        # Common error attributes
        self.error1 = None  # Directivity
        self.error2 = None  # Reflection tracking
        self.error3 = None  # Source match

    # ======================================================================
    #  OSM Calibration Method
    # ======================================================================
    def calculate_osm_errors(self):
        """Compute and save OSM (Open-Short-Match) calibration errors."""
        logging.info("[CalibrationErrors] Reading OSM calibration files")

        # Load OSM calibration files
        open_s, short_s, match_s = self._load_osm_files()

        # Extract frequency and S11 parameters
        freq = open_s.f
        s_open = open_s.s[:, 0, 0]
        s_short = short_s.s[:, 0, 0]
        s_match = match_s.s[:, 0, 0]

        n_points = len(freq)
        e00 = np.zeros(n_points, dtype=complex)  # Directivity
        e11 = np.zeros(n_points, dtype=complex)  # Reflection tracking
        e10e01 = np.zeros(n_points, dtype=complex)  # Source match

        # Compute 3-term OSM error model
        for i in range(n_points):
            e00[i] = s_match[i]
            e11[i] = (s_open[i] + s_short[i] - 2 * e00[i]) / (s_open[i] - s_short[i])
            e10e01[i] = -2 * (s_open[i] - e00[i]) * (s_short[i] - e00[i]) / (s_open[i] - s_short[i])

        # Save results as Touchstone S1P files
        self._save_error_file(freq, e00, "directivity.s1p", "Directivity")
        self._save_error_file(freq, e11, "reflection_tracking.s1p", "Reflection tracking")
        self._save_error_file(freq, e10e01, "source_match.s1p", "Source match")

        # Store results for later access
        self.error1 = e00
        self.error2 = e11
        self.error3 = e10e01

        logging.info("[CalibrationErrors] OSM error calculation completed successfully")

    def calculate_normalization_errors(self):
        """
        Compute and save normalization (THRU) calibration errors.

        This method processes the THRU calibration data, where the measured S21 
        represents the transmission tracking error (e10 * e32) used for 
        normalizing transmission measurements.
        """
        logging.info("[CalibrationErrors] Reading THRU calibration file")

        # File path for THRU measurement
        thru_file = os.path.join(self.calibration_dir, "thru.s1p")

        # Load THRU Touchstone file
        thru_network = rf.Network(thru_file)

        # Extract frequency and measured S21
        freq = thru_network.f
        s21_measured = thru_network.s[:, 0, 0]  # S21 term from the THRU measurement

        n_points = len(freq)

        # Define error terms
        e10e32 = np.zeros(n_points, dtype=complex)  # Transmission tracking error
        e00 = np.zeros(n_points, dtype=complex)     # Placeholder (unused)
        e11 = np.zeros(n_points, dtype=complex)     # Placeholder (unused)

        # For normalization, assume e10e32 = measured S21
        e10e32 = s21_measured

        # Save the normalization result as an S1P Touchstone file
        self._save_error_file(freq, e10e32, "transmission_tracking.s1p", "Transmission tracking")

        # Store result for later access
        self.error1 = None
        self.error2 = None
        self.error3 = e10e32

        logging.info("[CalibrationErrors] THRU (normalization) error calculation completed successfully")


    # ======================================================================
    #  Utility Methods
    # ======================================================================
    def _load_osm_files(self):
        """Load the Open, Short, and Match S1P files used for OSM calibration."""
        logging.info("[CalibrationErrors] Loading OSM calibration files...")

        open_file = os.path.join(self.calibration_dir, "open.s1p")
        short_file = os.path.join(self.calibration_dir, "short.s1p")
        match_file = os.path.join(self.calibration_dir, "match.s1p")

        # Validate existence
        for f in [open_file, short_file, match_file]:
            if not os.path.exists(f):
                raise FileNotFoundError(f"[CalibrationErrors] Missing calibration file: {f}")

        # Load files using scikit-rf
        open_s = rf.Network(open_file)
        short_s = rf.Network(short_file)
        match_s = rf.Network(match_file)

        logging.info("[CalibrationErrors] Successfully loaded OSM files")

        return open_s, short_s, match_s

    def _save_error_file(self, freq, s_data, filename, label):
        """Helper to export a computed error as an S1P Touchstone file."""
        network = rf.Network()
        network.frequency = rf.Frequency.from_f(freq, unit="Hz")
        network.s = s_data.reshape((len(freq), 1, 1))

        filepath = os.path.join(self.calibration_dir, filename)
        network.write_touchstone(filepath)
        logging.info(f"[CalibrationErrors] {label} error saved: {filepath}")
