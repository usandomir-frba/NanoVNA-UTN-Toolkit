from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox, 
    QColorDialog, QSpinBox, QCheckBox, QPushButton, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon

import qtawesome as qta

# --- Matplotlib ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

# --- Scikit-RF ---
import skrf as rf
import numpy as np

# Estilo para SpinBox redondeados y elegantes
spin_style = """
    QSpinBox {
        color: black;
        background-color: white;
        border: 1px solid gray;
        border-radius: 8px;
        padding: 2px 4px;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: top right; /* arranca en top para el up */
        width: 16px;
        height: 12px;
    }

    QSpinBox::up-button {
        subcontrol-position: top right;
    }

    QSpinBox::down-button {
        subcontrol-position: bottom right;
    }

    QSpinBox::up-arrow, QSpinBox::down-arrow {
        width: 8px;
        height: 8px;
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
    tab1 = QWidget()
    tab1_container = QVBoxLayout(tab1)
    tab1_container.setContentsMargins(0, 0, 0, 0)
    tab1_container.setSpacing(0)

    line_tab = QFrame()
    line_tab.setFixedHeight(3)
    line_tab.setStyleSheet("background-color: white;")  # dark por defecto
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

    # Trace color
    trace_layout = QHBoxLayout()
    lbl_trace = QLabel("Trace color:")
    lbl_trace.setStyleSheet("color: white;")

    btn_trace = QFrame()
    btn_trace.setFixedSize(30, 30)
    btn_trace.setStyleSheet("background-color: blue; border: 1px solid white; border-radius: 6px;")
    trace_layout.addWidget(lbl_trace)
    trace_layout.addWidget(btn_trace, alignment=Qt.AlignVCenter)
    left_layout.addLayout(trace_layout)

    # Marker color
    marker_layout = QHBoxLayout()
    lbl_marker = QLabel("Marker color:")
    lbl_marker.setStyleSheet("color: white;")
    btn_marker = QFrame()
    btn_marker.setFixedSize(30, 30)
    btn_marker.setStyleSheet("background-color: red; border: 1px solid white; border-radius: 6px;")
    marker_layout.addWidget(lbl_marker)
    marker_layout.addWidget(btn_marker, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_layout)

    # Line width
    line_layout = QHBoxLayout()
    lbl_line = QLabel("Line width (all):")
    lbl_line.setStyleSheet("color: white;")
    spin_line_tab1 = QSpinBox()
    spin_line_tab1.setRange(1, 10)
    spin_line_tab1.setValue(2)
    spin_line_tab1.setStyleSheet(spin_style)
    spin_line_tab1.setFixedWidth(50)
    line_layout.addWidget(lbl_line)
    line_layout.addWidget(spin_line_tab1, alignment=Qt.AlignVCenter)
    left_layout.addLayout(line_layout)

    # Marker size
    marker_size_layout = QHBoxLayout()
    lbl_marker_size = QLabel("Marker size (all):")
    lbl_marker_size.setStyleSheet("color: white;")
    spin_marker_tab1 = QSpinBox()
    spin_marker_tab1.setRange(1, 20)
    spin_marker_tab1.setValue(6)
    spin_marker_tab1.setStyleSheet(spin_style)
    spin_marker_tab1.setFixedWidth(50)
    marker_size_layout.addWidget(lbl_marker_size)
    marker_size_layout.addWidget(spin_marker_tab1, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_size_layout)

    # Dark mode
    dark_mode_layout = QHBoxLayout()
    dark_mode_layout.setAlignment(Qt.AlignLeft)

    lbl_dark_mode = QLabel("Dark Mode:")
    dark_mode_layout.addWidget(lbl_dark_mode)

    btn_dark_mode = QLabel("☀") 
    btn_dark_mode.setFixedSize(30, 30)
    btn_dark_mode.setAlignment(Qt.AlignCenter)
    btn_dark_mode.setStyleSheet("""
        border: 1px solid black;
        border-radius: 6px;
        font-size: 18px;
    """)
    btn_dark_mode.setCursor(Qt.PointingHandCursor)
    dark_mode_layout.addStretch()
    dark_mode_layout.addWidget(btn_dark_mode)

    left_layout.addLayout(dark_mode_layout)

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

    # --- Right Smith chart ---
    right_group = QGroupBox()  # sin título
    right_group.setStyleSheet("""
        QGroupBox {
            border: none;
            background-color: transparent;
        }
    """)
    right_layout = QVBoxLayout(right_group)
    right_layout.setAlignment(Qt.AlignCenter)
    right_layout.setSpacing(15)
    right_layout.setContentsMargins(0, 0, 0, 0)

    # --- Matplotlib figure y canvas ---
    fig, ax = plt.subplots(figsize=(5,5))
    fig.subplots_adjust(left=0.12, right=0.9, top=0.88, bottom=0.15)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(350, 350)
    canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    right_layout.addWidget(canvas)

    # --- Datos dummy ---
    N = 101
    freqs = np.linspace(1e6, 100e6, N)
    S_data = 0.5 * np.exp(1j * 2 * np.pi * freqs / 1e8)

    # --- Plot Smith chart ---
    ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
    ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)

    # --- Obtener línea principal ---
    smith_line = None
    for line in ax.lines:
        if len(line.get_xdata()) == len(freqs):
            line.set_color(get_trace_color())
            line.set_linewidth(get_line_width())
            smith_line = line
            break

    # --- Legend line ---
    legend_line = Line2D([0], [0], color=get_trace_color())
    ax.legend([legend_line], ["S11"], loc='upper left', bbox_to_anchor=(-0.17,1.14))

    # --- Cursor interactivo ---
    cursor_graph, = ax.plot([S_data[35].real], [S_data[35].imag], 'o',
                        markersize=get_marker_size(),
                        color=get_marker_color(),
                        visible=True)

    canvas.draw()

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
        if smith_line:
            smith_line.set_linewidth(get_line_width())
            canvas.draw()

    def update_marker_size():
        cursor_graph.set_markersize(get_marker_size())
        canvas.draw()

    # --- Funciones para elegir color ---
    def pick_trace_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            # Actualizamos el botón
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            # Actualizamos línea y leyenda con el color seleccionado
            if smith_line:
                smith_line.set_color(color.name())
                legend_line.set_color(color.name())
                canvas.draw()

    def pick_marker_color(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            cursor_graph.set_color(color.name())
            canvas.draw()

    # --- Conectar eventos ---
    btn_trace.mousePressEvent = pick_trace_color
    btn_marker.mousePressEvent = pick_marker_color
    spin_line_tab1.valueChanged.connect(lambda val: update_line_width())
    spin_marker_tab1.valueChanged.connect(lambda val: update_marker_size())

    # --- Igualar tamaño de los GroupBox ---
    left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    layout.addWidget(left_group, stretch=1)
    layout.addWidget(right_group, stretch=1)

    spacer = QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

    tab1_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

    # --- Line above buttons ---
    line_above_buttons = QFrame()
    line_above_buttons.setStyleSheet("color: white; background-color: white;")
    line_above_buttons.setFixedHeight(3)
    tab1_container.addWidget(line_above_buttons)

    def toggle_dark_mode(tabs, event=None):
        if btn_dark_mode.text() == "☀":  # Dark mode
            btn_dark_mode.setText("🌙")

            # Main widget style for dark mode
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                }
                QTabWidget::pane {
                    background-color: #3b3b3b; 
                }
                QTabBar::tab {
                    background-color: #2b2b2b;   /* fondo del tab */
                    color: white;
                    padding: 5px 12px;
                    border: none; 
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #4d4d4d;   /* más claro que el fondo */
                    color: white;
                }
                QSpinBox {
                    color: white;
                    background-color: #3b3b3b;
                    border: 1px solid white;
                    border-radius: 8px;
                }
                QGroupBox:title {
                    color: white;  
                }
            """)

            # Tabs style for dark mode
            tabs.setStyleSheet("""
                QTabBar::tab {
                    background-color: #2b2b2b;   /* fondo del tab */
                    color: white;
                    padding: 5px 12px;
                    border: none; 
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #4d4d4d;   /* más claro que el fondo */
                    color: white;
                }
            """)

            # Set lines color and height
            line_tab.setStyleSheet("background-color: white;")
            line_tab.setFixedHeight(3)
            line_above_buttons.setStyleSheet("background-color: white;")
            line_above_buttons.setFixedHeight(3)

            # GroupBox color in dark mode
            left_group.setStyleSheet("QGroupBox { color: white; }")
            right_group.setStyleSheet("QGroupBox { color: white; }")

            # Labels color
            for w in self.findChildren(QLabel):
                w.setStyleSheet("color: white;")

            # Dark mode button style: dark gray but lighter than background
            btn_dark_mode.setStyleSheet("border: 1px solid #555555; border-radius: 6px; background-color: #4d4d4d;")

        else:  # Light mode
            btn_dark_mode.setText("☀")

            # Main widget style for light mode
            self.setStyleSheet("""
                QWidget {
                    background-color: #e6e6e6;
                }
                QTabWidget::pane {
                    background-color: #dcdcdc; 
                }
                QTabBar::tab {
                    background-color: #dcdcdc;  
                    color: black;             
                    padding: 5px;
                    border: 1px solid #aaa;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #d0d0d0;  /* slightly darker gray for selected tab */
                    color: black;
                }
                QSpinBox {
                    color: black;
                    background-color: #ffffff;
                    border: 1px solid black;
                    border-radius: 8px;
                }
                QGroupBox:title {
                    color: black; 
                }
            """)

            # Tabs style for light mode
            tabs.setStyleSheet("""
                QTabBar::tab {
                    background-color: #dcdcdc; 
                    color: black;             
                    padding: 5px 12px;
                    border: none;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                QTabBar::tab:selected {
                    background-color: #d0d0d0; 
                    color: black;
                }
            """)

            # Set lines color and height
            line_tab.setStyleSheet("background-color: black;")
            line_tab.setFixedHeight(3)
            line_above_buttons.setStyleSheet("background-color: black;")
            line_above_buttons.setFixedHeight(3)

            # GroupBox color in light mode (black background)
            left_group.setStyleSheet("QGroupBox { color: black;}")
            right_group.setStyleSheet("QGroupBox { color: black;}")

            # Labels color
            for w in self.findChildren(QLabel):
                w.setStyleSheet("color: black;")

            # Dark mode button style: light gray distinct from background
            btn_dark_mode.setStyleSheet("border: 1px solid #bbbbbb; border-radius: 6px; background-color: #cccccc;")

    btn_dark_mode.mousePressEvent = lambda event: toggle_dark_mode(tabs)    

    return tab1, get_trace_color, get_marker_color, get_line_width, get_marker_size

