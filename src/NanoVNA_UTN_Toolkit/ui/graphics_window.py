"""
Graphic view window for NanoVNA devices with dual info panels and cursors.
"""
import os
import sys
import logging
import numpy as np
import skrf as rf

# Suppress verbose matplotlib logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.getLogger('matplotlib.pyplot').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

from PySide6.QtCore import QTimer, QThread, Qt, QSettings
from PySide6.QtWidgets import (
    QLabel, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QSizePolicy, QApplication, QGroupBox, QGridLayout,
    QMenu, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtGui import QIcon, QPixmap
from .export import ExportDialog

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

try:
    from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_left_panel
    from NanoVNA_UTN_Toolkit.ui.utils.graphics_utils import create_right_panel
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class NanoVNAGraphics(QMainWindow):
    def __init__(self, s11=None, s21=None, freqs=None, left_graph_type="Smith Diagram", left_s_param="S11", vna_device=None):
        super().__init__()

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

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
            QMenu{{
                color_ {menubar_color};
                background-color_ {menu_item_color};
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
        """)

        # Store VNA device reference
        self.vna_device = vna_device
        
        # Log graphics window initialization
        logging.info("[graphics_window.__init__] Initializing graphics window")
        if vna_device:
            device_type = type(vna_device).__name__
            logging.info(f"[graphics_window.__init__] VNA device provided: {device_type}")
        else:
            logging.warning("[graphics_window.__init__] No VNA device provided")

        config = self._load_graph_configuration()

        self.left_graph_type  = config['graph_type_tab1']
        self.left_s_param     = config['s_param_tab1']
        self.right_graph_type = config['graph_type_tab2']
        self.right_s_param    = config['s_param_tab2']

        # --- Marker visibility flags ---
        self.show_marker1 = True
        self.show_marker2 = True

        # --- Menu ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")
        view_menu = menu_bar.addMenu("View")
        sweep_menu = menu_bar.addMenu("Sweep")
        help_menu = menu_bar.addMenu("Help")

        file_menu.addAction("Open")
        file_menu.addAction("Save")
        save_as_action =  file_menu.addAction("Save As")
        save_as_action.triggered.connect(lambda: self.on_save_as())
        
        export_touchstone_action = file_menu.addAction("Export Touchstone Data")
        export_touchstone_action.triggered.connect(lambda: self.export_touchstone_data())

        graphics_markers = edit_menu.addAction("Graphics/Markers")
        graphics_markers.triggered.connect(lambda: self.edit_graphics_markers())

        text_light_dark = settings.value("Dark_Light/text_light_dark", "text_light_dark")

        light_dark_mode = edit_menu.addAction(text_light_dark)

        self.is_dark_mode = settings.value("Dark_Light/is_dark_mode", False, type=bool)

        def toggle_menu_dark_mode():

            ui_dir = os.path.dirname(os.path.dirname(__file__))  
            ruta_ini = os.path.join(ui_dir, "ui","graphics_windows", "ini", "config.ini")

            settings = QSettings(ruta_ini, QSettings.IniFormat)

            if self.is_dark_mode:
                light_dark_mode.setText("Light Mode 🔆")

                # --- QWidget ---
                settings.setValue("Dark_Light/QWidget/background-color", "#7f7f7f")

                # --- Qframe ---
                settings.setValue("Dark_Light/Qframe/background-color", "white")
                settings.setValue("Dark_Light/Qframe/color", "white")

                # --- QTabWidget pane ---
                settings.setValue("Dark_Light/QTabWidget_pane/background-color", "#6f6f6f")

                # --- QTabBar ---
                settings.setValue("Dark_Light/QTabBar/background-color", "#4d4d4d")
                settings.setValue("Dark_Light/QTabBar/color", "white")
                settings.setValue("Dark_Light/QTabBar/padding", "5px 12px")
                settings.setValue("Dark_Light/QTabBar/border", "none")
                settings.setValue("Dark_Light/QTabBar/border-top-left-radius", "6px")
                settings.setValue("Dark_Light/QTabBar/border-top-right-radius", "6px")

                # --- QTabBar selected ---
                settings.setValue("Dark_Light/QTabBar_selected/background-color", "#2b2b2b")
                settings.setValue("Dark_Light/QTabBar_selected/color", "white")

                # --- QSpinBox ---
                settings.setValue("Dark_Light/QSpinBox/color", "black")
                settings.setValue("Dark_Light/QSpinBox/background-color", "white")
                settings.setValue("Dark_Light/QSpinBox/border", "1px solid #5f5f5f")
                settings.setValue("Dark_Light/QSpinBox/border-radius", "8px")

                # --- QGroupBox title ---
                settings.setValue("Dark_Light/QGroupBox_title/color", "white")

                # --- QLabel ---
                settings.setValue("Dark_Light/QLabel/color", "white")

                # --- QLineEdit ---
                settings.setValue("Dark_Light/QLineEdit/background-color", "#6f6f6f")
                settings.setValue("Dark_Light/QLineEdit/color", "white")
                settings.setValue("Dark_Light/QLineEdit/border", "1px solid #5f5f5f")
                settings.setValue("Dark_Light/QLineEdit/border-radius", "6px")
                settings.setValue("Dark_Light/QLineEdit/padding", "4px")

                # --- QLineEdit focus ---
                settings.setValue("Dark_Light/QLineEdit_focus/background-color", "#5f5f5f")
                settings.setValue("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")

                # --- QPushButton ---
                settings.setValue("Dark_Light/QPushButton/background-color", "#6f6f6f")
                settings.setValue("Dark_Light/QPushButton/color", "white")
                settings.setValue("Dark_Light/QPushButton/border", "1px solid #5f5f5f")
                settings.setValue("Dark_Light/QPushButton/border-radius", "6px")
                settings.setValue("Dark_Light/QPushButton/padding", "4px 10px")

                # --- QPushButton hover/pressed ---
                settings.setValue("Dark_Light/QPushButton_hover/background-color", "#4d4d4d")
                settings.setValue("Dark_Light/QPushButton_pressed/background-color", "#5c5c5c")

                # --- QMenu ---
                settings.setValue("Dark_Light/QMenu/background", "#7f7f7f")
                settings.setValue("Dark_Light/QMenu/color", "white")
                settings.setValue("Dark_Light/QMenu/border", "1px solid #6f6f6f")

                # --- QMenuBar ---
                settings.setValue("Dark_Light/QMenuBar/background-color", "#7f7f7f")
                settings.setValue("Dark_Light/QMenuBar/color", "white")

                # --- QMenuBar items ---
                settings.setValue("Dark_Light/QMenuBar_item/background", "transparent")
                settings.setValue("Dark_Light/QMenuBar_item/color", "white")
                settings.setValue("Dark_Light/QMenuBar_item/padding", "4px 10px")

                # --- QMenuBar selected item ---
                settings.setValue("Dark_Light/QMenuBar_item_selected/background-color", "#4d4d4d")

                # --- QMenu selected item ---
                settings.setValue("Dark_Light/QMenu_item_selected/background-color", "#4d4d4d")

                # --- QCombo ---
                settings.setValue("Dark_Light/QComboBox/color", "white")

                self.setStyleSheet("""
                    QWidget {
                        background-color: #7f7f7f;
                    }
                    QTabWidget::pane {
                        background-color: #6f6f6f; 
                    }
                    QTabBar::tab {
                        background-color: #2b2b2b; 
                        color: white;
                        padding: 5px 12px;
                        border: none; 
                        border-top-left-radius: 6px;
                        border-top-right-radius: 6px;
                    }
                    QTabBar::tab:selected {
                        background-color: #4d4d4d;  
                        color: white;
                    }
                    QSpinBox {
                        background-color: #6f6f6f;
                        color: white;
                        border: 1px solid #5f5f5f;
                        border-radius: 8px;
                    }
                    QGroupBox:title {
                        color: white;  
                    }
                    QLabel {
                        color: white;  
                    }
                    QLineEdit {
                        background-color: #6f6f6f;
                        color: white;
                        border: 1px solid #5f5f5f;
                        border-radius: 6px;
                        padding: 4px;
                    }
                    QLineEdit:focus {
                        background-color: #5f5f5f;
                        border: 1px solid #4d90fe;
                    }

                    QPushButton {
                        background-color: #6f6f6f;
                        color: white;
                        border: 1px solid #5f5f5f;
                        border-radius: 6px;
                        padding: 4px 10px;
                    }
                    QPushButton:hover {
                        background-color: #4d4d4d;
                    }
                    QPushButton:pressed {
                        background-color: #5c5c5c;
                    }
                    QMenuBar {
                        background-color: #7f7f7f;
                        color: white;
                    }
                    QMenuBar::item {
                        background: transparent;
                        color: white;
                        padding: 4px 10px;
                    }
                    QMenuBar::item:selected {
                        background: #4d4d4d;
                    }
                    QMenu {
                        background-color: #7f7f7f;
                        color: white;
                        border: 1px solid #6f6f6f;
                    }
                    QMenu::item:selected {
                        background-color: #4d4d4d;
                    }
                """)


                self.is_dark_mode = False

                settings.setValue("Dark_Light/is_dark_mode", self.is_dark_mode)
                settings.setValue("Dark_Light/text_light_dark", "Light Mode 🔆")

            else:
                light_dark_mode.setText("Dark Mode 🌙")

                # --- QWidget ---
                settings.setValue("Dark_Light/QWidget/background-color", "#f0f0f0")

                # --- Qframe ---
                settings.setValue("Dark_Light/Qframe/background-color", "black")
                settings.setValue("Dark_Light/Qframe/color", "black")

                # --- QTabWidget pane ---
                settings.setValue("Dark_Light/QTabWidget_pane/background-color", "#e0e0e0")

                # --- QTabBar ---
                settings.setValue("Dark_Light/QTabBar/background-color", "#c8c8c8")
                settings.setValue("Dark_Light/QTabBar/color", "black")
                settings.setValue("Dark_Light/QTabBar/padding", "5px 12px")
                settings.setValue("Dark_Light/QTabBar/border", "none")
                settings.setValue("Dark_Light/QTabBar/border-top-left-radius", "6px")
                settings.setValue("Dark_Light/QTabBar/border-top-right-radius", "6px")

                # --- QTabBar selected ---
                settings.setValue("Dark_Light/QTabBar_selected/background-color", "#dcdcdc")
                settings.setValue("Dark_Light/QTabBar/color", "black")

                # --- QTabBar alternate background ---
                settings.setValue("Dark_Light/QTabBar/background-color", "#e0e0e0")

                # --- QSpinBox ---
                settings.setValue("Dark_Light/QSpinBox/color", "black")
                settings.setValue("Dark_Light/QSpinBox/border", "1px solid #b0b0b0")
                settings.setValue("Dark_Light/QSpinBox/border-radius", "8px")

                # --- QGroupBox title ---
                settings.setValue("Dark_Light/QGroupBox_title/color", "black")

                # --- QLabel ---
                settings.setValue("Dark_Light/QLabel/color", "black")

                # --- QLineEdit ---
                settings.setValue("Dark_Light/QLineEdit/background-color", "#ffffff")
                settings.setValue("Dark_Light/QLineEdit/color", "black")
                settings.setValue("Dark_Light/QLineEdit/border", "1px solid #b0b0b0")
                settings.setValue("Dark_Light/QLineEdit/border-radius", "6px")
                settings.setValue("Dark_Light/QLineEdit/padding", "4px")

                # --- QLineEdit focus ---
                settings.setValue("Dark_Light/QLineEdit_focus/background-color", "#f0f8ff")
                settings.setValue("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")

                # --- QPushButton ---
                settings.setValue("Dark_Light/QPushButton/background-color", "#e0e0e0")
                settings.setValue("Dark_Light/QPushButton/color", "black")
                settings.setValue("Dark_Light/QPushButton/border", "1px solid #b0b0b0")
                settings.setValue("Dark_Light/QPushButton/border-radius", "6px")
                settings.setValue("Dark_Light/QPushButton/padding", "4px 10px")

                # --- QPushButton hover/pressed ---
                settings.setValue("Dark_Light/QPushButton_hover/background-color", "#d0d0d0")
                settings.setValue("Dark_Light/QPushButton_pressed/background-color", "#c0c0c0")

                # --- QMenu ---
                settings.setValue("Dark_Light/QMenu/background", "#f0f0f0")
                settings.setValue("Dark_Light/QMenu/color", "black")
                settings.setValue("Dark_Light/QMenu/border", "1px solid #b0b0b0")

                # --- QMenuBar ---
                settings.setValue("Dark_Light/QMenuBar/background-color", "#f0f0f0")
                settings.setValue("Dark_Light/QMenuBar/color", "black")

                # --- QMenuBar items ---
                settings.setValue("Dark_Light/QMenuBar_item/background", "transparent")
                settings.setValue("Dark_Light/QMenuBar_item/color", "black")
                settings.setValue("Dark_Light/QMenuBar_item/padding", "4px 10px")

                # --- QMenuBar selected item ---
                settings.setValue("Dark_Light/QMenuBar_item_selected/background-color", "#dcdcdc")

                # --- QMenu selected item ---
                settings.setValue("Dark_Light/QMenu_item_selected/background-color", "#dcdcdc")

                # --- QCombo ---
                settings.setValue("Dark_Light/QComboBox/color", "white")

                self.setStyleSheet("""
                    QWidget {
                        background-color: #f0f0f0;
                    }
                    QTabWidget::pane {
                        background-color: #e0e0e0; 
                    }
                    QTabBar::tab {
                        background-color: #dcdcdc;  
                        color: black;             
                        padding: 5px 12px;
                        border: none;
                        border-top-left-radius: 6px;
                        border-top-right-radius: 6px;
                    }
                    QTabBar::tab:selected {
                        background-color: #c8c8c8;  
                        color: black;
                    }
                    QSpinBox {
                        background-color: #ffffff;
                        color: black;
                        border: 1px solid #b0b0b0;
                        border-radius: 8px;
                    }
                    QGroupBox:title {
                        color: black; 
                    }
                    QLabel {
                        color: black;
                    }
                    QLineEdit {
                        background-color: #ffffff;
                        color: black;
                        border: 1px solid #b0b0b0;
                        border-radius: 6px;
                        padding: 4px;
                    }
                    QLineEdit:focus {
                        background-color: #f0f8ff;
                        border: 1px solid #4d90fe;
                    }
                    QPushButton {
                        background-color: #e0e0e0;
                        color: black;
                        border: 1px solid #b0b0b0;
                        border-radius: 6px;
                        padding: 4px 10px;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                    }
                    QPushButton:pressed {
                        background-color: #c0c0c0;
                    }
                    QMenuBar {
                        background-color: #f0f0f0;
                        color: black;
                    }
                    QMenuBar::item {
                        background: transparent;
                        color: black;
                        padding: 4px 10px;
                    }
                    QMenuBar::item:selected {
                        background: #dcdcdc;
                    }
                    QMenu {
                        background-color: #f0f0f0;
                        color: black;
                        border: 1px solid #b0b0b0;
                    }
                    QMenu::item:selected {
                        background-color: #dcdcdc;
                    }
                """)

                self.is_dark_mode = True

                settings.setValue("Dark_Light/is_dark_mode", self.is_dark_mode)  
                settings.setValue("Dark_Light/text_light_dark", "Dark Mode 🌙")

        light_dark_mode.triggered.connect(toggle_menu_dark_mode)

        choose_graphics = view_menu.addAction("Graphics")
        choose_graphics.triggered.connect(self.open_view)  

        sweep_options = sweep_menu.addAction("Options")
        sweep_options.triggered.connect(lambda: self.open_sweep_options())
        
        sweep_run = sweep_menu.addAction("Run Sweep")
        sweep_run.triggered.connect(lambda: self.run_sweep())
        
        calibrate_option = sweep_menu.addAction("Calibration Wizard")

        calibrate_option.triggered.connect(lambda: self.open_calibration_wizard())

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

        # Auto-run sweep if device is available and connected
        if self.vna_device:
            device_type = type(self.vna_device).__name__
            is_connected = self.vna_device.connected()
            logging.info(f"[graphics_window.__init__] Device {device_type} connection status: {is_connected}")
            
            if not is_connected:
                logging.warning(f"[graphics_window.__init__] Device {device_type} not connected, attempting to reconnect...")
                try:
                    self.vna_device.connect()
                    is_connected = self.vna_device.connected()
                    logging.info(f"[graphics_window.__init__] Reconnection result: {is_connected}")
                except Exception as e:
                    logging.error(f"[graphics_window.__init__] Failed to reconnect device: {e}")
                    
            if is_connected:
                logging.info("[graphics_window.__init__] Device ready - scheduling auto-sweep")
                QTimer.singleShot(1000, self.run_sweep)  # Delay to allow UI to load
            else:
                logging.warning("[graphics_window.__init__] Device not available for auto-sweep")
        else:
            logging.warning("[graphics_window.__init__] No VNA device provided for auto-sweep")

        # --- Central widget ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout_vertical = QVBoxLayout(central_widget)
        main_layout_vertical.setContentsMargins(10, 10, 10, 10)
        main_layout_vertical.setSpacing(10)

        # --- Sweep Control Button ---
        sweep_control_layout = QHBoxLayout()
        
        # Reconnect button
        self.reconnect_button = QPushButton("Reconnect")
        self.reconnect_button.setMaximumWidth(100)
        self.reconnect_button.clicked.connect(self.reconnect_device)
        self.reconnect_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        
        # Sweep button
        self.sweep_button = QPushButton("Run Sweep")
        self.sweep_button.setMaximumWidth(120)
        self.sweep_button.clicked.connect(self.run_sweep)
        
        self.sweep_info_label = QLabel("Sweep: 0.050 MHz - 1500.000 MHz, 101 points")
        self.sweep_info_label.setStyleSheet("font-size: 12px;")

        # Initialize sweep configuration and auto-run sweep
        self.load_sweep_configuration()
        
        # Add progress bar (initially hidden)
        self.sweep_progress_bar = QProgressBar()
        self.sweep_progress_bar.setMaximumWidth(200)
        self.sweep_progress_bar.setVisible(False)
        self.sweep_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        sweep_control_layout.addWidget(self.reconnect_button)
        sweep_control_layout.addWidget(self.sweep_button)
        sweep_control_layout.addWidget(self.sweep_info_label)
        sweep_control_layout.addWidget(self.sweep_progress_bar)
        sweep_control_layout.addStretch()
        
        main_layout_vertical.addLayout(sweep_control_layout)
        
        # Set initial state of reconnect button after UI elements are created
        self._update_reconnect_button_state()

        # --- Initialize data arrays ---
        # Force everything to None for initial empty state
        self.freqs = None
        self.s11 = None 
        self.s21 = None
        
        # Log that plots will be empty until sweep is performed
        logging.info("[graphics_window.__init__] Initializing with empty plots - data will be loaded after first sweep")

        self.left_graph_type = left_graph_type
        self.left_s_param = left_s_param

        # =================== LEFT PANEL (EMPTY) ===================
        self.left_panel, self.fig_left, self.ax_left, self.canvas_left, \
        self.slider_left, self.cursor_left, self.labels_left, self.update_cursor, self.update_left_data = \
            create_left_panel(
                S_data=None,  # Force empty 
                freqs=None,   # Force empty
                settings=settings,
                graph_type=config['graph_type_tab1'], 
                s_param=config['s_param_tab1'], 
                tracecolor=config['trace_color1'],
                markercolor=config['marker_color1'],
                linewidth=config['trace_size1'],
                markersize=config['marker_size1']  
            )

        # =================== RIGHT PANEL (EMPTY) ===================
        self.right_panel, self.fig_right, self.ax_right, self.canvas_right, \
        self.slider_right, self.cursor_right, self.labels_right, self.update_right_cursor, self.update_right_data = \
            create_right_panel(
                settings=settings,
                S_data=None,  # Force empty
                freqs=None,   # Force empty
                graph_type=config['graph_type_tab2'], 
                s_param=config['s_param_tab2'],
                tracecolor=config['trace_color2'],
                markercolor=config['marker_color2'],
                linewidth=config['trace_size2'],
                markersize=config['marker_size2']
            )

        # =================== PANELS LAYOUT ===================

        panels_layout = QHBoxLayout()

        while panels_layout.count():
            item = panels_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

        panels_layout.addWidget(self.left_panel, 1)
        panels_layout.addWidget(self.right_panel, 1)
        main_layout_vertical.addLayout(panels_layout)

        self.markers = [
            {"cursor": self.cursor_left, "slider": self.slider_left, "label": self.labels_left, "update_cursor": self.update_cursor},
            {"cursor": self.cursor_right, "slider": self.slider_right, "label": self.labels_right, "update_cursor": self.update_right_cursor}
        ]
        
        # Clear all marker information fields until first sweep is completed
        self._clear_all_marker_fields()

    def _load_graph_configuration(self):
        """Load graph configuration from settings file."""
        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        return {
            'graph_type_tab1': settings.value("Tab1/GraphType1", "Smith Diagram"),
            's_param_tab1': settings.value("Tab1/SParameter", "S11"),
            'graph_type_tab2': settings.value("Tab2/GraphType2", "Magnitude"),
            's_param_tab2': settings.value("Tab2/SParameter", "S11"),
            'trace_color1': settings.value("Graphic1/TraceColor", "blue"),
            'marker_color1': settings.value("Graphic1/MarkerColor", "blue"),
            'trace_size1': int(settings.value("Graphic1/TraceWidth", 2)),
            'marker_size1': int(settings.value("Graphic1/MarkerWidth", 6)),
            'trace_color2': settings.value("Graphic2/TraceColor", "blue"),
            'marker_color2': settings.value("Graphic2/MarkerColor", "blue"),
            'trace_size2': int(settings.value("Graphic2/TraceWidth", 2)),
            'marker_size2': int(settings.value("Graphic2/MarkerWidth", 6))
        }

    def _clear_panel_labels(self, panel_side='left'):
        """Clear all labels for a specific panel (left or right)."""
        if panel_side == 'left' and hasattr(self, 'labels_left') and self.labels_left:
            self.labels_left.get("freq") and self.labels_left["freq"].setText("--")
            self.labels_left.get("val") and self.labels_left["val"].setText(f"{self.left_s_param}: -- + j--")
            self.labels_left.get("mag") and self.labels_left["mag"].setText(f"|{self.left_s_param}|: --")
            self.labels_left.get("phase") and self.labels_left["phase"].setText("Phase: --")
            self.labels_left.get("z") and self.labels_left["z"].setText("Z: -- + j--")
            self.labels_left.get("il") and self.labels_left["il"].setText("IL: --")
            self.labels_left.get("vswr") and self.labels_left["vswr"].setText("VSWR: --")
        elif panel_side == 'right' and hasattr(self, 'labels_right') and self.labels_right:
            self.labels_right.get("freq") and self.labels_right["freq"].setText("--")
            self.labels_right.get("val") and self.labels_right["val"].setText(f"{self.right_s_param}: -- + j--")
            self.labels_right.get("mag") and self.labels_right["mag"].setText(f"|{self.right_s_param}|: --")
            self.labels_right.get("phase") and self.labels_right["phase"].setText("Phase: --")
            self.labels_right.get("z") and self.labels_right["z"].setText("Z: -- + j--")
            self.labels_right.get("il") and self.labels_right["il"].setText("IL: --")
            self.labels_right.get("vswr") and self.labels_right["vswr"].setText("VSWR: --")

    def _clear_axis_and_show_message(self, panel_side='right', message_pos=(0.5, 0.5)):
        """Clear axis and show waiting message for a specific panel."""
        if panel_side == 'right':
            if hasattr(self, 'ax_right') and self.ax_right:
                self.ax_right.text(message_pos[0], message_pos[1], 'Waiting for sweep data...',
                                transform=self.ax_right.transAxes,
                                ha='center', va='center', fontsize=12, color='white')

                for line in self.ax_right.lines:
                    line.remove()

                self.ax_right.grid(False)

            if hasattr(self, 'canvas_right') and self.canvas_right:
                self.canvas_right.draw()
        elif panel_side == 'left':
            if hasattr(self, 'ax_left') and self.ax_left:
                self.ax_left.text(message_pos[0], message_pos[1], 'Waiting for sweep data...',
                                transform=self.ax_left.transAxes,
                                ha='center', va='center', fontsize=12, color='white')

                for line in self.ax_left.lines:
                    line.remove()

                self.ax_left.grid(False)

            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()

    def _clear_all_marker_fields(self):
        """Clear marker values but keep all panels and labels intact."""
        logging.info("[graphics_window._clear_all_marker_fields] Clearing marker values but keeping layout intact")

        config = self._load_graph_configuration()
        graph_type_tab1 = config['graph_type_tab1']
        graph_type_tab2 = config['graph_type_tab2']

        if graph_type_tab1 == "Smith Diagram":

            # Left panel
            self._clear_panel_labels('left')

            # Hide cursors
            if hasattr(self, 'cursor_left') and self.cursor_left:
                self.cursor_left.set_visible(False)
            
            # Clear axes but keep empty plot with message
            if hasattr(self, 'ax_left') and self.ax_left:
                #self.ax_left.clear()
                self.ax_left.text(0.5, -0.1, 'Waiting for sweep data...',
                                transform=self.ax_left.transAxes,
                                ha='center', va='center', fontsize=12, color='white')

                for line in self.ax_left.lines:
                    line.remove()

                """if self.cursor_left:
                    self.cursor_left.set_visible(False)"""

                #self.slider_left.ax.set_visible(False)

                self.ax_left.grid(False)

            # Redraw
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()
           
        if graph_type_tab2 == "Smith Diagram":

            # Right panel
            self._clear_panel_labels('right')


            if hasattr(self, 'cursor_right') and self.cursor_right:
                self.cursor_right.set_visible(False)

            self._clear_axis_and_show_message('right', (0.5, -0.1))

        if graph_type_tab1 == "Magnitude" or graph_type_tab1 == "Phase":
            # Left panel
            self._clear_panel_labels('left')

            # Hide cursors
            if hasattr(self, 'cursor_left') and self.cursor_left:
                self.cursor_left.set_visible(False)

            # Clear axes but keep empty plot with message
            if hasattr(self, 'ax_left') and self.ax_left:
                self.ax_left.text(0.5, 0.5, 'Waiting for sweep data...',
                                transform=self.ax_left.transAxes,
                                ha='center', va='center', fontsize=12, color='white')

                for line in self.ax_left.lines:
                    line.remove()

                self.ax_left.grid(False)

            # Redraw
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()

        if graph_type_tab2 == "Magnitude" or graph_type_tab2 == "Phase":

            # Right panel
            self._clear_panel_labels('right')

            if hasattr(self, 'cursor_right') and self.cursor_right:
                self.cursor_right.set_visible(False)

            self._clear_axis_and_show_message('right', (0.5, 0.5))


    def _reset_markers_after_sweep(self):
        """Reset markers and all marker-dependent information after a sweep completes."""
        logging.info("[graphics_window._reset_markers_after_sweep] Resetting markers after sweep completion")
        
        try:
            # Reset slider positions to leftmost position (index 0) if they exist
            if hasattr(self, 'slider_left') and self.slider_left:
                # Reset left slider to leftmost position
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Reset left slider to index 0 (leftmost)")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                # Reset right slider to leftmost position  
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Reset right slider to index 0 (leftmost)")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not reset right slider: {e}")
            
            # Reset ONLY marker field information - NOT the graphs themselves
            self._clear_marker_fields_only()
            
            # Update slider ranges to match the new sweep data
            self._update_slider_ranges()
            
            # Force cursor position updates if update functions exist
            if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                try:
                    # Always set cursor to leftmost position (index 0)
                    self.update_cursor(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Updated left cursor to index 0 (leftmost)")
                    
                    # Force cursor visibility and redraw after data update
                    if hasattr(self, 'cursor_left') and self.cursor_left and self.show_marker1:
                        self.cursor_left.set_visible(True)
                        if hasattr(self.cursor_left, 'get_data'):
                            x_data, y_data = self.cursor_left.get_data()
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Left cursor after update: x={x_data}, y={y_data}")
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not update left cursor: {e}")
            
            if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                try:
                    # Always set cursor to leftmost position (index 0)
                    self.update_right_cursor(0)
                    logging.info("[graphics_window._reset_markers_after_sweep] Updated right cursor to index 0 (leftmost)")
                    
                    # Force cursor visibility and redraw after data update
                    if hasattr(self, 'cursor_right') and self.cursor_right and self.show_marker2:
                        self.cursor_right.set_visible(True)
                        if hasattr(self.cursor_right, 'get_data'):
                            x_data, y_data = self.cursor_right.get_data()
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Right cursor after update: x={x_data}, y={y_data}")
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not update right cursor: {e}")
                    
            # Final forced redraw with explicit visibility check
            try:
                # Force canvas redraw to show the cursors with their new data
                if hasattr(self, 'canvas_left') and self.canvas_left:
                    self.canvas_left.draw()  # Use draw() instead of draw_idle() for immediate effect
                    logging.info("[graphics_window._reset_markers_after_sweep] Forced left canvas redraw")
                if hasattr(self, 'canvas_right') and self.canvas_right:
                    self.canvas_right.draw()  # Use draw() instead of draw_idle() for immediate effect
                    logging.info("[graphics_window._reset_markers_after_sweep] Forced right canvas redraw")
                    
            except Exception as e:
                logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not force canvas redraw: {e}")
                    
            # Force marker information update after everything is set up
            # Use QTimer to ensure all cursor recreation is complete before updating info
            def force_cursor_info_update():
                try:
                    if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                        self.update_cursor(0)
                        logging.info("[graphics_window._reset_markers_after_sweep] DELAYED: Updated left cursor info to index 0")
                    
                    if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                        self.update_right_cursor(0)
                        logging.info("[graphics_window._reset_markers_after_sweep] DELAYED: Updated right cursor info to index 0")
                        
                    # Force final canvas redraw
                    if hasattr(self, 'canvas_left') and self.canvas_left:
                        self.canvas_left.draw()
                    if hasattr(self, 'canvas_right') and self.canvas_right:
                        self.canvas_right.draw()
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Error in delayed cursor update: {e}")
            
            # Execute the delayed update after 100ms to ensure cursor recreation is complete
            QTimer.singleShot(100, force_cursor_info_update)
                    
            # Force marker visibility with debug AND fix cursor references
            self._force_marker_visibility()
                    
            logging.info("[graphics_window._reset_markers_after_sweep] Marker reset completed successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_markers_after_sweep] Error resetting markers: {e}")


    def _recreate_cursors_for_new_plots(self, marker_color_left, marker_color_right):
        """Recreate cursors when the plot type changes."""
        try:
            logging.info("[graphics_window._recreate_cursors_for_new_plots] Recreating cursors for plot type changes")
            
            # Clear any existing wrapper functions
            if hasattr(self, '_original_update_cursor'):
                self.update_cursor = self._original_update_cursor
                delattr(self, '_original_update_cursor')
            if hasattr(self, '_original_update_right_cursor'):
                self.update_right_cursor = self._original_update_right_cursor
                delattr(self, '_original_update_right_cursor')
            
            # Remove existing cursors from axes
            if hasattr(self, 'cursor_left') and self.cursor_left:
                try:
                    self.cursor_left.remove()
                except:
                    pass
                self.cursor_left = None
                
            if hasattr(self, 'cursor_right') and self.cursor_right:
                try:
                    self.cursor_right.remove()
                except:
                    pass
                self.cursor_right = None
            
            # Create new cursors at position (0,0) - they will be positioned correctly later
            # Make them invisible initially to avoid the "fixed cursor" problem
            if hasattr(self, 'ax_left') and self.ax_left:
                self.cursor_left = self.ax_left.plot(0, 0, 'o', color=marker_color_left, markersize=5, 
                                                    markeredgecolor='darkred', markeredgewidth=2, visible=False)[0]
            
            if hasattr(self, 'ax_right') and self.ax_right:
                self.cursor_right = self.ax_right.plot(0, 0, 'o', color=marker_color_right, markersize=5, 
                                                      markeredgecolor='darkred', markeredgewidth=2, visible=False)[0]
            
            # Update markers list with new cursor references
            if hasattr(self, 'markers') and self.markers:
                if len(self.markers) >= 1 and self.markers[0]:
                    self.markers[0]['cursor'] = self.cursor_left
                if len(self.markers) >= 2 and self.markers[1]:
                    self.markers[1]['cursor'] = self.cursor_right
            
            # Force marker visibility setup to create the wrapper functions again
            self._force_marker_visibility(marker_color_left=marker_color_left, marker_color_right=marker_color_right)
            
            logging.info("[graphics_window._recreate_cursors_for_new_plots] Cursors recreated successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._recreate_cursors_for_new_plots] Error recreating cursors: {e}")

    def _reset_sliders_and_markers_for_graph_change(self):
        """Reset sliders and markers to leftmost position specifically for graph type changes."""
        try:
            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Resetting sliders and markers for graph change")
            
            # Reset slider positions to leftmost position (index 0)
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not reset right slider: {e}")
            
            # Clear marker information fields
            self._clear_marker_fields_only()
            
            # Force cursor position updates to leftmost position (index 0)
            if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                try:
                    self.update_cursor(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Updated left cursor to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not update left cursor: {e}")
            
            if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                try:
                    self.update_right_cursor(0)
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Updated right cursor to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Could not update right cursor: {e}")
            
            # Make cursors visible
            if hasattr(self, 'cursor_left') and self.cursor_left:
                self.cursor_left.set_visible(True)
            if hasattr(self, 'cursor_right') and self.cursor_right:
                self.cursor_right.set_visible(True)
            
            # Force marker information update after everything is set up (for graph changes)
            def force_cursor_info_update_graph_change():
                try:
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Starting forced cursor info update")
                    
                    # Ensure sliders are at position 0 first
                    if hasattr(self, 'slider_left') and self.slider_left:
                        try:
                            self.slider_left.set_val(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Ensured left slider at position 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Could not set left slider: {e}")
                    
                    if hasattr(self, 'slider_right') and self.slider_right:
                        try:
                            self.slider_right.set_val(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Ensured right slider at position 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Could not set right slider: {e}")
                    
                    # Force cursor information update
                    if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                        try:
                            self.update_cursor(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Updated left cursor info to index 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Error updating left cursor: {e}")
                    
                    if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                        try:
                            self.update_right_cursor(0)
                            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Updated right cursor info to index 0")
                        except Exception as e:
                            logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Error updating right cursor: {e}")
                    
                    # Force canvas redraw to ensure visual update
                    if hasattr(self, 'canvas_left') and self.canvas_left:
                        self.canvas_left.draw()
                    if hasattr(self, 'canvas_right') and self.canvas_right:
                        self.canvas_right.draw()
                    
                    logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] DELAYED: Cursor info update completed")
                        
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Error in delayed cursor update: {e}")
            
            # Execute the delayed update after 150ms for graph changes (increased delay)
            QTimer.singleShot(150, force_cursor_info_update_graph_change)
            
            logging.info("[graphics_window._reset_sliders_and_markers_for_graph_change] Sliders and markers reset successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_sliders_and_markers_for_graph_change] Error resetting sliders and markers: {e}")

    def _reset_sliders_before_sweep(self):
        """Reset sliders and CLEAR all cursor information before starting a sweep."""
        try:
            logging.info("[graphics_window._reset_sliders_before_sweep] Resetting sliders and clearing info before sweep starts")
            
            # Reset slider positions to leftmost position (index 0)
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_sliders_before_sweep] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_before_sweep] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_sliders_before_sweep] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_before_sweep] Could not reset right slider: {e}")
            
            # CLEAR all marker information (DO NOT update cursor info - just clear it)
            self._clear_all_marker_fields()
            logging.info("[graphics_window._reset_sliders_before_sweep] Cleared all marker information display")
                    
            logging.info("[graphics_window._reset_sliders_before_sweep] Sliders reset and info cleared before sweep")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_sliders_before_sweep] Error resetting sliders before sweep: {e}")

    def _reset_sliders_after_reconnect(self):
        """Reset sliders and show cursor information after successful device reconnection."""
        try:
            logging.info("[graphics_window._reset_sliders_after_reconnect] Resetting sliders after successful reconnection")
            
            # Only reset if we have data available
            if not (hasattr(self, 'freqs') and self.freqs is not None and len(self.freqs) > 0):
                logging.info("[graphics_window._reset_sliders_after_reconnect] No sweep data available, skipping reset")
                return
            
            # Reset slider positions to leftmost position (index 0)
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    self.slider_left.set_val(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Reset left slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    self.slider_right.set_val(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Reset right slider to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not reset right slider: {e}")
            
            # Update cursor information to show data for minimum position
            if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                try:
                    self.update_cursor(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Updated left cursor info to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not update left cursor: {e}")
            
            if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                try:
                    self.update_right_cursor(0)
                    logging.info("[graphics_window._reset_sliders_after_reconnect] Updated right cursor info to index 0")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_sliders_after_reconnect] Could not update right cursor: {e}")
            
            # Force canvas redraw to ensure visual update
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw()
            if hasattr(self, 'canvas_right') and self.canvas_right:
                self.canvas_right.draw()
                    
            logging.info("[graphics_window._reset_sliders_after_reconnect] Sliders reset and info updated after reconnection")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_sliders_after_reconnect] Error resetting sliders after reconnection: {e}")

    def _force_marker_visibility(self, marker_color_left, marker_color_right):
        """Force markers to be visible by recreating them directly on axes"""
        
        if hasattr(self, 'cursor_left') and hasattr(self, 'ax_left') and self.cursor_left and self.ax_left:
            try:
                # Remove the old cursor first to avoid duplicates
                try:
                    if self.cursor_left:
                        self.cursor_left.remove()
                        logging.info("[graphics_window._force_marker_visibility] Removed old left cursor to prevent duplicates")
                except:
                    pass  # Ignore errors if cursor can't be removed
                
                # Get current data from the old cursor if possible, otherwise use defaults
                x_val, y_val = 0.0, 0.0
                try:
                    x_data = self.cursor_left.get_xdata()
                    y_data = self.cursor_left.get_ydata()
                    if hasattr(x_data, '__len__') and hasattr(y_data, '__len__') and len(x_data) > 0 and len(y_data) > 0:
                        x_val = float(x_data[0])
                        y_val = float(y_data[0])
                except:
                    pass  # Use defaults
                
                # Create new cursor directly on the axes
                new_cursor = self.ax_left.plot(x_val, y_val, 'o', color=marker_color_left, markersize=5, markeredgewidth=2)[0]
                self.cursor_left = new_cursor
                logging.info(f"[graphics_window._force_marker_visibility] Created new left cursor at ({x_val}, {y_val})")
                
                # Also update in markers list if it exists
                if hasattr(self, 'markers') and self.markers:
                    for i, marker in enumerate(self.markers):
                        if marker and marker.get('cursor') and i == 0:  # First marker
                            marker['cursor'] = new_cursor
                                
                    # Store the original update_cursor function and replace with a wrapper
                    if hasattr(self, 'update_cursor') and not hasattr(self, '_original_update_cursor'):
                        self._original_update_cursor = self.update_cursor
                        
                        def cursor_left_wrapper(index, from_slider=False):
                            # Call the original function first to update labels
                            result = self._original_update_cursor(index, from_slider)
                            
                            # Then update our visible cursor position 
                            if hasattr(self, 'cursor_left') and self.cursor_left and hasattr(self.cursor_left, 'set_data'):
                                try:
                                    # Get current graph type and S parameter for left panel
                                    actual_dir = os.path.dirname(os.path.dirname(__file__))  
                                    ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
                                    settings = QSettings(ruta_ini, QSettings.IniFormat)
                                    graph_type_left = settings.value("Tab1/GraphType1", "Smith Diagram")
                                    s_param_left = settings.value("Tab1/SParameter", "S11")
                                    
                                    # Determine which S parameter data to use
                                    s_data = None
                                    if s_param_left == "S21" and hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21
                                    elif s_param_left == "S11" and hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11
                                    elif hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21  # Default fallback to S21
                                    elif hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11  # Final fallback to S11
                                    
                                    if s_data is not None and hasattr(self, 'freqs') and self.freqs is not None and index < len(s_data) and index < len(self.freqs):
                                        val_complex = s_data[index]
                                        
                                        # Use appropriate coordinates based on graph type
                                        if graph_type_left == "Smith Diagram":
                                            # Smith diagram coordinates (real/imag)
                                            real_part = float(np.real(val_complex))
                                            imag_part = float(np.imag(val_complex))
                                            self.cursor_left.set_data([real_part], [imag_part])
                                        elif graph_type_left == "Magnitude":
                                            # Magnitude plot coordinates (freq in MHz, magnitude in dB)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            magnitude_db = float(20 * np.log10(np.abs(val_complex)))
                                            self.cursor_left.set_data([freq_mhz], [magnitude_db])
                                        elif graph_type_left == "Phase":
                                            # Phase plot coordinates (freq in MHz, phase in degrees)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            phase_deg = float(np.angle(val_complex) * 180 / np.pi)
                                            self.cursor_left.set_data([freq_mhz], [phase_deg])
                                        elif graph_type_left == "VSWR":
                                            # VSWR plot coordinates (freq in MHz, VSWR value)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            s_magnitude = np.abs(val_complex)
                                            vswr_val = (1 + s_magnitude) / (1 - s_magnitude) if s_magnitude < 1 else 999
                                            self.cursor_left.set_data([freq_mhz], [float(vswr_val)])
                                        
                                        # Force redraw
                                        if hasattr(self, 'canvas_left') and self.canvas_left:
                                            self.canvas_left.draw_idle()
                                except Exception as e:
                                    print(f"Error updating cursor_left position: {e}")
                            
                            return result
                        
                        self.update_cursor = cursor_left_wrapper
                        
                        # Reconnect the slider to use our wrapper
                        if hasattr(self, 'slider_left') and self.slider_left:
                            try:
                                self.slider_left.observers.clear()
                            except:
                                try:
                                    self.slider_left.disconnect()
                                except:
                                    pass
                            self.slider_left.on_changed(lambda val: cursor_left_wrapper(int(val), from_slider=True))
                
            except Exception as e:
                print(f"Error forcing cursor_left to ax_left: {e}")
                
        if hasattr(self, 'cursor_right') and hasattr(self, 'ax_right') and self.cursor_right and self.ax_right:
            try:
                # Remove the old cursor first to avoid duplicates
                try:
                    if self.cursor_right:
                        self.cursor_right.remove()
                        logging.info("[graphics_window._force_marker_visibility] Removed old right cursor to prevent duplicates")
                except:
                    pass  # Ignore errors if cursor can't be removed
                
                # Get current data from the old cursor if possible, otherwise use defaults
                x_val, y_val = 0.0, 0.0
                try:
                    x_data = self.cursor_right.get_xdata()
                    y_data = self.cursor_right.get_ydata()
                    if hasattr(x_data, '__len__') and hasattr(y_data, '__len__') and len(x_data) > 0 and len(y_data) > 0:
                        x_val = float(x_data[0])
                        y_val = float(y_data[0])
                except:
                    pass  # Use defaults
                
                # Create new cursor directly on the axes
                new_cursor = self.ax_right.plot(x_val, y_val, 'o', color=marker_color_right, markersize=5, markeredgewidth=2)[0]
                self.cursor_right = new_cursor
                logging.info(f"[graphics_window._force_marker_visibility] Created new right cursor at ({x_val}, {y_val})")
                
                if hasattr(self, 'slider_right') and self.slider_right:
                    self.slider_right.on_changed(lambda val: self.update_right_cursor(int(val), from_slider=True))

                # Also update in markers list if it exists
                if hasattr(self, 'markers') and self.markers:
                    for i, marker in enumerate(self.markers):
                        if marker and marker.get('cursor') and i == 1:  # Second marker
                            marker['cursor'] = new_cursor
                                
                    # Store the original update_right_cursor function and replace with a wrapper
                    if hasattr(self, 'update_right_cursor') and not hasattr(self, '_original_update_right_cursor'):
                        self._original_update_right_cursor = self.update_right_cursor
                        
                        def cursor_right_wrapper(index, from_slider=False):
                            # Call the original function first to update labels
                            result = self._original_update_right_cursor(index, from_slider)
                            
                            # Then update our visible cursor position 
                            if hasattr(self, 'cursor_right') and self.cursor_right and hasattr(self.cursor_right, 'set_data'):
                                try:
                                    # Get current graph type for right panel
                                    actual_dir = os.path.dirname(os.path.dirname(__file__))  
                                    ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
                                    settings = QSettings(ruta_ini, QSettings.IniFormat)
                                    graph_type_right = settings.value("Tab2/GraphType2", "Magnitude")
                                    s_param_right = settings.value("Tab2/SParameter", "S11")
                                    
                                    # Determine which S parameter data to use
                                    s_data = None
                                    if s_param_right == "S21" and hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21
                                    elif s_param_right == "S11" and hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11
                                    elif hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21  # Default fallback to S21
                                    elif hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11  # Final fallback to S11
                                    
                                    if s_data is not None and hasattr(self, 'freqs') and self.freqs is not None and index < len(s_data) and index < len(self.freqs):
                                        val_complex = s_data[index]
                                        
                                        # Use appropriate coordinates based on graph type
                                        if graph_type_right == "Smith Diagram":
                                            # Smith diagram coordinates (real/imag)
                                            real_part = float(np.real(val_complex))
                                            imag_part = float(np.imag(val_complex))
                                            self.cursor_right.set_data([real_part], [imag_part])
                                        elif graph_type_right == "Magnitude":
                                            # Magnitude plot coordinates (freq in MHz, magnitude in dB)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            magnitude_db = float(20 * np.log10(np.abs(val_complex)))
                                            self.cursor_right.set_data([freq_mhz], [magnitude_db])
                                        elif graph_type_right == "Phase":
                                            # Phase plot coordinates (freq in MHz, phase in degrees)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            phase_deg = float(np.angle(val_complex) * 180 / np.pi)
                                            self.cursor_right.set_data([freq_mhz], [phase_deg])
                                        elif graph_type_right == "VSWR":
                                            # VSWR plot coordinates (freq in MHz, VSWR value)
                                            freq_mhz = float(self.freqs[index] / 1e6)
                                            s_magnitude = np.abs(val_complex)
                                            vswr_val = (1 + s_magnitude) / (1 - s_magnitude) if s_magnitude < 1 else 999
                                            self.cursor_right.set_data([freq_mhz], [float(vswr_val)])
                                        
                                        # Force redraw
                                        if hasattr(self, 'canvas_right') and self.canvas_right:
                                            self.canvas_right.draw_idle()
                                except Exception as e:
                                    print(f"Error updating cursor_right position: {e}")
                            
                            return result
                        
                        self.update_right_cursor = cursor_right_wrapper
                        
                        # Reconnect the slider to use our wrapper
                        if hasattr(self, 'slider_right') and self.slider_right:
                            try:
                                self.slider_right.observers.clear()
                            except:
                                try:
                                    self.slider_right.disconnect()
                                except:
                                    pass
                            self.slider_right.on_changed(lambda val: cursor_right_wrapper(int(val), from_slider=True))
                
            except Exception as e:
                print(f"Error forcing cursor_right to ax_right: {e}")


    def _clear_marker_fields_only(self):
        """Clear only marker information fields without affecting the graphs."""
        logging.info("[graphics_window._clear_marker_fields_only] Clearing marker information fields only")
        
        # Clear left panel marker information
        if hasattr(self, 'labels_left') and self.labels_left:
            self.labels_left.get("freq", None) and self.labels_left["freq"].setText("--")
            self.labels_left.get("val", None) and self.labels_left["val"].setText("S11: -- + j--")
            self.labels_left.get("mag", None) and self.labels_left["mag"].setText("|S11|: --")
            self.labels_left.get("phase", None) and self.labels_left["phase"].setText("Phase: --")
            self.labels_left.get("z", None) and self.labels_left["z"].setText("Z: -- + j--")
            self.labels_left.get("il", None) and self.labels_left["il"].setText("IL: --")
            self.labels_left.get("vswr", None) and self.labels_left["vswr"].setText("VSWR: --")

        # Clear right panel marker information  
        if hasattr(self, 'labels_right') and self.labels_right:
            self.labels_right.get("freq", None) and self.labels_right["freq"].setText("--")
            self.labels_right.get("val", None) and self.labels_right["val"].setText("S21: -- + j--")
            self.labels_right.get("mag", None) and self.labels_right["mag"].setText("|S21|: --")
            self.labels_right.get("phase", None) and self.labels_right["phase"].setText("Phase: --")
            self.labels_right.get("z", None) and self.labels_right["z"].setText("Z: -- + j--")
            self.labels_right.get("il", None) and self.labels_right["il"].setText("IL: --")
            self.labels_right.get("vswr", None) and self.labels_right["vswr"].setText("VSWR: --")

        # Do NOT clear the graphs - leave them with the actual data
        logging.info("[graphics_window._clear_marker_fields_only] Marker fields cleared, graphs preserved")

    def _update_slider_ranges(self):
        """Update slider ranges and steps to match the current sweep data."""
        if not hasattr(self, 'freqs') or self.freqs is None or len(self.freqs) == 0:
            logging.warning("[graphics_window._update_slider_ranges] No frequency data available, cannot update sliders")
            return
            
        try:
            num_points = len(self.freqs)
            max_index = num_points - 1
            middle_index = max_index // 2
            
            logging.info(f"[graphics_window._update_slider_ranges] Updating sliders for {num_points} frequency points (indices 0 to {max_index})")
            logging.info(f"[graphics_window._update_slider_ranges] Frequency range: {self.freqs[0]/1e6:.3f} - {self.freqs[-1]/1e6:.3f} MHz")
            
            # Update left slider range if it exists and make it visible
            if hasattr(self, 'slider_left') and self.slider_left:
                try:
                    # Update slider range to match frequency data indices
                    self.slider_left.valmin = 0
                    self.slider_left.valmax = max_index
                    self.slider_left.valstep = 1
                    
                    # Set slider to middle position
                    self.slider_left.set_val(middle_index)
                    
                    # Make sure the slider is visible and active
                    if hasattr(self.slider_left, 'ax'):
                        self.slider_left.ax.set_visible(True)
                    if hasattr(self.slider_left, 'set_active'):
                        self.slider_left.set_active(True)
                    
                    logging.info(f"[graphics_window._update_slider_ranges] Left slider updated: range 0-{max_index}, positioned at index {middle_index} ({self.freqs[middle_index]/1e6:.3f} MHz)")
                except Exception as e:
                    logging.warning(f"[graphics_window._update_slider_ranges] Could not update left slider: {e}")
            
            # Update right slider range if it exists and make it visible
            if hasattr(self, 'slider_right') and self.slider_right:
                try:
                    # Update slider range to match frequency data indices  
                    self.slider_right.valmin = 0
                    self.slider_right.valmax = max_index
                    self.slider_right.valstep = 1
                    
                    # Set slider to middle position
                    self.slider_right.set_val(middle_index)
                    
                    # Make sure the slider is visible and active
                    if hasattr(self.slider_right, 'ax'):
                        self.slider_right.ax.set_visible(True)
                    if hasattr(self.slider_right, 'set_active'):
                        self.slider_right.set_active(True)
                    
                    logging.info(f"[graphics_window._update_slider_ranges] Right slider updated: range 0-{max_index}, positioned at index {middle_index} ({self.freqs[middle_index]/1e6:.3f} MHz)")
                except Exception as e:
                    logging.warning(f"[graphics_window._update_slider_ranges] Could not update right slider: {e}")
            
            # Force canvas redraw to show updated markers
            if hasattr(self, 'canvas_left') and self.canvas_left:
                self.canvas_left.draw_idle()
            if hasattr(self, 'canvas_right') and self.canvas_right:
                self.canvas_right.draw_idle()
                    
            logging.info("[graphics_window._update_slider_ranges] Slider ranges updated successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._update_slider_ranges] Error updating slider ranges: {e}")

    # =================== SAVE AS PNG ===================
    
    def on_save_as(self):
        from PySide6.QtWidgets import QFileDialog

        # Check if cursors are valid before accessing them
        marker1_visible = False
        marker2_visible = False
        if self.cursor_left is not None and hasattr(self.cursor_left, 'get_visible'):
            marker1_visible = self.cursor_left.get_visible()
        if self.cursor_right is not None and hasattr(self.cursor_right, 'get_visible'):
            marker2_visible = self.cursor_right.get_visible()
            
        slider1_visible = self.slider_left.ax.get_visible()
        slider2_visible = self.slider_right.ax.get_visible()

        if self.cursor_left is not None and hasattr(self.cursor_left, 'set_visible'):
            self.cursor_left.set_visible(False)
        if self.cursor_right is not None and hasattr(self.cursor_right, 'set_visible'):
            self.cursor_right.set_visible(False)
        self.slider_left.ax.set_visible(False)
        self.slider_right.ax.set_visible(False)

        self.fig_left.canvas.draw_idle()
        self.fig_right.canvas.draw_idle()

        file_path_left, _ = QFileDialog.getSaveFileName(
            self,
            "Save Left Figure As",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if file_path_left:
            self.fig_left.savefig(file_path_left)

        file_path_right, _ = QFileDialog.getSaveFileName(
            self,
            "Save Right Figure As",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        if file_path_right:
            self.fig_right.savefig(file_path_right)

        if self.cursor_left is not None and hasattr(self.cursor_left, 'set_visible'):
            self.cursor_left.set_visible(marker1_visible)
        if self.cursor_right is not None and hasattr(self.cursor_right, 'set_visible'):
            self.cursor_right.set_visible(marker2_visible)
        self.slider_left.ax.set_visible(slider1_visible)
        self.slider_right.ax.set_visible(slider2_visible)

        self.fig_left.canvas.draw()
        self.fig_right.canvas.draw()

    # =================== CALIBRATION WIZARD FUNCTION ==================

    def open_calibration_wizard(self):
        from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
        self.wizard_window = CalibrationWizard()
        self.wizard_window.show()
        self.close()

    # =================== SWEEP OPTIONS FUNCTION ==================

    def open_sweep_options(self):
        from NanoVNA_UTN_Toolkit.ui.sweep_window import SweepOptionsWindow

        # Log sweep options opening
        logging.info("[graphics_window.open_sweep_options] Opening sweep options window")

        # Try to get the current VNA device (this is a placeholder for now)
        vna_device = self.get_current_vna_device()

        # Log device information being passed to sweep options
        if vna_device:
            device_type = type(vna_device).__name__
            logging.info(f"[graphics_window.open_sweep_options] Device found: {device_type}")
            if hasattr(vna_device, 'sweep_points_min') and hasattr(vna_device, 'sweep_points_max'):
                logging.info(f"[graphics_window.open_sweep_options] Device sweep limits: {vna_device.sweep_points_min} to {vna_device.sweep_points_max}")
            else:
                logging.info("[graphics_window.open_sweep_options] Device has no sweep_points limits")
        else:
            logging.warning("[graphics_window.open_sweep_options] No VNA device available - using default limits")

        if hasattr(self, 'sweep_options_window') and self.sweep_options_window is not None:
            self.sweep_options_window.close()
            self.sweep_options_window.deleteLater()
            self.sweep_options_window = None

        logging.info("[graphics_window.open_sweep_options] Creating new sweep options window")
        self.sweep_options_window = SweepOptionsWindow(parent=self, vna_device=self.vna_device)

        self.sweep_options_window.show()
        self.sweep_options_window.raise_()
        self.sweep_options_window.activateWindow()

        
    def get_current_vna_device(self):
        """Try to get the current VNA device."""
        logging.info("[graphics_window.get_current_vna_device] Searching for current VNA device")
        
        try:
            # Check if we have device stored in this graphics window
            if hasattr(self, 'vna_device') and self.vna_device is not None:
                device_type = type(self.vna_device).__name__
                logging.info(f"[graphics_window.get_current_vna_device] Found stored device: {device_type}")
                return self.vna_device
                
            # Check if we can access the connection window device
            # This is a more advanced implementation for future development
            logging.warning("[graphics_window.get_current_vna_device] No VNA device found in graphics window")
            logging.warning("[graphics_window.get_current_vna_device] Device wasn't passed from previous window")
            
            return None
        except Exception as e:
            logging.error(f"[graphics_window.get_current_vna_device] Error getting current VNA device: {e}")
            return None

    # =================== RIGHT CLICK ==================

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        view_menu = menu.addAction("View")

        marker1_action = menu.addAction("Marker 1")
        marker1_action.setCheckable(True)
        marker1_action.setChecked(self.show_marker1)

        marker2_action = menu.addAction("Marker 2")
        marker2_action.setCheckable(True)
        marker2_action.setChecked(self.show_marker2)

        menu.addSeparator()
        export_action = menu.addAction("Export...")

        selected_action = menu.exec(event.globalPos())

        if selected_action == view_menu:
            self.open_view()
        elif selected_action == marker1_action:
            self.show_marker1 = not self.show_marker1
            self.toggle_marker_visibility(0, self.show_marker1)
        elif selected_action == marker2_action:
            self.show_marker2 = not self.show_marker2
            self.toggle_marker_visibility(1, self.show_marker2)
        elif selected_action == export_action:
            self.open_export_dialog(event)

    def open_export_dialog(self, event):
        """Open the export dialog for the clicked graph."""
        # Determine which graph was clicked based on event position
        widget_under_cursor = QApplication.widgetAt(event.globalPos())
        
        try:
            # Default to left figure
            figure_to_export = self.fig_left
            panel_name = "Left Panel"
            
            # Try to determine which canvas was clicked
            if hasattr(self, 'canvas_right') and widget_under_cursor:
                # Walk up the widget hierarchy to find the canvas
                current_widget = widget_under_cursor
                while current_widget:
                    if current_widget == self.canvas_right:
                        figure_to_export = self.fig_right
                        panel_name = "Right Panel"
                        break
                    elif current_widget == self.canvas_left:
                        figure_to_export = self.fig_left
                        panel_name = "Left Panel"
                        break
                    current_widget = current_widget.parent()

            # Close previous export dialog if it exists
            if hasattr(self, 'export_dialog') and self.export_dialog is not None:
                self.export_dialog.close()
                self.export_dialog.deleteLater()
                self.export_dialog = None

            # Create and show new export dialog
            self.export_dialog = ExportDialog(self, figure_to_export)
            self.export_dialog.setWindowTitle(f"Export Graph - {panel_name}")
            self.export_dialog.exec()
            
        except Exception as e:
            logging.error(f"Error opening export dialog: {e}")
            QMessageBox.warning(self, "Export Error", f"Failed to open export dialog: {str(e)}")


    # =================== MARKERS ==================

    def edit_graphics_markers(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.edit_graphics_window import EditGraphics
        self.edit_graphics_window = EditGraphics(nano_window=self) 
        self.edit_graphics_window.show()

    # =================== VIEW ==================

    def open_view(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.view_window import View
        
        # Cerrar la instancia anterior si existe
        if hasattr(self, 'view_window') and self.view_window is not None:
            self.view_window.close()
            self.view_window.deleteLater()
            self.view_window = None

        # Crear nueva instancia de View
        self.view_window = View(nano_window=self)
        self.view_window.show()
        self.view_window.raise_()
        self.view_window.activateWindow()

    # =================== TOGGLE MARKERS==================

    def clear_freq_edit(self, edit_widget):
        edit_widget.blockSignals(True) 
        edit_widget.setText("--")
        edit_widget.setFixedWidth(edit_widget.fontMetrics().horizontalAdvance(edit_widget.text()) + 4)
        edit_widget.blockSignals(False)


    def toggle_marker_visibility(self, marker_index, show=True):
        marker = self.markers[marker_index]
        cursor = marker["cursor"]
        slider = marker["slider"]
        labels = marker["label"]
        update_cursor_func = marker.get("update_cursor", None)

        # Check if cursor is valid before using it
        if cursor is None or cursor.figure is None:
            logging.warning(f"[graphics_window.toggle_marker_visibility] Cursor {marker_index} is invalid, skipping toggle")
            return

        cursor.set_visible(show)

        if show:
            slider.ax.set_visible(True)
            slider.set_active(True)
            if hasattr(marker, "slider_callback"):
                slider.on_changed(marker.slider_callback)

            if update_cursor_func:
                update_cursor_func(0)

            edit_value = labels["freq"]
            edit_value.setEnabled(True)
            if self.freqs is not None and len(self.freqs) > 0:
                if self.freqs[0] < 1e6:  
                    edit_value.setText(f"{self.freqs[0]/1e3:.3f}")
                elif self.freqs[0] < 1e9:  
                    edit_value.setText(f"{self.freqs[0]/1e6:.3f}")
                else: 
                    edit_value.setText(f"{self.freqs[0]/1e9:.3f}")
            else:
                edit_value.setText("--") 

        else:
            slider.set_val(0)
            slider.ax.set_visible(False)
            slider.set_active(False)

            edit_value = labels["freq"]
            edit_value.setEnabled(False)
            edit_value.setText("0")

            # --- Limpiar otros labels ---
            labels["val"].setText(f"{self.left_s_param if marker_index==0 else 'S11'}: -- + j--")
            labels["mag"].setText("|S11|: --")
            labels["phase"].setText("Phase: --")
            labels["z"].setText("Z: -- + j--")
            labels["il"].setText("IL: --")
            labels["vswr"].setText("VSWR: --")

        # Only draw if cursor and figure are valid
        if cursor is not None and cursor.figure is not None and cursor.figure.canvas is not None:
            cursor.figure.canvas.draw_idle()
        else:
            logging.warning(f"[graphics_window.toggle_marker_visibility] Cannot draw cursor {marker_index}, figure or canvas is None")

    # =================== SWEEP FUNCTIONALITY ===================
    
    def load_sweep_configuration(self):
        """Load sweep configuration from sweep options config file."""
        
        try:
            # Get path to sweep options config
            actual_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sweep_config_path = os.path.join(actual_dir, "ui", "sweep_window", "config", "config.ini")
            sweep_config_path = os.path.normpath(sweep_config_path)

            if os.path.exists(sweep_config_path):
                settings = QSettings(sweep_config_path, QSettings.Format.IniFormat)

                self.start_freq_hz = int(float(str(settings.value("Frequency/StartFreqHz", 50000))))
                self.stop_freq_hz = int(float(str(settings.value("Frequency/StopFreqHz", 1.5e9))))
                self.segments = int(str(settings.value("Frequency/Segments", 101)))

                logging.info(f"[graphics_window.load_sweep_configuration] Loaded sweep config: "
                            f"{self.start_freq_hz/1e6:.3f} MHz - {self.stop_freq_hz/1e6:.3f} MHz, "
                            f"{self.segments} points")

                self.start_unit = settings.value("Frequency/StartUnit", "kHz")
                self.stop_unit = settings.value("Frequency/StopUnit", "GHz")

                # Update info label if it exists
                if hasattr(self, 'sweep_info_label'):
                    self.update_sweep_info_label()

            else:
                # Default values if config file doesn't exist
                self.start_freq_hz = 50000
                self.stop_freq_hz = int(1.5e9)
                self.segments = 101
                logging.warning("[graphics_window.load_sweep_configuration] Config file not found, using defaults")

        except Exception as e:
            logging.error(f"[graphics_window.load_sweep_configuration] Error loading sweep config: {e}")
            # Fallback defaults
            self.start_freq_hz = 50000
            self.stop_freq_hz = int(1.5e9)
            self.segments = 101


    def update_sweep_info_label(self):
        """Update the sweep information label with current configuration."""
        try:
            start_val = self.start_freq_hz
            stop_val  = self.stop_freq_hz

            logging.info(f"[update_sweep_info_label] start_val={start_val} Hz")
            logging.info(f"[update_sweep_info_label] stop_val={stop_val} Hz")

            start_unit = self.start_unit
            stop_unit = self.stop_unit

            logging.info(f"[update_sweep_info_label] start_val={start_val}, stop_val={stop_val}")
            logging.info(f"[update_sweep_info_label] start_unit={start_unit}, stop_unit={stop_unit}")

            # Convert to proper units
            if start_unit.lower() == "khz":
                freq_start_str = f"{start_val/1e3:.1f} kHz"
            elif start_unit.lower() == "mhz":
                freq_start_str = f"{start_val/1e6:.3f} MHz"
            elif start_unit.lower() == "ghz":
                freq_start_str = f"{start_val/1e9:.3f} GHz"
            else:
                freq_start_str = f"{start_val} Hz"

            if stop_unit.lower() == "khz":
                freq_stop_str = f"{stop_val/1e3:.1f} kHz"
            elif stop_unit.lower() == "mhz":
                freq_stop_str = f"{stop_val/1e6:.3f} MHz"
            elif stop_unit.lower() == "ghz":
                freq_stop_str = f"{stop_val/1e9:.3f} GHz"
            else:
                freq_stop_str = f"{stop_val} Hz"

            info_text = f"Sweep: {freq_start_str} - {freq_stop_str}, {self.segments} points"
            self.sweep_info_label.setText(info_text)
            logging.info(f"[graphics_window.update_sweep_info_label] Updated info: {info_text}")
        except Exception as e:
            logging.error(f"[graphics_window.update_sweep_info_label] Error updating label: {e}")

    def run_sweep(self):
        """Run a sweep on the connected device."""
        logging.info("[graphics_window.run_sweep] Starting sweep operation")
        
        if not self.vna_device:
            error_msg = "No VNA device connected. Cannot perform sweep."
            QMessageBox.warning(self, "No Device", error_msg)
            logging.warning(f"[graphics_window.run_sweep] {error_msg}")
            return
            
        # Check and ensure device connection
        if not self.vna_device.connected():
            logging.warning("[graphics_window.run_sweep] Device not connected, attempting to reconnect...")
            try:
                self.vna_device.connect()
                if not self.vna_device.connected():
                    error_msg = "VNA device connection failed. Please check device and try again."
                    QMessageBox.warning(self, "Connection Failed", error_msg)
                    logging.error(f"[graphics_window.run_sweep] {error_msg}")
                    return
                logging.info("[graphics_window.run_sweep] Device reconnected successfully")
            except Exception as e:
                error_msg = f"Failed to reconnect to VNA device: {str(e)}"
                QMessageBox.critical(self, "Connection Error", error_msg)
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                return
            
        try:
            # Reset sliders and clear all marker information before starting sweep
            logging.info("[graphics_window.run_sweep] Preparing for sweep - resetting sliders and clearing info")
            self._reset_sliders_before_sweep()
            
            # Disable sweep button and show progress bar
            self.sweep_button.setEnabled(False)
            self.sweep_button.setText("Sweeping...")
            self.sweep_progress_bar.setVisible(True)
            self.sweep_progress_bar.setValue(0)
            
            # Also disable reconnect button during sweep
            self.reconnect_button.setEnabled(False)
            
            # Load current sweep configuration
            self.load_sweep_configuration()
            
            device_type = type(self.vna_device).__name__
            logging.info(f"[graphics_window.run_sweep] Running sweep on {device_type}")
            logging.info(f"[graphics_window.run_sweep] Frequency range: {self.start_freq_hz/1e6:.3f} MHz - {self.stop_freq_hz/1e6:.3f} MHz")
            logging.info(f"[graphics_window.run_sweep] Number of points: {self.segments}")
            
            # Validate sweep parameters
            if self.segments < 11 or self.segments > 101:
                error_msg = f"Invalid number of sweep points: {self.segments}. Must be between 11 and 101."
                QMessageBox.warning(self, "Invalid Parameters", error_msg)
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                self._reset_sweep_ui()
                return
                
            if self.start_freq_hz >= self.stop_freq_hz:
                error_msg = f"Invalid frequency range: start ({self.start_freq_hz/1e6:.3f} MHz) must be less than stop ({self.stop_freq_hz/1e6:.3f} MHz)"
                QMessageBox.warning(self, "Invalid Parameters", error_msg)
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                self._reset_sweep_ui()
                return
            
            # Update progress bar
            self.sweep_progress_bar.setValue(10)
            QApplication.processEvents()  # Force UI update
            
            # Configure VNA sweep parameters
            logging.info(f"[graphics_window.run_sweep] Setting datapoints to {self.segments}")
            self.vna_device.datapoints = self.segments
            self.sweep_progress_bar.setValue(20)
            QApplication.processEvents()
            
            # Set sweep range
            logging.info(f"[graphics_window.run_sweep] Setting sweep range: {self.start_freq_hz} - {self.stop_freq_hz} Hz")
            self.vna_device.setSweep(self.start_freq_hz, self.stop_freq_hz)
            self.sweep_progress_bar.setValue(40)
            QApplication.processEvents()
            
            # Read frequency points
            logging.info("[graphics_window.run_sweep] Reading frequency points...")
            freqs_data = self.vna_device.read_frequencies()
            freqs = np.array(freqs_data)
            logging.info(f"[graphics_window.run_sweep] Got {len(freqs)} frequency points")
            self.sweep_progress_bar.setValue(60)
            QApplication.processEvents()
            
            # Read S11 data
            logging.info("[graphics_window.run_sweep] Reading S11 data...")
            s11_data = self.vna_device.readValues("data 0")
            s11 = np.array(s11_data)
            logging.info(f"[graphics_window.run_sweep] Got {len(s11)} S11 data points")
            self.sweep_progress_bar.setValue(80)
            QApplication.processEvents()
            
            # Read S21 data
            logging.info("[graphics_window.run_sweep] Reading S21 data...")
            s21_data = self.vna_device.readValues("data 1")
            s21 = np.array(s21_data)
            logging.info(f"[graphics_window.run_sweep] Got {len(s21)} S21 data points")
            self.sweep_progress_bar.setValue(90)
            QApplication.processEvents()
            
            # Validate data consistency
            if len(freqs) != len(s11) or len(freqs) != len(s21):
                error_msg = f"Data length mismatch: freqs={len(freqs)}, s11={len(s11)}, s21={len(s21)}"
                logging.error(f"[graphics_window.run_sweep] {error_msg}")
                QMessageBox.critical(self, "Data Error", f"Sweep data inconsistency: {error_msg}")
                self._reset_sweep_ui()
                return
            
            # Update internal data
            self.freqs = freqs
            self.s11 = s11
            self.s21 = s21
            
            # Update plots with new data (skip graph-change reset since we're doing a sweep reset)
            self.update_plots_with_new_data(skip_reset=True)
            self.sweep_progress_bar.setValue(100)
            QApplication.processEvents()
            
            # Reset markers and all marker-dependent information after new sweep
            self._reset_markers_after_sweep()
            
            # Additional reset specifically for Run Sweep to ensure cursor info is updated
            def final_run_sweep_cursor_reset():
                try:
                    logging.info("[graphics_window.run_sweep] FINAL: Ensuring cursor information is displayed after run sweep")
                    
                    # Force sliders to leftmost position
                    if hasattr(self, 'slider_left') and self.slider_left:
                        self.slider_left.set_val(0)
                    if hasattr(self, 'slider_right') and self.slider_right:
                        self.slider_right.set_val(0)
                    
                    # Force cursor information update
                    if hasattr(self, 'update_cursor') and callable(self.update_cursor):
                        self.update_cursor(0)
                        logging.info("[graphics_window.run_sweep] FINAL: Left cursor info updated to show minimum frequency data")
                    
                    if hasattr(self, 'update_right_cursor') and callable(self.update_right_cursor):
                        self.update_right_cursor(0)
                        logging.info("[graphics_window.run_sweep] FINAL: Right cursor info updated to show minimum frequency data")
                        
                    # Force canvas redraw
                    if hasattr(self, 'canvas_left') and self.canvas_left:
                        self.canvas_left.draw()
                    if hasattr(self, 'canvas_right') and self.canvas_right:
                        self.canvas_right.draw()
                        
                except Exception as e:
                    logging.warning(f"[graphics_window.run_sweep] Error in final cursor reset: {e}")
            
            # Execute final reset after 200ms to ensure everything is configured
            QTimer.singleShot(200, final_run_sweep_cursor_reset)
            
            # Success message
            success_msg = f"Sweep completed successfully.\n{len(freqs)} data points acquired.\nFrequency range: {freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz"
            logging.info(f"[graphics_window.run_sweep] {success_msg}")
            
            # Reset UI after longer delay to show 100% completion and allow cursor updates
            QTimer.singleShot(700, self._reset_sweep_ui)
            
        except Exception as e:
            error_msg = f"Error during sweep: {str(e)}"
            logging.error(f"[graphics_window.run_sweep] {error_msg}")
            logging.error(f"[graphics_window.run_sweep] Exception details: {type(e).__name__}")
            QMessageBox.critical(self, "Sweep Error", error_msg)
            self._reset_sweep_ui()

    def _reset_sweep_ui(self):
        """Reset the sweep UI elements to their initial state."""
        self.sweep_button.setEnabled(True)
        self.sweep_button.setText("Run Sweep")
        self.sweep_progress_bar.setVisible(False)
        self.sweep_progress_bar.setValue(0)
        
        # Update reconnect button state based on device connection
        self._update_reconnect_button_state()

    def reconnect_device(self):
        """Reconnect to the VNA device."""
        logging.info("[graphics_window.reconnect_device] Manual reconnection requested")
        
        if not self.vna_device:
            error_msg = "No VNA device available to reconnect."
            QMessageBox.warning(self, "No Device", error_msg)
            logging.warning(f"[graphics_window.reconnect_device] {error_msg}")
            return
            
        # Disable reconnect button during reconnection
        self.reconnect_button.setEnabled(False)
        self.reconnect_button.setText("Connecting...")
        
        # Also disable sweep button during reconnection
        self.sweep_button.setEnabled(False)
        
        try:
            device_type = type(self.vna_device).__name__
            logging.info(f"[graphics_window.reconnect_device] Attempting to reconnect {device_type}")
            
            # If already connected, disconnect first
            if self.vna_device.connected():
                logging.info("[graphics_window.reconnect_device] Device already connected, disconnecting first")
                self.vna_device.disconnect()
                
            # Attempt reconnection
            self.vna_device.connect()
            
            if self.vna_device.connected():
                success_msg = f"Successfully reconnected to {device_type}"
                logging.info(f"[graphics_window.reconnect_device] {success_msg}")
                QMessageBox.information(self, "Reconnection Successful", success_msg)
                
                # Reset sliders and cursors to initial position after successful reconnection
                self._reset_sliders_after_reconnect()
                
                # Enable sweep button since device is now connected
                self.sweep_button.setEnabled(True)
            else:
                error_msg = f"Failed to reconnect to {device_type}. Please check device connection."
                logging.error(f"[graphics_window.reconnect_device] {error_msg}")
                QMessageBox.critical(self, "Reconnection Failed", error_msg)
                
        except Exception as e:
            error_msg = f"Error during reconnection: {str(e)}"
            logging.error(f"[graphics_window.reconnect_device] {error_msg}")
            QMessageBox.critical(self, "Reconnection Error", error_msg)
            
        finally:
            # Reset reconnect button state
            self._update_reconnect_button_state()
            
            # Re-enable sweep button after reconnection attempt
            self.sweep_button.setEnabled(True)
            
    def _update_reconnect_button_state(self):
        """Update the reconnect button state based on device connection."""
        if not self.vna_device:
            self.reconnect_button.setEnabled(False)
            self.reconnect_button.setText("No Device")
            return
            
        is_connected = self.vna_device.connected()
        
        if is_connected:
            self.reconnect_button.setEnabled(True)
            self.reconnect_button.setText("Reconnect")
            self.reconnect_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45A049;
                }
            """)
        else:
            self.reconnect_button.setEnabled(True)
            self.reconnect_button.setText("Connect")
            self.reconnect_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF5722;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #E64A19;
                }
            """)

    def update_plots_with_new_data(self, skip_reset=False):
        """Update both plots with new sweep data."""
        try:
            logging.info("[graphics_window.update_plots_with_new_data] Updating plots with new sweep data")
            
            if self.freqs is None or self.s11 is None or self.s21 is None:
                logging.warning("[graphics_window.update_plots_with_new_data] No data available for plotting")
                return
                
            logging.info(f"[graphics_window.update_plots_with_new_data] New data: {len(self.freqs)} frequency points")
            
            # Get current graph settings
            actual_dir = os.path.dirname(os.path.dirname(__file__))  
            ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")
            settings = QSettings(ruta_ini, QSettings.IniFormat)

            graph_type_tab1 = settings.value("Tab1/GraphType1", "Smith Diagram")
            s_param_tab1    = settings.value("Tab1/SParameter", "S11")
            graph_type_tab2 = settings.value("Tab2/GraphType2", "Magnitude")
            s_param_tab2    = settings.value("Tab2/SParameter", "S11")
            
            trace_color1 = settings.value("Graphic1/TraceColor", "blue")
            marker_color1 = settings.value("Graphic1/MarkerColor", "blue")
            background_color1 = settings.value("Graphic1/BackgroundColor", "blue")
            text_color1 = settings.value("Graphic1/TextColor", "blue")
            axis_color1 = settings.value("Graphic1/AxisColor", "blue")
            trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
            marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))
            
            trace_color2 = settings.value("Graphic2/TraceColor", "blue")
            marker_color2 = settings.value("Graphic2/MarkerColor", "blue")
            background_color2 = settings.value("Graphic2/BackgroundColor", "blue")
            text_color2 = settings.value("Graphic2/TextColor", "blue")
            axis_color2 = settings.value("Graphic2/AxisColor", "blue")
            trace_size2 = int(settings.value("Graphic2/TraceWidth", 2))
            marker_size2 = int(settings.value("Graphic2/MarkerWidth", 6))
            
            # Determine which data to plot for each panel
            s_data_left = self.s11 if s_param_tab1 == "S11" else self.s21
            s_data_right = self.s11 if s_param_tab2 == "S11" else self.s21
            
            # Clear existing plots
            self.ax_left.clear()
            self.ax_right.clear()

            # Recreate left panel plot
            logging.info(f"[graphics_window.update_plots_with_new_data] Recreating left plot: {graph_type_tab1} - {s_param_tab1}")
            self._recreate_single_plot(
                ax=self.ax_left,
                fig=self.fig_left,
                s_data=s_data_left,
                freqs=self.freqs,
                graph_type=graph_type_tab1,
                s_param=s_param_tab1,
                tracecolor=trace_color1,
                markercolor=marker_color1,
                brackground_color_graphics=background_color1,
                text_color=text_color1,
                axis_color=axis_color1,
                linewidth=trace_size1,
                markersize=marker_size1
            )
            
            # Recreate right panel plot
            logging.info(f"[graphics_window.update_plots_with_new_data] Recreating right plot: {graph_type_tab2} - {s_param_tab2}")
            self._recreate_single_plot(
                ax=self.ax_right,
                fig=self.fig_right,
                s_data=s_data_right,
                freqs=self.freqs,
                graph_type=graph_type_tab2,
                s_param=s_param_tab2,
                tracecolor=trace_color2,
                markercolor=marker_color2,
                brackground_color_graphics=background_color2,
                text_color=text_color2,
                axis_color=axis_color2,
                linewidth=trace_size2,
                markersize=marker_size2
            )
            
            # Update data references in cursor functions
            logging.info("[graphics_window.update_plots_with_new_data] Updating cursor data references")
            if hasattr(self, 'update_left_data') and self.update_left_data:
                self.update_left_data(s_data_left, self.freqs)
            if hasattr(self, 'update_right_data') and self.update_right_data:
                self.update_right_data(s_data_right, self.freqs)
            
            # Recreate cursors for the new graph types
            logging.info("[graphics_window.update_plots_with_new_data] Recreating cursors for new graph types")
            self._recreate_cursors_for_new_plots(marker_color_left=marker_color1, marker_color_right=marker_color2)
            
            # Reset sliders and markers to leftmost position (index 0) for graph type changes
            # Skip this reset if we're doing a sweep (will be handled by _reset_markers_after_sweep)
            if not skip_reset:
                logging.info("[graphics_window.update_plots_with_new_data] Resetting sliders and markers to initial position")
                self._reset_sliders_and_markers_for_graph_change()
            else:
                logging.info("[graphics_window.update_plots_with_new_data] Skipping reset - will be handled by sweep reset")
            
            # Force redraw
            self.canvas_left.draw()
            self.canvas_right.draw()
            
            logging.info("[graphics_window.update_plots_with_new_data] Plots updated successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window.update_plots_with_new_data] Error updating plots: {e}")
    
    def _recreate_single_plot(self, ax, fig, s_data, freqs, graph_type, s_param, 
                             tracecolor, markercolor, brackground_color_graphics, text_color, axis_color, linewidth, markersize):
        """Recreate a single plot with new data."""
        try:
            from matplotlib.lines import Line2D

            fig.patch.set_facecolor(f"{brackground_color_graphics}")
            ax.set_facecolor(f"{brackground_color_graphics}")

            if graph_type == "Smith Diagram":
                # Create network object for Smith chart
                
                ntw = rf.Network(frequency=freqs, s=s_data[:, np.newaxis, np.newaxis], z0=50)
                ntw.plot_s_smith(ax=ax, draw_labels=True)
                ax.legend([Line2D([0],[0], color=tracecolor)], [s_param], 
                    loc='upper left', bbox_to_anchor=(-0.17,1.14))

                for text in ax.texts:
                    text.set_color(f"{axis_color}")

                for patch in ax.patches:
                    patch.set_edgecolor(f"{axis_color}")   
                    patch.set_facecolor("none")    
                
                ax.hlines(0, -1, 1, color=f"{axis_color}", linewidth=1.1, zorder=10)
                
                # Update line properties
                for idx, line in enumerate(ax.lines):
                    xdata = line.get_xdata()
                    if len(xdata) == len(freqs):
                        line.set_color(tracecolor)
                        line.set_linewidth(linewidth)
                        
            elif graph_type == "Magnitude":
                # Plot magnitude
                magnitude_db = 20 * np.log10(np.abs(s_data))
                ax.plot(freqs / 1e6, magnitude_db, color=tracecolor, linewidth=linewidth)

                ax.set_xlabel("Frequency [MHz]", color=f"{text_color}")
                ax.set_ylabel(f"|{s_param}|", color=f"{text_color}")
                ax.set_title(f"{s_param} Magnitude", color=f"{text_color}")
                ax.tick_params(axis='x', colors=f"{axis_color}")
                ax.tick_params(axis='y', colors=f"{axis_color}")

                for spine in ax.spines.values():
                    spine.set_color("white")
                    
                ax.grid(True, which='both', axis='both', color=f"{axis_color}", linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)
                
            elif graph_type == "Phase":
                # Plot phase
                phase_deg = np.angle(s_data) * 180 / np.pi

                ax.plot(freqs / 1e6, phase_deg, color=tracecolor, linewidth=linewidth)
                ax.set_xlabel("Frequency [MHz]", color=f"{text_color}")
                ax.set_ylabel(r'$\phi_{%s}$ [°]' % s_param, color=f"{text_color}")
                ax.set_title(f"{s_param} Phase", color=f"{text_color}")
                ax.tick_params(axis='x', colors=f"{axis_color}")
                ax.tick_params(axis='y', colors=f"{axis_color}")

                for spine in ax.spines.values():
                    spine.set_color("white")
                    
                ax.grid(True, which='both', axis='both', color=f"{axis_color}", linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)
                
            elif graph_type == "VSWR":
                # Calculate and plot VSWR
                s_magnitude = np.abs(s_data)
                vswr = (1 + s_magnitude) / (1 - s_magnitude)
                ax.plot(freqs / 1e6, vswr, color=tracecolor, linewidth=linewidth)
                ax.set_xlabel('Frequency (MHz)')
                ax.set_ylabel('VSWR')
                ax.set_title(f'{s_param} VSWR')
                ax.grid(True)
                
            # Set axis properties
            ax.tick_params(axis='both', which='major', labelsize=8)
            #fig.tight_layout()
            
        except Exception as e:
            logging.error(f"[graphics_window._recreate_single_plot] Error recreating plot: {e}")

    def export_touchstone_data(self):
        """Export sweep data to Touchstone format."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        logging.info("[graphics_window.export_touchstone_data] Starting Touchstone export")
        
        # Check if we have sweep data available
        if not hasattr(self, 'freqs') or self.freqs is None:
            error_msg = "No sweep data available for export.\nPlease run a sweep first."
            QMessageBox.warning(self, "No Data", error_msg)
            logging.warning("[graphics_window.export_touchstone_data] No frequency data available")
            return
        
        if not hasattr(self, 's11') or self.s11 is None:
            error_msg = "No S11 data available for export.\nPlease run a sweep first."
            QMessageBox.warning(self, "No Data", error_msg)
            logging.warning("[graphics_window.export_touchstone_data] No S11 data available")
            return
        
        if not hasattr(self, 's21') or self.s21 is None:
            error_msg = "No S21 data available for export.\nPlease run a sweep first."
            QMessageBox.warning(self, "No Data", error_msg)
            logging.warning("[graphics_window.export_touchstone_data] No S21 data available")
            return
        
        # Check data consistency
        if len(self.freqs) != len(self.s11) or len(self.freqs) != len(self.s21):
            error_msg = f"Data length mismatch detected.\nFreqs: {len(self.freqs)}, S11: {len(self.s11)}, S21: {len(self.s21)}"
            QMessageBox.critical(self, "Data Error", error_msg)
            logging.error(f"[graphics_window.export_touchstone_data] {error_msg}")
            return
        
        # Get save file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Touchstone Data",
            "",
            "Touchstone S2P Files (*.s2p);;All Files (*)"
        )
        
        if not file_path:
            logging.info("[graphics_window.export_touchstone_data] Export cancelled by user")
            return
        
        # Ensure file has .s2p extension
        if not file_path.lower().endswith('.s2p'):
            file_path += '.s2p'
        
        try:
            # Create Touchstone content manually since the existing class doesn't support 2-parameter format
            self._export_touchstone_s2p(file_path)
            
            # Success message
            num_points = len(self.freqs)
            freq_range = f"{self.freqs[0]/1e6:.3f} - {self.freqs[-1]/1e6:.3f} MHz"
            success_msg = f"Touchstone data exported successfully!\n\nFile: {file_path}\nPoints: {num_points}\nFrequency range: {freq_range}"
            QMessageBox.information(self, "Export Successful", success_msg)
            logging.info(f"[graphics_window.export_touchstone_data] Successfully exported {num_points} points to {file_path}")
            
        except Exception as e:
            error_msg = f"Error exporting Touchstone data:\n{str(e)}"
            QMessageBox.critical(self, "Export Error", error_msg)
            logging.error(f"[graphics_window.export_touchstone_data] Export error: {e}")
            logging.error(f"[graphics_window.export_touchstone_data] Exception details: {type(e).__name__}")

    def _export_touchstone_s2p(self, file_path: str):
        """Export data to Touchstone S2P format with S11 and S21 parameters.
        
        Args:
            file_path: Path where to save the S2P file
        """
        import os
        from datetime import datetime
        
        logging.info(f"[graphics_window._export_touchstone_s2p] Writing S2P file: {file_path}")
        
        # Get device information if available
        device_name = "Unknown"
        if self.vna_device:
            device_name = getattr(self.vna_device, 'name', type(self.vna_device).__name__)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            # Write header comments
            f.write(f"! Touchstone file exported from NanoVNA UTN Toolkit\n")
            f.write(f"! Device: {device_name}\n")
            f.write(f"! Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"! Frequency range: {self.freqs[0]/1e6:.3f} - {self.freqs[-1]/1e6:.3f} MHz\n")
            f.write(f"! Number of points: {len(self.freqs)}\n")
            f.write(f"!\n")
            
            # Write option line (frequency in Hz, S-parameters, Real/Imaginary format, 50 ohm reference)
            f.write("# HZ S RI R 50\n")
            
            # Write data points
            for i in range(len(self.freqs)):
                freq_hz = int(self.freqs[i])
                
                # S11 data (reflection coefficient port 1)
                s11 = self.s11[i]
                s11_real = float(s11.real)
                s11_imag = float(s11.imag)
                
                # S21 data (transmission coefficient port 2 to port 1)
                s21 = self.s21[i]
                s21_real = float(s21.real)
                s21_imag = float(s21.imag)
                
                # For a 2-port S2P file, we need S11, S21, S12, S22
                # Since VNA typically only measures S11 and S21, we'll set S12=S21 and S22=0
                # This is a reasonable assumption for most VNA measurements
                s12_real = s21_real  # Assume reciprocal network (S12 = S21)
                s12_imag = s21_imag
                s22_real = 0.0       # Assume matched port 2 (no reflection)
                s22_imag = 0.0
                
                # Write data line: freq S11_real S11_imag S21_real S21_imag S12_real S12_imag S22_real S22_imag
                f.write(f"{freq_hz} {s11_real:.6e} {s11_imag:.6e} {s21_real:.6e} {s21_imag:.6e} "
                       f"{s12_real:.6e} {s12_imag:.6e} {s22_real:.6e} {s22_imag:.6e}\n")
        
        logging.info(f"[graphics_window._export_touchstone_s2p] Successfully wrote {len(self.freqs)} data points")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NanoVNAGraphics()
    window.show()
    sys.exit(app.exec())
