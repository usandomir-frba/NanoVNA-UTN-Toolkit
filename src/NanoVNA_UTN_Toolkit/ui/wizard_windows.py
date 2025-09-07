"""
Calibration Wizard status window for NanoVNA devices.
"""

import os
import sys

from PySide6.QtCore import QTimer, QThread, Qt
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton,
    QHBoxLayout, QProgressBar, QFrame, QGridLayout, QGroupBox, QComboBox,
    QGraphicsScene, QGraphicsView, QSizePolicy, QSlider, QLabel
)
from PySide6.QtGui import QIcon, QTextCursor, QFont, QPen

from ..workers.device_worker import DeviceWorker
from .log_handler import GuiLogHandler

try:
    from NanoVNA_UTN_Toolkit.ui.graphics_window import NanoVNAGraphics
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class CalibrationWizard(QMainWindow):
    def __init__(self):
        super().__init__()

        # === Icon ===

        icon_paths = [
            os.path.join(os.path.dirname(__file__), 'icon.ico'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'icon.ico'),
            'icon.ico'
        ]

        for icon_path in icon_paths:
            icon_path = os.path.abspath(icon_path)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                break
        else:
            logger = logging.getLogger(__name__)
            logger.warning("icon.ico not found in expected locations")
        # === Title ===

        self.setWindowTitle("Calibration Wizard")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        next_button = QPushButton("Next")
        next_button.setStyleSheet("padding: 12px; font-size: 14px;")
        main_layout.addWidget(next_button)
        self.setLayout(main_layout) 
        next_button.clicked.connect(self.next_step)

    def next_step(self):
        # Implement the logic for the next step in the calibration wizard
        self.graphics_windows = NanoVNAGraphics()
        self.graphics_windows.show()
        self.close() 
