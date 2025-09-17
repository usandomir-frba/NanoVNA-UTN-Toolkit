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
from PySide6.QtGui import QIcon

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
        
        # Store VNA device reference
        self.vna_device = vna_device
        
        # Log graphics window initialization
        logging.info("[graphics_window.__init__] Initializing graphics window")
        if vna_device:
            device_type = type(vna_device).__name__
            logging.info(f"[graphics_window.__init__] VNA device provided: {device_type}")
        else:
            logging.warning("[graphics_window.__init__] No VNA device provided")
            
        logging.info(f"[graphics_window.__init__] S11 data: {'Available' if s11 is not None else 'None'}")
        logging.info(f"[graphics_window.__init__] S21 data: {'Available' if s21 is not None else 'None'}")
        logging.info(f"[graphics_window.__init__] Frequency data: {'Available' if freqs is not None else 'None'}")
        logging.info(f"[graphics_window.__init__] Graph configuration - Type: {left_graph_type}, S-param: {left_s_param}")

        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui","graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        graph_type_tab1 = settings.value("Tab1/GraphType1", "Smith Diagram")
        s_param_tab1    = settings.value("Tab1/SParameter", "S11")

        graph_type_tab2 = settings.value("Tab2/GraphType2", "Magnitude")
        s_param_tab2    = settings.value("Tab2/SParameter", "S11")

        trace_color1 = settings.value("Graphic1/TraceColor", "blue")
        marker_color1 = settings.value("Graphic1/MarkerColor", "blue")

        trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
        marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))

        trace_color2 = settings.value("Graphic2/TraceColor", "blue")
        marker_color2 = settings.value("Graphic2/MarkerColor", "blue")

        trace_size2 = int(settings.value("Graphic2/TraceWidth", 2))
        marker_size2 = int(settings.value("Graphic2/MarkerWidth", 6))

        self.left_graph_type  = graph_type_tab1
        self.left_s_param     = s_param_tab1
        self.right_graph_type = graph_type_tab2
        self.right_s_param    = s_param_tab2

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
        file_menu.addAction("Export")

        graphics_markers = edit_menu.addAction("Graphics/Markers")
        graphics_markers.triggered.connect(lambda: self.edit_graphics_markers())

        light_dark_mode = edit_menu.addAction("Light Mode 🔆")

        self.is_dark_mode = False  

        def toggle_menu_dark_mode():
            if self.is_dark_mode:
                light_dark_mode.setText("Light Mode 🔆")
                self.is_dark_mode = False
                #toggle_dark_mode(tabs, force_light=True)
            else:
                light_dark_mode.setText("Dark Mode 🌙")
                self.is_dark_mode = True
                #toggle_dark_mode(tabs, force_light=True)

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

        # Initialize sweep configuration and auto-run sweep
        self.load_sweep_configuration()
        
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
        self.sweep_info_label.setStyleSheet("color: gray; font-size: 12px;")
        
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
                graph_type=graph_type_tab1, 
                s_param=s_param_tab1, 
                tracecolor=trace_color1,
                markercolor=marker_color1,
                linewidth=trace_size1,
                markersize=marker_size1   
            )

        # =================== RIGHT PANEL (EMPTY) ===================
        self.right_panel, self.fig_right, self.ax_right, self.canvas_right, \
        self.slider_right, self.cursor_right, self.labels_right, self.update_right_cursor, self.update_right_data = \
            create_right_panel(
                S_data=None,  # Force empty
                freqs=None,   # Force empty
                graph_type=graph_type_tab2, 
                s_param=s_param_tab2,
                tracecolor=trace_color2,
                markercolor=marker_color2,
                linewidth=trace_size2,
                markersize=marker_size2
            )

        # =================== PANELS LAYOUT ===================
        panels_layout = QHBoxLayout()
        panels_layout.addWidget(self.left_panel, 1)
        panels_layout.addWidget(self.right_panel, 1)
        main_layout_vertical.addLayout(panels_layout)

        self.markers = [
            {"cursor": self.cursor_left, "slider": self.slider_left, "label": self.labels_left, "update_cursor": self.update_cursor},
            {"cursor": self.cursor_right, "slider": self.slider_right, "label": self.labels_right, "update_cursor": self.update_right_cursor}
        ]
        
        # Clear all marker information fields until first sweep is completed
        self._clear_all_marker_fields()

    def _clear_all_marker_fields(self):
        """Clear all marker information fields and graphs to show empty state."""
        logging.info("[graphics_window._clear_all_marker_fields] Clearing all marker fields and graphs for initial empty state")
        
        # Clear left panel marker fields
        if hasattr(self, 'labels_left') and self.labels_left:
            self.labels_left.get("freq", None) and self.labels_left["freq"].setText("--")
            self.labels_left.get("val", None) and self.labels_left["val"].setText("S11: -- + j--")
            self.labels_left.get("mag", None) and self.labels_left["mag"].setText("|S11|: --")
            self.labels_left.get("phase", None) and self.labels_left["phase"].setText("Phase: --")
            self.labels_left.get("z", None) and self.labels_left["z"].setText("Z: -- + j--")
            self.labels_left.get("il", None) and self.labels_left["il"].setText("IL: --")
            self.labels_left.get("vswr", None) and self.labels_left["vswr"].setText("VSWR: --")
            
        # Clear right panel marker fields  
        if hasattr(self, 'labels_right') and self.labels_right:
            self.labels_right.get("freq", None) and self.labels_right["freq"].setText("--")
            self.labels_right.get("val", None) and self.labels_right["val"].setText("S21: -- + j--")
            self.labels_right.get("mag", None) and self.labels_right["mag"].setText("|S21|: --")
            self.labels_right.get("phase", None) and self.labels_right["phase"].setText("Phase: --")
            self.labels_right.get("z", None) and self.labels_right["z"].setText("Z: -- + j--")
            self.labels_right.get("il", None) and self.labels_right["il"].setText("IL: --")
            self.labels_right.get("vswr", None) and self.labels_right["vswr"].setText("VSWR: --")
            
        # Hide cursors initially
        if hasattr(self, 'cursor_left') and self.cursor_left:
            self.cursor_left.set_visible(False)
        if hasattr(self, 'cursor_right') and self.cursor_right:
            self.cursor_right.set_visible(False)
            
        # Clear the actual plots to show empty state
        if hasattr(self, 'ax_left') and self.ax_left:
            self.ax_left.clear()
            self.ax_left.text(0.5, 0.5, 'Waiting for sweep data...', 
                             transform=self.ax_left.transAxes, 
                             ha='center', va='center', fontsize=12, color='gray')
            self.ax_left.set_title('S11 - No Data')
            
        if hasattr(self, 'ax_right') and self.ax_right:
            self.ax_right.clear()
            self.ax_right.text(0.5, 0.5, 'Waiting for sweep data...', 
                              transform=self.ax_right.transAxes, 
                              ha='center', va='center', fontsize=12, color='gray')
            self.ax_right.set_title('S21 - No Data')
            
        # Force canvas redraw
        if hasattr(self, 'canvas_left') and self.canvas_left:
            self.canvas_left.draw()
        if hasattr(self, 'canvas_right') and self.canvas_right:
            self.canvas_right.draw()

    def _reset_markers_after_sweep(self):
        """Reset markers and all marker-dependent information after a sweep completes."""
        logging.info("[graphics_window._reset_markers_after_sweep] Resetting markers after sweep completion")
        
        try:
            # Reset slider positions to leftmost position (index 0) if they exist
            if hasattr(self, 'slider_left') and self.slider_left:
                # Reset left slider to leftmost position (try different methods)
                try:
                    if hasattr(self.slider_left, 'maximum') and hasattr(self.slider_left, 'minimum'):
                        min_range = self.slider_left.minimum()
                        if hasattr(self.slider_left, 'setValue'):
                            self.slider_left.setValue(min_range)
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Reset left slider to leftmost position {min_range}")
                    elif hasattr(self.slider_left, 'set') and hasattr(self.slider_left, 'get_value'):
                        # Alternative method for matplotlib sliders - always start at index 0
                        self.slider_left.set(0)
                        logging.info("[graphics_window._reset_markers_after_sweep] Reset left slider to index 0 (leftmost)")
                except Exception as e:
                    logging.warning(f"[graphics_window._reset_markers_after_sweep] Could not reset left slider: {e}")
            
            if hasattr(self, 'slider_right') and self.slider_right:
                # Reset right slider to leftmost position  
                try:
                    if hasattr(self.slider_right, 'maximum') and hasattr(self.slider_right, 'minimum'):
                        min_range = self.slider_right.minimum()
                        if hasattr(self.slider_right, 'setValue'):
                            self.slider_right.setValue(min_range)
                            logging.info(f"[graphics_window._reset_markers_after_sweep] Reset right slider to leftmost position {min_range}")
                    elif hasattr(self.slider_right, 'set') and hasattr(self.slider_right, 'get_value'):
                        # Alternative method for matplotlib sliders - always start at index 0
                        self.slider_right.set(0)
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
                    
            # Force marker visibility with debug AND fix cursor references
            self._force_marker_visibility()
                    
            logging.info("[graphics_window._reset_markers_after_sweep] Marker reset completed successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window._reset_markers_after_sweep] Error resetting markers: {e}")

    def _force_marker_visibility(self):
        """Force markers to be visible by recreating them directly on axes"""
        
        if hasattr(self, 'cursor_left') and hasattr(self, 'ax_left') and self.cursor_left and self.ax_left:
            try:
                # Get current data
                x_data = self.cursor_left.get_xdata()
                y_data = self.cursor_left.get_ydata()
                
                # Create new cursor directly on the axes
                if hasattr(x_data, '__len__') and hasattr(y_data, '__len__') and len(x_data) > 0 and len(y_data) > 0:
                    try:
                        x_val = float(x_data[0])
                        y_val = float(y_data[0])
                    except (TypeError, IndexError, ValueError):
                        x_val, y_val = 0.0, 0.0
                    
                    new_cursor = self.ax_left.plot(x_val, y_val, 'o', color='red', markersize=5, markeredgecolor='darkred', markeredgewidth=2)[0]
                    self.cursor_left = new_cursor
                    
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
                                    if hasattr(self, 's11') and hasattr(self, 'freqs') and self.s11 is not None and self.freqs is not None and index < len(self.s11) and index < len(self.freqs):
                                        val_complex = self.s11[index]
                                        
                                        # Use Smith diagram coordinates for left cursor
                                        real_part = float(np.real(val_complex))
                                        imag_part = float(np.imag(val_complex))
                                        self.cursor_left.set_data([real_part], [imag_part])
                                        
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
                # Get current data
                x_data = self.cursor_right.get_xdata()
                y_data = self.cursor_right.get_ydata()
                
                # Create new cursor directly on the axes
                if hasattr(x_data, '__len__') and hasattr(y_data, '__len__') and len(x_data) > 0 and len(y_data) > 0:
                    x_val = float(x_data[0])
                    y_val = float(y_data[0])
                    new_cursor = self.ax_right.plot(x_val, y_val, 'o', color='red', markersize=5, markeredgecolor='darkred', markeredgewidth=2)[0]
                    self.cursor_right = new_cursor
                    
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
                                    # Determine which S parameter is being displayed in the right panel
                                    s_data = None
                                    if hasattr(self, 's21') and self.s21 is not None:
                                        s_data = self.s21  # Default to S21 for right panel
                                    elif hasattr(self, 's11') and self.s11 is not None:
                                        s_data = self.s11
                                    
                                    if s_data is not None and hasattr(self, 'freqs') and self.freqs is not None and index < len(s_data) and index < len(self.freqs):
                                        val_complex = s_data[index]
                                        freq = self.freqs[index]
                                        magnitude = abs(val_complex)
                                        
                                        # Use magnitude in dB for right cursor (typical for magnitude plots)
                                        magnitude_db = 20 * np.log10(magnitude) if magnitude > 0 else -120
                                        freq_mhz = float(freq / 1e6)  # Convert to MHz as float
                                        magnitude_db_float = float(magnitude_db)  # Convert to float
                                        self.cursor_right.set_data([freq_mhz], [magnitude_db_float])
                                        
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

        # Ocultar ambos cursors y sliders para la captura
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

        # Restaurar visibilidad original de cursors y sliders
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
        
        if not hasattr(self, 'sweep_options_window') or self.sweep_options_window is None:
            logging.info("[graphics_window.open_sweep_options] Creating new sweep options window")
            self.sweep_options_window = SweepOptionsWindow(self, vna_device)
        else:
            logging.info("[graphics_window.open_sweep_options] Reusing existing sweep options window")
            
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
        menu.addAction("Copiar")
        menu.addAction("Pegar")
        menu.addAction("Eliminar")

        selected_action = menu.exec(event.globalPos())

        if selected_action == view_menu:
            self.open_view()
        elif selected_action == marker1_action:
            self.show_marker1 = not self.show_marker1
            self.toggle_marker_visibility(0, self.show_marker1)
        elif selected_action == marker2_action:
            self.show_marker2 = not self.show_marker2
            self.toggle_marker_visibility(1, self.show_marker2)

    # =================== MARKERS ==================

    def edit_graphics_markers(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.edit_graphics_window import EditGraphics
        self.edit_graphics_window = EditGraphics(nano_window=self) 
        self.edit_graphics_window.show()

    # =================== VIEW ==================

    def open_view(self):
        from NanoVNA_UTN_Toolkit.ui.graphics_windows.view_window import View
        if not hasattr(self, 'view_window') or self.view_window is None:
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
                edit_value.setText(f"{self.freqs[0]*1e-6:.2f}")
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
            actual_dir = os.path.dirname(os.path.dirname(__file__))
            sweep_config_path = os.path.join(actual_dir, "ui", "sweep_window", "config", "config.ini")
            
            if os.path.exists(sweep_config_path):
                settings = QSettings(sweep_config_path, QSettings.Format.IniFormat)
                
                self.start_freq_hz = int(float(str(settings.value("Frequency/StartFreqHz", 50000))))
                self.stop_freq_hz = int(float(str(settings.value("Frequency/StopFreqHz", 1.5e9))))
                self.segments = int(str(settings.value("Frequency/Segments", 101)))
                
                # Update info label if it exists
                if hasattr(self, 'sweep_info_label'):
                    self.update_sweep_info_label()
                
                logging.info(f"[graphics_window.load_sweep_configuration] Loaded sweep config: {self.start_freq_hz/1e6:.3f} MHz - {self.stop_freq_hz/1e6:.3f} MHz, {self.segments} points")
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
            freq_start_str = f"{self.start_freq_hz/1e6:.3f} MHz" if self.start_freq_hz >= 1e6 else f"{self.start_freq_hz/1e3:.1f} kHz"
            freq_stop_str = f"{self.stop_freq_hz/1e6:.0f} MHz" if self.stop_freq_hz >= 1e6 else f"{self.stop_freq_hz/1e3:.1f} kHz"
            
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
            # Clear all graphics and marker information immediately when sweep starts
            logging.info("[graphics_window.run_sweep] Clearing graphics and markers before starting sweep")
            self._clear_all_marker_fields()
            
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
            
            # Update plots with new data
            self.update_plots_with_new_data()
            self.sweep_progress_bar.setValue(100)
            QApplication.processEvents()
            
            # Reset markers and all marker-dependent information after new sweep
            self._reset_markers_after_sweep()
            
            # Success message
            success_msg = f"Sweep completed successfully.\n{len(freqs)} data points acquired.\nFrequency range: {freqs[0]/1e6:.3f} - {freqs[-1]/1e6:.3f} MHz"
            logging.info(f"[graphics_window.run_sweep] {success_msg}")
            
            # Reset UI after short delay to show 100% completion
            QTimer.singleShot(500, self._reset_sweep_ui)
            
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

    def update_plots_with_new_data(self):
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
            trace_size1 = int(settings.value("Graphic1/TraceWidth", 2))
            marker_size1 = int(settings.value("Graphic1/MarkerWidth", 6))
            
            trace_color2 = settings.value("Graphic2/TraceColor", "blue")
            marker_color2 = settings.value("Graphic2/MarkerColor", "blue")
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
                linewidth=trace_size2,
                markersize=marker_size2
            )
            
            # Update data references in cursor functions
            logging.info("[graphics_window.update_plots_with_new_data] Updating cursor data references")
            if hasattr(self, 'update_left_data') and self.update_left_data:
                self.update_left_data(s_data_left, self.freqs)
            if hasattr(self, 'update_right_data') and self.update_right_data:
                self.update_right_data(s_data_right, self.freqs)
            
            # Force redraw
            self.canvas_left.draw()
            self.canvas_right.draw()
            
            logging.info("[graphics_window.update_plots_with_new_data] Plots updated successfully")
            
        except Exception as e:
            logging.error(f"[graphics_window.update_plots_with_new_data] Error updating plots: {e}")
    
    def _recreate_single_plot(self, ax, fig, s_data, freqs, graph_type, s_param, 
                             tracecolor, markercolor, linewidth, markersize):
        """Recreate a single plot with new data."""
        try:
            import skrf as rf
            from matplotlib.lines import Line2D
            
            if graph_type == "Smith Diagram":
                # Create network object for Smith chart
                ntw = rf.Network(frequency=freqs, s=s_data[:, np.newaxis, np.newaxis], z0=50)
                ntw.plot_s_smith(ax=ax, draw_labels=True)
                ax.legend([Line2D([0],[0], color=tracecolor)], [s_param], 
                         loc='upper left', bbox_to_anchor=(-0.17,1.14))
                
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
                ax.set_xlabel('Frequency (MHz)')
                ax.set_ylabel('Magnitude (dB)')
                ax.set_title(f'{s_param} Magnitude')
                ax.grid(True)
                
            elif graph_type == "Phase":
                # Plot phase
                phase_deg = np.angle(s_data) * 180 / np.pi
                ax.plot(freqs / 1e6, phase_deg, color=tracecolor, linewidth=linewidth)
                ax.set_xlabel('Frequency (MHz)')
                ax.set_ylabel('Phase (degrees)')
                ax.set_title(f'{s_param} Phase')
                ax.grid(True)
                
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
            fig.tight_layout()
            
        except Exception as e:
            logging.error(f"[graphics_window._recreate_single_plot] Error recreating plot: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NanoVNAGraphics()
    window.show()
    sys.exit(app.exec())
