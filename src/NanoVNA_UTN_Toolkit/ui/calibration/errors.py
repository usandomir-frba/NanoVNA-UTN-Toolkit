import os
import logging
import numpy as np
import skrf as rf

class CalibrationErrors:
    """General calibration error handler supporting different calibration methods."""

    def __init__(self, calibration_dir, error_subfolder="errors"):
        """
        Initialize the error calculator with the folder containing calibration S1P files.
        All error files will be saved in a subfolder (default: 'errors').
        """
        self.calibration_dir = calibration_dir
        self.error_dir = os.path.join(calibration_dir, error_subfolder)
        os.makedirs(self.error_dir, exist_ok=True)
        logging.info(f"[CalibrationErrors] Initialized with calibration directory: {calibration_dir}")
        logging.info(f"[CalibrationErrors] Error files will be saved in: {self.error_dir}")

        # Common error attributes
        self.directivity = None
        self.reflection_tracking = None
        self.source_match = None

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
        self._save_osm_error_file(freq, e00, "directivity.s1p", "Directivity")
        self._save_osm_error_file(freq, e11, "reflection_tracking.s1p", "Reflection tracking")
        self._save_osm_error_file(freq, e10e01, "source_match.s1p", "Source match")

        # Store results for later access
        self.directivity = e00
        self.reflection_tracking = e11
        self.source_match = e10e01

        logging.info("[CalibrationErrors] OSM error calculation completed successfully")

    def calculate_normalization_errors(self):
        """
        Compute and save normalization (THRU) calibration errors.

        This method processes the THRU calibration data, where the measured S21 
        represents the transmission tracking error (e10 * e32) used for 
        normalizing transmission measurements.
        """
        logging.info("[CalibrationErrors] Reading THRU calibration file")

        # Load THRU calibration files
        thru_s = self._load_thru_file()

         # Extract frequency and S21 parameters
        freq = thru_s.f
        s21_measured = thru_s.s[:, 1, 0]  # S21 term from the THRU measurement

        n_points = len(freq)

        # Define error terms
        e10e32 = np.zeros(n_points, dtype=complex)  # Transmission tracking error
        e00 = np.zeros(n_points, dtype=complex)     # Placeholder (unused)
        e11 = np.zeros(n_points, dtype=complex)     # Placeholder (unused)

        # For normalization, assume e10e32 = measured S21
        e10e32 = s21_measured

        # Save the normalization result as an S1P Touchstone file
        self._save_normalization_error_file(freq, e10e32, "transmission_tracking.s2p", "Transmission tracking")

        # Store result for later access
        self.directivity = None
        self.reflection_tracking = None
        self.transmission_tracking = e10e32

        logging.info("[CalibrationErrors] THRU (normalization) error calculation completed successfully")

    def calculate_1PortN_errors(self, osm_dir, thru_dir):
        """
        Calculate errors for the 1-Port+N calibration method.

        This method combines the OSM (Open-Short-Match) error terms for S11
        (directivity, reflection tracking, source match) with the normalization (THRU)
        error term for S21 (transmission tracking). The results are saved in the
        corresponding error subfolder.

        Parameters
        ----------
        osm_dir : str
            Path to the OSM calibration folder (should contain open.s1p, short.s1p, match.s1p)
        thru_dir : str
            Path to the THRU calibration folder (should contain thru.s2p)
        """
        logging.info("[CalibrationErrors] Calculating 1-Port+N errors (OSM + Normalization)")

        # Load OSM calibration files
        open_file = os.path.join(osm_dir, "open.s1p")
        short_file = os.path.join(osm_dir, "short.s1p")
        match_file = os.path.join(osm_dir, "match.s1p")

        # Validate existence
        for f in [open_file, short_file, match_file]:
            if not os.path.exists(f):
                raise FileNotFoundError(f"[CalibrationErrors] Missing calibration file: {f}")

        # Load files using scikit-rf
        open_s = rf.Network(open_file)
        short_s = rf.Network(short_file)
        match_s = rf.Network(match_file)

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

        # Load THRU calibration file
        logging.info("[CalibrationErrors] Loading THRU calibration file...")

        thru_file = os.path.join(thru_dir, "thru.s2p")

        if not os.path.exists(thru_file):
            raise FileNotFoundError(f"[CalibrationErrors] Missing THRU calibration file: {thru_file}")

        thru_s = rf.Network(thru_file)

        # Extract frequency and S21 parameters
        thru_freq = thru_s.f
        s21_measured = thru_s.s[:, 1, 0]
        e10e32 = s21_measured  # Transmission tracking error

        # --- Save errors in the current error_dir ---
        self._save_osm_error_file(freq, e00, "directivity.s1p", "Directivity (1-Port+N)")
        self._save_osm_error_file(freq, e11, "reflection_tracking.s1p", "Reflection Tracking (1-Port+N)")
        self._save_osm_error_file(freq, e10e01, "source_match.s1p", "Source Match (1-Port+N)")
        self._save_normalization_error_file(thru_freq, e10e32, "transmission_tracking.s2p", "Transmission Tracking (1-Port+N)")

        # Store results for later access
        self.directivity_1PortN = e00
        self.reflection_tracking_1PortN = e11
        self.source_match_1PortN = e10e01
        self.transmission_tracking_1PortN = e10e32

        logging.info("[CalibrationErrors] 1-Port+N error calculation completed successfully")

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

    def _load_thru_file(self):
        """Load the THRU S1P file used for normalization calibration."""
        logging.info("[CalibrationErrors] Loading THRU calibration file...")

        thru_file = os.path.join(self.calibration_dir, "thru.s2p")

        if not os.path.exists(thru_file):
            raise FileNotFoundError(f"[CalibrationErrors] Missing THRU calibration file: {thru_file}")

        thru_network = rf.Network(thru_file)

        logging.info("[CalibrationErrors] Successfully loaded THRU file")

        return thru_network

    def _save_osm_error_file(self, freq, s_data, filename, label):

        network = rf.Network()
        network.frequency = rf.Frequency.from_f(freq, unit="Hz")
        network.s = s_data.reshape((len(freq), 1, 1))
        filepath = os.path.join(self.error_dir, filename)
        network.write_touchstone(filepath)
        logging.info(f"[CalibrationErrors] {label} error saved: {filepath}")

    def _save_normalization_error_file(self, freq, s_data, filename, label):

        network = rf.Network()
        network.frequency = rf.Frequency.from_f(freq, unit="Hz")
        s_matrix = np.zeros((len(freq), 2, 2), dtype=complex)
        s_matrix[:, 1, 0] = s_data  # S21
        network.s = s_matrix
        filepath = os.path.join(self.error_dir, filename)
        network.write_touchstone(filepath)
        logging.info(f"[CalibrationErrors] {label} error saved: {filepath}")

