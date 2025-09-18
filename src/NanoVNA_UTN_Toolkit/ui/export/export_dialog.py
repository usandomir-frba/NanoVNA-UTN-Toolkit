"""
Export Dialog for Graphics Window
Provides functionality to export graph data and images in various formats.
"""

import io
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QMessageBox, QApplication, QFileDialog)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ExportDialog(QDialog):
    """Dialog for exporting graph data and images."""
    
    def __init__(self, parent=None, figure=None):
        super().__init__(parent)
        self.figure = figure
        self.parent_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface for the export dialog."""
        self.setWindowTitle("Export Graph")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Preview section
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)
        
        # Create and add preview image
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: white;")
        self.preview_label.setMinimumHeight(300)
        
        # Generate static preview
        preview_pixmap = self.create_static_preview()
        if preview_pixmap:
            # Scale preview to fit while maintaining aspect ratio
            scaled_pixmap = preview_pixmap.scaled(
                self.preview_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
        
        layout.addWidget(self.preview_label)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        
        # Copy to clipboard button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        buttons_layout.addWidget(copy_button)
        
        # Save as image button
        save_image_button = QPushButton("Save as Image")
        save_image_button.clicked.connect(self.save_as_image)
        buttons_layout.addWidget(save_image_button)
        
        # Save as CSV button
        save_csv_button = QPushButton("Save as CSV")
        save_csv_button.clicked.connect(self.save_as_csv)
        buttons_layout.addWidget(save_csv_button)
        
        layout.addLayout(buttons_layout)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_layout.addWidget(close_button)
        layout.addLayout(close_layout)

    def create_static_preview(self):
        """Create a static preview image of the graph."""
        if not self.figure:
            return None
            
        try:
            # Hide interactive elements (sliders) but keep cursors visible
            interactive_elements = []
            for ax in self.figure.axes:
                # Hide slider axes (usually have very small height/width)
                if hasattr(ax, 'get_position'):
                    pos = ax.get_position()
                    if pos.height < 0.1 or pos.width < 0.1:  # Likely a slider
                        if ax.get_visible():
                            interactive_elements.append((ax, True))
                            ax.set_visible(False)
                        continue
            
            # Force canvas update
            self.figure.canvas.draw()
            
            # Generate preview image
            buf = io.BytesIO()
            self.figure.savefig(buf, format='png', dpi=100, 
                    facecolor='white', edgecolor='none')
            buf.seek(0)
            
            # Restore interactive elements
            for element, was_visible in interactive_elements:
                element.set_visible(was_visible)
            
            # Force canvas redraw after restoring elements
            self.figure.canvas.draw()
            
            # Create QPixmap from bytes
            pixmap = QPixmap()
            if pixmap.loadFromData(buf.getvalue()):
                return pixmap
                
        except Exception as e:
            print(f"Preview generation error: {e}")
            
        return None

    def copy_to_clipboard(self):
        """Copy the graph image to clipboard with fresh high-resolution capture."""
        try:
            # Create a COMPLETELY NEW figure with high DPI for clipboard
            # Force a large size in inches (10x8 inches at 300 DPI = 3000x2400 pixels)
            # This ensures we get truly high resolution output
            fig_copy = plt.figure(figsize=(10, 8), dpi=300)
            
            # Copy all axes from original figure to the new high-DPI figure
            for i, original_ax in enumerate(self.figure.axes):
                # Skip slider axes (small height/width)
                if hasattr(original_ax, 'get_position'):
                    pos = original_ax.get_position()
                    if pos.height < 0.1 or pos.width < 0.1:  # Likely a slider
                        continue
                
                # Create new axis in the high-DPI figure
                new_ax = fig_copy.add_subplot(1, 1, 1)
                
                # Copy all lines (including cursors and main plot)
                for line in original_ax.lines:
                    if line.get_visible():
                        # Scale line width for high resolution
                        scaled_linewidth = line.get_linewidth() * 2  # Scale up for high-res
                        scaled_markersize = line.get_markersize() * 2 if line.get_markersize() else 0
                        
                        new_ax.plot(line.get_xdata(), line.get_ydata(),
                                  color=line.get_color(),
                                  linewidth=scaled_linewidth,
                                  linestyle=line.get_linestyle(),
                                  marker=line.get_marker(),
                                  markersize=scaled_markersize,
                                  markerfacecolor=line.get_markerfacecolor(),
                                  markeredgecolor=line.get_markeredgecolor())
                
                # Copy patches (for Smith charts)
                for patch in original_ax.patches:
                    if hasattr(patch, 'center') and hasattr(patch, 'radius'):
                        import matplotlib.patches as mpatches
                        new_patch = mpatches.Circle(patch.center, patch.radius,
                                                  fill=patch.get_fill(),
                                                  facecolor=patch.get_facecolor(),
                                                  edgecolor=patch.get_edgecolor(),
                                                  linewidth=patch.get_linewidth())
                        new_ax.add_patch(new_patch)
                
                # Copy axis properties
                new_ax.set_xlim(original_ax.get_xlim())
                new_ax.set_ylim(original_ax.get_ylim())
                new_ax.set_xlabel(original_ax.get_xlabel())
                new_ax.set_ylabel(original_ax.get_ylabel())
                new_ax.set_title(original_ax.get_title())
                
                # Copy grid settings
                new_ax.grid(original_ax.get_xgridlines()[0].get_visible() if original_ax.get_xgridlines() else False)
                
                # For Smith charts, set equal aspect ratio
                if "Smith" in original_ax.get_title() or len(original_ax.patches) > 10:
                    new_ax.set_aspect('equal')
                
                break  # Only copy the first main axis
            
            # Generate HIGH RESOLUTION capture
            buf_clipboard = io.BytesIO()
            fig_copy.savefig(buf_clipboard, 
                           format='png', 
                           dpi=300,  # Force high DPI
                           bbox_inches='tight', 
                           facecolor='white', 
                           edgecolor='none')
            buf_clipboard.seek(0)
            
            # Clean up the temporary figure
            plt.close(fig_copy)
            
            # Create QPixmap from the high-resolution data
            pixmap = QPixmap()
            if pixmap.loadFromData(buf_clipboard.getvalue()):
                # Verify we have a high-resolution image
                image_size = pixmap.size()
                print(f"High-res capture: {image_size.width()}x{image_size.height()}")
                
                # Copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(pixmap)
                
                QMessageBox.information(self, "Copy", 
                    f"Graph copied to clipboard!")
            else:
                QMessageBox.warning(self, "Copy Error", "Failed to create image.")
            
        except Exception as e:
            import traceback
            print(f"Clipboard error: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Copy Error", f"Failed to copy image to clipboard: {str(e)}")

    def save_as_image(self):
        """Save the graph as an image file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Graph as Image", 
                "graph.png", 
                "PNG Files (*.png);;JPG Files (*.jpg);;PDF Files (*.pdf);;SVG Files (*.svg)"
            )
            
            if file_path:
                # Clonar la figura completa
                import copy
                fig_copy = copy.deepcopy(self.figure)
                
                # Ajustar DPI y tamaño
                fig_copy.set_size_inches(10, 8)
                
                # Ajustar límites y aspecto para cada eje
                for ax in fig_copy.axes:
                    if "Smith" in ax.get_title() or len(ax.patches) > 10:
                        ax.set_aspect('equal')
                    
                    # Opcional: recortar ejes muy pequeños (sliders)
                    pos = ax.get_position()
                    new_pos = [pos.x0, pos.y0 + 0.02, pos.width - 0.02, pos.height - 0.02]
                    ax.set_position(new_pos)
                    if pos.height < 0.1 or pos.width < 0.1:
                        fig_copy.delaxes(ax)
                
                # Guardar
                fig_copy.savefig(file_path, dpi=300, facecolor='white', edgecolor='none')
                plt.close(fig_copy)
                
                QMessageBox.information(self, "Save", f"Graph saved as: {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save image: {str(e)}")

    def save_as_csv(self):
        """Save the graph data as CSV."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Graph Data as CSV", 
                "graph_data.csv", 
                "CSV Files (*.csv)"
            )
            
            if file_path:
                # Extract data from the graph
                csv_data = []
                headers = []
                
                for ax in self.figure.axes:
                    # Skip slider axes
                    if hasattr(ax, 'get_position'):
                        pos = ax.get_position()
                        if pos.height < 0.1 or pos.width < 0.1:
                            continue
                    
                    for i, line in enumerate(ax.lines):
                        if line.get_visible() and len(line.get_xdata()) > 1:  # Skip single-point markers
                            x_data = line.get_xdata()
                            y_data = line.get_ydata()
                            
                            # Add headers if this is the first line with data
                            if not headers:
                                headers = ['X', 'Y']
                                csv_data = [[x, y] for x, y in zip(x_data, y_data)]
                            else:
                                # Add additional columns for multiple traces
                                headers.extend([f'X_{i+1}', f'Y_{i+1}'])
                                for j, (x, y) in enumerate(zip(x_data, y_data)):
                                    if j < len(csv_data):
                                        csv_data[j].extend([x, y])
                
                # Write CSV file
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    writer.writerows(csv_data)
                
                QMessageBox.information(self, "Save", f"Graph data saved as: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save CSV: {str(e)}")
