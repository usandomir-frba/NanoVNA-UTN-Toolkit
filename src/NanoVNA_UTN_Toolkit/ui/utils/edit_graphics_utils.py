from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGroupBox,
    QColorDialog, QSpinBox
)
from PySide6.QtCore import Qt

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

# ------------------------ TAB 1 ------------------------
def create_edit_tab1(self):
    tab1 = QWidget()
    tab1_container = QVBoxLayout(tab1)
    tab1_container.setContentsMargins(0,0,0,0)
    tab1_container.setSpacing(0)

    # Línea blanca pegada al tab
    line_tab = QFrame()
    line_tab.setFrameShape(QFrame.HLine)
    line_tab.setFrameShadow(QFrame.Plain)
    line_tab.setStyleSheet("color: white; background-color: white;")
    line_tab.setFixedHeight(2)
    tab1_container.addWidget(line_tab)

    # Layout principal
    layout_container = QWidget()
    layout = QHBoxLayout(layout_container)
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignVCenter)
    tab1_container.addWidget(layout_container)

    # --- Left Size GroupBox ---
    left_group = QGroupBox("Sizes")
    left_group.setStyleSheet(groupbox_style)
    left_group.setFixedHeight(300)
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

    # --- Right Options GroupBox ---
    right_group = QGroupBox("Options")
    right_group.setStyleSheet(groupbox_style)
    right_group.setFixedHeight(220)
    right_layout = QVBoxLayout(right_group)
    right_layout.setAlignment(Qt.AlignTop)
    right_layout.setSpacing(15)

    option_layout = QHBoxLayout()
    lbl_right = QLabel("Change option color:")
    lbl_right.setStyleSheet("color: white;")
    btn_right = QFrame()
    btn_right.setFixedSize(30, 30)
    btn_right.setStyleSheet("background-color: green; border: 1px solid white; border-radius: 6px;")
    option_layout.addWidget(lbl_right)
    option_layout.addWidget(btn_right, alignment=Qt.AlignVCenter)
    right_layout.addLayout(option_layout)

    layout.addWidget(left_group)
    layout.addWidget(right_group)

    # --- Funciones internas ---
    def pick_trace_color():
        color = QColorDialog.getColor()
        if color.isValid():
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")

    def pick_marker_color():
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")

    def pick_right_color():
        color = QColorDialog.getColor()
        if color.isValid():
            btn_right.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")

    btn_trace.mousePressEvent = lambda event: pick_trace_color()
    btn_marker.mousePressEvent = lambda event: pick_marker_color()
    btn_right.mousePressEvent = lambda event: pick_right_color()

    # --- Getters ---
    def get_trace_color():
        return btn_trace.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_marker_color():
        return btn_marker.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_line_width():
        return spin_line_tab1.value()

    def get_marker_size():
        return spin_marker_tab1.value()

    return tab1, get_trace_color, get_marker_color, get_line_width, get_marker_size


# ------------------------ TAB 2 ------------------------
def create_edit_tab2(self):
    tab2 = QWidget()
    tab2_container = QVBoxLayout(tab2)
    tab2_container.setContentsMargins(0,0,0,0)
    tab2_container.setSpacing(0)

    # Línea blanca pegada al tab
    line_tab = QFrame()
    line_tab.setFrameShape(QFrame.HLine)
    line_tab.setFrameShadow(QFrame.Plain)
    line_tab.setStyleSheet("color: white; background-color: white;")
    line_tab.setFixedHeight(2)
    tab2_container.addWidget(line_tab)

    # Layout principal
    layout_container = QWidget()
    layout = QHBoxLayout(layout_container)
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(20)
    layout.setAlignment(Qt.AlignVCenter)
    tab2_container.addWidget(layout_container)

    # --- Left Size GroupBox ---
    left_group = QGroupBox("Sizes")
    left_group.setStyleSheet(groupbox_style)
    left_group.setFixedHeight(300)
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

    # --- Right Options GroupBox ---
    right_group = QGroupBox("Options")
    right_group.setStyleSheet(groupbox_style)
    right_group.setFixedHeight(220)
    right_layout = QVBoxLayout(right_group)
    right_layout.setAlignment(Qt.AlignTop)
    right_layout.setSpacing(15)

    option_layout = QHBoxLayout()
    lbl_right = QLabel("Change option color:")
    lbl_right.setStyleSheet("color: white;")
    btn_right = QFrame()
    btn_right.setFixedSize(30, 30)
    btn_right.setStyleSheet("background-color: green; border: 1px solid white; border-radius: 6px;")
    option_layout.addWidget(lbl_right)
    option_layout.addWidget(btn_right, alignment=Qt.AlignVCenter)
    right_layout.addLayout(option_layout)

    layout.addWidget(left_group)
    layout.addWidget(right_group)

    # --- Funciones internas ---
    def pick_trace_color2():
        color = QColorDialog.getColor()
        if color.isValid():
            btn_trace.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")

    def pick_marker_color2():
        color = QColorDialog.getColor()
        if color.isValid():
            btn_marker.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")

    def pick_right_color2():
        color = QColorDialog.getColor()
        if color.isValid():
            btn_right.setStyleSheet(f"background-color: {color.name()}; border: 1px solid white; border-radius: 6px;")

    btn_trace.mousePressEvent = lambda event: pick_trace_color2()
    btn_marker.mousePressEvent = lambda event: pick_marker_color2()
    btn_right.mousePressEvent = lambda event: pick_right_color2()

    # --- Getters ---
    def get_trace_color2():
        return btn_trace.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_marker_color2():
        return btn_marker.styleSheet().split("background-color:")[1].split(";")[0].strip()

    def get_line_width2():
        return spin_line_tab2.value()

    def get_marker_size2():
        return spin_marker_tab2.value()

    return tab2, get_trace_color2, get_marker_color2, get_line_width2, get_marker_size2

