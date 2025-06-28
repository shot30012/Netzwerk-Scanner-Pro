Netzwerk-Scanner Pro
![alt text](https://img.shields.io/github/license/shot30012/Netzwerk-Scanner-Pro)

![alt text](https://img.shields.io/github/v/release/shot30012/Netzwerk-Scanner-Pro)

![alt text](https://img.shields.io/badge/Plattform-Windows%20%7C%20macOS-blue)
Ein benutzerfreundlicher, grafischer Netzwerk-Scanner für Windows und macOS, geschrieben in Python mit PySide6. Dieses Tool ermöglicht es, schnell und effizient aktive Hosts in einem Netzwerk zu entdecken und deren offene Ports zu überprüfen.
![alt text](screenshot-hosts.png)

(Hier könnte ein zweiter Screenshot der Port-Detailansicht gut passen)
✨ Hauptfunktionen
Automatische Netzwerkerkennung: Schlägt beim Start automatisch den lokalen Netzwerkbereich als Scan-Ziel vor.
Host Discovery: Findet aktive Hosts im Zielnetzwerk und zeigt IP-Adressen sowie (falls auflösbar) Hostnamen an.
Multi-Threaded Port-Scanner: Scannt ausgewählte Hosts mit hoher Geschwindigkeit auf offene Ports.
Flexible Scan-Modi:
Schnell: Überprüft die Top 20 der häufigsten Ports.
Standard: Scannt die Top 1000 Ports.
Intensiv: Führt einen kompletten Scan aller 65.535 TCP-Ports durch.
Benutzerdefiniert: Ermöglicht die Angabe eigener Ports und Bereiche (z.B. 80, 443, 8000-8010).
Leistungsstarke Diensterkennung: Nutzt die Power von Nmap im Hintergrund, um Dienste und deren Versionen auf offenen Ports zu identifizieren.
Daten-Export: Speichert die detaillierten Scan-Ergebnisse als übersichtliche .csv-Datei zur weiteren Analyse.
Plattformübergreifend: Bietet native Builds für Windows und macOS.
🚀 Download & Installation
Die neueste Version kann einfach über die Releases-Seite heruntergeladen werden.
➡️ Zur neuesten Release-Version
Windows
Laden Sie die Netzwerk-Scanner-Pro-Windows.exe der aktuellsten Version herunter.
Wichtiger Hinweis: Windows Defender SmartScreen wird wahrscheinlich eine Warnung anzeigen, da die Anwendung nicht kommerziell signiert ist. Klicken Sie auf "Weitere Informationen" und dann auf "Trotzdem ausführen", um die Anwendung zu starten.
macOS
Laden Sie die Netzwerk-Scanner-Pro-macOS.zip herunter und entpacken Sie sie.
Ziehen Sie die Netzwerk-Scanner Pro.app in Ihren Programme-Ordner.
Wichtiger Hinweis: macOS Gatekeeper wird den Start blockieren. Um die App zu öffnen, machen Sie einen Rechtsklick auf das App-Icon, wählen Sie im Kontextmenü "Öffnen" und bestätigen Sie im Dialogfenster erneut mit "Öffnen". Dies ist nur beim allerersten Start notwendig.
💡 Benutzung
Ziel eingeben: Starten Sie die Anwendung. Der lokale Netzwerkbereich ist bereits vorausgefüllt. Passen Sie ihn bei Bedarf an.
Netzwerk scannen: Klicken Sie auf "Netzwerk Scannen", um nach aktiven Geräten zu suchen. Diese erscheinen in der Liste "Gefundene Hosts".
Ports überprüfen: Wählen Sie einen Scan-Typ (z.B. "Schnell") und klicken Sie dann auf einen Host in der Liste, um dessen Ports zu scannen. Die Ergebnisse werden in der Tabelle rechts angezeigt.
🛠️ Für Entwickler: Aus dem Quellcode bauen
Möchten Sie das Projekt selbst kompilieren oder weiterentwickeln?
Voraussetzungen:
Python 3.9+
Nmap muss auf dem System installiert und im PATH verfügbar sein.
macOS: brew install nmap
Windows: Installer von nmap.org
Linux: sudo apt install nmap oder sudo dnf install nmap
Setup:
Generated bash
# 1. Klonen Sie das Repository
git clone https://github.com/shot30012/Netzwerk-Scanner-Pro.git
cd Netzwerk-Scanner-Pro

# 2. (Empfohlen) Erstellen Sie eine virtuelle Umgebung
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# 3. Installieren Sie die Abhängigkeiten
pip install -r requirements.txt

# 4. Starten Sie die Anwendung
python main.py
Use code with caution.
Bash
Anwendung bauen:
Um die ausführbaren Dateien für Ihr Betriebssystem zu erstellen, führen Sie das Build-Skript aus:
Generated bash
python main.py --build
Use code with caution.
Bash
Die fertigen Dateien finden Sie anschließend im dist-Ordner.
⚠️ Hinweis zu Antiviren-Programmen
Da dieses Tool Netzwerk-Scan-Funktionen (wie Nmap) nutzt, die auch für bösartige Zwecke verwendet werden können, könnten einige Antivirenprogramme eine Warnung (False Positive) anzeigen. Dies ist zu erwarten, da die Anwendung nicht kommerziell signiert und noch nicht weit verbreitet ist. Der Quellcode ist vollständig einsehbar und sicher.
📜 Lizenz
Dieses Projekt steht unter der MIT License.
