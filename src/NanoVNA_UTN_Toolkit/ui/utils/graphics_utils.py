import numpy as np
import skrf as rf
import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QSizePolicy, QLineEdit, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.widgets import Slider
from PySide6.QtCore import Qt
from matplotlib.lines import Line2D

from PySide6.QtCore import QObject, QEvent, QSettings

from PySide6.QtGui import QDoubleValidator

#############################################################################################
# =================== LEFT PANEL ========================================================= #
#############################################################################################

def create_left_panel(S_data, freqs, graph_type="Smith Diagram", s_param="S11",
                      tracecolor="red", markercolor="red", linewidth=2,
                      markersize=2, marker_visible=True):
                      
    freqs = freqs if freqs is not None else np.linspace(1e6, 100e6, 101)
    
    if S_data is None:
        phase = -2*np.pi*freqs/1e8
        S_data = 0.5 * np.exp(1j*phase)
    
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setContentsMargins(10,10,10,10)
    left_layout.setSpacing(10)

    # --- Figura ---
    if graph_type == "Smith Diagram":
        fig, ax = plt.subplots(figsize=(5,5))
        fig.subplots_adjust(left=0.12, right=0.9, top=0.88, bottom=0.15)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(canvas)

        ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
        ntw.plot_s_smith(ax=ax, draw_labels=True)
        ax.legend([Line2D([0],[0], color=tracecolor)], [s_param], loc='upper left', bbox_to_anchor=(-0.17,1.14))

        for idx, line in enumerate(ax.lines):
            xdata = line.get_xdata()
            if len(xdata) == len(freqs):
                line.set_color(tracecolor)
                line.set_linewidth(linewidth)
                break
        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)

    elif graph_type == "Magnitude":
        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(canvas)
        ax.plot(freqs*1e-6, np.abs(S_data), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth)
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel(f"|{s_param}|")
        ax.set_title(f"{s_param} Magnitude")
        ax.grid(True)
        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)

    elif graph_type == "Phase":
        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(canvas)
        ax.plot(freqs*1e-6, np.angle(S_data, deg=True), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth)
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel(r'$\phi_{%s}$ [°]' % s_param)
        ax.set_title(f"{s_param} Phase")
        ax.grid(True)
        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)

    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")

    # --- Panel info ---
    info_panel = QWidget()
    info_layout = QGridLayout(info_panel)
    info_layout.setHorizontalSpacing(20)
    info_layout.setVerticalSpacing(5)

    # QGroupBox S11
    box_s = QGroupBox(s_param)
    layout_s = QVBoxLayout()
    box_s.setLayout(layout_s)

    # --- Frecuencia editable ---
    hbox_freq = QHBoxLayout()
    hbox_freq.setAlignment(Qt.AlignLeft)
    hbox_freq.setSpacing(0)

    # Label "Frequency:"
    lbl_text = QLabel("Frequency:")
    lbl_text.setStyleSheet("font-size:14px;")
    lbl_text.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_text.setContentsMargins(0, 0, 5, 0)
    hbox_freq.addWidget(lbl_text)
    edit_value = QLineEdit(f"{freqs[0]*1e-6:.2f}")

    def limit_frequency_input(text, max_digits=3, max_decimals=2, allow_dashes=False):
        if allow_dashes and text == "--":
            return text

        filtered = "".join(c for c in text if c.isdigit() or c == ".")
        
        if filtered.count(".") > 1:
            parts = filtered.split(".", 1)
            filtered = parts[0] + "." + "".join(parts[1:]).replace(".", "")
        
        if "." in filtered:
            integer_part, decimal_part = filtered.split(".", 1)
            integer_part = integer_part[:max_digits]
            decimal_part = decimal_part[:max_decimals]
            filtered = integer_part + "." + decimal_part
        else:
            filtered = filtered[:max_digits]

        return filtered

    def on_text_changed():
        new_text = limit_frequency_input(edit_value.text(), 3, 2)
        if new_text != edit_value.text():
            edit_value.setText(new_text)
        edit_value.setFixedWidth(edit_value.fontMetrics().horizontalAdvance(edit_value.text()) + 4)

    edit_value.textChanged.connect(lambda _: edit_value.setText(limit_frequency_input(edit_value.text(), 3, 2)))
    edit_value.textChanged.connect(lambda _: on_text_changed())

    edit_value.setStyleSheet("font-size:14px; border:none; background:transparent;")
    edit_value.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    edit_value.setFixedWidth(edit_value.fontMetrics().horizontalAdvance(edit_value.text()) + 4)
    hbox_freq.addWidget(edit_value)

    # Label de unidad "MHz"
    lbl_unit = QLabel("MHz")
    lbl_unit.setStyleSheet("font-size:14px;")
    lbl_unit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_unit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    lbl_unit.setContentsMargins(2, 0, 0, 0)
    hbox_freq.addWidget(lbl_unit)

    layout_s.addLayout(hbox_freq)

    # --- Labels ---
    label_val = QLabel(f"{s_param}: -- + j--")
    label_mag = QLabel(f"|{s_param}|: --")
    label_phase = QLabel("Phase: --")
    for lbl in [label_val, label_mag, label_phase]:
        lbl.setStyleSheet("font-size:14px; padding:1px;")
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        layout_s.addWidget(lbl)

    # --- Otras cajas ---
    box_z = QGroupBox("Normalized Impedance (Z0=50Ω)")
    layout_z = QVBoxLayout()
    box_z.setLayout(layout_z)
    label_z = QLabel("Z: -- + j--")
    layout_z.addWidget(label_z)
    label_z.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    box_il = QGroupBox("Insertion Loss")
    layout_il = QVBoxLayout()
    box_il.setLayout(layout_il)
    label_il = QLabel("IL: -- dB")
    layout_il.addWidget(label_il)
    label_il.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    box_vswr = QGroupBox("VSWR")
    layout_vswr = QVBoxLayout()
    box_vswr.setLayout(layout_vswr)
    label_vswr = QLabel("VSWR: --")
    layout_vswr.addWidget(label_vswr)
    label_vswr.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    for box in [box_s, box_z, box_il, box_vswr]:
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        for i in range(box.layout().count()):
            w = box.layout().itemAt(i).widget()
            if w is not None:
                w.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")

    info_layout.addWidget(box_s, 0, 0, 3, 1)
    info_layout.addWidget(box_z, 0, 1)
    info_layout.addWidget(box_il, 1, 1)
    info_layout.addWidget(box_vswr, 2, 1)

    left_layout.addWidget(info_panel)

    labels_dict = {
        "val": label_val,
        "mag": label_mag,
        "phase": label_phase,
        "z": label_z,
        "il": label_il,
        "vswr": label_vswr,
        "freq": edit_value
    }

    # --- Función actualización ---
    def update_cursor(index, from_slider=False):
        val_complex = S_data[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        if graph_type == "Smith Diagram":
            cursor_graph.set_data([np.real(val_complex)], [np.imag(val_complex)])
        elif graph_type == "Magnitude":
            cursor_graph.set_data([freqs[index]*1e-6], [magnitude])
        elif graph_type == "Phase":
            cursor_graph.set_data([freqs[index]*1e-6], [phase_deg])

        edit_value.setText(f"{freqs[index]*1e-6:.3f}")
        labels_dict["val"].setText(f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex)>=0 else '-'} j{abs(np.imag(val_complex)):.3f}")
        labels_dict["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict["phase"].setText(f"Phase: {phase_deg:.2f}°")
        z = (1 + val_complex)/(1 - val_complex)
        labels_dict["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")
        il_db = -20*np.log10(magnitude)
        labels_dict["il"].setText(f"IL: {il_db:.2f} dB")
        vswr_val = (1 + magnitude)/(1 - magnitude) if magnitude < 1 else np.inf
        labels_dict["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")
        fig.canvas.draw_idle()

        if not from_slider:
            slider.set_val(index)

        edit_value.clearFocus()

        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        settings.setValue("Cursor1/index", index)

    # --- Slider ---

    if fig is not None:
        slider_ax = fig.add_axes([0.25,0.05,0.5,0.03], facecolor='lightgray')
        slider = Slider(slider_ax, '', 0, len(freqs)-1, valinit=0, valstep=1)
        slider.vline.set_visible(False)
        slider.label.set_visible(False)
        slider.on_changed(lambda val: update_cursor(int(val), from_slider=True))

    # --- Conectar edición manual ---
    def freq_edited():
        try:
            val_mhz = float(edit_value.text().replace(",","."))
            index = np.argmin(np.abs(freqs*1e-6 - val_mhz))
            update_cursor(index)
            edit_value.clearFocus()
        except:
            pass
    edit_value.editingFinished.connect(freq_edited)

    # --- Inicializar ---
    update_cursor(0)

    # --- Cursor draggable ---
    dragging = {"active": False}
    def on_pick(event):
        if event.artist == cursor_graph:
            dragging["active"] = True
    def on_release(event):
        dragging["active"] = False
    def on_motion(event):
        if dragging["active"] and event.inaxes == ax:
            if graph_type in ["Magnitude", "Phase"]:
                mouse_x = event.xdata
                index = np.argmin(np.abs(freqs*1e-6 - mouse_x))
                update_cursor(index)
            else:
                mouse_point = complex(event.xdata, event.ydata)
                distances = np.abs(S_data - mouse_point)
                index = np.argmin(distances)
                update_cursor(index)
    cursor_graph.set_picker(5)
    canvas.mpl_connect("pick_event", on_pick)
    canvas.mpl_connect("button_release_event", on_release)
    canvas.mpl_connect("motion_notify_event", on_motion)

    return left_panel, fig, ax, canvas, slider, cursor_graph, labels_dict, update_cursor

#############################################################################################
# =================== RIGHT PANEL ========================================================= #
#############################################################################################

def create_right_panel(S_data=None, freqs=None, graph_type="Smith Diagram", s_param="S11",
                       tracecolor="red", markercolor="red", linewidth=2, markersize=2, marker_visible=True):

    freqs = freqs if freqs is not None else np.linspace(1e6, 100e6, 101)
    
    if S_data is None:
        phase = -2*np.pi*freqs/1e8
        S_data = 0.5 * np.exp(1j*phase)

    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setAlignment(Qt.AlignTop)
    right_layout.setContentsMargins(10,10,10,10)
    right_layout.setSpacing(10)

    # --- Figura ---
    if graph_type == "Smith Diagram":
        fig, ax = plt.subplots(figsize=(5,5))
        fig.subplots_adjust(left=0.12, right=0.9, top=0.88, bottom=0.15)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(canvas)

        ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
        ntw.plot_s_smith(ax=ax, draw_labels=True)
        ax.legend([Line2D([0],[0], color=tracecolor)], [s_param], loc='upper left', bbox_to_anchor=(-0.17,1.14))

        for idx, line in enumerate(ax.lines):
            if len(line.get_xdata()) == len(freqs):
                line.set_color(tracecolor)
                line.set_linewidth(linewidth)
                break
        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)

    elif graph_type == "Magnitude":
        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(canvas)
        ax.plot(freqs*1e-6, np.abs(S_data), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth)
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel(f"|{s_param}|")
        ax.set_title(f"{s_param} Magnitude")
        ax.grid(True)
        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)

    elif graph_type == "Phase":
        fig, ax = plt.subplots(figsize=(4,3))
        fig.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(canvas)
        ax.plot(freqs*1e-6, np.angle(S_data, deg=True), color=tracecolor, marker='.', linestyle='-', linewidth=linewidth)
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel(r'$\phi_{%s}$ [°]' % s_param)
        ax.set_title(f"{s_param} Phase")
        ax.grid(True)
        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color=markercolor, visible=marker_visible)

    # --- Panel info ---
    info_panel = QWidget()
    info_layout = QGridLayout(info_panel)
    info_layout.setHorizontalSpacing(20)
    info_layout.setVerticalSpacing(5)

    box_s = QGroupBox(s_param)
    layout_s = QVBoxLayout()
    box_s.setLayout(layout_s)

    # --- Frecuencia editable (Right Panel) ---
    hbox_freq = QHBoxLayout()
    hbox_freq.setAlignment(Qt.AlignLeft)
    hbox_freq.setSpacing(0) 
    # Label "Frequency:"
    lbl_text = QLabel("Frequency:")
    lbl_text.setStyleSheet("font-size:14px;")
    lbl_text.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_text.setContentsMargins(0, 0, 5, 0)  # margen derecho de 5 px
    hbox_freq.addWidget(lbl_text)

    edit_value = QLineEdit(f"{freqs[0]*1e-6:.2f}")

    def limit_frequency_input(text, max_digits=3, max_decimals=2):
        filtered = "".join(c for c in text if c.isdigit() or c == ".")
        
        if filtered.count(".") > 1:
            parts = filtered.split(".", 1)
            filtered = parts[0] + "." + "".join(parts[1:]).replace(".", "")
        
        if "." in filtered:
            integer_part, decimal_part = filtered.split(".", 1)
            integer_part = integer_part[:max_digits]
            decimal_part = decimal_part[:max_decimals]
            filtered = integer_part + "." + decimal_part
        else:
            filtered = filtered[:max_digits]

        return filtered

    def on_text_changed():
        new_text = limit_frequency_input(edit_value.text(), 3, 2)
        if new_text != edit_value.text():
            edit_value.setText(new_text)
        edit_value.setFixedWidth(edit_value.fontMetrics().horizontalAdvance(edit_value.text()) + 4)

    edit_value.textChanged.connect(lambda _: edit_value.setText(limit_frequency_input(edit_value.text(), 3, 2)))
    edit_value.textChanged.connect(lambda _: on_text_changed())

    edit_value.setStyleSheet("font-size:14px; border:none; background:transparent;")
    edit_value.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    edit_value.setFixedWidth(edit_value.fontMetrics().horizontalAdvance(edit_value.text()) + 4)
    hbox_freq.addWidget(edit_value)

    # Label de unidad "MHz"
    lbl_unit = QLabel("MHz")
    lbl_unit.setStyleSheet("font-size:14px;")
    lbl_unit.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
    lbl_unit.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    lbl_unit.setContentsMargins(2, 0, 0, 0)  # margen izquierdo mínimo
    hbox_freq.addWidget(lbl_unit)

    # Agregar al layout de la caja
    layout_s.addLayout(hbox_freq)

    label_val = QLabel(f"{s_param}: -- + j--")
    label_mag = QLabel(f"|{s_param}|: --")
    label_phase = QLabel("Phase: --")
    for lbl in [label_val, label_mag, label_phase]:
        lbl.setStyleSheet("font-size:14px; padding:1px;")
        lbl.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        layout_s.addWidget(lbl)

    box_z = QGroupBox("Normalized Impedance (Z0=50Ω)")
    layout_z = QVBoxLayout()
    box_z.setLayout(layout_z)
    label_z = QLabel("Z: -- + j--")
    layout_z.addWidget(label_z)
    label_z.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    box_il = QGroupBox("Insertion Loss")
    layout_il = QVBoxLayout()
    box_il.setLayout(layout_il)
    label_il = QLabel("IL: -- dB")
    layout_il.addWidget(label_il)
    label_il.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    box_vswr = QGroupBox("VSWR")
    layout_vswr = QVBoxLayout()
    box_vswr.setLayout(layout_vswr)
    label_vswr = QLabel("VSWR: --")
    layout_vswr.addWidget(label_vswr)
    label_vswr.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

    info_layout.addWidget(box_s, 0, 0, 3, 1)
    info_layout.addWidget(box_z, 0, 1)
    info_layout.addWidget(box_il, 1, 1)
    info_layout.addWidget(box_vswr, 2, 1)

    right_layout.addWidget(info_panel)

    for box in [box_s, box_z, box_il, box_vswr]:
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        for i in range(box.layout().count()):
            w = box.layout().itemAt(i).widget()
            if w is not None:
                w.setStyleSheet("font-size:14px; padding:1px; border:none; background:transparent;")

    labels_dict = {
        "freq": edit_value,
        "val": label_val,
        "mag": label_mag,
        "phase": label_phase,
        "z": label_z,
        "il": label_il,
        "vswr": label_vswr
    }

    def update_cursor(index, from_slider=False):
        val_complex = S_data[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        if graph_type == "Smith Diagram":
            cursor_graph.set_data([np.real(val_complex)], [np.imag(val_complex)])
        elif graph_type == "Magnitude":
            cursor_graph.set_data([freqs[index]*1e-6], [magnitude])
        elif graph_type == "Phase":
            cursor_graph.set_data([freqs[index]*1e-6], [phase_deg])


        edit_value.setText(f"  {freqs[index]*1e-6:.2f}")

        labels_dict["val"].setText(f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex)>=0 else '-'} j{abs(np.imag(val_complex)):.3f}")
        labels_dict["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict["phase"].setText(f"Phase: {phase_deg:.2f}°")
        z = (1 + val_complex)/(1 - val_complex)
        labels_dict["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")
        il_db = -20*np.log10(magnitude)
        labels_dict["il"].setText(f"IL: {il_db:.2f} dB")
        vswr_val = (1 + magnitude)/(1 - magnitude) if magnitude < 1 else np.inf
        labels_dict["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")
        fig.canvas.draw_idle()

        if not from_slider:
            slider.set_val(index)

        edit_value.clearFocus()

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        settings.setValue("Cursor2/index", index)

    # --- Slider ---
    slider_ax = fig.add_axes([0.25,0.05,0.5,0.03], facecolor='lightgray')
    slider = Slider(slider_ax, '', 0, len(freqs)-1, valinit=0, valstep=1)
    slider.vline.set_visible(False)
    slider.label.set_visible(False)
    slider.on_changed(lambda val: update_cursor(int(val), from_slider=True))

    # --- Conectar edición manual ---
    def freq_edited():
        try:
            val_mhz = float(edit_value.text().replace(",","."))
            index = np.argmin(np.abs(freqs*1e-6 - val_mhz))
            update_cursor(index)
            edit_value.clearFocus()
        except:
            pass
    edit_value.editingFinished.connect(freq_edited)

    # --- Inicializar ---
    update_cursor(0)

    # --- Cursor draggable ---
    dragging = {"active": False}
    def on_pick(event):
        if event.artist == cursor_graph:
            dragging["active"] = True
    def on_release(event):
        dragging["active"] = False
    def on_motion(event):
        if dragging["active"] and event.inaxes == ax:
            if graph_type in ["Magnitude", "Phase"]:
                mouse_x = event.xdata
                index = np.argmin(np.abs(freqs*1e-6 - mouse_x))
                update_cursor(index)
            else:
                mouse_point = complex(event.xdata, event.ydata)
                distances = np.abs(S_data - mouse_point)
                index = np.argmin(distances)
                update_cursor(index)
    cursor_graph.set_picker(5)
    canvas.mpl_connect("pick_event", on_pick)
    canvas.mpl_connect("button_release_event", on_release)
    canvas.mpl_connect("motion_notify_event", on_motion)

    return right_panel, fig, ax, canvas, slider, cursor_graph, labels_dict, update_cursor
