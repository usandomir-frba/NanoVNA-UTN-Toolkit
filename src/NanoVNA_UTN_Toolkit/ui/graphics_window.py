"""
Graphic view window for NanoVNA devices with dual info panels and cursors.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QSizePolicy, QApplication, QGroupBox, QGridLayout
    , QMenu
)
from PySide6.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

class NanoVNAGraphics(QMainWindow):
    def __init__(self, s11=None, freqs=None):
        super().__init__()

        # --- Menu ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        help_menu = menu_bar.addMenu("Help")

        file_menu.addAction("Open")
        file_menu.addAction("Save")

        # --- Icon ---
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

        self.setWindowTitle("NanoVNA Graphics")
        self.setGeometry(100, 100, 1300, 700)

        # --- Central widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout_vertical = QVBoxLayout(central_widget)
        main_layout_vertical.setContentsMargins(10, 10, 10, 10)
        main_layout_vertical.setSpacing(10)

        # --- Example data ---
        freqs = np.linspace(1e6, 100e6, 101) if freqs is None else freqs
        modulus = 0.5
        phase = -2 * np.pi * freqs / 1e8
        S11 = modulus * np.exp(1j*phase) if s11 is None else s11

        # =================== LEFT PANEL ===================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignTop)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        # --- RF Network ---
        ntw = rf.Network(frequency=freqs, s=S11[:, np.newaxis, np.newaxis], z0=50)

        # --- Smith chart ---
        fig, ax = plt.subplots(figsize=(5,5))
        ntw.plot_s_smith(ax=ax, draw_labels=True)
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addWidget(canvas)

        # --- Smith cursor ---
        cursor_smith, = ax.plot([], [], 'ro', markersize=6)

        # =================== LEFT INFO PANEL ===================
        info_panel_left = QWidget()
        info_layout_left = QGridLayout(info_panel_left)
        info_layout_left.setHorizontalSpacing(20)
        info_layout_left.setVerticalSpacing(5)
        info_panel_left.setLayout(info_layout_left)

        # --- Left Box: S11 ---
        box_s11_left = QGroupBox("S11")
        layout_s11_left = QVBoxLayout()
        box_s11_left.setLayout(layout_s11_left)
        label_freq_left = QLabel("Frequency: -- MHz")
        label_s11_val_left = QLabel("S11: -- + j--")
        label_mag_left = QLabel("|S11|: --")
        label_phase_left = QLabel("Phase: --")
        for lbl in [label_freq_left, label_s11_val_left, label_mag_left, label_phase_left]:
            lbl.setStyleSheet("font-size:14px; padding:1px;")
            layout_s11_left.addWidget(lbl)

        # --- Right Boxes ---
        box_z_left = QGroupBox("Normalized Impedance (Z0=50Ω)")
        layout_z_left = QVBoxLayout()
        box_z_left.setLayout(layout_z_left)
        label_z_left = QLabel("Z: -- + j--")
        label_z_left.setStyleSheet("font-size:14px; padding:1px;")
        layout_z_left.addWidget(label_z_left)

        box_il_left = QGroupBox("Insertion Loss")
        layout_il_left = QVBoxLayout()
        box_il_left.setLayout(layout_il_left)
        label_il_left = QLabel("IL: -- dB")
        label_il_left.setStyleSheet("font-size:14px; padding:1px;")
        layout_il_left.addWidget(label_il_left)

        box_vswr_left = QGroupBox("VSWR")
        layout_vswr_left = QVBoxLayout()
        box_vswr_left.setLayout(layout_vswr_left)
        label_vswr_left = QLabel("VSWR: --")
        label_vswr_left.setStyleSheet("font-size:14px; padding:1px;")
        layout_vswr_left.addWidget(label_vswr_left)

        # --- Add to left grid ---
        info_layout_left.addWidget(box_s11_left, 0, 0, 3, 1)
        info_layout_left.addWidget(box_z_left, 0, 1)
        info_layout_left.addWidget(box_il_left, 1, 1)
        info_layout_left.addWidget(box_vswr_left, 2, 1)

        left_layout.addWidget(info_panel_left)

        # =================== SMITH CURSOR FUNCTION ===================
        def update_smith_cursor(index):
            x = np.real(S11[index])
            y = np.imag(S11[index])
            cursor_smith.set_data([x], [y])

            real_part = np.real(S11[index])
            imag_part = np.imag(S11[index])
            magnitude = abs(S11[index])
            phase_deg = np.angle(S11[index], deg=True)

            label_freq_left.setText(f"Frequency: {freqs[index]*1e-6:.3f} MHz")
            label_s11_val_left.setText(f"S11: {real_part:.3f} {'+' if imag_part>=0 else '-'} j{abs(imag_part):.3f}")
            label_mag_left.setText(f"|S11|: {magnitude:.3f}")
            label_phase_left.setText(f"Phase: {phase_deg:.2f}°")

            z_real = np.real((1+S11[index])/(1-S11[index]))
            z_imag = np.imag((1+S11[index])/(1-S11[index]))
            label_z_left.setText(f"Z: {z_real:.2f} + j{z_imag:.2f}")

            il_db = -20*np.log10(magnitude)
            label_il_left.setText(f"IL: {il_db:.2f} dB")

            vswr_val = (1 + magnitude)/(1 - magnitude) if magnitude < 1 else np.inf
            label_vswr_left.setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")

            fig.canvas.draw_idle()
            slider_smith.set_val(index)

        # --- Smith Slider ---
        slider_ax = fig.add_axes([0.25, 0.05, 0.5, 0.03], facecolor='lightgray')
        slider_smith = Slider(slider_ax, '', 0, len(freqs)-1, valinit=0, valstep=1)
        slider_smith.vline.set_visible(False)
        slider_smith.label.set_visible(False)
        slider_smith.on_changed(lambda val: update_smith_cursor(int(val)))
        update_smith_cursor(0)

        # --- Smith Cursor Drag ---
        dragging_smith = {"active": False}
        def on_mouse_press(event):
            if event.xdata is None or event.ydata is None: return
            contains, _ = cursor_smith.contains(event)
            if contains: dragging_smith["active"] = True
        def on_mouse_release(event):
            dragging_smith["active"] = False
        def on_mouse_move(event):
            if not dragging_smith["active"]: return
            if event.xdata is None or event.ydata is None: return
            mouse_point = event.xdata + 1j*event.ydata
            idx = np.argmin(np.abs(S11 - mouse_point))
            update_smith_cursor(idx)
        fig.canvas.mpl_connect('button_press_event', on_mouse_press)
        fig.canvas.mpl_connect('button_release_event', on_mouse_release)
        fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

        # =================== RIGHT PANEL ===================
        right_panel = QWidget()
        right_layout_main = QVBoxLayout(right_panel)
        right_layout_main.setContentsMargins(10,10,10,10)
        right_layout_main.setSpacing(10)

        # --- S11 Magnitude Plot ---
        fig2, ax2 = plt.subplots(figsize=(4,3)) 
        fig2.subplots_adjust(left=0.22, right=0.8, top=0.8, bottom=0.22)
        line_s11_mod, = ax2.plot(freqs*1e-6, np.abs(S11), 'b.-')
        ax2.set_xlabel("Frequency [MHz]")
        ax2.set_ylabel("|S11|")
        ax2.set_title("S11 Magnitude")
        ax2.grid(True)
        canvas2 = FigureCanvas(fig2)
        canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout_main.addWidget(canvas2, 1)

        # --- Right Cursor ---
        cursor_right, = ax2.plot([], [], 'ro', markersize=6)

        # =================== RIGHT INFO PANEL ===================
        info_panel_right = QWidget()
        info_layout_right = QGridLayout(info_panel_right)
        info_layout_right.setHorizontalSpacing(20)
        info_layout_right.setVerticalSpacing(5)
        info_panel_right.setLayout(info_layout_right)

        box_s11_right = QGroupBox("S11")
        layout_s11_right = QVBoxLayout()
        box_s11_right.setLayout(layout_s11_right)
        label_freq_right = QLabel("Frequency: -- MHz")
        label_s11_val_right = QLabel("S11: -- + j--")
        label_mag_right = QLabel("|S11|: --")
        label_phase_right = QLabel("Phase: --")
        for lbl in [label_freq_right, label_s11_val_right, label_mag_right, label_phase_right]:
            lbl.setStyleSheet("font-size:14px; padding:1px;")
            layout_s11_right.addWidget(lbl)

        box_z_right = QGroupBox("Normalized Impedance (Z0=50Ω)")
        layout_z_right = QVBoxLayout()
        box_z_right.setLayout(layout_z_right)
        label_z_right = QLabel("Z: -- + j--")
        label_z_right.setStyleSheet("font-size:14px; padding:1px;")
        layout_z_right.addWidget(label_z_right)

        box_il_right = QGroupBox("Insertion Loss")
        layout_il_right = QVBoxLayout()
        box_il_right.setLayout(layout_il_right)
        label_il_right = QLabel("IL: -- dB")
        label_il_right.setStyleSheet("font-size:14px; padding:1px;")
        layout_il_right.addWidget(label_il_right)

        box_vswr_right = QGroupBox("VSWR")
        layout_vswr_right = QVBoxLayout()
        box_vswr_right.setLayout(layout_vswr_right)
        label_vswr_right = QLabel("VSWR: --")
        label_vswr_right.setStyleSheet("font-size:14px; padding:1px;")
        layout_vswr_right.addWidget(label_vswr_right)

        info_layout_right.addWidget(box_s11_right, 0, 0, 3, 1)
        info_layout_right.addWidget(box_z_right, 0, 1)
        info_layout_right.addWidget(box_il_right, 1, 1)
        info_layout_right.addWidget(box_vswr_right, 2, 1)

        right_layout_main.addWidget(info_panel_right)

        # =================== RIGHT CURSOR FUNCTION ===================
        def update_right_cursor(index):
            x = freqs[index]*1e-6
            y = abs(S11[index])
            cursor_right.set_data([x], [y])

            real_part = np.real(S11[index])
            imag_part = np.imag(S11[index])
            magnitude = abs(S11[index])
            phase_deg = np.angle(S11[index], deg=True)

            label_freq_right.setText(f"Frequency: {freqs[index]*1e-6:.3f} MHz")
            label_s11_val_right.setText(f"S11: {real_part:.3f} {'+' if imag_part>=0 else '-'} j{abs(imag_part):.3f}")
            label_mag_right.setText(f"|S11|: {magnitude:.3f}")
            label_phase_right.setText(f"Phase: {phase_deg:.2f}°")

            z_real = np.real((1+S11[index])/(1-S11[index]))
            z_imag = np.imag((1+S11[index])/(1-S11[index]))
            label_z_right.setText(f"Z: {z_real:.2f} + j{z_imag:.2f}")

            il_db = -20*np.log10(magnitude)
            label_il_right.setText(f"IL: {il_db:.2f} dB")

            vswr_val = (1 + magnitude)/(1 - magnitude) if magnitude < 1 else np.inf
            label_vswr_right.setText(f"VSWR: {vswr_val:.2f}" if np.isfinite(vswr_val) else "VSWR: ∞")

            fig2.canvas.draw_idle()
            slider_right.set_val(index)

        # --- Right Slider ---
        slider_ax2 = fig2.add_axes([0.25, 0.05, 0.5, 0.03], facecolor='lightgray')
        slider_right = Slider(slider_ax2, '', 0, len(freqs)-1, valinit=0, valstep=1)
        slider_right.vline.set_visible(False)
        slider_right.label.set_visible(False)
        slider_right.on_changed(lambda val: update_right_cursor(int(val)))
        
        update_right_cursor(0)

        # --- Right Cursor Drag ---
        dragging_right = {"active": False}

        def on_mouse_press_right(event):
            if event.xdata is None or event.ydata is None:
                return
            contains, _ = cursor_right.contains(event)
            if contains:
                dragging_right["active"] = True

        def on_mouse_release_right(event):
            dragging_right["active"] = False

        def on_mouse_move_right(event):
            if not dragging_right["active"]:
                return
            if event.xdata is None or event.ydata is None:
                return
            # buscamos índice por frecuencia, no solo por magnitud
            freq_mhz = event.xdata
            idx = np.argmin(np.abs(freqs*1e-6 - freq_mhz))
            update_right_cursor(idx)

        fig2.canvas.mpl_connect('button_press_event', on_mouse_press_right)
        fig2.canvas.mpl_connect('button_release_event', on_mouse_release_right)
        fig2.canvas.mpl_connect('motion_notify_event', on_mouse_move_right)


        # =================== PANELS LAYOUT ===================
        panels_layout = QHBoxLayout()
        panels_layout.addWidget(left_panel, 1)
        panels_layout.addWidget(right_panel, 1)
        main_layout_vertical.addLayout(panels_layout)

        # =================== Buttons below all, centered ===================
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)  # vertical layout
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(10)

        # --- Top row: Calibration y Preferences ---
        top_buttons_widget = QWidget()
        top_buttons_layout = QHBoxLayout(top_buttons_widget)
        top_buttons_layout.setAlignment(Qt.AlignCenter)
        top_buttons_layout.setSpacing(20)

        # --- Calibration Wizard Button ---
        btn_calibration = QPushButton("Calibration Wizard")
        btn_calibration.clicked.connect(self.open_calibration_wizard)
     
        top_buttons_layout.addWidget(btn_calibration)

        # --- Preferences Button ---
        btn_preferences = QPushButton("Preferences")
        top_buttons_layout.addWidget(btn_preferences)

        buttons_layout.addWidget(top_buttons_widget)

        # --- Bottom: Console button ---
        console_btn_final = QPushButton("Console")
        console_btn_final.setStyleSheet("background-color: black; color: white;")
        buttons_layout.addWidget(console_btn_final)

        main_layout_vertical.addWidget(buttons_widget)

    # =================== CALIBRATION WIZARD FUNCTION ===================

    def open_calibration_wizard(self):
        from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
        self.wizard_window = CalibrationWizard()
        self.wizard_window.show()
        self.close()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        view_menu = menu.addAction("View")
        menu.addAction("Copiar")
        menu.addAction("Pegar")
        menu.addAction("Eliminar")
        menu = menu.exec(event.globalPos())

        if menu == view_menu:
            self.open_view()

    def open_view(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.view_window import View
        self.view_window = View()
        self.view_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NanoVNAGraphics()
    window.show()
    sys.exit(app.exec())
