import sys
from src.NanoVNA_UTN_Toolkit.utils import check_required_packages, cleanup_rutine

def run_app():
    """Ejecuta la aplicación gráfica."""
    try:
        from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
        from PyQt5.QtGui import QIcon

        class HelloWorldApp(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowIcon(QIcon("icon.ico"))
                self.setWindowTitle("Hello World - Desktop")
                self.setGeometry(100, 100, 400, 200)
                label = QLabel("Hello World!", self)
                label.setGeometry(150, 80, 200, 40)

        # Ejecutar la aplicación de escritorio
        app = QApplication(sys.argv)
        window = HelloWorldApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error al ejecutar la aplicación: {e}")
        input("Presiona Enter para cerrar el programa...")
        sys.exit(1)

def main():
    check_required_packages()
    run_app()
    cleanup_rutine()

if __name__ == "__main__":
    main()
