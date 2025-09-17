"""
Welcome setup window for NanoVNA devices.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf

# Suppress verbose matplotlib logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.getLogger('matplotlib.pyplot').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

from PySide6.QtCore import QTimer, QThread, Qt
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton,
    QHBoxLayout, QProgressBar, QFrame, QGridLayout, QGroupBox, QComboBox,
    QGraphicsScene, QGraphicsView, QSizePolicy, QSlider, QLabel, QRadioButton
)
from PySide6.QtGui import QIcon, QTextCursor, QFont, QPen

from ..workers.device_worker import DeviceWorker
from .log_handler import GuiLogHandler

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

try:
    from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class NanoVNAWelcome(QMainWindow):
    def __init__(self, s11=None, freqs=None, vna_device=None):
        super().__init__()
        
        # Store VNA device reference
        self.vna_device = vna_device
        
        # Log welcome window initialization
        logging.info("[welcome_windows.__init__] Initializing welcome window")
        if vna_device:
            device_type = type(vna_device).__name__
            logging.info(f"[welcome_windows.__init__] VNA device provided: {device_type}")
        else:
            logging.warning("[welcome_windows.__init__] No VNA device provided")

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

        self.setWindowTitle("Welcome")
        self.setGeometry(100, 100, 1000, 600)

        # === Central Widget ===

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # === Welcome message ===

        welcome_label = QLabel("Welcome to the NanoVNA UTN Toolkit!")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        main_layout.addWidget(welcome_label)

        # === Buttons (Left - Right) ===

        button_layout = QHBoxLayout()
        self.left_button = QPushButton("Calibration Kit")

        self.right_button = QPushButton("Calibration Wizard")
        self.right_button.clicked.connect(self.open_calibration_wizard)

        button_layout.addWidget(self.left_button)
        button_layout.addWidget(self.right_button)

        main_layout.addLayout(button_layout)

        # === Graphics layout (two columns) ===

        graphics_selector_layout = QHBoxLayout()

        # --- Selector 1 ---

        graphic1_selector = QGroupBox("Selector 1")
        g1_layout = QVBoxLayout()
        for i in range(1, 5):
            g1_layout.addWidget(QRadioButton(f"Option {i}"))
        graphic1_selector.setLayout(g1_layout)

        # --- Selector 2 ---
        graphic2_selector = QGroupBox("Selector 2")
        g2_layout = QVBoxLayout()
        for i in range(1, 5):
            g2_layout.addWidget(QRadioButton(f"Option {i}"))
        graphic2_selector.setLayout(g2_layout)

        graphics_selector_layout.addWidget(graphic1_selector)
        graphics_selector_layout.addWidget(graphic2_selector)

        main_layout.addLayout(graphics_selector_layout)

    def open_calibration_wizard(self):
        logging.info("[welcome_windows.open_calibration_wizard] Opening calibration wizard")
        
        if self.vna_device:
            device_type = type(self.vna_device).__name__
            logging.info(f"[welcome_windows.open_calibration_wizard] Passing device {device_type} to calibration wizard")
            self.welcome_windows = CalibrationWizard(self.vna_device)
        else:
            logging.warning("[welcome_windows.open_calibration_wizard] No device to pass to calibration wizard")
            self.welcome_windows = CalibrationWizard()
            
        self.welcome_windows.show()
        self.close() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())
