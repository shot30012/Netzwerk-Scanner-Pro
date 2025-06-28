# Netzwerk-Scanner Pro

![Lizenz](https://img.shields.io/github/license/shot30012/Netzwerk-Scanner-Pro)
![Letztes Release](https://img.shields.io/github/v/release/shot30012/Netzwerk-Scanner-Pro)
![Plattformen](https://img.shields.io/badge/Plattform-Windows%20%7C%20macOS-blue)

Ein benutzerfreundlicher, grafischer Netzwerk-Scanner für Windows und macOS, geschrieben in Python mit PySide6. Dieses Tool ermöglicht es, schnell und effizient aktive Hosts in einem Netzwerk zu entdecken und deren offene Ports zu überprüfen.

![Screenshot der Host-Übersicht](screenshot-hosts.png)

## ✨ Hauptfunktionen

| Icon  | Funktion                        | Beschreibung                                                               |
| :---: | ------------------------------- | -------------------------------------------------------------------------- |
| 📡    | **Automatische Netzwerkerkennung** | Schlägt beim Start automatisch den lokalen Netzwerkbereich als Scan-Ziel vor. |
| 🔍    | **Host Discovery**              | Findet aktive Hosts und zeigt IP-Adressen sowie (falls auflösbar) Hostnamen an. |
| ⚡    | **Multi-Threaded Port-Scanner** | Scannt ausgewählte Hosts mit hoher Geschwindigkeit auf offene Ports.        |
| 🔧    | **Flexible Scan-Modi**          | Bietet schnelle, Standard-, intensive und benutzerdefinierte Scans.        |
| 🕵️    | **Diensterkennung**             | Identifiziert Dienste und Versionen auf offenen Ports mithilfe von Nmap.   |
| 📄    | **Daten-Export**                | Speichert Scan-Ergebnisse als übersichtliche `.csv`-Datei zur weiteren Analyse.    |

## 🚀 Download & Installation

Die neueste Version kann einfach über die Releases-Seite heruntergeladen werden.

**➡️ [Zur neuesten Release-Version](https://github.com/shot30012/Netzwerk-Scanner-Pro/releases/latest)**

### Windows

1.  Laden Sie die `Netzwerk-Scanner-Pro-Windows.exe` der aktuellsten Version herunter.
2.  > **Wichtiger Hinweis:** Windows Defender SmartScreen wird wahrscheinlich eine Warnung anzeigen, da die Anwendung nicht kommerziell signiert ist. Klicken Sie auf **"Weitere Informationen"** und dann auf **"Trotzdem ausführen"**, um die Anwendung zu starten.

### macOS

1.  Laden Sie die `Netzwerk-Scanner-Pro-macOS.zip` herunter und entpacken Sie sie.
2.  Ziehen Sie die `Netzwerk-Scanner Pro.app` in Ihren `Programme`-Ordner.
3.  > **Wichtiger Hinweis:** macOS Gatekeeper wird den Start blockieren. Um die App zu öffnen, machen Sie einen **Rechtsklick** auf das App-Icon, wählen Sie im Kontextmenü **"Öffnen"** und bestätigen Sie im Dialogfenster erneut mit "Öffnen". Dies ist nur beim allerersten Start notwendig.

## 💡 Benutzung

1.  **Ziel eingeben:** Starten Sie die Anwendung. Der lokale Netzwerkbereich ist bereits vorausgefüllt. Passen Sie ihn bei Bedarf an.
2.  **Netzwerk scannen:** Klicken Sie auf "Netzwerk Scannen", um nach aktiven Geräten zu suchen. Diese erscheinen in der Liste "Gefundene Hosts".
3.  **Ports überprüfen:** Wählen Sie einen Scan-Typ (z.B. "Schnell") und klicken Sie dann auf einen Host in der Liste, um dessen Ports zu scannen. Die Ergebnisse werden in der Tabelle rechts angezeigt.

## 🛠️ Für Entwickler: Aus dem Quellcode bauen

Möchten Sie das Projekt selbst kompilieren oder weiterentwickeln?

**Voraussetzungen:**
*   Python 3.9+
*   Nmap muss auf dem System installiert und im PATH verfügbar sein.
    *   macOS: `brew install nmap`
    *   Windows: Installer von [nmap.org](https://nmap.org/download.html)
    *   Linux: `sudo apt install nmap` oder `sudo dnf install nmap`

**Setup:**
```bash
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
```

**Anwendung bauen:**
Um die ausführbaren Dateien für Ihr Betriebssystem zu erstellen, führen Sie das Build-Skript aus:
```bash
python main.py --build
```
Die fertigen Dateien finden Sie anschließend im `dist`-Ordner.

## ⚠️ Hinweis zu Antiviren-Programmen

Da dieses Tool Netzwerk-Scan-Funktionen (wie Nmap) nutzt, die auch für bösartige Zwecke verwendet werden können, könnten einige Antivirenprogramme eine Warnung (False Positive) anzeigen. Dies ist zu erwarten, da die Anwendung nicht kommerziell signiert und noch nicht weit verbreitet ist. Der Quellcode ist vollständig einsehbar und sicher.

## 📜 Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE).
