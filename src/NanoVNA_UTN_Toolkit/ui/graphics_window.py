"""
Graphic view window for NanoVNA devices.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf
from PySide6.QtCore import QTimer, QThread, Qt
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton,
    QHBoxLayout, QProgressBar, QFrame, QGridLayout, QGroupBox, QComboBox,
    QGraphicsScene, QGraphicsView, QSizePolicy, QSlider, QLabel
)
from PySide6.QtGui import QIcon, QTextCursor, QFont, QPen

from ..workers.device_worker import DeviceWorker
from .log_handler import GuiLogHandler

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class NanoVNAGraphics(QMainWindow):
    def __init__(self, s11=None, freqs=None):
        super().__init__()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        file_menu.addAction("Open")
        file_menu.addAction("Save")

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

        self.setWindowTitle("Diagrama de Smith")
        self.setGeometry(100, 100, 1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # --- Left panel ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignTop) 
        left_layout.setContentsMargins(10,10,10,10)
        left_layout.setSpacing(10)

        # --- Frecuencies ---

        freqs = np.linspace(1e6, 100e6, 101)
        modulo = 0.5
        fase = -2 * np.pi * freqs / 1e8  

        # --- S11 ---
        S11 = modulo * np.exp(1j * fase)
        #S11 = np.full_like(freqs, modulo, dtype=complex)

        # --- RF Network ---
        ntw = rf.Network(frequency=freqs, s=S11[:, np.newaxis, np.newaxis], z0=50)

        # --- Smith chart ---
        fig, ax = plt.subplots(figsize=(5,5))
        ntw.plot_s_smith(ax=ax, draw_labels=True)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        left_layout.addWidget(canvas)

        # --- Cursor  ---
        cursor_dot, = ax.plot([], [], 'ro', markersize=6)
        text_annotation = ax.annotate('', xy=(-1.1,-1.1), xytext=(10,10), textcoords='offset points',
                                    bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7))

        # --- Label ---
        freq_label = QLabel(f"f={freqs[0]*1e-6:.3f} MHz")
        freq_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(freq_label)

        # --- Slider  ---
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(len(freqs)-1)
        slider.setValue(0)
        left_layout.addWidget(slider)

        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #cccccc;
                margin: 0px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ff0000;
                border: 1px solid #5c5c5c;
                width: 20px;
                height: 20px;
                margin: -6px 0;  /* centra el handle en la barra */
                border-radius: 10px;
            }
        """)

        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(10) 

        # --- Cursor ---
        def update_cursor(index):
            cursor_dot.set_data([np.real(S11[index])], [np.imag(S11[index])])
            text_annotation.set_text(f"f={freqs[index]*1e-6:.3f} MHz\nS11={S11[index]:.2f}")
            text_annotation.set_position((np.real(S11[index]), np.imag(S11[index])))
            freq_label.setText(f"f={freqs[index]*1e-6:.3f} MHz")
            slider.setValue(index)
            fig.canvas.draw_idle()

        slider.valueChanged.connect(update_cursor)
        update_cursor(0)

        # --- Mouse ---
        def on_mouse_move(event):
            if event.xdata is None or event.ydata is None:
                return
            mouse_point = event.xdata + 1j*event.ydata
            idx = np.argmin(np.abs(S11 - mouse_point))
            update_cursor(idx)

        fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

        main_layout.addWidget(left_panel, 1)

        # --- Right panel ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        # --- Graphic ---
        fig2, ax2 = plt.subplots()
        ax2.set_xlim(1, 100)        
        ax2.set_ylim(0, 1)
        ax2.set_xlabel("Frecuencia [MHz]")
        ax2.set_ylabel("S11")
        ax2.set_title("Módulo de S11")
        ax2.grid(True)

        canvas2 = FigureCanvas(fig2)
        canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(canvas2, 1)  

        # --- Buttons ---
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QPushButton("Calibration Wizard"))
        bottom_layout.addWidget(QPushButton("Preferences"))
        right_layout.addLayout(bottom_layout)

        # --- Console ---
        console_btn = QPushButton("Console")
        console_btn.setStyleSheet("background-color: black; color: white;")
        right_layout.addWidget(console_btn)

        main_layout.addWidget(right_panel, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())
