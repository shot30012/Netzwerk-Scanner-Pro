# main.py - Vollständige Version mit GUI und Build-Logik

import sys
import os
import csv
import platform
import shutil
import subprocess
from typing import List, Tuple, Optional, Callable

# PySide6 Imports
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Qt, QSize, QThread, Slot
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QListWidget, QProgressBar,
    QRadioButton, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)

# Eigene Engine-Imports
# Stellen Sie sicher, dass eine scanner_engine.py existiert und die Funktionen enthält
try:
    from scanner_engine import (
        get_network_info, discover_hosts, scan_single_port, parse_ports, check_nmap_availability
    )
except ImportError:
    print("WARNUNG: scanner_engine.py nicht gefunden. Verwende Dummy-Funktionen.")
    def get_network_info(): return ("127.0.0.1", "127.0.0.1")
    def discover_hosts(target, signal, stop_flag): pass
    def scan_single_port(ip, port): return None
    def parse_ports(ports_str): return []
    def check_nmap_availability(): return True


def resource_path(relative_path):
    """ Ermittelt den korrekten Pfad zu Ressourcen, funktioniert für Skript und .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Dark Style Theme für die Anwendung
DARK_STYLE = """
    QWidget { background-color: #2b2b2b; color: #f0f0f0; font-family: Segoe UI, Arial, sans-serif; }
    QGroupBox { font-weight: bold; border: 1px solid #444; border-radius: 4px; margin-top: 10px; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
    QMainWindow { background-color: #1e1e1e; }
    QLineEdit, QTableWidget, QListWidget, QProgressBar { background-color: #3c3c3c; border: 1px solid #555; border-radius: 4px; padding: 5px; font-size: 14px; }
    QTableWidget { gridline-color: #555; }
    QHeaderView::section { background-color: #444; padding: 4px; border: 1px solid #555; font-weight: bold; }
    QProgressBar::chunk { background-color: #0a7e07; border-radius: 4px; }
    QPushButton { background-color: #007acc; color: #ffffff; border: none; border-radius: 4px; padding: 10px; font-size: 14px; font-weight: bold; text-align: center; }
    QPushButton:hover { background-color: #008ae6; }
    QPushButton:pressed { background-color: #006bb3; }
    QPushButton:disabled { background-color: #444; color: #888; }
    QLabel { font-size: 14px; font-weight: bold; }
    QListWidget::item:hover { background-color: #4a4a4a; }
    QListWidget::item:selected { background-color: #007acc; color: white; }
    QMenuBar { background-color: #3c3c3c; }
    QMenuBar::item:selected { background-color: #007acc; }
    QMenu { background-color: #3c3c3c; border: 1px solid #555; }
    QMenu::item:selected { background-color: #007acc; }
"""

# --- Worker Klassen für Threading ---

class WorkerSignals(QObject):
    result = Signal(dict)
    progress = Signal()
    finished = Signal()

class PortScanWorker(QRunnable):
    def __init__(self, target_ip, port):
        super().__init__()
        self.target_ip = target_ip
        self.port = port
        self.signals = WorkerSignals()
    def run(self):
        result = scan_single_port(self.target_ip, self.port)
        if result: self.signals.result.emit(result)
        self.signals.progress.emit()

class HostScanWorker(QObject):
    update_signal = Signal(str)
    finished = Signal()
    def __init__(self, target):
        super().__init__()
        self.target = target
        self._is_stopping = False
    @Slot()
    def run(self):
        discover_hosts(self.target, self.update_signal, lambda: self._is_stopping)
        if not self._is_stopping: self.finished.emit()
    def stop(self): self._is_stopping = True

# --- Hauptfenster der Anwendung ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Netzwerk-Scanner Pro")
        self.setWindowIcon(QIcon(resource_path("icons/target.svg")))
        self.setGeometry(100, 100, 1400, 800)
        
        self.host_scan_worker = None
        self.host_scan_thread = None
        self.current_scan_target = None
        self.ports_to_scan_total = 0
        self.ports_scanned_count = 0
        
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(50)
        
        self._create_actions()
        self._create_menu_bar()
        self._create_main_widget()

        if not check_nmap_availability():
            self.show_nmap_warning()

    def show_nmap_warning(self):
        # ... (Ihre show_nmap_warning Methode)
        pass
    def _create_main_widget(self):
        # ... (Ihre _create_main_widget Methode)
        pass
    def _create_actions(self):
        # ... (Ihre _create_actions Methode)
        pass
    def _create_menu_bar(self):
        # ... (Ihre _create_menu_bar Methode)
        pass
    # ... (Alle Ihre anderen GUI-Methoden wie start_host_scan, start_port_scan etc.)


# ==============================================================================
# BUILD-LOGIK (Wichtiger Teil)
# ==============================================================================

def run_build_command(command):
    """Führt einen Befehl im Terminal aus und gibt den Output live aus."""
    print(f"--- Führe aus: {' '.join(command)} ---")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        rc = process.poll()
        if rc != 0:
            print(f"--- FEHLER: Befehl schlug mit Code {rc} fehl. ---")
            sys.exit(rc)
    except FileNotFoundError:
        print(f"--- FEHLER: Befehl '{command[0]}' nicht gefunden. Ist PyInstaller installiert?")
        sys.exit(1)
    print(f"--- Befehl erfolgreich ausgeführt. ---")

def build_application():
    """Startet den plattformspezifischen Build-Prozess."""
    system = platform.system().lower()
    
    # Dieser Name mit Leerzeichen ist wichtig für die Konsistenz mit setup.iss
    app_name = "Netzwerk-Scanner Pro"
    main_script = "main.py"

    print(f"Starte Build für Plattform: {system.capitalize()}")

    for folder in ["dist", "build", "Output"]:
        if os.path.exists(folder):
            print(f"Lösche alten Ordner: {folder}")
            shutil.rmtree(folder)

    base_command = [
        "pyinstaller",
        "--name", app_name,
        "--noconfirm",
        "--windowed",
        main_script
    ]
    
    if system == "windows":
        print(">>> Konfiguriere für Windows (One-Folder-Build für Installer)...")
        command = base_command + [
            # Kein --onefile, damit der Installer den gesamten App-Ordner packen kann.
            # Das ist die empfohlene Methode für große Apps mit PySide6.
            f"--icon={os.path.join('icons', 'target.ico')}",
            "--manifest=admin.manifest"
        ]
    elif system == "darwin":
        print(">>> Konfiguriere für macOS...")
        command = base_command # macOS-Build bleibt einfach, ohne Icon
    else:
        print(f"FEHLER: Nicht unterstütztes Betriebssystem: {system}")
        sys.exit(1)

    run_build_command(command)

    print("\n========================================================")
    print(f"Build für {system.capitalize()} erfolgreich abgeschlossen!")
    print(f"Das Ergebnis befindet sich im Ordner 'dist'.")
    print("========================================================")

# ==============================================================================
# Haupt-Einstiegspunkt des Skripts
# ==============================================================================
if __name__ == "__main__":
    if "--build" in sys.argv:
        try:
            import PyInstaller
        except ImportError:
            print("PyInstaller nicht gefunden. Installiere...")
            run_build_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        build_application()
    else:
        # Dies ist der Code, der Ihre GUI startet.
        # Er wird ausgeführt, wenn das Skript ohne --build aufgerufen wird.
        app = QApplication(sys.argv)
        app.setStyleSheet(DARK_STYLE)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
