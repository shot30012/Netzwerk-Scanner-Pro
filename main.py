# main.py - Vollständige Version mit GUI und korrigierter Build-Logik

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
from scanner_engine import (
    get_network_info, discover_hosts, scan_single_port, parse_ports, check_nmap_availability
)

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
    """ Signale für den PortScanWorker """
    result = Signal(dict)
    progress = Signal()
    finished = Signal()

class PortScanWorker(QRunnable):
    """ Worker für das Scannen eines einzelnen Ports """
    def __init__(self, target_ip, port):
        super().__init__()
        self.target_ip = target_ip
        self.port = port
        self.signals = WorkerSignals()

    def run(self):
        result = scan_single_port(self.target_ip, self.port)
        if result:
            self.signals.result.emit(result)
        self.signals.progress.emit()

class HostScanWorker(QObject):
    """ Worker für die Host-Suche """
    update_signal = Signal(str)
    finished = Signal()

    def __init__(self, target):
        super().__init__()
        self.target = target
        self._is_stopping = False

    @Slot()
    def run(self):
        discover_hosts(self.target, self.update_signal, lambda: self._is_stopping)
        if not self._is_stopping:
            self.finished.emit()

    def stop(self):
        self._is_stopping = True

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

        # Nmap-Check beim Start
        if not check_nmap_availability():
            self.show_nmap_warning()
            try:
                self.hosts_list.itemClicked.disconnect(self.start_port_scan)
                self.hosts_list.setToolTip("Port-Scans sind deaktiviert, da Nmap nicht gefunden wurde.")
            except RuntimeError:
                pass # Falls Verbindung schon getrennt war

    def show_nmap_warning(self):
        """ Zeigt eine Warnung mit plattformspezifischen Anweisungen an, wenn Nmap nicht gefunden wird. """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Nmap nicht gefunden")
        msg_box.setText("<b>Die Kernkomponente 'Nmap' wurde nicht gefunden.</b>")
        
        system = platform.system().lower()
        if system == 'darwin': # macOS
            instruction = "Bitte installieren Sie es mit Homebrew: <br><code>brew install nmap</code>"
        elif system == 'linux':
            instruction = "Bitte installieren Sie es mit dem Paketmanager Ihrer Distribution, z.B.: <br><code>sudo apt-get install nmap</code> (für Debian/Ubuntu) <br><code>sudo dnf install nmap</code> (für Fedora)"
        else: # Windows
            instruction = "Bitte installieren Sie Nmap von <a href='https://nmap.org/download.html'>nmap.org</a> und stellen Sie sicher, dass es im System-PATH ist.<br>(Sollte durch den Installer automatisch erledigt werden.)"

        msg_box.setInformativeText(f"Die Port-Scan-Funktionen sind deaktiviert, bis Nmap installiert ist.<br><br>{instruction}")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def _create_main_widget(self):
        self.scan_icon = QIcon(resource_path("icons/search.svg"))
        self.stop_icon = QIcon(resource_path("icons/x-circle.svg"))
        self.export_icon = QIcon(resource_path("icons/save.svg"))
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(280)
        
        target_label = QLabel("Ziel (IP / Host / Range):")
        self.target_input = QLineEdit()
        self.discover_and_set_target()
        
        self.scan_button = QPushButton(" Netzwerk Scannen")
        self.scan_button.setIcon(self.scan_icon)
        self.scan_button.clicked.connect(self.start_host_scan)
        
        self.stop_button = QPushButton(" Stop")
        self.stop_button.setIcon(self.stop_icon)
        self.stop_button.clicked.connect(self.stop_scans)
        self.stop_button.setEnabled(False)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        
        left_layout.addWidget(target_label)
        left_layout.addWidget(self.target_input)
        left_layout.addWidget(self.scan_button)
        left_layout.addWidget(self.stop_button)
        left_layout.addWidget(QLabel("Fortschritt:"))
        left_layout.addWidget(self.progress_bar)
        
        port_options_group = QGroupBox("Port-Scan Typ")
        port_options_layout = QVBoxLayout(port_options_group)
        self.radio_quick = QRadioButton("Schnell (Top 20)")
        self.radio_quick.setChecked(True)
        self.radio_standard = QRadioButton("Standard (Top 1000)")
        self.radio_intensive = QRadioButton("Intensiv (Alle 65535 Ports)")
        self.radio_custom = QRadioButton("Eigener Bereich:")
        self.custom_ports_input = QLineEdit()
        self.custom_ports_input.setPlaceholderText("z.B. 80, 443, 8000-8010")
        self.custom_ports_input.setEnabled(False)
        
        self.radio_quick.toggled.connect(lambda: self.custom_ports_input.setEnabled(False))
        self.radio_standard.toggled.connect(lambda: self.custom_ports_input.setEnabled(False))
        self.radio_intensive.toggled.connect(lambda: self.custom_ports_input.setEnabled(False))
        self.radio_custom.toggled.connect(lambda: self.custom_ports_input.setEnabled(True))
        
        port_options_layout.addWidget(self.radio_quick)
        port_options_layout.addWidget(self.radio_standard)
        port_options_layout.addWidget(self.radio_intensive)
        port_options_layout.addWidget(self.radio_custom)
        port_options_layout.addWidget(self.custom_ports_input)
        
        left_layout.addSpacing(20)
        left_layout.addWidget(port_options_group)
        left_layout.addStretch()
        
        # Middle Panel
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        hosts_label = QLabel("Gefundene Hosts:")
        self.hosts_list = QListWidget()
        self.hosts_list.itemClicked.connect(self.start_port_scan)
        middle_layout.addWidget(hosts_label)
        middle_layout.addWidget(self.hosts_list)
        
        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        details_header_layout = QHBoxLayout()
        details_label = QLabel("Details:")
        details_header_layout.addWidget(details_label)
        details_header_layout.addStretch()
        
        self.export_button = QPushButton(" Exportieren")
        self.export_button.setIcon(self.export_icon)
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        details_header_layout.addWidget(self.export_button)
        
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(4)
        self.details_table.setHorizontalHeaderLabels(["Port", "Status", "Service", "Version / Details"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.details_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.details_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.details_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.details_table.verticalHeader().setVisible(False)
        
        self.status_label = QLabel("Wähle einen Host aus, um einen Port-Scan zu starten.")
        self.status_label.setWordWrap(True)
        
        right_layout.addLayout(details_header_layout)
        right_layout.addWidget(self.details_table)
        right_layout.addWidget(self.status_label)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(middle_panel, 1)
        main_layout.addWidget(right_panel, 2)

    def _create_actions(self):
        self.quit_action = QAction(QIcon(resource_path("icons/x.svg")), "&Beenden", self)
        self.quit_action.triggered.connect(self.close)
        self.about_action = QAction(QIcon(resource_path("icons/info.svg")), "&Über Netzwerk-Scanner Pro", self)
        self.about_action.triggered.connect(self.show_about_dialog)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&Datei")
        file_menu.addAction(self.quit_action)
        help_menu = menu_bar.addMenu("&Hilfe")
        help_menu.addAction(self.about_action)

    def show_about_dialog(self):
        QMessageBox.about(self, "Über Netzwerk-Scanner Pro", "<b>Netzwerk-Scanner Pro v1.2</b><p>Ein grafischer Netzwerk-Scanner für Windows, macOS und Linux.</p><p>GUI erstellt mit dem Qt Framework über PySide6.</p>")
    
    def stop_scans(self):
        if self.host_scan_thread and self.host_scan_thread.isRunning():
            self.host_scan_worker.stop()
        
        self.threadpool.clear()
        
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Alle Scans vom Benutzer abgebrochen.")

    def start_host_scan(self):
        if not check_nmap_availability():
            self.show_nmap_warning()
            return
            
        self.stop_scans()
        self.hosts_list.clear()
        self.details_table.setRowCount(0)
        self.status_label.setText("Starte Host-Scan...")
        self.export_button.setEnabled(False)
        self.progress_bar.setValue(0)
        target = self.target_input.text()
        if not target:
            self.status_label.setText("FEHLER: Bitte ein Ziel eingeben.")
            return
            
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        self.host_scan_thread = QThread()
        self.host_scan_worker = HostScanWorker(target)
        self.host_scan_worker.moveToThread(self.host_scan_thread)
        self.host_scan_thread.started.connect(self.host_scan_worker.run)
        self.host_scan_worker.finished.connect(self.host_scan_thread.quit)
        self.host_scan_worker.update_signal.connect(self.handle_host_scan_update)
        self.host_scan_worker.finished.connect(self.host_scan_finished)
        self.host_scan_worker.finished.connect(self.host_scan_worker.deleteLater)
        self.host_scan_thread.finished.connect(self.host_scan_thread.deleteLater)
        self.host_scan_thread.start()

    def handle_host_scan_update(self, message):
        if message.startswith("progress:"):
            self.progress_bar.setValue(int(message.split(":", 1)[1]))
        elif message.startswith("host_found:"):
            parts = message.split("|||")
            ip_address = parts[0].split(":", 1)[1]
            hostname = parts[1] if len(parts) > 1 and parts[1] else ""
            display_text = ip_address
            if hostname:
                display_text += f" ({hostname})"
            self.hosts_list.addItem(display_text)
        elif message.startswith("error:"):
            self.status_label.setText(f"<font color='#FF5733'>FEHLER: {message.split(':', 1)[1]}</font>")
    
    def host_scan_finished(self):
        if not self.stop_button.isEnabled():
            return
            
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if self.hosts_list.count() == 0:
            self.status_label.setText("Host-Scan beendet. Keine aktiven Hosts gefunden.")
        else:
            self.status_label.setText(f"Host-Scan beendet. {self.hosts_list.count()} Host(s) gefunden.")

    def start_port_scan(self, item):
        self.stop_scans()
        self.export_button.setEnabled(False)
        full_text = item.text()
        self.current_scan_target = full_text.split(" ")[0]
        
        ports_to_scan = []
        if self.radio_quick.isChecked():
            ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080]
        elif self.radio_standard.isChecked():
            ports_to_scan = list(range(1, 1025))
        elif self.radio_intensive.isChecked():
            ports_to_scan = list(range(1, 65536))
        elif self.radio_custom.isChecked():
            ports_to_scan = parse_ports(self.custom_ports_input.text())
        
        if not ports_to_scan:
            self.status_label.setText("<font color='#FF5733'>FEHLER: Kein gültiger Port-Bereich.</font>")
            return

        self.details_table.setRowCount(0)
        self.ports_to_scan_total = len(ports_to_scan)
        self.ports_scanned_count = 0
        self.progress_bar.setValue(0)
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText(f"<b>Starte Multi-Threaded Port-Scan für: {self.current_scan_target}</b>")

        for port in ports_to_scan:
            worker = PortScanWorker(self.current_scan_target, port)
            worker.signals.result.connect(self.handle_port_scan_result)
            worker.signals.progress.connect(self.update_port_scan_progress)
            self.threadpool.start(worker)

    def handle_port_scan_result(self, result):
        row_position = self.details_table.rowCount()
        self.details_table.insertRow(row_position)
        self.details_table.setItem(row_position, 0, QTableWidgetItem(result["port"]))
        status_item = QTableWidgetItem("OFFEN")
        status_item.setForeground(Qt.GlobalColor.green)
        self.details_table.setItem(row_position, 1, status_item)
        self.details_table.setItem(row_position, 2, QTableWidgetItem(result["service"]))
        self.details_table.setItem(row_position, 3, QTableWidgetItem(result["details"]))
    
    def update_port_scan_progress(self):
        if not self.stop_button.isEnabled():
            return
            
        self.ports_scanned_count += 1
        progress = int((self.ports_scanned_count / self.ports_to_scan_total) * 100)
        self.progress_bar.setValue(progress)
        
        if self.ports_scanned_count >= self.ports_to_scan_total:
            self.status_label.setText(f"Port-Scan für {self.current_scan_target} beendet.")
            self.scan_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            if self.details_table.rowCount() > 0:
                self.export_button.setEnabled(True)
    
    def export_results(self):
        if self.details_table.rowCount() == 0:
            self.status_label.setText("Keine Ergebnisse zum Exportieren vorhanden.")
            return
        safe_filename = self.current_scan_target.replace('.', '_')
        filename_suggestion = f"scan_results_{safe_filename}.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Ergebnisse speichern", filename_suggestion, "CSV-Dateien (*.csv)")
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as csv_file:
                    writer = csv.writer(csv_file)
                    headers = [self.details_table.horizontalHeaderItem(i).text() for i in range(self.details_table.columnCount())]
                    writer.writerow(headers)
                    for row in range(self.details_table.rowCount()):
                        row_data = [self.details_table.item(row, col).text() for col in range(self.details_table.columnCount())]
                        writer.writerow(row_data)
                self.status_label.setText(f"Ergebnisse erfolgreich nach {os.path.basename(path)} exportiert.")
            except Exception as e:
                self.status_label.setText(f"<font color='#FF5733'><b>FEHLER beim Export:</b> {e}</font>")
    
    def discover_and_set_target(self):
        local_ip, network_range = get_network_info()
        if network_range:
            self.target_input.setText(network_range)
        else:
            self.target_input.setText("127.0.0.1")

