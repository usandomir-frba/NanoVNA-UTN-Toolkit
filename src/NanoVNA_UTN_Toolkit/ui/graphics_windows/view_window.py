import skrf as rf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTabWidget, QFrame, QSizePolicy, QApplication,
    QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt

class View(QMainWindow):
    def __init__(self, freqs=None):
        super().__init__()
        self.setWindowTitle("Graphic View")
        self.setFixedSize(800, 500)

        if freqs is None:
            freqs = np.linspace(1e6, 100e6, 101)
        self.freqs = freqs

        # s11 vacío inicialmente
        self.s11 = np.zeros_like(freqs, dtype=complex)

        # --- Widget central ---
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(15,15,15,15)
        central_layout.setSpacing(10)

        # --- Tabs ---
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
            QTabWidget::pane {
                border: 0px;
                margin: 0px;
                padding: 0px;
                background: transparent;
            }
        """)

        # --- Tab 1: Panel izquierdo + gráfico ---
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        tab1_layout.setContentsMargins(0,0,0,0)
        tab1_layout.setSpacing(20)

        # Panel izquierdo
        left_panel = QWidget()
        left_panel.setStyleSheet("color: white;") 
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignTop)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(0,14,0,0)

        # --- Radio Buttons ---
        graphic1_selector = QGroupBox("Selector Graphic 1")
        graphic1_selector.setStyleSheet("color: white;")  
        g1_layout = QVBoxLayout()
        self.radio_buttons = {}
        options = ["Diagrama de Smith", "Módulo", "Fase"]
        for option in options:
            rb = QRadioButton(option)
            rb.setStyleSheet("color: white;")  
            rb.toggled.connect(self.update_graph)
            g1_layout.addWidget(rb)
            self.radio_buttons[option] = rb

        self.radio_buttons["Diagrama de Smith"].setChecked(True)
        graphic1_selector.setLayout(g1_layout)
        left_layout.addWidget(graphic1_selector)

        # --- Figura y Canvas ---
        self.fig, self.ax = plt.subplots(figsize=(5,5))
        # Ajustamos márgenes para que el contenido sea más ancho y menos alto
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.15)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas.setFixedSize(350, 350)

        tab1_layout.addWidget(left_panel, 1)   
        tab1_layout.addWidget(self.canvas, 2)       

        # --- Línea debajo del tab ---
        line_tab = QFrame()
        line_tab.setFrameShape(QFrame.HLine)
        line_tab.setFrameShadow(QFrame.Plain)
        line_tab.setStyleSheet("color: white; background-color: white;")
        line_tab.setFixedHeight(2)
        tab1_container = QVBoxLayout()
        tab1_container.setContentsMargins(0,0,0,0)
        tab1_container.setSpacing(0)
        tab1_container.addWidget(line_tab)
        tab1_container.addWidget(tab1)

        tab1_widget = QWidget()
        tab1_widget.setLayout(tab1_container)

        # --- Tab 2: Placeholder ---
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        line_tab2 = QFrame()
        line_tab2.setFrameShape(QFrame.HLine)
        line_tab2.setFrameShadow(QFrame.Plain)
        line_tab2.setStyleSheet("color: white; background-color: white;")
        line_tab2.setFixedHeight(2)
        tab2_layout.addWidget(line_tab2)
        tab2_layout.addWidget(QLabel("Graphic 2", alignment=Qt.AlignCenter))

        tabs.addTab(tab1_widget, "Graphic 1")
        tabs.addTab(tab2, "Graphic 2")

        central_layout.addWidget(tabs)

        # --- Línea blanca encima de los botones ---
        line_above_buttons = QFrame()
        line_above_buttons.setFrameShape(QFrame.HLine)
        line_above_buttons.setFrameShadow(QFrame.Plain)
        line_above_buttons.setStyleSheet("color: white; background-color: white;")
        line_above_buttons.setFixedHeight(2)
        central_layout.addWidget(line_above_buttons)

        # --- Botones ---
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
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_apply)

        central_layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)
        self.setStyleSheet("background-color: #7f7f7f;")

        self.update_graph()

    def update_graph(self):
        self.ax.clear()
        # Ajustamos márgenes internos para contenido ancho y menos alto
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.15)

        if self.radio_buttons["Diagrama de Smith"].isChecked():
            ntw = rf.Network(frequency=self.freqs, s=self.s11[:, np.newaxis, np.newaxis], z0=50)
            ntw.plot_s_smith(ax=self.ax, draw_labels=False)
        elif self.radio_buttons["Módulo"].isChecked():
            if np.any(self.s11):
                self.ax.plot(self.freqs*1e-6, np.abs(self.s11))
            self.ax.set_xlabel("Frequency [MHz]")
            self.ax.set_ylabel("|S11|")
            self.ax.grid(True)
        elif self.radio_buttons["Fase"].isChecked():
            if np.any(self.s11):
                self.ax.plot(self.freqs*1e-6, np.angle(self.s11, deg=True))
            self.ax.set_xlabel("Frequency [MHz]")
            self.ax.set_ylabel("Phase [°]")
            self.ax.grid(True)

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication([])
    window = View()
    window.show()
    app.exec()
