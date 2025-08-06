import sys
import os
import logging
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QVBoxLayout, 
                            QWidget, QTextEdit, QPushButton, QHBoxLayout)
from PySide6.QtGui import QIcon, QTextCursor, QFont

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the compatibility layer first
from NanoVNA_UTN_Toolkit.compat import apply_patches

# Apply compatibility patches
apply_patches()

try:
    # Now import the original modules after applying patches
    from NanoVNA_UTN_Toolkit.Hardware.Hardware import get_interfaces, get_VNA
    from NanoVNA_UTN_Toolkit.utils import check_required_packages, cleanup_routine
except ImportError as e:
    logging.error("Failed to import required modules: %s", e)
    logging.info("Please make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable debug logging for the compatibility module
logging.getLogger('NanoVNA_UTN_Toolkit.compat').setLevel(logging.DEBUG)

def main():
    app = QApplication(sys.argv)
    window = NanoVNAStatusApp()
    window.show()
    sys.exit(app.exec())

class NanoVNAStatusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vna = None
        self.init_ui()
        self.check_connection()
        
        # Configurar un temporizador para verificar la conexión periódicamente
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_connection)
        self.timer.start(3000)  # Verificar cada 3 segundos

    def init_ui(self):
        """Inicializar la interfaz de usuario."""
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle("NanoVNA Connection Status")
        self.setGeometry(100, 100, 600, 400)
        
        # Widget principal y layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Etiqueta de estado
        self.status_label = QLabel("Estado: Desconectado")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Información del dispositivo
        self.device_info = QLabel("Dispositivo: No detectado")
        layout.addWidget(self.device_info)
        
        # Salida de consola
        console_label = QLabel("Salida de consola:")
        layout.addWidget(console_label)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Courier", 10))
        layout.addWidget(self.console, 1)  # Hacer la consola expansible
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.clicked.connect(self.check_connection)
        button_layout.addWidget(self.refresh_btn)
        
        clear_btn = QPushButton("Limpiar consola")
        clear_btn.clicked.connect(self.console.clear)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Configurar ventana
        self.show()
    
    def log_message(self, message):
        """Agregar un mensaje a la salida de la consola."""
        self.console.append(f"> {message}")
        self.console.moveCursor(QTextCursor.End)
        logger.info(message)
    
    def check_connection(self):
        """Verificar dispositivos NanoVNA conectados y actualizar la interfaz."""
        try:
            # Verificar interfaces conectadas
            interfaces = get_interfaces()
            
            if not interfaces:
                self.status_label.setText("Estado: Desconectado")
                self.status_label.setStyleSheet(
                    "color: red; font-size: 16px; font-weight: bold;"
                )
                self.device_info.setText("Dispositivo: No detectado")
                self.log_message("No se detectó ningún dispositivo NanoVNA conectado.")
                return
            
            # Obtener la primera interfaz disponible
            iface = interfaces[0]
            self.log_message(f"Dispositivo detectado en: {iface}")
            
            try:
                # Cerrar la conexión anterior si existe
                if hasattr(self, 'vna') and self.vna is not None:
                    try:
                        self.vna.disconnect()
                    except Exception as e:
                        self.log_message(f"Error al cerrar la conexión anterior: {str(e)}")
                
                # Intentar conectar al VNA
                self.log_message(f"Intentando conectar a {iface.port}...")
                self.vna = get_VNA(iface)
                
                if self.vna:
                    try:
                        # Verificar si el dispositivo está realmente conectado
                        if not hasattr(self.vna, 'connected') or not self.vna.connected:
                            self.log_message("Error: No se pudo establecer conexión con el dispositivo")
                            self.status_label.setText("Estado: Error de conexión")
                            self.status_label.setStyleSheet("color: orange; font-size: 16px; font-weight: bold;")
                            return
                            
                        self.status_label.setText("Estado: Conectado")
                        self.status_label.setStyleSheet(
                            "color: green; font-size: 16px; font-weight: bold;"
                        )
                        
                        # Obtener información del dispositivo
                        info = self.vna.readFirmware()
                        # Parsear la información del firmware que viene como string
                        device_name = "NanoVNA"
                        fw_version = "Desconocida"
                        
                        # Intentar extraer información del firmware del string
                        if info:
                            # Buscar líneas que contengan información de hardware y versión
                            lines = info.split('\n')
                            for line in lines:
                                if 'HW:' in line:
                                    device_name = line.split('HW:')[-1].strip()
                                elif 'FW:' in line:
                                    fw_version = line.split('FW:')[-1].strip()
                        
                        device_info = f"Dispositivo: {device_name} - Versión: {fw_version}"
                        self.device_info.setText(device_info)
                        
                        self.log_message(f"Conexión exitosa con {device_name}")
                        self.log_message(f"Versión del firmware: {fw_version}")
                        
                    except Exception as e:
                        self.status_label.setText("Estado: Error de comunicación")
                        self.status_label.setStyleSheet("color: orange; font-size: 16px; font-weight: bold;")
                        self.log_message(f"Error al comunicarse con el dispositivo: {str(e)}")
                        if hasattr(self.vna, 'disconnect'):
                            try:
                                self.vna.disconnect()
                            except:
                                pass
                        self.vna = None
                        
            except Exception as e:
                self.status_label.setText("Estado: Error de conexión")
                self.status_label.setStyleSheet("color: orange; font-size: 16px; font-weight: bold;")
                self.log_message(f"Error al conectar con el dispositivo: {str(e)}")
                if hasattr(self, 'vna') and self.vna is not None:
                    try:
                        self.vna.disconnect()
                    except:
                        pass
                    self.vna = None
                
        except Exception as e:
            self.log_message(f"Error al verificar la conexión: {str(e)}")
            if hasattr(self, 'vna') and self.vna is not None:
                try:
                    self.vna.disconnect()
                except:
                    pass
                self.vna = None

def run_app():
    """Ejecuta la aplicación gráfica."""
    try:
        app = QApplication(sys.argv)
        window = NanoVNAStatusApp()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Error al ejecutar la aplicación: {e}")
        input("Presiona Enter para cerrar el programa...")
        sys.exit(1)

def main():
    check_required_packages()
    run_app()
    cleanup_rutine()

if __name__ == "__main__":
    main()
