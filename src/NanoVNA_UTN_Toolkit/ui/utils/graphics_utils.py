import numpy as np
import skrf as rf
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from PySide6.QtCore import Qt
from matplotlib.lines import Line2D

#############################################################################################
# =================== LEFT PANEL ========================================================= #
#############################################################################################

def create_left_panel(S_data, freqs, graph_type="Diagrama de Smith", s_param="S11", tracecolor="red", markercolor ="red", 
                        linewidth=2, markersize=2, marker_visible=True):

    freqs = freqs if freqs is not None else np.linspace(1e6, 100e6, 101)
    
    if S_data is None:
        phase = -2*np.pi*freqs/1e8
        S_data = 0.5 * np.exp(1j*phase)
    
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setAlignment(Qt.AlignTop)
    left_layout.setContentsMargins(10,10,10,10)
    left_layout.setSpacing(10)

    cursor_graph = None

    if graph_type == "Diagrama de Smith":
        fig, ax = plt.subplots(figsize=(5,5))
        fig.subplots_adjust(left=0.12, right=0.9, top=0.88, bottom=0.15)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(canvas)

        ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
        ntw.plot_s_smith(ax=ax, draw_labels=True)

        ax.legend(
            [Line2D([0], [0], color=tracecolor)],  # línea de ejemplo para la leyenda
            [s_param],                          # etiqueta correspondiente
            loc='upper left',
            bbox_to_anchor=(-0.17, 1.14)
        )

        for idx, line in enumerate(ax.lines):
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            if len(xdata) == len(freqs):
                line_color = tracecolor
                line.set_color(line_color)
                line.set_linewidth(linewidth)
                break
        canvas.draw_idle()

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color = markercolor, visible=marker_visible)

    elif graph_type == "Modulo":
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

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color = markercolor, visible=marker_visible)

    elif graph_type == "Fase":
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

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color = markercolor, visible=marker_visible)

    # --- Panel info ---
    info_panel = QWidget()
    info_layout = QGridLayout(info_panel)
    info_layout.setHorizontalSpacing(20)
    info_layout.setVerticalSpacing(5)

    box_s = QGroupBox(s_param)
    layout_s = QVBoxLayout()
    box_s.setLayout(layout_s)
    label_freq = QLabel("Frequency: -- MHz")
    label_val = QLabel(f"{s_param}: -- + j--")
    label_mag = QLabel(f"|{s_param}|: --")
    label_phase = QLabel("Phase: --")
    for lbl in [label_freq, label_val, label_mag, label_phase]:
        lbl.setStyleSheet("font-size:14px; padding:1px;")
        layout_s.addWidget(lbl)

    box_z = QGroupBox("Normalized Impedance (Z0=50Ω)")
    layout_z = QVBoxLayout()
    box_z.setLayout(layout_z)
    label_z = QLabel("Z: -- + j--")
    layout_z.addWidget(label_z)

    box_il = QGroupBox("Insertion Loss")
    layout_il = QVBoxLayout()
    box_il.setLayout(layout_il)
    label_il = QLabel("IL: -- dB")
    layout_il.addWidget(label_il)

    box_vswr = QGroupBox("VSWR")
    layout_vswr = QVBoxLayout()
    box_vswr.setLayout(layout_vswr)
    label_vswr = QLabel("VSWR: --")
    layout_vswr.addWidget(label_vswr)

    for box in [box_z, box_il, box_vswr]:
        for i in range(box.layout().count()):
            box.layout().itemAt(i).widget().setStyleSheet("font-size:14px; padding:1px;")

    info_layout.addWidget(box_s, 0, 0, 3, 1)
    info_layout.addWidget(box_z, 0, 1)
    info_layout.addWidget(box_il, 1, 1)
    info_layout.addWidget(box_vswr, 2, 1)
    left_layout.addWidget(info_panel)

    labels_dict = {
        "freq": label_freq,
        "val": label_val,
        "mag": label_mag,
        "phase": label_phase,
        "z": label_z,
        "il": label_il,
        "vswr": label_vswr
    }

    # --- Función de actualización del cursor ---
    def update_cursor(index, S_data_current=None):
        if S_data_current is None:
            S_data_current = S_data

        val_complex = S_data_current[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        # --- Actualizar cursor en el gráfico ---
        if graph_type == "Diagrama de Smith":
            cursor_graph.set_data([np.real(val_complex)], [np.imag(val_complex)])
        elif graph_type == "Modulo":
            cursor_graph.set_data([freqs[index]*1e-6], [magnitude])
        elif graph_type == "Fase":
            cursor_graph.set_data([freqs[index]*1e-6], [phase_deg])

        # --- Labels ---
        labels_dict["freq"].setText(f"Frequency: {freqs[index]*1e-6:.3f} MHz")
        labels_dict["val"].setText(f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex)>=0 else '-'} j{abs(np.imag(val_complex)):.3f}")
        labels_dict["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict["phase"].setText(f"Phase: {phase_deg:.2f}°")

        z = (1 + val_complex) / (1 - val_complex)
        labels_dict["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")
        il_db = -20*np.log10(magnitude)
        labels_dict["il"].setText(f"IL: {il_db:.2f} dB")
        vswr_val = (1 + magnitude)/(1 - magnitude) if magnitude < 1 else np.inf
        labels_dict["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")

        for label in labels_dict.values():
            label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        fig.canvas.draw_idle()
        slider.set_val(index)

    # --- Slider ---
    slider_ax = fig.add_axes([0.25, 0.05, 0.5, 0.03], facecolor='lightgray')
    slider = Slider(slider_ax, '', 0, len(freqs)-1, valinit=0, valstep=1)
    slider.vline.set_visible(False)
    slider.label.set_visible(False)
    slider.on_changed(lambda val: update_cursor(int(val), S_data_current=S_data))
    slider.ax.set_visible(marker_visible)

    # --- Inicializar cursor y labels ---
    update_cursor(0, S_data_current=S_data)

    #####################################################################################
    # --- AGREGAR CURSOR DRAGGABLE ---
    #####################################################################################

    dragging = {"active": False}

    def on_pick(event):
        if event.artist == cursor_graph:
            dragging["active"] = True

    def on_release(event):
        dragging["active"] = False

    def on_motion(event):
        if dragging["active"] and event.inaxes == ax:
            if graph_type in ["Modulo", "Fase"]:
                xdata = freqs*1e-6
                mouse_x = event.xdata
                index = np.argmin(np.abs(xdata - mouse_x))
                update_cursor(index)
            elif graph_type == "Diagrama de Smith":
                # Encontrar el punto más cercano en el diagrama de Smith
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

def create_right_panel(S_data=None, freqs=None, graph_type="Diagrama de Smith", s_param="S11", tracecolor="red", markercolor ="red", 
                        linewidth=2, markersize=2):

    freqs = freqs if freqs is not None else np.linspace(1e6, 100e6, 101)
    if S_data is None:
        phase = -2*np.pi*freqs/1e8
        S_data = 0.5 * np.exp(1j*phase)

    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setAlignment(Qt.AlignTop)
    right_layout.setContentsMargins(10,10,10,10)
    right_layout.setSpacing(10)

    # --- Crear figura y canvas según tipo ---
    if graph_type == "Diagrama de Smith":
        fig, ax = plt.subplots(figsize=(5,5))
        fig.subplots_adjust(left=0.12, right=0.9, top=0.88, bottom=0.15)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(canvas)

        ntw = rf.Network(frequency=freqs, s=S_data[:, np.newaxis, np.newaxis], z0=50)
        ntw.plot_s_smith(ax=ax, draw_labels=True)

        ax.legend(
            [Line2D([0], [0], color=tracecolor)],  
            [s_param],                          
            loc='upper left',
            bbox_to_anchor=(-0.17, 1.14)
        )
        
        for idx, line in enumerate(ax.lines):
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            if len(xdata) == len(freqs):
                line_color = tracecolor
                line.set_color(line_color)
                line.set_linewidth(linewidth)
                break
        canvas.draw_idle()

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color = markercolor)

    elif graph_type == "Modulo":
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

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color = markercolor)

    elif graph_type == "Fase":
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

        cursor_graph, = ax.plot([], [], 'o', markersize=markersize, color = markercolor)

    # --- Panel info ---
    info_panel = QWidget()
    info_layout = QGridLayout(info_panel)
    info_layout.setHorizontalSpacing(20)
    info_layout.setVerticalSpacing(5)

    box_s = QGroupBox(s_param)
    layout_s = QVBoxLayout()
    box_s.setLayout(layout_s)
    label_freq = QLabel("Frequency: -- MHz")
    label_val = QLabel(f"{s_param}: -- + j--")
    label_mag = QLabel(f"|{s_param}|: --")
    label_phase = QLabel("Phase: --")
    for lbl in [label_freq, label_val, label_mag, label_phase]:
        lbl.setStyleSheet("font-size:14px; padding:1px;")
        layout_s.addWidget(lbl)

    box_z = QGroupBox("Normalized Impedance (Z0=50Ω)")
    layout_z = QVBoxLayout()
    box_z.setLayout(layout_z)
    label_z = QLabel("Z: -- + j--")
    layout_z.addWidget(label_z)

    box_il = QGroupBox("Insertion Loss")
    layout_il = QVBoxLayout()
    box_il.setLayout(layout_il)
    label_il = QLabel("IL: -- dB")
    layout_il.addWidget(label_il)

    box_vswr = QGroupBox("VSWR")
    layout_vswr = QVBoxLayout()
    box_vswr.setLayout(layout_vswr)
    label_vswr = QLabel("VSWR: --")
    layout_vswr.addWidget(label_vswr)

    for box in [box_z, box_il, box_vswr]:
        for i in range(box.layout().count()):
            box.layout().itemAt(i).widget().setStyleSheet("font-size:14px; padding:1px;")

    info_layout.addWidget(box_s, 0, 0, 3, 1)
    info_layout.addWidget(box_z, 0, 1)
    info_layout.addWidget(box_il, 1, 1)
    info_layout.addWidget(box_vswr, 2, 1)
    right_layout.addWidget(info_panel)

    labels_dict = {
        "freq": label_freq,
        "val": label_val,
        "mag": label_mag,
        "phase": label_phase,
        "z": label_z,
        "il": label_il,
        "vswr": label_vswr
    }

    # --- Función de actualización del cursor ---
    def update_cursor(index, S_data_current=None):
        if S_data_current is None:
            S_data_current = S_data

        val_complex = S_data_current[index]
        magnitude = abs(val_complex)
        phase_deg = np.angle(val_complex, deg=True)

        # --- Actualizar cursor ---
        if graph_type == "Diagrama de Smith":
            cursor_graph.set_data([np.real(val_complex)], [np.imag(val_complex)])
        elif graph_type == "Modulo":
            cursor_graph.set_data([freqs[index]*1e-6], [magnitude])
        elif graph_type == "Fase":
            cursor_graph.set_data([freqs[index]*1e-6], [phase_deg])

        # --- Labels ---
        labels_dict["freq"].setText(f"Frequency: {freqs[index]*1e-6:.3f} MHz")
        labels_dict["val"].setText(f"{s_param}: {np.real(val_complex):.3f} {'+' if np.imag(val_complex)>=0 else '-'} j{abs(np.imag(val_complex)):.3f}")
        labels_dict["mag"].setText(f"|{s_param}|: {magnitude:.3f}")
        labels_dict["phase"].setText(f"Phase: {phase_deg:.2f}°")

        z = (1 + val_complex) / (1 - val_complex)
        labels_dict["z"].setText(f"Z: {np.real(z):.2f} + j{np.imag(z):.2f}")
        il_db = -20*np.log10(magnitude)
        labels_dict["il"].setText(f"IL: {il_db:.2f} dB")
        vswr_val = (1 + magnitude)/(1 - magnitude) if magnitude < 1 else np.inf
        labels_dict["vswr"].setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")

        for label in labels_dict.values():
            label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        fig.canvas.draw_idle()
        slider.set_val(index)

    # --- Slider ---
    slider_ax = fig.add_axes([0.25, 0.05, 0.5, 0.03], facecolor='lightgray')
    slider = Slider(slider_ax, '', 0, len(freqs)-1, valinit=0, valstep=1)
    slider.vline.set_visible(False)
    slider.label.set_visible(False)
    slider.on_changed(lambda val: update_cursor(int(val), S_data_current=S_data))

    # --- Inicializar cursor ---
    update_cursor(0, S_data_current=S_data)

    #####################################################################################
    # --- AGREGAR CURSOR DRAGGABLE ---
    #####################################################################################
    dragging = {"active": False}

    def on_pick(event):
        if event.artist == cursor_graph:
            dragging["active"] = True

    def on_release(event):
        dragging["active"] = False

    def on_motion(event):
        if dragging["active"] and event.inaxes == ax:
            if graph_type in ["Modulo", "Fase"]:
                xdata = freqs*1e-6
                mouse_x = event.xdata
                index = np.argmin(np.abs(xdata - mouse_x))
                update_cursor(index)
            elif graph_type == "Diagrama de Smith":
                mouse_point = complex(event.xdata, event.ydata)
                distances = np.abs(S_data - mouse_point)
                index = np.argmin(distances)
                update_cursor(index)

    canvas.mpl_connect("pick_event", on_pick)
    canvas.mpl_connect("button_release_event", on_release)
    canvas.mpl_connect("motion_notify_event", on_motion)

    cursor_graph.set_picker(5)

    return right_panel, fig, ax, canvas, slider, cursor_graph, labels_dict, update_cursor
