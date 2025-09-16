"""
Edit graphics window for NanoVNA devices.
"""

import skrf as rf
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTabWidget, QFrame, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QSettings

try:
    from NanoVNA_UTN_Toolkit.ui.utils.edit_graphics_utils import create_edit_tab1, create_edit_tab2
except ImportError as e:
    import logging, sys
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)


class EditGraphics(QMainWindow):
    def __init__(self, nano_window=None, freqs=None):
        super().__init__()

        carpeta_ini = os.path.join(os.path.dirname(__file__), "ini")

        os.makedirs(carpeta_ini, exist_ok=True)

        ruta_ini = os.path.join(carpeta_ini, "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        self.nano_window = nano_window

        self.setWindowTitle("Edit Graphics")
        self.setFixedSize(800, 500)

        # --- Frequency array placeholder ---
        if freqs is None:
            freqs = np.linspace(1e6, 100e6, 101)
        self.freqs = freqs

        # --- Data placeholders ---
        self.s11 = np.zeros_like(freqs, dtype=complex)  # S11 data
        self.s21 = np.zeros_like(freqs, dtype=complex)  # S21 data

        # --- Central widget setup ---
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(15, 15, 15, 15)
        central_layout.setSpacing(10)

        # --- Tabs setup ---
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 5px 12px; 
                background: #5a5a5a;
                color: white;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected { background: #333333; }
            QTabBar::tab:hover { background-color: #777777; }
            QTabWidget::pane { border: 0px; margin: 0px; padding: 0px; background: transparent; }
        """)

        tab1_widget, trace_color, marker_color, line_width, marker_size = create_edit_tab1(self, tabs=tabs)
        tab2_widget, trace_color2, marker_color2, line_width2, marker_size2 = create_edit_tab2(self, tabs=tabs)

        tabs.addTab(tab1_widget, "Graphic 1")
        tabs.addTab(tab2_widget, "Graphic 2")

        central_layout.addWidget(tabs)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        btn_cancel = QPushButton("Cancel")
        btn_apply = QPushButton("Apply")
        btn_style = """
            QPushButton {
                background-color: #555555;
                color: white;
                border-radius: 8px;
                padding: 6px 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #777777; }
            QPushButton:pressed { background-color: #333333; }
        """

        btn_cancel.setStyleSheet(btn_style)
        btn_apply.setStyleSheet(btn_style)
        btn_cancel.clicked.connect(self.close)
        btn_apply.clicked.connect(lambda: self.on_apply_clicked(trace_color=trace_color(), trace_color2=trace_color2(), 
                                                                marker_color=marker_color() , marker_color2=marker_color2(),
                                                                line_width=line_width(), line_width2=line_width2(),
                                                                marker_size=marker_size(), marker_size2=marker_size2(),
                                                                settings=settings))

        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_apply)
        central_layout.addLayout(button_layout)

        # --- Apply styles ---
        self.setCentralWidget(central_widget)
        self.setStyleSheet("background-color: #7f7f7f;")

    def on_apply_clicked(self, settings, trace_color="blue", trace_color2="blue", marker_color="blue", marker_color2="blue", 
                     line_width=2, line_width2=2, marker_size=2, marker_size2=2):
        from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_left_panel, create_right_panel

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        graph_type1 = settings.value("Tab1/GraphType1", "Smith Diagram")
        s_param1 = settings.value("Tab1/SParameter", "S11")

        graph_type2 = settings.value("Tab2/GraphType2", "Smith Diagram")
        s_param2 = settings.value("Tab2/SParameter", "S11")

        self.s11 = self.nano_window.s11
        self.s21 = self.nano_window.s21
        self.freqs = self.nano_window.freqs

        # --- Layout principal donde están los panels ---
        panels_layout = self.nano_window.centralWidget().layout().itemAt(0).layout()  # HBox

        # --- Desconectar sliders viejos para evitar errores de Qt ---
        if hasattr(self.nano_window, "markers"):
                for marker in self.nano_window.markers:
                    slider = marker["slider"]
                    slider.disconnect_events()

        # --- Remover y borrar paneles antiguos ---
        old_left_item = panels_layout.takeAt(0)
        if old_left_item and old_left_item.widget():
            old_left_item.widget().deleteLater()

        old_right_item = panels_layout.takeAt(0)
        if old_right_item and old_right_item.widget():
            old_right_item.widget().deleteLater()

        # --- Crear nuevo panel izquierdo ---
        self.nano_window.left_panel, self.nano_window.fig_left, self.nano_window.ax_left, \
        self.nano_window.canvas_left, self.nano_window.slider_left, self.nano_window.cursor_left, \
        self.nano_window.labels_left, self.nano_window.update_cursor_left = \
            create_left_panel(
                S_data=self.s11,
                freqs=self.freqs,
                graph_type=graph_type1,
                s_param=s_param1,
                tracecolor=trace_color,
                markercolor=marker_color,
                linewidth=line_width,
                markersize=marker_size
            )

        # --- Crear nuevo panel derecho ---
        self.nano_window.right_panel, self.nano_window.fig_right, self.nano_window.ax_right, \
        self.nano_window.canvas_right, self.nano_window.slider_right, self.nano_window.cursor_right, \
        self.nano_window.labels_right, self.nano_window.update_cursor_right = \
            create_right_panel(
                S_data=self.s11,
                freqs=self.freqs,
                graph_type=graph_type2,
                s_param=s_param2,
                tracecolor=trace_color2,
                markercolor=marker_color2,
                linewidth=line_width2,
                markersize=marker_size2    
            )

        self.nano_window.markers = [
            {
                "cursor": self.nano_window.cursor_left,
                "slider": self.nano_window.slider_left,
                "label": self.nano_window.labels_left,
                "update_cursor": self.nano_window.update_cursor_left
            },
            {
                "cursor": self.nano_window.cursor_right,
                "slider": self.nano_window.slider_right,
                "label": self.nano_window.labels_right,
                "update_cursor": self.nano_window.update_cursor_right
            }
        ]

        # --- Insertar nuevos panels en el layout ---
        panels_layout.addWidget(self.nano_window.left_panel, 1)
        panels_layout.addWidget(self.nano_window.right_panel, 1)

        # --- Redibujar ---
        self.nano_window.canvas_left.draw_idle()
        self.nano_window.canvas_right.draw_idle()

        settings.setValue("Graphic1/TraceColor", trace_color)
        settings.setValue("Graphic1/MarkerColor", marker_color)
        settings.setValue("Graphic1/TraceWidth", line_width)
        settings.setValue("Graphic1/MarkerWidth", marker_size)

        settings.setValue("Graphic2/TraceColor", trace_color2)
        settings.setValue("Graphic2/MarkerColor", marker_color2)
        settings.setValue("Graphic2/TraceWidth", line_width2)
        settings.setValue("Graphic2/MarkerWidth", marker_size2)

        settings.sync()

        self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = EditGraphics()
    window.show()
    app.exec()
