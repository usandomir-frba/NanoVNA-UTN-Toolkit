"""
Graphic view window for NanoVNA devices with dual info panels and cursors.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf
from PySide6.QtCore import QTimer, QThread, Qt
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QSizePolicy, QApplication, QGroupBox, QGridLayout
    , QMenu
)
from PySide6.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

try:
    from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_left_panel
    from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_right_panel
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class NanoVNAGraphics(QMainWindow):
    def __init__(self, s11=None, s21=None, freqs=None, left_graph_type="Diagrama de Smith", left_s_param="S11"):
        super().__init__()

        # --- Menu ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        file_menu.addAction("Open")
        file_menu.addAction("Save")

        # --- Icon ---
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

        self.setWindowTitle("NanoVNA Graphics")
        self.setGeometry(100, 100, 1300, 700)

        # --- Central widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout_vertical = QVBoxLayout(central_widget)
        main_layout_vertical.setContentsMargins(10, 10, 10, 10)
        main_layout_vertical.setSpacing(10)

        # --- Datos de ejemplo ---
        freqs = np.linspace(1e6, 100e6, 101) if freqs is None else freqs
        modulus = 0.5
        phase = -2 * np.pi * freqs / 1e8
        S11 = modulus * np.exp(1j*phase) if s11 is None else s11
        S21 = modulus * np.exp(1j*phase) if s21 is None else s21

        self.s11 = S11
        self.s21 = S21
        self.freqs = freqs
        self.left_graph_type = left_graph_type
        self.left_s_param = left_s_param

        # =================== LEFT PANEL ===================

        self.left_panel, self.fig_smith, self.ax_smith, self.canvas_smith, \
        self.slider_smith, self.cursor_smith, self.labels_left, self.update_cursor = \
            create_left_panel(S_data=S11, freqs=freqs, graph_type="Diagrama de Smith", s_param="S11")

        # =================== RIGHT PANEL ===================

        self.right_panel, self.fig_right, self.ax_right, self.canvas_right, \
        self.slider_right, self.cursor_right, self.labels_right, self.update_right_cursor = \
            create_right_panel(S_data=S11, freqs=freqs, graph_type="Modulo", s_param="S11")

        # =================== PANELS LAYOUT ===================
        panels_layout = QHBoxLayout()
        panels_layout.addWidget(self.left_panel, 1)
        panels_layout.addWidget(self.right_panel, 1)
        main_layout_vertical.addLayout(panels_layout)

        # =================== Buttons below all, centered ===================
        
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)  # vertical layout
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(10)

        # --- Top row: Calibration y Preferences ---
        top_buttons_widget = QWidget()
        top_buttons_layout = QHBoxLayout(top_buttons_widget)
        top_buttons_layout.setAlignment(Qt.AlignCenter)
        top_buttons_layout.setSpacing(20)

        # --- Calibration Wizard Button ---
        btn_calibration = QPushButton("Calibration Wizard")
        btn_calibration.clicked.connect(self.open_calibration_wizard)
     
        top_buttons_layout.addWidget(btn_calibration)

        # --- Preferences Button ---
        btn_preferences = QPushButton("Preferences")
        top_buttons_layout.addWidget(btn_preferences)

        buttons_layout.addWidget(top_buttons_widget)

        # --- Bottom: Console button ---
        console_btn_final = QPushButton("Console")
        console_btn_final.setStyleSheet("background-color: black; color: white;")
        buttons_layout.addWidget(console_btn_final)

        main_layout_vertical.addWidget(buttons_widget)

    # =================== CALIBRATION WIZARD FUNCTION ===================

    def open_calibration_wizard(self):
        from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
        self.wizard_window = CalibrationWizard()
        self.wizard_window.show()
        self.close()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        view_menu = menu.addAction("View")
        menu.addAction("Copiar")
        menu.addAction("Pegar")
        menu.addAction("Eliminar")
        menu = menu.exec(event.globalPos())

        if menu == view_menu:
            self.open_view()

    def open_view(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.view_window import View
        self.view_window = View(nano_window=self) 
        self.view_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NanoVNAGraphics()
    window.show()
    sys.exit(app.exec())
