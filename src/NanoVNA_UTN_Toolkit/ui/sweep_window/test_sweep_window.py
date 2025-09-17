"""
Test script for the SweepOptionsWindow.
Run this script to test the sweep options window independently.
"""
import sys
import os

# Add the src path to sys.path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from PySide6.QtWidgets import QApplication
from NanoVNA_UTN_Toolkit.ui.sweep_window import SweepOptionsWindow


def main():
    """Main function to test the SweepOptionsWindow."""
    app = QApplication(sys.argv)
    
    # Create and show the window
    window = SweepOptionsWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