####################################################################################################
#--------- Tab 2  ---------------------------------------------------------------------------------#
####################################################################################################

def create_edit_tab2(self, tabs):
    tab2 = QWidget()
    tab2_container = QVBoxLayout(tab2)
    tab2_container.setContentsMargins(0, 0, 0, 0)
    tab2_container.setSpacing(0)

    # Línea arriba
    line_tab = QFrame()
    line_tab.setFixedHeight(3)
    line_tab.setStyleSheet("background-color: white;")
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
    lbl_trace.setStyleSheet("color: white;")
    btn_trace = QFrame()
    btn_trace.setFixedSize(30, 30)
    btn_trace.setStyleSheet("background-color: blue; border: 1px solid white; border-radius: 6px;")
    trace_layout.addWidget(lbl_trace)
    trace_layout.addWidget(btn_trace, alignment=Qt.AlignVCenter)
    left_layout.addLayout(trace_layout)

    # Marker color
    marker_layout = QHBoxLayout()
    lbl_marker = QLabel("Marker color:")
    lbl_marker.setStyleSheet("color: white;")
    btn_marker = QFrame()
    btn_marker.setFixedSize(30, 30)
    btn_marker.setStyleSheet("background-color: red; border: 1px solid white; border-radius: 6px;")
    marker_layout.addWidget(lbl_marker)
    marker_layout.addWidget(btn_marker, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_layout)

    # Line width
    line_layout = QHBoxLayout()
    lbl_line = QLabel("Line width (all):")
    lbl_line.setStyleSheet("color: white;")
    spin_line_tab2 = QSpinBox()
    spin_line_tab2.setRange(1, 10)
    spin_line_tab2.setValue(2)
    spin_line_tab2.setStyleSheet(spin_style)
    spin_line_tab2.setFixedWidth(50)
    line_layout.addWidget(lbl_line)
    line_layout.addWidget(spin_line_tab2, alignment=Qt.AlignVCenter)
    left_layout.addLayout(line_layout)

    # Marker size
    marker_size_layout = QHBoxLayout()
    lbl_marker_size = QLabel("Marker size (all):")
    lbl_marker_size.setStyleSheet("color: white;")
    spin_marker_tab2 = QSpinBox()
    spin_marker_tab2.setRange(1, 20)
    spin_marker_tab2.setValue(6)
    spin_marker_tab2.setStyleSheet(spin_style)
    spin_marker_tab2.setFixedWidth(50)
    marker_size_layout.addWidget(lbl_marker_size)
    marker_size_layout.addWidget(spin_marker_tab2, alignment=Qt.AlignVCenter)
    left_layout.addLayout(marker_size_layout)

    # Dark mode
    dark_mode_layout = QHBoxLayout()
    dark_mode_layout.setAlignment(Qt.AlignLeft)

    lbl_dark_mode = QLabel("Dark Mode:")
    dark_mode_layout.addWidget(lbl_dark_mode)

    btn_dark_mode = QLabel("☀") 
    btn_dark_mode.setFixedSize(30, 30)
    btn_dark_mode.setAlignment(Qt.AlignCenter)
    btn_dark_mode.setStyleSheet("""
        border: 1px solid black;
        border-radius: 6px;
        font-size: 18px;
    """)
    btn_dark_mode.setCursor(Qt.PointingHandCursor)
    dark_mode_layout.addStretch()
    dark_mode_layout.addWidget(btn_dark_mode)
    left_layout.addLayout(dark_mode_layout)

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
#--------- Smith  ---------------------------------------------------------------------------------#
####################################################################################################

    # --- Right Smith chart ---
    right_group = QGroupBox()
    right_group.setStyleSheet("""
        QGroupBox {
            border: none;
            background-color: transparent;
        }
    """)
    right_layout = QVBoxLayout(right_group)
    right_layout.setAlignment(Qt.AlignCenter)
    right_layout.setSpacing(15)
    right_layout.setContentsMargins(0, 0, 0, 0)

    # Matplotlib figure
    fig, ax = plt.subplots(figsize=(5,5))
    fig.subplots_adjust(left=0.12, right=0.9, top=0.88, bottom=0.15)
    canvas = FigureCanvas(fig)
    canvas.setFixedSize(350, 350)
    canvas.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    right_layout.addWidget(canvas)

    # Datos dummy
    N = 101
    freqs = np.linspace(1e6, 100e6, N)
    S_data = 0.5 * np.exp(1j * 2 * np.pi * freqs / 1e8)

    # Plot Smith chart
    ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
    ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)

    # Obtener línea principal
    smith_line2 = None
    for line in ax.lines:
        if len(line.get_xdata()) == len(freqs):
            line.set_color(get_trace_color2())
            line.set_linewidth(get_line_width2())
            smith_line2 = line
            break

    # Legend
    legend_line2 = Line2D([0],[0], color=get_trace_color2())
    ax.legend([legend_line2], ["S11"], loc='upper left', bbox_to_anchor=(-0.17,1.14))

    # Cursor interactivo fijo
    cursor_graph2, = ax.plot([S_data[35].real], [S_data[35].imag], 'o',
                        markersize=get_marker_size2(),
                        color=get_marker_color2(),
                        visible=True)

    canvas.draw()