# ==============================================================================
# BUILD-LOGIK
# ==============================================================================

def run_build_command(command):
    """Führt einen Befehl im Terminal aus und gibt den Output live aus."""
    print(f"--- Führe aus: {' '.join(command)} ---")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')
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
        print(f"--- FEHLER: Befehl '{command[0]}' nicht gefunden. Ist das Programm (z.B. PyInstaller) installiert?")
        sys.exit(1)
    print(f"--- Befehl erfolgreich ausgeführt. ---")

def build_application():
    """Startet den plattformspezifischen Build-Prozess."""
    system = platform.system().lower()
    app_name = "Netzwerk-Scanner Pro"
    main_script = "main.py"

    # Bestimme den Pfad zum Skriptverzeichnis, um Pfadprobleme zu vermeiden.
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Starte Build für Plattform: {system.capitalize()}")
    print(f"Skriptverzeichnis: {script_dir}")

    # Bereinige alte Build-Ordner
    for folder in ["dist", "build"]:
        if os.path.exists(folder):
            print(f"Lösche alten Ordner: {folder}")
            shutil.rmtree(folder)

    # Basis-Befehl für PyInstaller
    base_command = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        main_script
    ]
    
    command = base_command + ["--name", app_name]
    
    # Plattformspezifische Anpassungen
    if system == "windows":
        print(">>> Konfiguriere für Windows...")
        command += [
            "--onefile",
            "--icon", os.path.join(script_dir, 'icons', 'target.ico'),
            "--manifest", "admin.manifest"
        ]
    elif system == "darwin": # macOS
        print(">>> Konfiguriere für macOS...")
        command += [
            "--icon", os.path.join(script_dir, 'icons', 'target.icns')
        ]
    elif system == "linux":
        print(">>> Konfiguriere für Linux...")
        # Keine zusätzlichen Optionen für den Basis-Build nötig
        pass
    else:
        print(f"FEHLER: Nicht unterstütztes Betriebssystem: {system}")
        sys.exit(1)

    # Führe den PyInstaller-Befehl aus
    run_build_command(command)

    print("\n========================================================")
    print(f"Build für {system.capitalize()} erfolgreich abgeschlossen!")
    print(f"Das Ergebnis befindet sich im Ordner 'dist'.")
    print("========================================================")

# ==============================================================================
# Haupt-Einstiegspunkt des Skripts
# ==============================================================================
if __name__ == "__main__":
    # Prüfen, ob das Build-Argument übergeben wurde
    if "--build" in sys.argv:
        try:
            import PyInstaller
        except ImportError:
            print("PyInstaller nicht gefunden. Installiere...")
            run_build_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        build_application()
    else:
        # Normaler Start der GUI-Anwendung
        app = QApplication(sys.argv)
        app.setStyleSheet(DARK_STYLE)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
