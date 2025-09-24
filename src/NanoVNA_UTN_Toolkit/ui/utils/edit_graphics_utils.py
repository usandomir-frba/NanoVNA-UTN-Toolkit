from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox, 
    QColorDialog, QSpinBox, QCheckBox, QPushButton, QSizePolicy, QSpacerItem, QApplication
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QPixmap, QIcon

import qtawesome as qta

# --- Matplotlib ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

# --- Scikit-RF ---
import skrf as rf
import numpy as np
import os

# Estilo para SpinBox redondeados y elegantes
spin_style = """
    QSpinBox {
        color: black;
        background-color: white;
        border: 1px solid gray;
        border-radius: 2px;
        padding: 0px 2px;
    }
"""

groupbox_style = """
    QGroupBox {
        color: white;
        font-weight: bold;
    }
"""

####################################################################################################
#--------- Tab 1  ---------------------------------------------------------------------------------#
####################################################################################################

def create_edit_tab1(self, tabs):

    ui_dir = os.path.dirname(os.path.dirname(__file__))  
    ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

    settings = QSettings(ruta_ini, QSettings.IniFormat)

    trace_color1 = settings.value("Graphic1/TraceColor", "blue")
    marker_color1 = settings.value("Graphic1/MarkerColor", "blue")

    trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
    marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))

    graph_type1 = settings.value("Tab1/GraphType1", "Smith Diagram")
    s_param1 = settings.value("Tab1/SParameter", "S11")

    index = int(settings.value("Cursor1/index", 0))

####################################################################################################
#--------- Tab1 -----------------------------------------------------------------------------------#
####################################################################################################

    tab1 = QWidget()
    tab1_container = QVBoxLayout(tab1)
    tab1_container.setContentsMargins(0, 0, 0, 0)
    tab1_container.setSpacing(0)

    line_tab = QFrame()
    line_tab.setObjectName("separatorLine")
    line_tab.setFixedHeight(2)
    tab1_container.addWidget(line_tab)

    spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

    tab1_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

####################################################################################################
#--------- Left Data ------------------------------------------------------------------------------#
####################################################################################################

    # Layout principal
    layout_container = QWidget()
    layout = QHBoxLayout(layout_container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignVCenter)
    tab1_container.addWidget(layout_container)
    
    # --- Left Size GroupBox ---
    left_group = QGroupBox(" Sizes ")
    left_group.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(15)

    # --- Vertical layout inside the existing GroupBox ---
    group_v_layout = QVBoxLayout()
    group_v_layout.setAlignment(Qt.AlignTop)
    group_v_layout.setSpacing(15)
    group_v_layout.setContentsMargins(10, 10, 10, 10)

    # --- Trace color ---
    trace_layout = QHBoxLayout()
    lbl_trace = QLabel("Trace color:")
    lbl_trace.setStyleSheet("font-size: 13pt;")
    btn_trace = QFrame()
    btn_trace.setFixedSize(30, 30)
    btn_trace.setStyleSheet(f"background-color: {trace_color1}; border: 1px solid white; border-radius: 6px;")
    trace_layout.addWidget(lbl_trace)
    trace_layout.addWidget(btn_trace, alignment=Qt.AlignVCenter)
    left_layout.addLayout(trace_layout)

    # --- Marker color ---
    marker_layout = QHBoxLayout()
    lbl_marker = QLabel("Marker color:")
    lbl_marker.setStyleSheet("font-size: 13pt;")
    btn_marker = QFrame()
    btn_marker.setFixedSize(30, 30)
    btn_marker.setStyleSheet(f"background-color: {marker_color1}; border: 1px solid white; border-radius: 6px;")
    marker_layout.addWidget(lbl_marker)
    marker_layout.addWidget(btn_marker, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_layout)

    # --- Line width ---
    line_layout = QHBoxLayout()
    lbl_line = QLabel("Line width (all):")
    lbl_line.setStyleSheet("font-size: 13pt;")
    spin_line_tab1 = QSpinBox()
    spin_line_tab1.setRange(1, 10)
    spin_line_tab1.setValue(trace_size1)
    spin_line_tab1.setStyle(QApplication.style())
    spin_line_tab1.setAlignment(Qt.AlignCenter)
    spin_line_tab1.setFrame(True)                
    spin_line_tab1.setFixedWidth(50)
    line_layout.addWidget(lbl_line)
    line_layout.addWidget(spin_line_tab1, alignment=Qt.AlignVCenter)
    left_layout.addLayout(line_layout)

    # --- Marker size ---
    marker_size_layout = QHBoxLayout()
    lbl_marker_size = QLabel("Marker size (all):")
    lbl_marker_size.setStyleSheet("font-size: 13pt;")
    spin_marker_tab1 = QSpinBox()
    spin_marker_tab1.setRange(1, 20)
    spin_marker_tab1.setValue(marker_size1)
    spin_marker_tab1.setStyle(QApplication.style())
    spin_marker_tab1.setFrame(True)  
    spin_marker_tab1.setAlignment(Qt.AlignCenter)             
    spin_marker_tab1.setFixedWidth(50)
    marker_size_layout.addWidget(lbl_marker_size)
    marker_size_layout.addWidget(spin_marker_tab1, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_size_layout)

