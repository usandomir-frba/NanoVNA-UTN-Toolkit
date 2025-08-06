import sys
import subprocess
import importlib.metadata
import time
import os
import shutil

def check_required_packages():
    """Verifica e instala los paquetes necesarios si no están presentes."""

    # Si el programa está compilado, no intentamos instalar dependencias
    if getattr(sys, 'frozen', False):
        print("Ejecutando el programa. No cierre esta ventana!")
        return

    required_packages = ['PyQt5']
    for package in required_packages:
        retries = 3  # Número de reintentos
        while retries > 0:
            try:
                # Verificar si el paquete está instalado
                importlib.metadata.version(package)
                break  # Si el paquete está instalado, salir del bucle
            except importlib.metadata.PackageNotFoundError:
                print(f"El paquete {package} no está instalado. Instalándolo ahora...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                except subprocess.CalledProcessError as e:
                    print(f"Error al instalar el paquete {package}: {e}")
                    retries -= 1
                    if retries > 0:
                        print(f"Reintentando... ({3 - retries} intentos restantes)")
                        time.sleep(2)  # Esperar 2 segundos antes de reintentar
                    else:
                        print(f"No se pudo instalar el paquete {package} después de varios intentos.")
                        input("Presiona Enter para cerrar el programa...")
                        sys.exit(1)

def cleanup_rutine():
    """Realiza una limpieza de rutina al cerrar el programa."""
    print("Cerrando el programa. Realizando limpieza de rutina...")
    TO_DELETE = [
        "build",
        "dist",
        "*.spec",
        "__pycache__",
        ".pytest_cache",
        "*.egg-info",
        ".mypy_cache",
        ".eggs",
    ]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    for pattern in TO_DELETE:
        for root, dirs, files in os.walk(base_dir):
            # Eliminar directorios
            for dir_name in dirs:
                if dir_name == pattern or dir_name.endswith(pattern.strip("*")):
                    dir_path = os.path.join(root, dir_name)
                    print(f"Eliminando directorio: {dir_path}")
                    shutil.rmtree(dir_path, ignore_errors=True)
            # Eliminar archivos
            for file_name in files:
                if file_name.endswith(pattern.strip("*")):
                    file_path = os.path.join(root, file_name)
                    print(f"Eliminando archivo: {file_path}")
                    os.remove(file_path)
    print("Limpieza completa. El programa se cerrará ahora.")
