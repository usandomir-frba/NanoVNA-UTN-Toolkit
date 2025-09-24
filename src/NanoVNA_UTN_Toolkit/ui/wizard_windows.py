import sys
import logging
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox
)
from PySide6.QtGui import QIcon, QColor
from PySide6.QtCore import Qt, QSettings

# Import NanoVNAGraphics for the final step
try:
    from NanoVNA_UTN_Toolkit.ui.graphics_window import NanoVNAGraphics
except ImportError as e:
    logging.error("Failed to import NanoVNAGraphics: %s", e)
    NanoVNAGraphics = None  # Safe fallback


class CalibrationWizard(QMainWindow):
    def __init__(self, vna_device=None):
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

        # Container that keeps content at the top
        top_container = QVBoxLayout()
        top_container.setAlignment(Qt.AlignTop)
        top_container.addSpacing(30)  # small margin from top

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

        # Add the container to the main content layout
        self.content_layout.addLayout(top_container)

        # Hide back button on first screen
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

    # --- Step definitions (each step es único) ---------------------------------
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

    # Podes agregar pasos únicos para Enhanced-Response y 1-Path 2-Port de la misma forma

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
        """Show the given step (unique QLabel) top-right."""
        self.clear_content()

        steps = self.get_steps_for_method()

        top_wrapper = QVBoxLayout()
        top_wrapper.setAlignment(Qt.AlignTop)
        top_wrapper.addSpacing(10)

        row = QHBoxLayout()

        # get the QLabel for this step
        if step <= len(steps):
            step_label = steps[step - 1]()
        else:
            step_label = QLabel("Calibrated!")
            step_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
            step_label.setAlignment(Qt.AlignRight | Qt.AlignTop)

        row.addWidget(step_label)
        row.addStretch()  # empuja el label hacia la derecha
        top_wrapper.addLayout(row)
        self.content_layout.addLayout(top_wrapper)

        self.current_step = step
        self.back_button.setVisible(step > 0)

        # Configure next button
        if step > len(steps):
            self.next_button.setText("Finish")
            try:
                self.next_button.clicked.disconnect()
            except Exception:
                pass
            self.next_button.clicked.connect(self.finish_wizard)
        else:
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
        else:
            self.show_step_screen(self.current_step - 1)

    def finish_wizard(self):
        logging.info("Opening NanoVNAGraphics window")
        if NanoVNAGraphics:
            if self.vna_device:
                graphics_window = NanoVNAGraphics(vna_device=self.vna_device)
            else:
                graphics_window = NanoVNAGraphics()
            graphics_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = CalibrationWizard()
    wizard.show()
    sys.exit(app.exec())