####################################################################################################
#--------- Getters --------------------------------------------------------------------------------#
####################################################################################################

    def get_trace_color():
        return btn_trace.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_marker_color():
        return btn_marker.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_line_width():
        return spin_line_tab1.value()

    def get_marker_size():
        return spin_marker_tab1.value()

####################################################################################################
#--------- Smith  ---------------------------------------------------------------------------------#
####################################################################################################

    # --- Matplotlib figure y canvas ---
    fig, ax = plt.subplots(figsize=(4,4))
    fig.subplots_adjust(left=0.2, right=0.88, top=0.9, bottom=0.2)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(340, 340)

    # --- Datos dummy ---
    N = 101
    freqs = np.linspace(1e6, 100e6, N)
    S_data = 0.5 * np.exp(1j * -2 * np.pi * freqs / 1e8)

    def update_graph(graph_type1):
        ax.clear()
        ax.legend().remove()

        if graph_type1 == "Smith Diagram":  
            ntw = rf.Network(frequency=self.freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
            ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)
            ax.legend([Line2D([0],[0], color=get_trace_color())],[s_param1], loc='upper left', bbox_to_anchor=(-0.17, 1.14))

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color())
                    line.set_linewidth(get_line_width())
                    break

            cursor_graph, = ax.plot(np.real(S_data[index]), np.imag(S_data[index]), 'o', markersize=get_marker_size(), color=get_marker_color(), visible=True)

        elif graph_type1 == "Magnitude":  
            if np.any(S_data):
                ax.plot(self.freqs*1e-6, np.abs(S_data), color=get_trace_color(), label=s_param1)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(f"|{s_param1}|")
            ax.grid(True)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color())
                    line.set_linewidth(get_line_width())
                    break
            
            cursor_graph, = ax.plot(self.freqs[index]*1e-6, np.abs(S_data[index]), 'o', markersize=get_marker_size(), color=get_marker_color(), visible=True)

            ax.spines['bottom'].set_color('grey')     
            ax.spines['bottom'].set_linewidth(0.7)

            ax.spines['left'].set_color('grey')      
            ax.spines['left'].set_linewidth(0.7)
            
        elif graph_type1 == "Phase":  
            if np.any(S_data):
                ax.plot(self.freqs*1e-6, np.angle(S_data, deg=True), color=get_trace_color(), label=s_param1)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(r'$\phi_{%s}$ [°]' % s_param1)
            ax.yaxis.set_label_coords(-0.18, 0.5)
            ax.grid(True)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color())
                    line.set_linewidth(get_line_width())
                    break

            cursor_graph, = ax.plot(freqs[index]*1e-6, np.angle(S_data[index], deg=True), 'o', markersize=get_marker_size(), color=get_marker_color(), visible=True)

            ax.spines['bottom'].set_color('grey')     
            ax.spines['bottom'].set_linewidth(0.7)

            ax.spines['left'].set_color('grey')      
            ax.spines['left'].set_linewidth(0.7)
            
        canvas.draw()

    # --- Inicializa el gráfico ---
    update_graph(graph_type1=graph_type1)

    # --- Funciones de actualización ---
    def update_trace_color():
        color = get_trace_color()
        if smith_line:
            smith_line.set_color(color)
            legend_line.set_color(color)
            canvas.draw()

    def update_marker_color():
        color = get_marker_color()
        cursor_graph.set_color(color)
        canvas.draw()

    def update_line_width():
        update_graph(graph_type1=graph_type1)

    def update_marker_size():
        update_graph(graph_type1=graph_type1)

    def pick_trace_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph(graph_type1=graph_type1)

    def pick_marker_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph(graph_type1=graph_type1)
            canvas.draw()

    btn_trace.mousePressEvent = pick_trace_color
    btn_marker.mousePressEvent = pick_marker_color
    spin_line_tab1.valueChanged.connect(lambda val: update_line_width())
    spin_marker_tab1.valueChanged.connect(lambda val: update_marker_size())

    layout.addWidget(left_group, 1)
    layout.addWidget(canvas, 2)

    spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

    tab1_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

    # --- Line above buttons ---
    line_above_buttons = QFrame()
    line_above_buttons.setObjectName("separatorLine")
    line_above_buttons.setFixedHeight(2)
    tab1_container.addWidget(line_above_buttons)

    return tab1, get_trace_color, get_marker_color, get_line_width, get_marker_size

