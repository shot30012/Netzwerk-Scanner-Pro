import sys
import os
import csv
# KORRIGIERTER IMPORT HIER: 'Slot' wurde für den Worker-Thread hinzugefügt.
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Qt, QSize, QThread, Slot
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QListWidget, QProgressBar,
    QRadioButton, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)

# Wir gehen davon aus, dass diese Engine-Datei existiert und die Funktionen bereitstellt.
from scanner_engine import get_network_info, discover_hosts, scan_single_port, parse_ports

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
        if result:
            self.signals.result.emit(result)
        self.signals.progress.emit()

# KORREKTUR: Die unsichere HostScanThread-Klasse wurde durch ein Worker/QThread-Muster ersetzt.
# Dies ist der von Qt empfohlene Weg für langlebige Aufgaben, um ein sicheres Beenden
# zu ermöglichen und die GUI nicht zu blockieren.
class HostScanWorker(QObject):
    update_signal = Signal(str)
    finished = Signal()

    def __init__(self, target):
        super().__init__()
        self.target = target
        self._is_stopping = False

    @Slot()
    def run(self):
        """ Führt den Host-Scan durch. """
        # HINWEIS: Damit der "Stop"-Button diesen Host-Scan effektiv unterbrechen kann,
        # muss die zugrunde liegende Funktion 'discover_hosts' eine Abbruchmöglichkeit unterstützen.
        # Ein einfacher blockierender Aufruf von 'discover_hosts' verhindert, dass der Scan
        # angehalten wird, bis er von selbst abgeschlossen ist.
        discover_hosts(self.target, self.update_signal)
        if not self._is_stopping:
            self.finished.emit()

    def stop(self):
        """ Signalisiert dem Worker, dass er anhalten soll. """
        self._is_stopping = True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Netzwerk-Scanner Pro")
        self.setWindowIcon(QIcon(resource_path("icons/target.svg")))
        self.setGeometry(100, 100, 1400, 800)
        
        # Worker und Thread für den Host-Scan
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
        QMessageBox.about(self, "Über Netzwerk-Scanner Pro", "<b>Netzwerk-Scanner Pro v2.0</b><p>Ein mächtiger, grafischer Netzwerk-Scanner.</p><p>Entwickelt von: Dir!</p><p>Dieses Tool nutzt die Nmap Security Scanner Engine. Großer Dank an das Nmap-Projekt (nmap.org).</p><p>GUI erstellt mit dem Qt Framework über PySide6.</p>")
    
    def stop_scans(self):
        """Stoppt alle laufenden Scans auf sichere Weise."""
        # Host-Scan anhalten
        if self.host_scan_thread and self.host_scan_thread.isRunning():
            self.host_scan_worker.stop()
        
        # Port-Scans anhalten
        # KORREKTUR: waitForDone() wird entfernt, da es die GUI blockiert.
        # clear() verhindert, dass neue Aufgaben gestartet werden.
        # Die bereits laufenden Tasks (max. 50) laufen zu Ende.
        self.threadpool.clear()
        
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Alle Scans vom Benutzer abgebrochen.")

    def start_host_scan(self):
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

        # KORREKTUR: Worker/Thread-Pattern für sichere Ausführung und Beendigung
        self.host_scan_thread = QThread()
        self.host_scan_worker = HostScanWorker(target)
        self.host_scan_worker.moveToThread(self.host_scan_thread)

        self.host_scan_thread.started.connect(self.host_scan_worker.run)
        self.host_scan_worker.finished.connect(self.host_scan_thread.quit)
        
        # Signale für UI-Updates verbinden
        self.host_scan_worker.update_signal.connect(self.handle_host_scan_update)
        self.host_scan_worker.finished.connect(self.host_scan_finished)
        
        # KORREKTUR: Ressourcen nach Beendigung freigeben, um Speicherlecks zu vermeiden
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
        if not self.stop_button.isEnabled(): # Prüft, ob der Scan nicht manuell gestoppt wurde
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())