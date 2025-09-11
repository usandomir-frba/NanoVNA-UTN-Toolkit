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
    QPushButton, QHBoxLayout, QSizePolicy, QApplication, QGroupBox, QGridLayout,
    QMenu, QFileDialog
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

        # --- Marker visibility flags ---
        self.show_marker1 = True
        self.show_marker2 = True

        # --- Menu ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        file_menu.addAction("Open")
        file_menu.addAction("Save")
        save_as_action =  file_menu.addAction("Save As")
        save_as_action.triggered.connect(lambda: self.on_save_as())

        graphics_markers = edit_menu.addAction("Graphics/Markers")
        graphics_markers.triggered.connect(lambda: self.edit_graphics_markers())

        choose_graphics = view_menu.addAction("Graphics")
        choose_graphics.triggered.connect(self.open_view)  # CORREGIDO

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
        self.left_panel, self.fig_left, self.ax_smith, self.canvas_smith, \
        self.slider_smith, self.cursor_smith, self.labels_left, self.update_cursor, = \
            create_left_panel(
                S_data=S11, 
                freqs=freqs, 
                graph_type="Diagrama de Smith", 
                s_param="S11", 
                tracecolor="red",
                markercolor="blue",
                linewidth=2,
                markersize=5    
            )

        # =================== RIGHT PANEL ===================
        self.right_panel, self.fig_right, self.ax_right, self.canvas_right, \
        self.slider_right, self.cursor_right, self.labels_right, self.update_right_cursor = \
            create_right_panel(
                S_data=S11, 
                freqs=freqs, 
                graph_type="Modulo", 
                s_param="S11",
                tracecolor="red",
                markercolor="blue",
                linewidth=2  ,
                markersize=5
            )

        # =================== PANELS LAYOUT ===================
        panels_layout = QHBoxLayout()
        panels_layout.addWidget(self.left_panel, 1)
        panels_layout.addWidget(self.right_panel, 1)
        main_layout_vertical.addLayout(panels_layout)

        # =================== Buttons below all, centered ===================
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(10)

        # --- Top row: Calibration y Preferences ---
        top_buttons_widget = QWidget()
        top_buttons_layout = QHBoxLayout(top_buttons_widget)
        top_buttons_layout.setAlignment(Qt.AlignCenter)
        top_buttons_layout.setSpacing(20)

        btn_calibration = QPushButton("Calibration Wizard")
        btn_calibration.clicked.connect(self.open_calibration_wizard)
        top_buttons_layout.addWidget(btn_calibration)

        btn_preferences = QPushButton("Preferences")
        top_buttons_layout.addWidget(btn_preferences)

        buttons_layout.addWidget(top_buttons_widget)

        # --- Bottom: Console button ---
        console_btn_final = QPushButton("Console")
        console_btn_final.setStyleSheet("background-color: black; color: white;")
        buttons_layout.addWidget(console_btn_final)

        main_layout_vertical.addWidget(buttons_widget)

        self.markers = [
            {"cursor": self.cursor_smith, "slider": self.slider_smith, "label": self.labels_left, "update_cursor": self.update_cursor},
            {"cursor": self.cursor_right, "slider": self.slider_right, "label": self.labels_right, "update_cursor": self.update_right_cursor}
        ]

    # =================== CALIBRATION WIZARD FUNCTION ===================
    def on_save_as(self):
        from PySide6.QtWidgets import QFileDialog

        # Guardar visibilidad original de cursors y sliders
        marker1_visible = self.cursor_smith.get_visible()
        marker2_visible = self.cursor_right.get_visible()
        slider1_visible = self.slider_smith.ax.get_visible()
        slider2_visible = self.slider_right.ax.get_visible()

        # Ocultar ambos cursors y sliders para la captura
        self.cursor_smith.set_visible(False)
        self.cursor_right.set_visible(False)
        self.slider_smith.ax.set_visible(False)
        self.slider_right.ax.set_visible(False)

        # Actualizar canvas antes de guardar
        self.fig_left.canvas.draw_idle()
        self.fig_right.canvas.draw_idle()

        # Guardar figura izquierda (Smith)
        file_path_left, _ = QFileDialog.getSaveFileName(
            self,
            "Save Left Figure As",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if file_path_left:
            self.fig_left.savefig(file_path_left)

        # Guardar figura derecha
        file_path_right, _ = QFileDialog.getSaveFileName(
            self,
            "Save Right Figure As",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if file_path_right:
            self.fig_right.savefig(file_path_right)

        # Restaurar visibilidad original de cursors y sliders
        self.cursor_smith.set_visible(marker1_visible)
        self.cursor_right.set_visible(marker2_visible)
        self.slider_smith.ax.set_visible(slider1_visible)
        self.slider_right.ax.set_visible(slider2_visible)

        # Refrescar canvas
        self.fig_left.canvas.draw_idle()
        self.fig_right.canvas.draw_idle()

    def open_calibration_wizard(self):
        from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
        self.wizard_window = CalibrationWizard()
        self.wizard_window.show()
        self.close()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        view_menu = menu.addAction("View")
        edit_graphics_menu = menu.addAction("Edit Graphics")

        marker1_action = menu.addAction("Marker 1")
        marker1_action.setCheckable(True)
        marker1_action.setChecked(self.show_marker1)

        marker2_action = menu.addAction("Marker 2")
        marker2_action.setCheckable(True)
        marker2_action.setChecked(self.show_marker2)

        menu.addSeparator()
        menu.addAction("Copiar")
        menu.addAction("Pegar")
        menu.addAction("Eliminar")

        selected_action = menu.exec(event.globalPos())

        if selected_action == view_menu:
            self.open_view()
        elif selected_action == edit_graphics_menu:
            from NanoVNA_UTN_Toolkit.ui.graphics_windows.edit_graphics_window import EditGraphics
            self.edit_graphics_window = EditGraphics(nano_window=self) 
            self.edit_graphics_window.show()
        elif selected_action == marker1_action:
            self.show_marker1 = not self.show_marker1
            self.toggle_marker_visibility(0, self.show_marker1)
        elif selected_action == marker2_action:
            self.show_marker2 = not self.show_marker2
            self.toggle_marker_visibility(1, self.show_marker2)

    def edit_graphics_markers(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.edit_graphics_window import EditGraphics
        self.edit_graphics_window = EditGraphics(nano_window=self) 
        self.edit_graphics_window.show()

    def open_view(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.view_window import View
        if not hasattr(self, 'view_window') or self.view_window is None:
            self.view_window = View(nano_window=self)
        self.view_window.show()
        self.view_window.raise_()
        self.view_window.activateWindow()

    def toggle_marker_visibility(self, marker_index, show=True):
        marker = self.markers[marker_index]
        cursor = marker["cursor"]
        slider = marker["slider"]
        labels = marker["label"]
        update_cursor_func = marker.get("update_cursor", None)

        cursor.set_visible(show)
        
        if show:
            slider.ax.set_visible(True)
            slider.set_active(True)
            if hasattr(marker, "slider_callback"):
                slider.on_changed(marker.slider_callback)

            if update_cursor_func:
                update_cursor_func(0)  
        else:
            slider.set_val(0)
            slider.ax.set_visible(False)
            slider.set_active(False)
            # --- Limpiar labels con guiones ---
            labels["freq"].setText("Frequency: --")
            labels["val"].setText(f"{self.left_s_param if marker_index==0 else 'S11'}: -- + j--")
            labels["mag"].setText("|S11|: --")
            labels["phase"].setText("Phase: --")
            labels["z"].setText("Z: -- + j--")
            labels["il"].setText("IL: --")
            labels["vswr"].setText("VSWR: --")

        cursor.figure.canvas.draw_idle()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NanoVNAGraphics()
    window.show()
    sys.exit(app.exec())
