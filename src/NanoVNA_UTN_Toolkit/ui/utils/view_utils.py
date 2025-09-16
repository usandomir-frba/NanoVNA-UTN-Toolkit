import skrf as rf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTabWidget, QFrame, QSizePolicy, QApplication,
    QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt

def create_tab1(self):

    tab1 = QWidget()
    tab1_layout = QHBoxLayout(tab1)
    tab1_layout.setContentsMargins(0, 0, 0, 0)
    tab1_layout.setSpacing(20)

    # --- Left panel ---
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(10)
    left_layout.setContentsMargins(0, 14, 0, 0)

    # --- Selector for S parameter ---
    graphic_param_selector = QGroupBox("Select Parameter")
    graphic_param_selector.setStyleSheet("color: white;")
    param_layout = QVBoxLayout()
    self.radio_s_tab1 = {}  # <-- corregido
    for option in ["S11", "S21"]:
        rb = QRadioButton(option)
        rb.setStyleSheet("color: white;")
        param_layout.addWidget(rb)
        self.radio_s_tab1[option] = rb  # <-- corregido
    self.radio_s_tab1["S11"].setChecked(True)
    graphic_param_selector.setLayout(param_layout)
    left_layout.addWidget(graphic_param_selector)

    # --- Selector for graph type ---
    graphic_type_selector = QGroupBox("Selector Graphic 1")
    graphic_type_selector.setStyleSheet("color: white;")
    type_layout = QVBoxLayout()
    self.radio_buttons_tab1 = {}  # <-- corregido
    for option in ["Smith Diagram", "Magnitude", "Phase"]:
        rb = QRadioButton(option)
        rb.setStyleSheet("color: white;")
        type_layout.addWidget(rb)
        self.radio_buttons_tab1[option] = rb  # <-- corregido
    self.radio_buttons_tab1["Smith Diagram"].setChecked(True)
    graphic_type_selector.setLayout(type_layout)
    left_layout.addWidget(graphic_type_selector)

    # --- Figure and Canvas ---
    fig, ax = plt.subplots(figsize=(4,4))
    fig.subplots_adjust(left=0.12, right=0.95, top=0.82, bottom=0.18)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(350, 350)

    tab1_layout.addWidget(left_panel, 1)
    tab1_layout.addWidget(canvas, 2)

    # --- Line below tab ---
    line_tab = QFrame()
    line_tab.setFrameShape(QFrame.HLine)
    line_tab.setFrameShadow(QFrame.Plain)
    line_tab.setStyleSheet("color: white; background-color: white;")
    line_tab.setFixedHeight(2)

    tab1_container = QVBoxLayout()
    tab1_container.setContentsMargins(0, 0, 0, 0)
    tab1_container.setSpacing(0)
    tab1_container.addWidget(line_tab)
    tab1_container.addWidget(tab1)
    tab1_widget = QWidget()
    tab1_widget.setLayout(tab1_container)

    self.current_s_tab1 = "S11"
    self.current_graph_tab1 = "Smith Diagram"

    # --- Función update_graph local ---
    def update_graph():
        ax.clear()
        ax.legend().remove()

        self.current_s_tab1 = "S11" if self.radio_s_tab1["S11"].isChecked() else "S21"
        #data = self.s11 if self.current_s_tab1 == "S11" else self.s21
        data = np.array([])

        if self.radio_buttons_tab1["Smith Diagram"].isChecked():
            self.current_graph_tab1 = "Smith Diagram"
            ntw = rf.Network(frequency=self.freqs, s=data[:, np.newaxis, np.newaxis], z0=50)
            ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)
            ax.legend([Line2D([0],[0], color='blue')],[self.current_s_tab1], loc='upper left', bbox_to_anchor=(-0.17, 1.14))

        elif self.radio_buttons_tab1["Magnitude"].isChecked():
            self.current_graph_tab1 = "Magnitude"
            if np.any(data):
                ax.plot(self.freqs*1e-6, np.abs(data), color='blue', label=self.current_s_tab1)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(f"|{self.current_s_tab1}|")
            ax.grid(True)

            ax.spines['bottom'].set_color('grey')     
            ax.spines['bottom'].set_linewidth(0.7)

            ax.spines['left'].set_color('grey')      
            ax.spines['left'].set_linewidth(0.7)
            

        elif self.radio_buttons_tab1["Phase"].isChecked():
            self.current_graph_tab1 = "Phase"
            if np.any(data):
                ax.plot(self.freqs*1e-6, np.angle(data, deg=True), color='blue', label=self.current_s_tab1)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(r'$\phi_{%s}$ [°]' % self.current_s_tab1)
            ax.grid(True)

            ax.spines['bottom'].set_color('grey')     
            ax.spines['bottom'].set_linewidth(0.7)

            ax.spines['left'].set_color('grey')      
            ax.spines['left'].set_linewidth(0.7)

        canvas.draw()

    # --- Conectar radio buttons a update_graph ---
    for rb in self.radio_s_tab1.values():
        rb.toggled.connect(update_graph)
    for rb in self.radio_buttons_tab1.values():
        rb.toggled.connect(update_graph)

    # --- Inicializa el gráfico ---
    update_graph()

    return tab1_widget, fig, ax, canvas, left_panel, update_graph, self.current_s_tab1, self.current_graph_tab1


