#!/usr/bin/env python3
"""
NanoVNA UTN Toolkit - Main application entry point
"""

import sys
import os
import logging
from PySide6.QtWidgets import QApplication

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the compatibility layer first
from NanoVNA_UTN_Toolkit.compat import apply_patches

# Apply compatibility patches
apply_patches()

try:
    # Import required modules
    from NanoVNA_UTN_Toolkit.utils import check_required_packages, cleanup_routine
    from NanoVNA_UTN_Toolkit.ui.connection_window import NanoVNAStatusApp
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable debug logging for specific modules
logging.getLogger('NanoVNA_UTN_Toolkit.compat').setLevel(logging.DEBUG)
logging.getLogger('NanoVNA_UTN_Toolkit.Hardware.VNA').setLevel(logging.DEBUG)
logging.getLogger('NanoVNA_UTN_Toolkit.Hardware.Hardware').setLevel(logging.INFO)  # Less verbose for Hardware


def run_app():
    """Run the graphical application."""
    try:
        app = QApplication(sys.argv)
        window = NanoVNAStatusApp()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Error running application: {e}")
        input("Press Enter to close the program...")
        sys.exit(1)


def main():
    """Main function."""
    check_required_packages()
    run_app()
    cleanup_routine()


if __name__ == "__main__":
    main()
