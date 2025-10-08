import sys
import logging
import os
from shiboken6 import isValid
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QMessageBox
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, QSettings
from PySide6.QtCore import QSettings as QtSettings
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QComboBox, QSpacerItem, 
                               QSizePolicy, QProgressBar, QMessageBox, QInputDialog)

# Import NanoVNAGraphics for the final step
try:
    from NanoVNA_UTN_Toolkit.ui.graphics_window import NanoVNAGraphics
except ImportError as e:
    logging.error("Failed to import NanoVNAGraphics: %s", e)
    NanoVNAGraphics = None  # Safe fallback

# Import calibration data storage
try:
    from NanoVNA_UTN_Toolkit.calibration.calibration_manager import OSMCalibrationManager
except ImportError as e:
    logging.error("Failed to import OSMCalibrationManager: %s", e)
    OSMCalibrationManager = None

import numpy as np
import skrf as rf
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D

class CalibrationWizard(QMainWindow):
    def __init__(self, vna_device=None):
        super().__init__()

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.Format.IniFormat)

        # QWidget
        background_color = settings.value("Dark_Light/QWidget/background-color", "#3a3a3a")

        # QTabWidget pane
        tabwidget_pane_bg = settings.value("Dark_Light/QTabWidget_pane/background-color", "#3b3b3b")

        # QTabBar
        tabbar_bg = settings.value("Dark_Light/QTabBar/background-color", "#2b2b2b")
        tabbar_color = settings.value("Dark_Light/QTabBar/color", "white")
        tabbar_padding = settings.value("Dark_Light/QTabBar/padding", "5px 12px")
        tabbar_border = settings.value("Dark_Light/QTabBar/border", "none")
        tabbar_border_tl_radius = settings.value("Dark_Light/QTabBar/border-top-left-radius", "6px")
        tabbar_border_tr_radius = settings.value("Dark_Light/QTabBar/border-top-right-radius", "6px")

        # QTabBar selected
        tabbar_selected_bg = settings.value("Dark_Light/QTabBar_selected/background-color", "#4d4d4d")
        tabbar_selected_color = settings.value("Dark_Light/QTabBar/color", "white")

        # QSpinBox
        spinbox_bg = settings.value("Dark_Light/QSpinBox/background-color", "#3b3b3b")
        spinbox_color = settings.value("Dark_Light/QSpinBox/color", "white")
        spinbox_border = settings.value("Dark_Light/QSpinBox/border", "1px solid white")
        spinbox_border_radius = settings.value("Dark_Light/QSpinBox/border-radius", "8px")

        # QGroupBox title
        groupbox_title_color = settings.value("Dark_Light/QGroupBox_title/color", "white")

        # QLabel
        label_color = settings.value("Dark_Light/QLabel/color", "white")

        # QLineEdit
        lineedit_bg = settings.value("Dark_Light/QLineEdit/background-color", "#3b3b3b")
        lineedit_color = settings.value("Dark_Light/QLineEdit/color", "white")
        lineedit_border = settings.value("Dark_Light/QLineEdit/border", "1px solid white")
        lineedit_border_radius = settings.value("Dark_Light/QLineEdit/border-radius", "6px")
        lineedit_padding = settings.value("Dark_Light/QLineEdit/padding", "4px")
        lineedit_focus_bg = settings.value("Dark_Light/QLineEdit_focus/background-color", "#454545")
        lineedit_focus_border = settings.value("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")

        # QPushButton
        pushbutton_bg = settings.value("Dark_Light/QPushButton/background-color", "#3b3b3b")
        pushbutton_color = settings.value("Dark_Light/QPushButton/color", "white")
        pushbutton_border = settings.value("Dark_Light/QPushButton/border", "1px solid white")
        pushbutton_border_radius = settings.value("Dark_Light/QPushButton/border-radius", "6px")
        pushbutton_padding = settings.value("Dark_Light/QPushButton/padding", "4px 10px")
        pushbutton_hover_bg = settings.value("Dark_Light/QPushButton_hover/background-color", "#4d4d4d")
        pushbutton_pressed_bg = settings.value("Dark_Light/QPushButton_pressed/background-color", "#5c5c5c")

        # QMenu
        menu_bg = settings.value("Dark_Light/QMenu/background", "#3a3a3a")
        menu_color = settings.value("Dark_Light/QMenu/color", "white")
        menu_border = settings.value("Dark_Light/QMenu/border", "1px solid #3b3b3b")
        menu_item_selected_bg = settings.value("Dark_Light/QMenu::item:selected/background-color", "#4d4d4d")

        # QMenuBar
        menu_item_color = settings.value("Dark_Light/QMenu_item_selected/background-color", "4d4d4d")
        menubar_bg = settings.value("Dark_Light/QMenuBar/background-color", "#3a3a3a")
        menubar_color = settings.value("Dark_Light/QMenuBar/color", "white")
        menubar_item_bg = settings.value("Dark_Light/QMenuBar_item/background", "transparent")
        menubar_item_color = settings.value("Dark_Light/QMenuBar_item/color", "white")
        menubar_item_padding = settings.value("Dark_Light/QMenuBar_item/padding", "4px 10px")
        menubar_item_selected_bg = settings.value("Dark_Light/QMenuBar_item_selected/background-color", "#4d4d4d")

        # QCombo

        color_text_QCombo = settings.value("Dark_Light/QComboBox/color", "white")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
            }}
            QTabWidget::pane {{
                background-color: {tabwidget_pane_bg}; 
            }}
            QTabBar::tab {{
                background-color: {tabbar_bg}; 
                color: {tabbar_color};
                padding: {tabbar_padding};
                border: {tabbar_border}; 
                border-top-left-radius: {tabbar_border_tl_radius};
                border-top-right-radius: {tabbar_border_tr_radius};
            }}
            QTabBar::tab:selected {{
                background-color: {tabbar_selected_bg};  
                color: {tabbar_selected_color};
            }}
            QSpinBox {{
                background-color: {spinbox_bg};
                color: {spinbox_color};
                border: {spinbox_border};
                border-radius: {spinbox_border_radius};
            }}
            QGroupBox:title {{
                color: {groupbox_title_color};  
            }}
            QLabel {{
                color: {label_color};  
            }}
            QLineEdit {{
                background-color: {lineedit_bg};
                color: {lineedit_color};
                border: {lineedit_border};
                border-radius: {lineedit_border_radius};
                padding: {lineedit_padding};
            }}
            QLineEdit:focus {{
                background-color: {lineedit_focus_bg};
                border: {lineedit_focus_border};
            }}
            QPushButton {{
                background-color: {pushbutton_bg};
                color: {pushbutton_color};
                border: {pushbutton_border};
                border-radius: {pushbutton_border_radius};
                padding: {pushbutton_padding};
            }}
            QPushButton:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pushbutton_pressed_bg};
            }}
            QMenuBar {{
                background-color: {menubar_bg};
                color: {menubar_color};
            }}
            QMenuBar::item {{
                background: {menubar_item_bg};
                color: {menubar_item_color};
                padding: {menubar_item_padding};
            }}
            QMenuBar::item:selected {{
                background: {menubar_item_selected_bg};
            }}
            QMenu {{
                background-color: {menu_bg};
                color: {menu_color};
                border: {menu_border};
            }}
            QMenu::item:selected {{
                background-color: {menu_item_color};
            }}
            QComboBox {{
                color: black;                 
                background-color: white;
                border: 1px solid #5f5f5f;
                border-radius: 5px;
                padding-left: 5px;            
            }}
            QComboBox QAbstractItemView {{
                color: black;
                background-color: white;             
                selection-background-color: lightgray; 
                selection-color: black;
            }}
            QComboBox:focus {{
                background-color: white;
            }}
            QComboBox::placeholder {{
                color: lightgray;
            }}
        """)

        self.setWindowTitle("Calibration Wizard")
        self.setGeometry(150, 150, 700, 500)

        icon_path = "icon.ico"
        self.setWindowIcon(QIcon(icon_path))

        self.vna_device = vna_device
        
        # Initialize OSM calibration storage with new manager
        if OSMCalibrationManager:
            self.osm_calibration = OSMCalibrationManager()
            if vna_device and hasattr(vna_device, 'name'):
                self.osm_calibration.device_name = vna_device.name
            logging.info("[CalibrationWizard] OSM calibration manager initialized")
        else:
            self.osm_calibration = None
            logging.warning("[CalibrationWizard] OSMCalibrationManager not available")
        
        # Store measured data state for UI consistency
        self.measured_data = {
            'open': None,
            'short': None, 
            'match': None
        }
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Content area (this is where screens are placed)
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # Step tracking
        self.current_step = 0
        self.selected_method = None

        # Bottom button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 10, 0, 0)

        # Back button (left)
        self.back_button = QPushButton("◀◀")
        self.back_button.setFixedSize(100, 30)
        self.back_button.setStyleSheet("font-size: 14px;")
        self.back_button.clicked.connect(self.previous_step)
        self.button_layout.addWidget(self.back_button)

        self.button_layout.addStretch()

        # Save Calibration button (will be shown only in final step)
        self.save_button = QPushButton("Save Calibration")
        self.save_button.setFixedSize(130, 30)
        self.save_button.setStyleSheet("font-size: 12px; background-color: #4CAF50; color: white; font-weight: bold;")
        self.save_button.clicked.connect(self.save_calibration_dialog)
        self.save_button.setVisible(False)  # Hidden by default
        self.button_layout.addWidget(self.save_button)

        # Next button (right)
        self.next_button = QPushButton("▶▶")
        self.next_button.setFixedSize(100, 30)
        self.next_button.setStyleSheet("font-size: 14px;")
        self.next_button.clicked.connect(self.next_step)
        self.next_button.setEnabled(False)  # start locked until user selects
        self.button_layout.addWidget(self.next_button)

        self.main_layout.addLayout(self.button_layout)

        # Show first screen
        self.show_first_screen()

    # --- layout clearing helpers ------------------------------------------------
    def clear_layout(self, layout):
        """Recursively remove widgets and nested layouts from a layout."""
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            elif child_layout:
                # Recursively clear nested layout
                self.clear_layout(child_layout)

    def clear_main_content(self):
        """Clear everything inside content_layout and remove old panels if exist."""
        self.clear_content()  # limpia content_layout
        # elimina widgets antiguos si existen
        if hasattr(self, "left_panel_widget") and self.left_panel_widget:
            if isValid(self.left_panel_widget):
                self.left_panel_widget.setParent(None)
            self.left_panel_widget = None

        if hasattr(self, "right_panel_widget") and self.right_panel_widget:
            if isValid(self.right_panel_widget):
                self.right_panel_widget.setParent(None)
            self.right_panel_widget = None

    def clear_content(self):
        """Clear everything inside content_layout (handles nested layouts)."""
        self.clear_layout(self.content_layout)

    # --- screens --------------------------------------------------------------
    def show_first_screen(self):
        """Initial screen: Calibration Methods dropdown (aligned near top)."""
        self.clear_content()

        # Reset selection state
        self.selected_method = None
        self.next_button.setEnabled(False)

        # --- 🔴 FIX: Reset button when returning to start ---
        self.next_button.setText("▶▶")
        try:
            self.next_button.clicked.disconnect()
        except Exception:
            pass
        self.next_button.clicked.connect(self.next_step)

        # Container que mantiene el contenido arriba
        top_container = QVBoxLayout()
        top_container.setAlignment(Qt.AlignTop)
        top_container.addSpacing(30)

        label = QLabel("Calibration Methods:")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        label.setAlignment(Qt.AlignLeft)

        self.freq_dropdown = QComboBox()
        self.freq_dropdown.setEditable(False)

        # Placeholder
        self.freq_dropdown.addItem("Select Method")
        item = self.freq_dropdown.model().item(0)
        item.setEnabled(False)
        placeholder_color = QColor(120, 120, 120)
        item.setForeground(placeholder_color)

        methods = [
            "OSM (Open - Short - Match)",
            "Normalization",
            "1-Port+N",
            "Enhanced-Response",
            "1-Path 2-Port"
        ]
        self.freq_dropdown.addItems(methods)
        self.freq_dropdown.activated.connect(self.on_method_activated)

        top_container.addWidget(label)
        top_container.addWidget(self.freq_dropdown)

        self.content_layout.addLayout(top_container)

        # Hide back button
        self.back_button.setVisible(False)
        self.current_step = 0


    def on_method_activated(self, index):
        """Called when user selects a method from the combo box."""

        if index == 0:
            self.selected_method = None
            self.next_button.setEnabled(False)
        else:
            self.selected_method = self.freq_dropdown.itemText(index)
            self.next_button.setEnabled(True)

    # --- Step definitions (each step is unique) ---------------------------------
    def step_OSM_OPEN(self):
        label = QLabel("Step 1: OPEN (OSM)")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    def step_OSM_SHORT(self):
        label = QLabel("Step 2: SHORT (OSM)")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    def step_OSM_MATCH(self):
        label = QLabel("Step 3: MATCH (OSM)")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    def step_Normalization(self):
        label = QLabel("Step 1: Normalization")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    def step_OnePortN_OPEN(self):
        label = QLabel("Step 1: OPEN (1-Port+N)")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    def step_OnePortN_SHORT(self):
        label = QLabel("Step 2: SHORT (1-Port+N)")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    def step_OnePortN_MATCH(self):
        label = QLabel("Step 3: MATCH (1-Port+N)")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    def step_OnePortN_THRU(self):
        label = QLabel("Step 4: THRU (1-Port+N)")
        label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        return label

    # You can add unique steps for Enhanced-Response and 1-Path 2-Port in the same way

    # --- Get steps for current method -----------------------------------------
    def get_steps_for_method(self):
        """Return a list of unique step methods for the selected method."""
        if self.selected_method == "OSM (Open - Short - Match)":
            return [
                self.step_OSM_OPEN,
                self.step_OSM_SHORT,
                self.step_OSM_MATCH
            ]
        elif self.selected_method == "Normalization":
            return [self.step_Normalization]
        elif self.selected_method == "1-Port+N":
            return [
                self.step_OnePortN_OPEN,
                self.step_OnePortN_SHORT,
                self.step_OnePortN_MATCH,
                self.step_OnePortN_THRU
            ]
        elif self.selected_method == "Enhanced-Response":
            return [
                lambda: QLabel("Step 1: OPEN (Enhanced-Response)", alignment=Qt.AlignRight | Qt.AlignTop),
                lambda: QLabel("Step 2: SHORT (Enhanced-Response)", alignment=Qt.AlignRight | Qt.AlignTop),
                lambda: QLabel("Step 3: MATCH (Enhanced-Response)", alignment=Qt.AlignRight | Qt.AlignTop),
                lambda: QLabel("Step 4: THRU (Enhanced-Response)", alignment=Qt.AlignRight | Qt.AlignTop)
            ]
        elif self.selected_method == "1-Path 2-Port":
            return [
                lambda: QLabel("Step 1: OPEN (1-Path 2-Port)", alignment=Qt.AlignRight | Qt.AlignTop),
                lambda: QLabel("Step 2: SHORT (1-Path 2-Port)", alignment=Qt.AlignRight | Qt.AlignTop),
                lambda: QLabel("Step 3: MATCH (1-Path 2-Port)", alignment=Qt.AlignRight | Qt.AlignTop),
                lambda: QLabel("Step 4: THRU (1-Path 2-Port)", alignment=Qt.AlignRight | Qt.AlignTop)
            ]
        else:
            return []

    def show_step_screen(self, step):
        """Show the given step with left info panel and right Smith chart."""
        self.clear_main_content()
        steps = self.get_steps_for_method()

        # Pantalla final
        if step > len(steps):
            final_label = QLabel("Calibration Finished!")
            final_label.setAlignment(Qt.AlignCenter)
            final_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            self.content_layout.addWidget(final_label)
            self.back_button.setVisible(True)
            self.next_button.setVisible(False)
            self.current_step = step
            return

        # Panel izquierdo
        self.left_panel_widget = QWidget()
        left_layout = QVBoxLayout(self.left_panel_widget)
        left_layout.setAlignment(Qt.AlignTop)
        info_label = QLabel(f"Method: {self.selected_method}\nStep {step}/{len(steps)}")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 8px;")
        left_layout.addWidget(info_label)
        
        # Determine which standard is being measured for OSM
        step_name = "UNKNOWN"
        if self.selected_method == "OSM (Open - Short - Match)":
            if step == 1:
                step_name = "OPEN"
            elif step == 2:
                step_name = "SHORT"
            elif step == 3:
                step_name = "MATCH"
        
        # Check if this standard has already been measured
        is_measured = False
        if self.osm_calibration:
            is_measured = self.osm_calibration.is_standard_measured(step_name.lower())
        
        # Instrucciones del paso actual
        if is_measured:
            instruction_text = f"{step_name} standard already measured ✓"
            instruction_style = "font-size: 14px; padding: 8px; color: lightgreen;"
        else:
            instruction_text = f"Connect {step_name} standard and press Measure"
            instruction_style = "font-size: 14px; padding: 8px; color: yellow;"
            
        instruction_label = QLabel(instruction_text)
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setStyleSheet(instruction_style)
        instruction_label.setWordWrap(True)
        left_layout.addWidget(instruction_label)
        
        # Button to perform measurement
        measure_button = QPushButton("Re-measure" if is_measured else "Measure")
        measure_button.setStyleSheet("font-size: 16px; padding: 10px; font-weight: bold;")
        measure_button.clicked.connect(lambda: self.perform_calibration_measurement(step, step_name))
        left_layout.addWidget(measure_button)
        
        # Status label to show measurement state
        if is_measured:
            status_text = f"{step_name} measurement complete"
            status_style = "font-size: 12px; padding: 4px; color: lightgreen;"
        else:
            status_text = "Ready to measure"
            status_style = "font-size: 12px; padding: 4px;"
            
        self.status_label = QLabel(status_text)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(status_style)
        left_layout.addWidget(self.status_label)
        
        # Measurement completion status
        if self.osm_calibration and self.selected_method == "OSM (Open - Short - Match)":
            status = self.osm_calibration.get_completion_status()
            
            status_label = QLabel("Calibration Status:")
            status_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
            left_layout.addWidget(status_label)
            
            # Store references to status widgets for later updates
            self.calibration_status_widgets = {}
            
            for standard, completed in status.items():
                if standard == 'complete':
                    continue
                icon = "✓" if completed else "✗"
                color = "green" if completed else "red"
                status_text = 'Completed' if completed else 'Pending'
                label = QLabel(f"{icon} {standard.upper()}: {status_text}")
                label.setStyleSheet(f"font-size: 14px; color: {color}; margin-left: 10px;")
                left_layout.addWidget(label)
                
                # Store reference for later updates
                self.calibration_status_widgets[standard] = label
        
        left_layout.addStretch()

        # Panel derecho: Smith chart con canvas de matplotlib
        self.right_panel_widget = QWidget()
        right_layout = QVBoxLayout(self.right_panel_widget)

        fig = Figure(figsize=(5, 4), facecolor='white')
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Store reference to figure and canvas for later updates
        self.current_fig = fig
        self.current_canvas = canvas
        self.current_ax = ax

        # Create a Network placeholder
        freqs = np.linspace(1e6, 1e9, 101)
        s = np.zeros((len(freqs), 1, 1), dtype=complex)
        ntw = rf.Network(frequency=freqs, s=s, z0=50)

                # Draw clean Smith chart with reference circles
        ntw.plot_s_smith(ax=ax, draw_labels=True, show_legend=False)

        # Add blue line for data visualization
        ax.plot(np.real(ntw.s[:,0,0]), np.imag(ntw.s[:,0,0]), color='blue', lw=2)
        ax.legend([Line2D([0],[0], color='blue')], ["S11"], loc='upper left', bbox_to_anchor=(-0.17, 1.14))

        # Remove Re/Im ticks
        ax.set_xticks([])
        ax.set_yticks([])

        right_layout.addWidget(canvas)

        # Layout horizontal
        panel_row = QHBoxLayout()
        panel_row.addWidget(self.left_panel_widget, 2)
        panel_row.addWidget(self.right_panel_widget, 2)
        self.content_layout.addLayout(panel_row)

        # Show only the measurement for the current step if it exists
        if self.osm_calibration and self.selected_method == "OSM (Open - Short - Match)":
            self.show_current_step_measurement(step)

        self.current_step = step
        self.back_button.setVisible(step > 0)

        try:
            self.next_button.clicked.disconnect(self.next_step)
        except (TypeError, RuntimeError):
            pass
        try:
            self.next_button.clicked.disconnect(self.finish_wizard)
        except (TypeError, RuntimeError):
            pass

        if step == len(steps):
            # Always show save button in final step for OSM calibration
            if self.osm_calibration and self.selected_method == "OSM (Open - Short - Match)":
                self.save_button.setVisible(True)
            else:
                self.save_button.setVisible(False)
                
            self.next_button.setText("Finish")
            try:
                self.next_button.clicked.disconnect()
            except Exception:
                pass
            self.next_button.clicked.connect(self.finish_wizard)
        else:
            self.save_button.setVisible(False)  # Hide save button in non-final steps
            self.next_button.setText("▶▶")
            try:
                self.next_button.clicked.disconnect()
            except Exception:
                pass
            self.next_button.clicked.connect(self.next_step)

    # --- navigation handlers -------------------------------------------------
    def next_step(self):
        if self.current_step == 0:
            if not self.selected_method:
                return
            self.show_step_screen(1)
        else:
            steps = self.get_steps_for_method()
            if self.current_step < len(steps):
                self.show_step_screen(self.current_step + 1)
            else:
                self.show_step_screen(self.current_step + 1)

    def previous_step(self):
        if self.current_step <= 1:
            self.show_first_screen() 
            self.next_button.setEnabled(False)  
        else:
            self.show_step_screen(self.current_step - 1)

    def finish_wizard(self):
        """Finish wizard and open graphics window"""
        logging.info("Calibration wizard completed - opening graphics window")
        self.open_graphics_window()

    def perform_calibration_measurement(self, step, standard_name):
        """Perform sweep measurement for calibration standard."""
        logging.info(f"[CalibrationWizard] Starting measurement for {standard_name}")
        
        # Check if we have a device or need to simulate
        device_available = self.vna_device and hasattr(self.vna_device, 'connected')
        
        if not device_available:
            # Simulate measurement when no device is available
            logging.info("[CalibrationWizard] No device available, simulating measurement...")
            
            try:
                # Update status
                self.status_label.setText(f"Simulating {standard_name} measurement...")
                self.status_label.setStyleSheet("font-size: 12px; padding: 4px; color: orange;")
                QApplication.processEvents()
                
                # Generate simulated data
                freqs = np.linspace(50e3, 6e9, 101)  # 50 kHz to 6 GHz, 101 points
                
                # Generate characteristic responses for each standard
                if standard_name == "OPEN":
                    # Open circuit: high reflection, phase changes with frequency
                    s11 = 0.95 * np.exp(1j * np.linspace(0, 4*np.pi, len(freqs)))
                elif standard_name == "SHORT":
                    # Short circuit: high reflection, opposite phase to open
                    s11 = -0.95 * np.exp(1j * np.linspace(0, -4*np.pi, len(freqs)))
                elif standard_name == "MATCH":
                    # Matched load: low reflection
                    s11 = 0.05 * np.exp(1j * np.linspace(0, np.pi, len(freqs)))
                else:
                    # Default response
                    s11 = 0.1 * np.exp(1j * np.linspace(0, 2*np.pi, len(freqs)))
                
                # Save simulated data in calibration structure
                if self.osm_calibration:
                    if standard_name == "OPEN":
                        self.osm_calibration.set_measurement("open", freqs, s11)
                    elif standard_name == "SHORT":
                        self.osm_calibration.set_measurement("short", freqs, s11)
                    elif standard_name == "MATCH":
                        self.osm_calibration.set_measurement("match", freqs, s11)
                    
                    # Show completion status
                    status = self.osm_calibration.get_completion_status()
                    logging.info(f"[CalibrationWizard] Calibration status after simulation: {status}")
                    
                    # Update the status display immediately after measurement
                    self.update_calibration_status_display()
                
                # Update Smith chart with simulated data
                self.update_smith_chart(freqs, s11, standard_name)
                
                # Update status
                self.status_label.setText(f"{standard_name} simulated successfully!")
                self.status_label.setStyleSheet("font-size: 12px; padding: 4px; color: lightgreen;")
                
                logging.info(f"[CalibrationWizard] Simulated measurement for {standard_name} completed successfully")
                return
                
            except Exception as e:
                error_msg = f"Error during simulation: {str(e)}"
                logging.error(f"[CalibrationWizard] {error_msg}")
                QMessageBox.critical(self, "Simulation Error", error_msg)
                self.status_label.setText("Simulation failed!")
                self.status_label.setStyleSheet("font-size: 12px; padding: 4px; color: red;")
                return
        
        
        # Real device measurement
        if not self.vna_device.connected():
            logging.warning("[CalibrationWizard] Device not connected, attempting to connect...")
            try:
                self.vna_device.connect()
                if not self.vna_device.connected():
                    QMessageBox.warning(self, "Connection Failed", "Could not connect to VNA device.")
                    return
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", f"Failed to connect: {str(e)}")
                return

        try:
            # Update status
            self.status_label.setText(f"Measuring {standard_name}...")
            self.status_label.setStyleSheet("font-size: 12px; padding: 4px; color: orange;")
            QApplication.processEvents()
            
            # Get full frequency range from device
            if hasattr(self.vna_device, 'sweep_max_freq_hz'):
                stop_freq = self.vna_device.sweep_max_freq_hz
            else:
                stop_freq = 6000000000  # 6 GHz default
            
            start_freq = 50000  # 50 kHz
            
            # Use maximum number of available points
            if hasattr(self.vna_device, 'sweep_points_max'):
                num_points = self.vna_device.sweep_points_max
            else:
                num_points = 101  # Default
            
            logging.info(f"[CalibrationWizard] Sweep config: {start_freq/1e6:.3f} - {stop_freq/1e6:.3f} MHz, {num_points} points")
            
            # Configure sweep
            self.vna_device.datapoints = num_points
            self.vna_device.setSweep(start_freq, stop_freq)
            
            # Perform measurements
            logging.info(f"[CalibrationWizard] Reading frequencies...")
            freqs_data = self.vna_device.read_frequencies()
            freqs = np.array(freqs_data)
            
            logging.info(f"[CalibrationWizard] Reading S11 data...")
            s11_data = self.vna_device.readValues("data 0")
            s11 = np.array(s11_data)
            
            logging.info(f"[CalibrationWizard] Got {len(freqs)} points")
            
            # Save data in calibration structure
            if self.osm_calibration:
                if standard_name == "OPEN":
                    self.osm_calibration.set_measurement("open", freqs, s11)
                elif standard_name == "SHORT":
                    self.osm_calibration.set_measurement("short", freqs, s11)
                elif standard_name == "MATCH":
                    self.osm_calibration.set_measurement("match", freqs, s11)
                
                # Show completion status
                status = self.osm_calibration.get_completion_status()
                logging.info(f"[CalibrationWizard] Calibration status: {status}")
                
                # Update the status display immediately after measurement
                self.update_calibration_status_display()
                
                # Update UI state after measurement
                self.status_label.setText(f"{standard_name} measurement complete")
                self.status_label.setStyleSheet("font-size: 12px; padding: 4px; color: lightgreen;")
            
            # Update Smith chart with measured data
            self.update_smith_chart(freqs, s11, standard_name)
            
            # Update status
            self.status_label.setText(f"{standard_name} measured successfully!")
            self.status_label.setStyleSheet("font-size: 12px; padding: 4px; color: lightgreen;")
            
            logging.info(f"[CalibrationWizard] Measurement for {standard_name} completed successfully")
            
        except Exception as e:
            error_msg = f"Error during measurement: {str(e)}"
            logging.error(f"[CalibrationWizard] {error_msg}")
            QMessageBox.critical(self, "Measurement Error", error_msg)
            self.status_label.setText("Measurement failed!")
            self.status_label.setStyleSheet("font-size: 12px; padding: 4px; color: red;")
    
    def save_calibration_dialog(self):
        """Shows a dialog to save the calibration without advancing to graphics window"""
        if not self.osm_calibration:
            return
            
        # Check which measurements are available
        status = self.osm_calibration.get_completion_status()
        measured_standards = [std for std, completed in status.items() if completed and std != 'complete']
        
        if not measured_standards:
            QMessageBox.warning(
                self, 
                "No Measurements", 
                "No calibration measurements have been taken yet.\nPlease perform at least one measurement before saving."
            )
            return
            
        # Dialog to enter calibration name
        from PySide6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(
            self, 
            'Save Calibration', 
            f'Enter calibration name:\n\nMeasurements to save: {", ".join(measured_standards).upper()}',
            text=f'OSM_Calibration_{self.get_current_timestamp()}'
        )
        
        if ok and name:
            try:
                # Save calibration (it will save only the available measurements)
                success = self.osm_calibration.save_calibration_file(name)
                if success:
                    # Show success message
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Calibration '{name}' saved successfully!\n\nSaved measurements: {', '.join(measured_standards).upper()}\n\nFiles saved in:\n- Touchstone format\n- .cal format\n\nUse 'Finish' button to continue to graphics window."
                    )
                    
                    # Stay in wizard - do not advance to graphics window
                    logging.info(f"Calibration '{name}' saved successfully - staying in wizard")
                    
                else:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "Error", "Failed to save calibration")
                    
            except Exception as e:
                logging.error(f"[CalibrationWizard] Error saving calibration: {e}")
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Error saving calibration: {str(e)}")
    
    def get_current_timestamp(self):
        """Generate timestamp for filenames"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def update_calibration_status_display(self):
        """Update the calibration status display in the final step"""
        # Only update if we're in the final step and have the status widgets
        if hasattr(self, 'calibration_status_widgets') and self.osm_calibration:
            status = self.osm_calibration.get_completion_status()
            
            # Update each status widget
            for standard, widget in self.calibration_status_widgets.items():
                if standard in status:
                    completed = status[standard]
                    icon = "✓" if completed else "✗"
                    color = "green" if completed else "red"
                    status_text = 'Completed' if completed else 'Pending'
                    widget.setText(f"{icon} {standard.upper()}: {status_text}")
                    widget.setStyleSheet(f"font-size: 14px; color: {color}; margin-left: 10px;")
    
    def open_graphics_window(self):
        """Open the NanoVNA Graphics window and update calibration info"""
        try:
            logging.info("Opening NanoVNAGraphics window after calibration completion")
            
            if NanoVNAGraphics:
                # Create graphics window with VNA device if available
                if self.vna_device:
                    graphics_window = NanoVNAGraphics(vna_device=self.vna_device)
                else:
                    graphics_window = NanoVNAGraphics()
                
                # Update calibration label with current method
                try:
                    graphics_window.update_calibration_label_from_method(self.selected_method)
                except Exception as e:
                    logging.error(f"Failed to update calibration label in graphics window: {e}")
                
                # Save calibration configuration to config file
                self._save_calibration_config()
                
                # Show the graphics window
                graphics_window.show()
                logging.info("Graphics window opened successfully")
                
                # Close wizard after opening graphics window
                self.close()
                
            else:
                logging.error("NanoVNAGraphics not available - cannot open graphics window")
                QMessageBox.warning(
                    self, 
                    "Warning", 
                    "Graphics window is not available. Please restart the application."
                )
                
        except Exception as e:
            logging.error(f"Error opening graphics window: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to open graphics window: {str(e)}"
            )
    
    def _save_calibration_config(self):
        """Save calibration configuration to config file"""
        try:
            # Use new calibration structure
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_dir = os.path.join(base_dir, "calibration", "config")
            os.makedirs(config_dir, exist_ok=True)

            config_path = os.path.join(config_dir, "calibration_config.ini")
            settings = QSettings(config_path, QSettings.Format.IniFormat)

            settings.setValue("Calibration/Method", self.selected_method)

            if self.selected_method == "OSM (Open - Short - Match)":
                parameter = "S11"
            elif self.selected_method == "Normalization":
                parameter = "S21"
            else:
                parameter = "S11, S21"

            settings.setValue("Calibration/Parameter", parameter)
            settings.sync()

            logging.info(f"Calibration method saved: {self.selected_method}")
            logging.info(f"Calibrated parameter saved: {parameter}")
            
        except Exception as e:
            logging.error(f"Failed to save calibration config: {e}")
    
    def show_existing_measurements_on_chart(self):
        """Show all existing measurements on Smith chart to preserve state"""
        if not self.osm_calibration or not hasattr(self, 'current_ax'):
            return
            
        try:
            # First clear the axis
            self.current_ax.clear()
            
            # Create an empty base Smith chart
            freqs_base = np.linspace(1e6, 1e9, 101)
            s_base = np.zeros((len(freqs_base), 1, 1), dtype=complex)
            ntw_base = rf.Network(frequency=freqs_base, s=s_base, z0=50)
            ntw_base.plot_s_smith(ax=self.current_ax, draw_labels=True, show_legend=False)
            
            # Colors for each standard
            colors = {'open': 'red', 'short': 'green', 'match': 'blue'}
            legend_lines = []
            legend_labels = []
            
            # Check each standard and plot if it exists
            for standard_name in ['open', 'short', 'match']:
                if self.osm_calibration.is_standard_measured(standard_name):
                    measurement = self.osm_calibration.get_measurement(standard_name)
                    if measurement:
                        freqs, s11 = measurement
                        
                        # Create Network object for this standard
                        ntw_std = rf.Network(frequency=freqs, s=s11[:, np.newaxis, np.newaxis], z0=50)
                        
                        # Plot only the data without reference lines
                        self.current_ax.plot(np.real(s11), np.imag(s11), 'o-',
                                           color=colors[standard_name],
                                           markersize=3, linewidth=2,
                                           label=f'{standard_name.upper()}')
                        
                        # Add to legend
                        from matplotlib.lines import Line2D
                        legend_lines.append(Line2D([0], [0], color=colors[standard_name]))
                        legend_labels.append(f'{standard_name.upper()}')
            
            # Configure Smith chart colors
            for text in self.current_ax.texts:
                text.set_color('black')
            
            for patch in self.current_ax.patches:
                patch.set_edgecolor('gray')   
                patch.set_facecolor("none")    
            
            # Horizontal line at center
            self.current_ax.hlines(0, -1, 1, color='gray', linewidth=1.1, zorder=10)
            
            # Update legend if there are measurements
            if legend_lines:
                self.current_ax.legend(legend_lines, legend_labels, 
                                     loc='upper left', bbox_to_anchor=(-0.17, 1.14))
            
            # Remove ticks
            self.current_ax.set_xticks([])
            self.current_ax.set_yticks([])
            
            # Redraw canvas
            self.current_canvas.draw()
            
        except Exception as e:
            logging.error(f"[CalibrationWizard] Error showing existing measurements: {e}")
    
    def show_current_step_measurement(self, step):
        """Show only the measurement for the current step on Smith chart."""
        if not self.osm_calibration or not hasattr(self, 'current_ax'):
            return
            
        try:
            # First clear the axis
            self.current_ax.clear()
            
            # Create an empty base Smith chart
            freqs_base = np.linspace(1e6, 1e9, 101)
            s_base = np.zeros((len(freqs_base), 1, 1), dtype=complex)
            ntw_base = rf.Network(frequency=freqs_base, s=s_base, z0=50)
            ntw_base.plot_s_smith(ax=self.current_ax, draw_labels=True, show_legend=False)
            
            # Determine which standard corresponds to current step
            step_name = None
            if step == 1:
                step_name = "open"
            elif step == 2:
                step_name = "short"
            elif step == 3:
                step_name = "match"
            
            # Colors for each standard
            colors = {'open': 'red', 'short': 'green', 'match': 'blue'}
            
            # Show only the measurement for the current step if it exists
            if step_name and self.osm_calibration.is_standard_measured(step_name):
                measurement = self.osm_calibration.get_measurement(step_name)
                if measurement:
                    freqs, s11 = measurement
                    
                    # Plot only the data for this step
                    self.current_ax.plot(np.real(s11), np.imag(s11), 'o-',
                                       color=colors[step_name],
                                       markersize=3, linewidth=2,
                                       label=f'{step_name.upper()}')
                    
                    # Add legend for this step only
                    from matplotlib.lines import Line2D
                    self.current_ax.legend([Line2D([0], [0], color=colors[step_name])], 
                                         [f'{step_name.upper()}'], 
                                         loc='upper left', bbox_to_anchor=(-0.17, 1.14))
            
            # Configure Smith chart colors
            for text in self.current_ax.texts:
                text.set_color('black')
            
            for patch in self.current_ax.patches:
                patch.set_edgecolor('gray')   
                patch.set_facecolor("none")    
            
            # Horizontal line at center
            self.current_ax.hlines(0, -1, 1, color='gray', linewidth=1.1, zorder=10)
            
            # Remove ticks
            self.current_ax.set_xticks([])
            self.current_ax.set_yticks([])
            
            # Redraw canvas
            self.current_canvas.draw()
            
        except Exception as e:
            logging.error(f"[CalibrationWizard] Error showing current step measurement: {e}")
    
    def update_smith_chart(self, freqs, s11, standard_name):
        """Update Smith chart with measured calibration data."""
        try:
            if not hasattr(self, 'current_ax') or not self.current_ax:
                logging.warning("[CalibrationWizard] No Smith chart axis available")
                return
            
            # Clear previous plot
            self.current_ax.clear()
            
            # Create Network object for Smith chart (same as in graphics_window.py)
            ntw = rf.Network(frequency=freqs, s=s11[:, np.newaxis, np.newaxis], z0=50)
            
            # Draw Smith chart with reference lines
            ntw.plot_s_smith(ax=self.current_ax, draw_labels=True, show_legend=False)
            
            # Configure custom legend (same as in graphics_window.py)
            from matplotlib.lines import Line2D
            self.current_ax.legend([Line2D([0],[0], color='blue')], [f"S11 - {standard_name}"], 
                                 loc='upper left', bbox_to_anchor=(-0.17, 1.14))
            
            # Configure Smith chart colors
            for text in self.current_ax.texts:
                text.set_color('black')
            
            for patch in self.current_ax.patches:
                patch.set_edgecolor('gray')   
                patch.set_facecolor("none")    
            
            # Horizontal line at center (same as in graphics_window.py)
            self.current_ax.hlines(0, -1, 1, color='gray', linewidth=1.1, zorder=10)
            
            # Update properties of data lines
            for idx, line in enumerate(self.current_ax.lines):
                # Apply blue style to measurement data lines
                try:
                    xdata = line.get_xdata()
                    # If it's a line with significant data, apply style
                    if hasattr(xdata, '__len__') and np.array(xdata).size > 10:
                        line.set_color('blue')
                        line.set_linewidth(2)
                except:
                    # Fallback: apply style to lines that can be modified
                    if hasattr(line, 'set_color') and hasattr(line, 'set_linewidth'):
                        line.set_color('blue')
                        line.set_linewidth(2)
            
            # Remove ticks (same as in initialization)
            self.current_ax.set_xticks([])
            self.current_ax.set_yticks([])
            
            # Redraw canvas
            self.current_canvas.draw()
            
            logging.info(f"[CalibrationWizard] Smith chart updated for {standard_name}")
            
        except Exception as e:
            logging.error(f"[CalibrationWizard] Error updating Smith chart: {e}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = CalibrationWizard()
    wizard.show()
    sys.exit(app.exec())