def create_tab2(self):

    tab2 = QWidget()
    tab2_layout = QHBoxLayout(tab2)
    tab2_layout.setContentsMargins(0, 0, 0, 0)
    tab2_layout.setSpacing(20)

    # --- Right panel ---
    right_panel2 = QWidget()
    right_layout2 = QVBoxLayout(right_panel2)
    right_layout2.setAlignment(Qt.AlignTop)
    right_layout2.setSpacing(10)
    right_layout2.setContentsMargins(0, 14, 0, 0)

    # --- Selector for S parameter ---
    graphic_param_selector = QGroupBox("Select Parameter")
    graphic_param_selector.setStyleSheet("color: white;")
    param_layout = QVBoxLayout()
    self.radio_s_tab2 = {}
    for option in ["S11", "S21"]:
        rb = QRadioButton(option)
        rb.setStyleSheet("color: white;")
        param_layout.addWidget(rb)
        self.radio_s_tab2[option] = rb
    self.radio_s_tab2["S11"].setChecked(True)
    graphic_param_selector.setLayout(param_layout)
    right_layout2.addWidget(graphic_param_selector)

    # --- Selector for graph type ---
    graphic_type_selector = QGroupBox("Selector Graphic 2")
    graphic_type_selector.setStyleSheet("color: white;")
    type_layout = QVBoxLayout()
    self.radio_buttons_tab2 = {}
    for option in ["Smith Diagram", "Magnitude", "Phase"]:
        rb = QRadioButton(option)
        rb.setStyleSheet("color: white;")
        type_layout.addWidget(rb)
        self.radio_buttons_tab2[option] = rb
    self.radio_buttons_tab2["Smith Diagram"].setChecked(True)
    graphic_type_selector.setLayout(type_layout)
    right_layout2.addWidget(graphic_type_selector)

    # --- Figure and Canvas ---
    fig, ax = plt.subplots(figsize=(4,4))
    fig.subplots_adjust(left=0.12, right=0.95, top=0.82, bottom=0.18)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(350, 350)

    tab2_layout.addWidget(right_panel2, 1)
    tab2_layout.addWidget(canvas, 2)

    # --- Line below tab ---
    line_tab = QFrame()
    line_tab.setFrameShape(QFrame.HLine)
    line_tab.setFrameShadow(QFrame.Plain)
    line_tab.setStyleSheet("color: white; background-color: white;")
    line_tab.setFixedHeight(2)

    tab2_container = QVBoxLayout()
    tab2_container.setContentsMargins(0, 0, 0, 0)
    tab2_container.setSpacing(0)
    tab2_container.addWidget(line_tab)
    tab2_container.addWidget(tab2)
    tab2_widget = QWidget()
    tab2_widget.setLayout(tab2_container)

    self.current_s_tab2 = "S11"
    self.current_graph_tab2 = "Magnitude"

    def update_graph():
        ax.clear()
        ax.legend().remove()

        self.current_s_tab2 = "S11" if self.radio_s_tab2["S11"].isChecked() else "S21"
        #data = self.s11 if self.current_s_tab2 == "S11" else self.s21

        data = np.array([])

        if self.radio_buttons_tab2["Smith Diagram"].isChecked():  
            self.current_graph_tab2 = "Smith Diagram"
            ntw = rf.Network(frequency=self.freqs, s=data[:, np.newaxis, np.newaxis], z0=50)
            ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)
            ax.legend([Line2D([0],[0], color='blue')],[self.current_s_tab2], loc='upper left', bbox_to_anchor=(-0.17, 1.14))

        elif self.radio_buttons_tab2["Magnitude"].isChecked(): 
            self.current_graph_tab2 = "Magnitude"
            if np.any(data):
                ax.plot(self.freqs*1e-6, np.abs(data), color='blue', label=self.current_s_tab2)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(f"|{self.current_s_tab2}|")
            ax.grid(True)

            ax.spines['bottom'].set_color('grey')     
            ax.spines['bottom'].set_linewidth(0.7)

            ax.spines['left'].set_color('grey')      
            ax.spines['left'].set_linewidth(0.7)
            
        elif self.radio_buttons_tab2["Phase"].isChecked(): 
            self.current_graph_tab2 = "Phase"
            if np.any(data):
                ax.plot(self.freqs*1e-6, np.angle(data, deg=True), color='blue', label=self.current_s_tab2)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(r'$\phi_{%s}$ [°]' % self.current_s_tab2)
            ax.grid(True)

            ax.spines['bottom'].set_color('grey')     
            ax.spines['bottom'].set_linewidth(0.7)

            ax.spines['left'].set_color('grey')      
            ax.spines['left'].set_linewidth(0.7)
            
        canvas.draw()

    for rb in self.radio_s_tab2.values(): 
        rb.toggled.connect(update_graph)
    for rb in self.radio_buttons_tab2.values():  
        rb.toggled.connect(update_graph)

    # --- Inicializa el gráfico ---
    update_graph()

    return tab2_widget, fig, ax, canvas, right_panel2, update_graph, self.current_s_tab2, self.current_graph_tab2

