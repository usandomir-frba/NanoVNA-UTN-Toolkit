"""
Graphic view window for NanoVNA devices.
"""

import skrf as rf
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTabWidget, QFrame, QSizePolicy, QApplication,
    QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt, QSettings

try:
    from NanoVNA_UTN_Toolkit.ui.utils.view_utils import create_tab1
    from NanoVNA_UTN_Toolkit.ui.utils.view_utils import create_tab2
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class View(QMainWindow):
    def __init__(self, nano_window=None, freqs=None):
        super().__init__()

        self.nano_window = nano_window 

        self.setWindowTitle("Graphic View")
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

        tab1_widget, self.fig, self.ax, self.canvas, self.left_panel, self.update_graph, self.current_s_tab1, self.current_graph_tab1 = create_tab1(self)

        tab2_widget, self.fig_right, self.ax_right, self.canvas_right, self.right_panel2, self.update_graph_right, self.current_s_tab2, self.current_graph_tab2 = create_tab2(self)

        tabs.addTab(tab1_widget, "Graphic 1")
        tabs.addTab(tab2_widget, "Graphic 2")

        central_layout.addWidget(tabs)

        # --- Line above buttons ---
        line_above_buttons = QFrame()
        line_above_buttons.setFrameShape(QFrame.HLine)
        line_above_buttons.setFrameShadow(QFrame.Plain)
        line_above_buttons.setStyleSheet("color: white; background-color: white;")
        line_above_buttons.setFixedHeight(2)
        central_layout.addWidget(line_above_buttons)

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
        btn_apply.clicked.connect(lambda: self.on_apply_clicked())

        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_apply)
        central_layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)
        self.setStyleSheet("background-color: #7f7f7f;")

        # --- Initial plot ---
        self.update_graph()

    def on_apply_clicked(self):
        from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_left_panel, create_right_panel

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        trace_color1 = settings.value("Graphic1/TraceColor", "blue")
        marker_color1 = settings.value("Graphic1/MarkerColor", "blue")

        trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
        marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))

        trace_color2 = settings.value("Graphic2/TraceColor", "blue")
        marker_color2 = settings.value("Graphic2/MarkerColor", "blue")

        trace_size2 = int(settings.value("Graphic2/TraceWidth", 2))
        marker_size2 = int(settings.value("Graphic2/MarkerWidth", 6))

        graph_type_tab1 = settings.value("Tab1/GraphType1", "Smith Diagram")
        s_param_tab1    = settings.value("Tab1/SParameter", "S11")

        graph_type_tab2 = settings.value("Tab2/GraphType2", "Magnitude")
        s_param_tab2    = settings.value("Tab2/SParameter", "S11")

        self.s11 = self.nano_window.s11
        self.s21 = self.nano_window.s21
        self.freqs = self.nano_window.freqs

        data_left = self.s11 if self.current_s_tab1 == "S11" else self.s21
        data_right = self.s11 if self.current_s_tab2 == "S11" else self.s21

        selected_graph_left = self.current_graph_tab1
        selected_graph_right = self.current_graph_tab2

        settings.setValue("Tab1/SParameter", self.current_s_tab1)
        settings.setValue("Tab1/GraphType1", selected_graph_left)

        settings.setValue("Tab2/SParameter", self.current_s_tab2)
        settings.setValue("Tab2/GraphType2", selected_graph_right)

        settings.sync()

        if self.nano_window is not None:
            panels_layout = self.nano_window.centralWidget().layout().itemAt(1).layout()  # HBox

            if hasattr(self.nano_window, "markers"):
                for marker in self.nano_window.markers:
                    slider = marker["slider"]
                    slider.disconnect_events()

            while panels_layout.count():
                item = panels_layout.takeAt(0)  
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

            self.nano_window.left_panel, self.nano_window.fig_left, self.nano_window.ax_left, \
            self.nano_window.canvas_left, self.nano_window.slider_left, self.nano_window.cursor_left, \
            self.nano_window.labels_left, self.nano_window.update_cursor_left, self.nano_window.update_left_data = \
                create_left_panel(
                    S_data=None,  # Force empty 
                    freqs=None,   # Force empty
                    graph_type=selected_graph_left,
                    s_param=self.current_s_tab1,
                    tracecolor=trace_color1,
                    markercolor=marker_color1,
                    linewidth=trace_size1,
                    markersize=marker_size1
                )

            self.nano_window.right_panel, self.nano_window.fig_right, self.nano_window.ax_right, \
            self.nano_window.canvas_right, self.nano_window.slider_right, self.nano_window.cursor_right, \
            self.nano_window.labels_right, self.nano_window.update_cursor_right, self.nano_window.update_right_data = \
                create_right_panel(
                    S_data=None,  # Force empty 
                    freqs=None,   # Force empty
                    graph_type=selected_graph_right,
                    s_param=self.current_s_tab2,
                    tracecolor=trace_color2,
                    markercolor=marker_color2,
                    linewidth=trace_size2,
                    markersize=marker_size2
                )

            self.nano_window.update_plots_with_new_data()

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

            self.nano_window.left_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.nano_window.right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            panels_layout.insertWidget(0, self.nano_window.left_panel, 1)
            panels_layout.insertWidget(1, self.nano_window.right_panel, 1)

            self.nano_window.s11 = self.s11
            self.nano_window.s21 = self.s21
            self.nano_window.freqs = self.freqs
            self.nano_window.left_graph_type = selected_graph_left
            self.nano_window.left_s_param = self.current_s_tab1
            self.nano_window.right_graph_type = selected_graph_right
            self.nano_window.right_s_param = self.current_s_tab2

            self.nano_window.show()

        else:
            from NanoVNA_UTN_Toolkit.ui.graphics_windows.graphics import NanoVNAGraphics
            self.nano_window = NanoVNAGraphics(
                s11=self.s11,
                s21=self.s21,
                freqs=self.freqs,
                left_graph_type=selected_graph_left,
                left_s_param=self.current_s_tab1,
                right_graph_type=selected_graph_right,
                right_s_param=self.current_s_tab2
            )
            self.nano_window.show()

        self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = View()
    window.show()
    app.exec()