def create_edit_tab2(self, tabs):

    ui_dir = os.path.dirname(os.path.dirname(__file__))  
    ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

    settings = QSettings(ruta_ini, QSettings.IniFormat)

    trace_color2 = settings.value("Graphic2/TraceColor", "red")
    marker_color2 = settings.value("Graphic2/MarkerColor", "red")

    line_width2 = int(settings.value("Graphic2/TraceWidth", 2))
    marker_size2 = int(settings.value("Graphic2/MarkerWidth", 6))

    graph_type2 = settings.value("Tab2/GraphType2", "Smith Diagram")
    s_param2 = settings.value("Tab2/SParameter", "S11")

    index = int(settings.value("Cursor2/index", 0))

####################################################################################################
#--------- Tab2 -----------------------------------------------------------------------------------#
####################################################################################################

    tab2 = QWidget()
    tab2_container = QVBoxLayout(tab2)
    tab2_container.setContentsMargins(0, 0, 0, 0)
    tab2_container.setSpacing(0)

    # Línea arriba
    line_tab = QFrame()
    line_tab.setFixedHeight(2)
    line_tab.setObjectName("separatorLine")
    tab2_container.addWidget(line_tab)

    tab2_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

####################################################################################################
#--------- Left Data ------------------------------------------------------------------------------#
####################################################################################################

    # Layout principal
    layout_container = QWidget()
    layout = QHBoxLayout(layout_container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignVCenter)
    tab2_container.addWidget(layout_container)

    # --- Left Size GroupBox ---
    left_group = QGroupBox(" Sizes ")
    left_group.setStyleSheet(groupbox_style)
    left_layout = QVBoxLayout(left_group)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setSpacing(15)

    # Trace color
    trace_layout = QHBoxLayout()
    lbl_trace = QLabel("Trace color:")
    lbl_trace.setStyleSheet("font-size: 13pt;")
    btn_trace = QFrame()
    btn_trace.setFixedSize(30, 30)
    btn_trace.setStyleSheet(f"background-color: {trace_color2}; border: 1px solid white; border-radius: 6px;")
    trace_layout.addWidget(lbl_trace)
    trace_layout.addWidget(btn_trace, alignment=Qt.AlignVCenter)
    left_layout.addLayout(trace_layout)

    # Marker color
    marker_layout = QHBoxLayout()
    lbl_marker = QLabel("Marker color:")
    lbl_marker.setStyleSheet("font-size: 13pt;")
    btn_marker = QFrame()
    btn_marker.setFixedSize(30, 30)
    btn_marker.setStyleSheet(f"background-color: {marker_color2}; border: 1px solid white; border-radius: 6px;")
    marker_layout.addWidget(lbl_marker)
    marker_layout.addWidget(btn_marker, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_layout)

    # Line width
    line_layout = QHBoxLayout()
    lbl_line = QLabel("Line width (all):")
    lbl_line.setStyleSheet("font-size: 13pt;")
    spin_line_tab2 = QSpinBox()
    spin_line_tab2.setRange(1, 10)
    spin_line_tab2.setValue(line_width2)
    spin_line_tab2.setStyle(QApplication.style())
    spin_line_tab2.setAlignment(Qt.AlignCenter)
    spin_line_tab2.setFrame(True)      
    spin_line_tab2.setFixedWidth(50)
    line_layout.addWidget(lbl_line)
    line_layout.addWidget(spin_line_tab2, alignment=Qt.AlignVCenter)
    left_layout.addLayout(line_layout)

    # Marker size
    marker_size_layout = QHBoxLayout()
    lbl_marker_size = QLabel("Marker size (all):")
    lbl_marker_size.setStyleSheet("font-size: 13pt;")
    spin_marker_tab2 = QSpinBox()
    spin_marker_tab2.setRange(1, 20)
    spin_marker_tab2.setValue(marker_size2)
    spin_marker_tab2.setStyle(QApplication.style())
    spin_marker_tab2.setAlignment(Qt.AlignCenter)
    spin_marker_tab2.setFrame(True)  
    spin_marker_tab2.setFixedWidth(50)
    marker_size_layout.addWidget(lbl_marker_size)
    marker_size_layout.addWidget(spin_marker_tab2, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_size_layout)

