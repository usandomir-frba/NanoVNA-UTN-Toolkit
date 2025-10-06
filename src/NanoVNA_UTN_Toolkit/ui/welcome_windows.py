"""
Welcome setup window for NanoVNA devices.
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
    QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QHBoxLayout, QGroupBox, QComboBox, QToolButton, QMenu, 
)
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QPen, QColor

try:
    from NanoVNA_UTN_Toolkit.ui.graphics_window import NanoVNAGraphics
except ImportError as e:
    logging.error("Failed to import NanoVNAGraphics: %s", e)
    NanoVNAGraphics = None

from ..workers.device_worker import DeviceWorker
from .log_handler import GuiLogHandler

try:
    from NanoVNA_UTN_Toolkit.ui.wizard_windows import CalibrationWizard
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)


class NanoVNAWelcome(QMainWindow):
    def __init__(self, s11=None, freqs=None, vna_device=None):
        super().__init__()

        # Load configuration for UI colors and styles
        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "ui", "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.IniFormat)

        # Read colors for different widgets
        background_color = settings.value("Dark_Light/QWidget/background-color", "#3a3a3a")
        tabwidget_pane_bg = settings.value("Dark_Light/QTabWidget_pane/background-color", "#3b3b3b")
        tabbar_bg = settings.value("Dark_Light/QTabBar/background-color", "#2b2b2b")
        tabbar_color = settings.value("Dark_Light/QTabBar/color", "white")
        tabbar_padding = settings.value("Dark_Light/QTabBar/padding", "5px 12px")
        tabbar_border = settings.value("Dark_Light/QTabBar/border", "none")
        tabbar_border_tl_radius = settings.value("Dark_Light/QTabBar/border-top-left-radius", "6px")
        tabbar_border_tr_radius = settings.value("Dark_Light/QTabBar/border-top-right-radius", "6px")
        tabbar_selected_bg = settings.value("Dark_Light/QTabBar_selected/background-color", "#4d4d4d")
        tabbar_selected_color = settings.value("Dark_Light/QTabBar/color", "white")
        spinbox_bg = settings.value("Dark_Light/QSpinBox/background-color", "#3b3b3b")
        spinbox_color = settings.value("Dark_Light/QSpinBox/color", "white")
        spinbox_border = settings.value("Dark_Light/QSpinBox/border", "1px solid white")
        spinbox_border_radius = settings.value("Dark_Light/QSpinBox/border-radius", "8px")
        groupbox_title_color = settings.value("Dark_Light/QGroupBox_title/color", "white")
        label_color = settings.value("Dark_Light/QLabel/color", "white")
        lineedit_bg = settings.value("Dark_Light/QLineEdit/background-color", "#3b3b3b")
        lineedit_color = settings.value("Dark_Light/QLineEdit/color", "white")
        lineedit_border = settings.value("Dark_Light/QLineEdit/border", "1px solid white")
        lineedit_border_radius = settings.value("Dark_Light/QLineEdit/border-radius", "6px")
        lineedit_padding = settings.value("Dark_Light/QLineEdit/padding", "4px")
        lineedit_focus_bg = settings.value("Dark_Light/QLineEdit_focus/background-color", "#454545")
        lineedit_focus_border = settings.value("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")
        pushbutton_bg = settings.value("Dark_Light/QPushButton/background-color", "#3b3b3b")
        pushbutton_color = settings.value("Dark_Light/QPushButton/color", "white")
        pushbutton_border = settings.value("Dark_Light/QPushButton/border", "1px solid white")
        pushbutton_border_radius = settings.value("Dark_Light/QPushButton/border-radius", "6px")
        pushbutton_padding = settings.value("Dark_Light/QPushButton/padding", "4px 10px")
        pushbutton_hover_bg = settings.value("Dark_Light/QPushButton_hover/background-color", "#4d4d4d")
        pushbutton_pressed_bg = settings.value("Dark_Light/QPushButton_pressed/background-color", "#5c5c5c")
        menu_bg = settings.value("Dark_Light/QMenu/background", "#3a3a3a")
        menu_color = settings.value("Dark_Light/QMenu/color", "white")
        menu_border = settings.value("Dark_Light/QMenu/border", "1px solid #3b3b3b")
        menubar_bg = settings.value("Dark_Light/QMenuBar/background-color", "#3a3a3a")
        menubar_color = settings.value("Dark_Light/QMenuBar/color", "white")
        menubar_item_bg = settings.value("Dark_Light/QMenuBar_item/background", "transparent")
        menubar_item_color = settings.value("Dark_Light/QMenuBar_item/color", "white")
        menubar_item_padding = settings.value("Dark_Light/QMenuBar_item/padding", "4px 10px")
        menubar_item_selected_bg = settings.value("Dark_Light/QMenuBar_item_selected/background-color", "#4d4d4d")

        # === Apply stylesheet to unify QPushButton and QToolButton appearance ===
        self.setStyleSheet(f"""
            /* --- QToolButton styled like QPushButton --- */
            QToolButton {{
                background-color: {pushbutton_bg};
                color: {pushbutton_color};
                border: {pushbutton_border};
                border-radius: {pushbutton_border_radius};
                font-size: 16px;
                font-weight: bold;
                padding: {pushbutton_padding};
                margin: 20px;
            }}
            QToolButton:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QToolButton:pressed {{
                background-color: {pushbutton_pressed_bg};
            }}
            QToolButton::menu-indicator {{
                image: none;
            }}
            QToolButton::arrow {{
                width: 10px;
                height: 10px;
                border-left: 2px solid {pushbutton_color};  /* mismo color que el texto */
                border-top: 2px solid {pushbutton_color};   /* mismo color que el texto */
                transform: rotate(45deg);
                margin-right: 5px;
                margin-top: 5px;
            }}
            /* --- Other widgets --- */
            QWidget {{ background-color: {background_color}; }}
            QTabWidget::pane {{ background-color: {tabwidget_pane_bg}; }}
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
            QGroupBox:title {{ color: {groupbox_title_color}; }}
            QLabel {{ color: {label_color}; }}
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
            QPushButton:hover {{ background-color: {pushbutton_hover_bg}; }}
            QPushButton:pressed {{ background-color: {pushbutton_pressed_bg}; }}
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
        """)

        # === Store VNA device reference ===
        self.vna_device = vna_device

        logging.info("[welcome_windows.__init__] Initializing welcome window")

        # === Set application icon ===
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

        self.setWindowTitle("Welcome")
        self.setGeometry(100, 100, 1000, 600)

        # === Central widget and main layout ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Welcome label ---
        welcome_label = QLabel("Welcome to the NanoVNA UTN Toolkit!")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        main_layout.addWidget(welcome_label, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # --- Horizontal buttons layout ---
        middle_layout = QVBoxLayout()
        middle_layout.addStretch()
        button_layout = QHBoxLayout()

        self.right_button = QPushButton("Calibration Wizard")
        self.bottom_button = QPushButton("Graphics")
        self.right_button.clicked.connect(self.open_calibration_wizard)
        self.bottom_button.clicked.connect(self.graphics_clicked)

        self.right_button.setFixedHeight(45)
        self.bottom_button.setFixedHeight(45)
        self.right_button.setStyleSheet("font-size: 16px; margin: 10px;")
        self.bottom_button.setStyleSheet("font-size: 16px; margin: 10px;")

        button_layout.addStretch()
        button_layout.addWidget(self.right_button)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.bottom_button)
        button_layout.addStretch()

        middle_layout.addLayout(button_layout)
        middle_layout.addStretch()
        main_layout.addLayout(middle_layout)

        self.left_button = QToolButton()
        self.left_button.setFixedSize(200, 200)
        self.left_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.left_button.setPopupMode(QToolButton.InstantPopup)  # evita que se mueva la flecha
        self.left_button.setAutoRaise(False)  # evita look transparente

        # Aplica colores del botón igual que QPushButton
        self.left_button.setStyleSheet(f"""
            QToolButton {{
                background-color: {pushbutton_bg};
                color: {pushbutton_color};
                border: {pushbutton_border};
                border-radius: {pushbutton_border_radius};
                font-size: 16px;
                font-weight: bold;
                padding: {pushbutton_padding};
            }}
            QToolButton:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QToolButton:pressed {{
                background-color: {pushbutton_pressed_bg};
            }}
            QToolButton::menu-indicator {{
                image: none;
            }}
            QToolButton::arrow {{
                width: 10px;
                height: 10px;
                border-left: 2px solid {pushbutton_color};
                border-top: 2px solid {pushbutton_color};
                transform: rotate(45deg);
                margin-right: 5px;
                margin-top: 5px;
            }}
            /* === Corrige el fondo azul y mantiene el borde === */
            QToolButton::menu-button {{
                background-color: {pushbutton_bg};
                border-left: {pushbutton_border};  /* restaura el borde */
                border-top: none;
                border-right: none;
                border-bottom: none;
                border-top-right-radius: {pushbutton_border_radius};
                border-bottom-right-radius: {pushbutton_border_radius};
                width: 20px;
            }}
        """)
        # Crear flecha personalizada usando el color de fondo del botón
        arrow_pixmap = QPixmap(12, 12)
        arrow_pixmap.fill(Qt.transparent)
        painter = QPainter(arrow_pixmap)
        pen = QPen(QColor(pushbutton_bg))  # color igual al fondo del botón
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(2, 4, 6, 8)
        painter.drawLine(6, 8, 10, 4)
        painter.end()

        # Usar la flecha como icono del botón
        self.left_button.setArrowType(Qt.NoArrow)
        self.left_button.setIcon(QIcon(arrow_pixmap))
        self.left_button.setIconSize(arrow_pixmap.size())
        self.left_button.setPopupMode(QToolButton.InstantPopup)
        self.left_button.setAutoRaise(False)


        # --- Load calibration kits ---
        settings_calibration = QSettings(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "Calibration_Config", "calibration_config.ini"),
            QSettings.IniFormat
        )
        kit_groups = [g for g in settings_calibration.childGroups() if g.startswith("Kit_")]
        kit_names = [settings_calibration.value(f"{g}/kit_name", "") for g in kit_groups]

        # --- Get current calibration ---
        calibration_name = settings_calibration.value("Calibration/Name", "No Calibration")
        if "_" in calibration_name:
            calibration_name = calibration_name.rsplit("_", 1)[0]

        # --- Setup QToolButton text and menu ---
        if len(kit_names) <= 1:
            self.left_button.setText(f"Calibration:\n{kit_names[0] if kit_names else 'No Calibration'}")
            self.left_button.setMenu(None)
        else:
            self.left_button.setText(f"Calibration:\n{calibration_name if calibration_name else kit_names[0]}")
            self.left_button.setPopupMode(QToolButton.MenuButtonPopup)
            menu = QMenu(self.left_button)
            for name in kit_names:
                action = QAction(name, self.left_button)
                menu.addAction(action)

            # --- Update text when a kit is selected ---
            def on_kit_selected(action):
                selected_name = action.text()
                self.left_button.setText(f"Calibration:\n{selected_name}")
                # Save selected kit to settings
                for g in kit_groups:
                    name = settings_calibration.value(f"{g}/kit_name", "")
                    if name == selected_name:
                        settings_calibration.beginGroup("Calibration")
                        settings_calibration.setValue("Name", f"{selected_name}_{g.split('_')[1]}")
                        settings_calibration.endGroup()
                        settings_calibration.sync()
                        break

            menu.triggered.connect(on_kit_selected)
            self.left_button.setMenu(menu)

        # --- Add calibration button to layout ---
        main_layout.addWidget(self.left_button, alignment=Qt.AlignHCenter | Qt.AlignBottom)

    # --- Open calibration wizard window ---
    def open_calibration_wizard(self):
        logging.info("[welcome_windows.open_calibration_wizard] Opening calibration wizard")
        if self.vna_device:
            self.welcome_windows = CalibrationWizard(self.vna_device)
        else:
            self.welcome_windows = CalibrationWizard()
        self.welcome_windows.show()
        self.close()

    # --- Open graphics window ---
    def graphics_clicked(self):
        if self.vna_device:
            graphics_window = NanoVNAGraphics(vna_device=self.vna_device)
        else:
            graphics_window = NanoVNAGraphics()
        graphics_window.show()
        self.close()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ventana = NanoVNAWelcome()
    ventana.show()
    sys.exit(app.exec())