####################################################################################################
#--------- Funciones de actualización ------------------------------------------------------------#
####################################################################################################

    def update_trace_color2():
        color = get_trace_color2()
        if smith_line2:
            smith_line2.set_color(color)
            legend_line2.set_color(color)
            canvas.draw()

    def update_marker_color2():
        color = get_marker_color2()
        cursor_graph2.set_color(color)
        canvas.draw()

    def update_line_width2():
        if smith_line2:
            smith_line2.set_linewidth(get_line_width2())
            canvas.draw()

    def update_marker_size2():
        cursor_graph2.set_markersize(get_marker_size2())
        canvas.draw()

####################################################################################################
#--------- Funciones de elección de color ---------------------------------------------------------#
####################################################################################################

    def pick_trace_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            if smith_line2:
                smith_line2.set_color(color.name())
                legend_line2.set_color(color.name())
                canvas.draw()

    def pick_marker_color2(event=None):
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")
            cursor_graph2.set_color(color.name())
            canvas.draw()

####################################################################################################
#--------- Conexiones eventos --------------------------------------------------------------------#
####################################################################################################

    btn_trace.mousePressEvent = pick_trace_color2
    btn_marker.mousePressEvent = pick_marker_color2
    spin_line_tab2.valueChanged.connect(lambda val: update_line_width2())
    spin_marker_tab2.valueChanged.connect(lambda val: update_marker_size2())

####################################################################################################
#--------- Igualar tamaño GroupBox ---------------------------------------------------------------#
####################################################################################################

    left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    layout.addWidget(left_group, stretch=1)
    layout.addWidget(right_group, stretch=1)

    tab2_container.addItem(QSpacerItem(0, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

    # Línea debajo
    line_above_buttons = QFrame()
    line_above_buttons.setStyleSheet("background-color: white;")
    line_above_buttons.setFixedHeight(3)
    tab2_container.addWidget(line_above_buttons)

####################################################################################################
#--------- Dark mode toggle ----------------------------------------------------------------------#
####################################################################################################

    def toggle_dark_mode2(tabs, event=None):
        if btn_dark_mode.text() == "☀":
            btn_dark_mode.setText("🌙")
            # aquí podes poner el mismo styling dark mode que tab1 para tab2
        else:
            btn_dark_mode.setText("☀")
            # igual, revertir a light mode

    btn_dark_mode.mousePressEvent = lambda event: toggle_dark_mode2(tabs)

    return tab2, get_trace_color2, get_marker_color2, get_line_width2, get_marker_size2