####################################################################################################
#--------- Getters --------------------------------------------------------------------------------#
####################################################################################################

    def get_trace_color2():
        return btn_trace.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_marker_color2():
        return btn_marker.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_line_width2():
        return spin_line_tab2.value()

    def get_marker_size2():
        return spin_marker_tab2.value()

####################################################################################################
#--------- Matplotlib Graph ----------------------------------------------------------------------#
####################################################################################################

    fig, ax = plt.subplots(figsize=(4,4))
    fig.subplots_adjust(left=0.2, right=0.88, top=0.9, bottom=0.2)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(340, 340)

    # Datos dummy
    N = 101
    freqs = np.linspace(1e6, 100e6, N)
    S_data = 0.5 * np.exp(1j * -2 * np.pi * freqs / 1e8)

    def update_graph2(graph_type2):
        ax.clear()
        ax.legend().remove()

        if graph_type2 == "Smith Diagram":  
            ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
            ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)
            ax.legend([Line2D([0],[0], color=get_trace_color2())],[s_param2], loc='upper left', bbox_to_anchor=(-0.17, 1.14))

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color2())
                    line.set_linewidth(get_line_width2())
                    break

            cursor_graph2, = ax.plot(np.real(S_data[index]), np.imag(S_data[index]), 'o', markersize=get_marker_size2(), color=get_marker_color2(), visible=True)

        elif graph_type2 == "Magnitude":  
            if np.any(S_data):
                ax.plot(freqs*1e-6, np.abs(S_data), color=get_trace_color2(), label=s_param2)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(f"|{s_param2}|")
            ax.grid(True)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color2())
                    line.set_linewidth(get_line_width2())
                    break
            
            cursor_graph2, = ax.plot(freqs[index]*1e-6, np.abs(S_data[index]), 'o', markersize=get_marker_size2(), color=get_marker_color2(), visible=True)

        elif graph_type2 == "Phase":  
            if np.any(S_data):
                ax.plot(freqs*1e-6, np.angle(S_data, deg=True), color=get_trace_color2(), label=s_param2)
            ax.set_xlabel("Frequency [MHz]")
            ax.set_ylabel(r'$\phi_{%s}$ [°]' % s_param2)
            ax.grid(True)

            for idx, line in enumerate(ax.lines):
                xdata = line.get_xdata()
                if len(xdata) == len(freqs):
                    line.set_color(get_trace_color2())
                    line.set_linewidth(get_line_width2())
                    break

            cursor_graph2, = ax.plot(freqs[index]*1e-6, np.angle(S_data[index], deg=True), 'o', markersize=get_marker_size2(), color=get_marker_color2(), visible=True)

        canvas.draw()

    update_graph2(graph_type2=graph_type2)

####################################################################################################
#--------- Events & Color Pickers ----------------------------------------------------------------#
####################################################################################################

    def update_trace_color2_event():
        color = get_trace_color2()
        for line in ax.lines:
            line.set_color(color)
        canvas.draw()

    def update_marker_color2_event():
        color = get_marker_color2()
        cursor_graph2.set_color(color)
        canvas.draw()

    def update_line_width2_event():
        update_graph2(graph_type2=graph_type2)

    def update_marker_size2_event():
        update_graph2(graph_type2=graph_type2)

    def pick_trace_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph2(graph_type2=graph_type2)

    def pick_marker_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            update_graph2(graph_type2=graph_type2)
            canvas.draw()

    btn_trace.mousePressEvent = pick_trace_color2
    btn_marker.mousePressEvent = pick_marker_color2
    spin_line_tab2.valueChanged.connect(lambda val: update_line_width2_event())
    spin_marker_tab2.valueChanged.connect(lambda val: update_marker_size2_event())

####################################################################################################
#--------- Layout Final --------------------------------------------------------------------------#
####################################################################################################

    layout.addWidget(left_group, 1)
    layout.addWidget(canvas, 2)

    tab2_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

    # Line above the buttons
    line_above_buttons = QFrame()
    line_above_buttons.setObjectName("separatorLine")
    line_above_buttons.setFixedHeight(2)
    tab2_container.addWidget(line_above_buttons)

    return tab2, get_trace_color2, get_marker_color2, get_line_width2, get_marker_size2
