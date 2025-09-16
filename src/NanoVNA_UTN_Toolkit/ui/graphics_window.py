"""
Graphic view window for NanoVNA devices with dual info panels and cursors.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf
from PySide6.QtCore import QTimer, QThread, Qt, QSettings
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
    def __init__(self, s11=None, s21=None, freqs=None, left_graph_type="Smith Diagram", left_s_param="S11"):
        super().__init__()

        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        graph_type_tab1 = settings.value("Tab1/GraphType1", "Smith Diagram")
        s_param_tab1    = settings.value("Tab1/SParameter", "S11")

        graph_type_tab2 = settings.value("Tab2/GraphType2", "Magnitude")
        s_param_tab2    = settings.value("Tab2/SParameter", "S11")

        trace_color1 = settings.value("Graphic1/TraceColor", "blue")
        marker_color1 = settings.value("Graphic1/MarkerColor", "blue")

        trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
        marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))

        trace_color2 = settings.value("Graphic2/TraceColor", "blue")
        marker_color2 = settings.value("Graphic2/MarkerColor", "blue")

        trace_size2 = int(settings.value("Graphic2/TraceWidth", 2))
        marker_size2 = int(settings.value("Graphic2/MarkerWidth", 6))

        self.left_graph_type  = graph_type_tab1
        self.left_s_param     = s_param_tab1
        self.right_graph_type = graph_type_tab2
        self.right_s_param    = s_param_tab2

        # --- Marker visibility flags ---
        self.show_marker1 = True
        self.show_marker2 = True

        # --- Menu ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        sweep_menu = menu_bar.addMenu("Sweep")
        help_menu = menu_bar.addMenu("Help")

        file_menu.addAction("Open")
        file_menu.addAction("Save")
        save_as_action =  file_menu.addAction("Save As")
        save_as_action.triggered.connect(lambda: self.on_save_as())
        file_menu.addAction("Export")

        graphics_markers = edit_menu.addAction("Graphics/Markers")
        graphics_markers.triggered.connect(lambda: self.edit_graphics_markers())

        light_dark_mode = edit_menu.addAction("Light Mode 🔆")

        self.is_dark_mode = False  

        def toggle_menu_dark_mode():
            if self.is_dark_mode:
                light_dark_mode.setText("Light Mode 🔆")
                self.is_dark_mode = False
                #toggle_dark_mode(tabs, force_light=True)
            else:
                light_dark_mode.setText("Dark Mode 🌙")
                self.is_dark_mode = True
                #toggle_dark_mode(tabs, force_light=True)

        light_dark_mode.triggered.connect(toggle_menu_dark_mode)

        choose_graphics = view_menu.addAction("Graphics")
        choose_graphics.triggered.connect(self.open_view)  

        sweep_menu.addAction("Options")
        calibrate_option = sweep_menu.addAction("Calibration Wizard")

        calibrate_option.triggered.connect(lambda: self.open_calibration_wizard())

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
        self.left_panel, self.fig_left, self.ax_left, self.canvas_left, \
        self.slider_left, self.cursor_left, self.labels_left, self.update_cursor, = \
            create_left_panel(
                S_data=S11, 
                freqs=freqs, 
                graph_type=graph_type_tab1, 
                s_param=s_param_tab1, 
                tracecolor=trace_color1,
                markercolor=marker_color1,
                linewidth=trace_size1,
                markersize=marker_size1   
            )

        # =================== RIGHT PANEL ===================
        self.right_panel, self.fig_right, self.ax_right, self.canvas_right, \
        self.slider_right, self.cursor_right, self.labels_right, self.update_right_cursor = \
            create_right_panel(
                S_data=S11, 
                freqs=freqs, 
                graph_type=graph_type_tab2, 
                s_param=s_param_tab2,
                tracecolor=trace_color2,
                markercolor=marker_color2,
                linewidth=trace_size2,
                markersize=marker_size2
            )

        # =================== PANELS LAYOUT ===================
        panels_layout = QHBoxLayout()
        panels_layout.addWidget(self.left_panel, 1)
        panels_layout.addWidget(self.right_panel, 1)
        main_layout_vertical.addLayout(panels_layout)

        self.markers = [
            {"cursor": self.cursor_left, "slider": self.slider_left, "label": self.labels_left, "update_cursor": self.update_cursor},
            {"cursor": self.cursor_right, "slider": self.slider_right, "label": self.labels_right, "update_cursor": self.update_right_cursor}
        ]

    # =================== SAVE AS PNG ===================
    
    def on_save_as(self):
        from PySide6.QtWidgets import QFileDialog

        marker1_visible = self.cursor_left.get_visible()
        marker2_visible = self.cursor_right.get_visible()
        slider1_visible = self.slider_left.ax.get_visible()
        slider2_visible = self.slider_right.ax.get_visible()

        # Ocultar ambos cursors y sliders para la captura
        self.cursor_left.set_visible(False)
        self.cursor_right.set_visible(False)
        self.slider_left.ax.set_visible(False)
        self.slider_right.ax.set_visible(False)

        self.fig_left.canvas.draw_idle()
        self.fig_right.canvas.draw_idle()

        file_path_left, _ = QFileDialog.getSaveFileName(
            self,
            "Save Left Figure As",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if file_path_left:
            self.fig_left.savefig(file_path_left)

        file_path_right, _ = QFileDialog.getSaveFileName(
            self,
            "Save Right Figure As",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if file_path_right:
            self.fig_right.savefig(file_path_right)

        # Restaurar visibilidad original de cursors y sliders
        self.cursor_left.set_visible(marker1_visible)
        self.cursor_right.set_visible(marker2_visible)
        self.slider_left.ax.set_visible(slider1_visible)
        self.slider_right.ax.set_visible(slider2_visible)

        self.fig_left.canvas.draw()
        self.fig_right.canvas.draw()

    # =================== CALIBRATION WIZARD FUNCTION ==================

    def open_calibration_wizard(self):
        from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
        self.wizard_window = CalibrationWizard()
        self.wizard_window.show()
        self.close()

    # =================== RIGHT CLICK ==================

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        view_menu = menu.addAction("View")

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
        elif selected_action == marker1_action:
            self.show_marker1 = not self.show_marker1
            self.toggle_marker_visibility(0, self.show_marker1)
        elif selected_action == marker2_action:
            self.show_marker2 = not self.show_marker2
            self.toggle_marker_visibility(1, self.show_marker2)

    # =================== MARKERS ==================

    def edit_graphics_markers(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.edit_graphics_window import EditGraphics
        self.edit_graphics_window = EditGraphics(nano_window=self) 
        self.edit_graphics_window.show()

    # =================== VIEW ==================

    def open_view(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.view_window import View
        if not hasattr(self, 'view_window') or self.view_window is None:
            self.view_window = View(nano_window=self)
        self.view_window.show()
        self.view_window.raise_()
        self.view_window.activateWindow()

    # =================== TOGGLE MARKERS==================

    def clear_freq_edit(edit_widget):
        edit_widget.blockSignals(True) 
        edit_widget.setText("--")
        edit_widget.setFixedWidth(edit_widget.fontMetrics().horizontalAdvance(edit_widget.text()) + 4)
        edit_widget.blockSignals(False)


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

            edit_value = labels["freq"]
            edit_value.setEnabled(True)
            edit_value.setText(f"{self.freqs[0]*1e-6:.2f}") 

        else:
            slider.set_val(0)
            slider.ax.set_visible(False)
            slider.set_active(False)

            edit_value = labels["freq"]
            edit_value.setEnabled(False)
            edit_value.setText("0")

            # --- Limpiar otros labels ---
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
