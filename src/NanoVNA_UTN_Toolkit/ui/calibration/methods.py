import os
import logging
import skrf as rf
import numpy as np

class Methods:
    """
    Class to handle VNA calibration using OSM 3-term method.
    """
    def __init__(self, calibration_dir):
        """
        Initialize the calibrator with the folder where the S1P error files are saved.

        Parameters
        ----------
        calibration_dir : str
            Path to the folder containing S1P error files.
        """
        self.calibration_dir = calibration_dir
        logging.info(f"[Calibrator] Initialized with calibration directory: {calibration_dir}")

    def osm_calibrate_s11(self, s11_med):
        """
        Calibrate measured S11 using OSM error terms.

        Parameters
        ----------
        s11_med : np.array
            Measured S11 from the VNA.

        Returns
        -------
        s11_cal : np.array
            Calibrated S11 array.
        """
        logging.info("[Calibrator] Loading error terms from S1P files...")

        # Construct full paths to error S1P files
        error1_file = os.path.join(self.calibration_dir, "directivity.s1p")  # Directivity
        error2_file = os.path.join(self.calibration_dir, "reflection_tracking.s1p")  # Reflection tracking
        error3_file = os.path.join(self.calibration_dir, "source_match.s1p")  # Source match (ignored for 2-term)

        # Read S1P files using skrf
        e00 = rf.Network(error1_file).s[:,0,0]  # Directivity
        e11 = rf.Network(error2_file).s[:,0,0]  # Reflection tracking
        e10e01 = rf.Network(error3_file).s[:,0,0]  # Source match

        # Compute delta_e (for 2-term calibration, source match is ignored)
        delta_e = e11 * e00 - e10e01

        logging.info("[Calibrator] Calculating calibrated S11 using OSM formula...")
        s11_cal = (s11_med - e00) / (s11_med * e11 - delta_e)
        return s11_cal
