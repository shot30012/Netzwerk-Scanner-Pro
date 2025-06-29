# Netzwerk-Scanner Pro

![Lizenz](https://img.shields.io/github/license/shot30012/Netzwerk-Scanner-Pro)
![Letztes Release](https://img.shields.io/github/v/release/shot30012/Netzwerk-Scanner-Pro)
![Plattformen](https://img.shields.io/badge/Plattform-Windows%20%7C%20macOS-blue)

Ein benutzerfreundlicher, plattformübergreifender Netzwerk-Scanner mit grafischer Oberfläche, geschrieben in Python und PySide6. Entdecken Sie schnell und effizient aktive Geräte in Ihrem Netzwerk und überprüfen Sie deren offene Ports.

---

![Screenshot der Anwendung](screenshot-hosts.png)
*(Stellen Sie sicher, dass eine Datei `screenshot-hosts.png` in Ihrem Repository existiert)*

---

## 🚀 Download

Die neueste Version ist immer hier verfügbar:

**➡️ [Zur neuesten Release-Version](https://github.com/shot30012/Netzwerk-Scanner-Pro/releases/latest)**

---

## ✨ Hauptfunktionen

| Icon  | Funktion                        | Beschreibung                                                                                                                             |
| :---: | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 📦    | **All-in-One Installer (Windows)** | Ein sauberes Setup-Programm installiert die Anwendung und **alle Abhängigkeiten (wie Nmap)** automatisch. Kein manueller Aufwand nötig! |
| 🔍    | **Host & Port Discovery**       | Findet aktive Hosts und scannt sie mit verschiedenen Modi (Schnell, Standard, Intensiv, Benutzerdefiniert) auf offene Ports.          |
| 🕵️    | **Diensterkennung**             | Identifiziert dank der Power von Nmap die Dienste und Versionen, die auf den gefundenen Ports laufen.                                   |
| 📄    | **Daten-Export**                | Speichern Sie die detaillierten Scan-Ergebnisse zur weiteren Analyse einfach als `.csv`-Datei.                                           |
| 💻    | **Plattformübergreifend**       | Bietet native, installationsfertige Pakete für Windows und macOS.                                                                        |

---

## 📝 Installationsanleitung

#### Windows
1.  Laden Sie die `Netzwerk-Scanner-Pro-Windows-Setup.exe` von der [Releases-Seite](https://github.com/shot30012/Netzwerk-Scanner-Pro/releases/latest) herunter.
2.  Führen Sie die Setup-Datei aus und folgen Sie den Anweisungen.

> **Wichtiger Hinweis:** Windows Defender könnte eine Warnung anzeigen. Klicken Sie auf **"Weitere Informationen" → "Trotzdem ausführen"**.

#### macOS
1.  Laden Sie die `Netzwerk-Scanner-Pro-macOS.zip` herunter und entpacken Sie sie.
2.  Ziehen Sie die `Netzwerk-Scanner Pro.app` in Ihren `Programme`-Ordner.

> **Wichtiger Hinweis:** Beim ersten Start müssen Sie einen **Rechtsklick** auf das App-Icon machen, **"Öffnen"** wählen und im Dialogfenster erneut "Öffnen" bestätigen.

---

<details>
<summary>🛠️ <b>Für Entwickler: Aus dem Quellcode bauen</b></summary>

<br>

Möchten Sie das Projekt selbst kompilieren oder weiterentwickeln? So geht's:

**Voraussetzungen:**
*   Python 3.9+
*   Nmap muss auf dem System installiert und im `PATH` verfügbar sein.
    *   **Windows:** `choco install nmap`
    *   **macOS:** `brew install nmap`
    *   **Linux:** `sudo apt install nmap` oder `sudo dnf install nmap`

**Setup-Anleitung:**

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/shot30012/Netzwerk-Scanner-Pro.git
    cd Netzwerk-Scanner-Pro
    ```

2.  **(Empfohlen) Virtuelle Umgebung erstellen:**
    ```bash
    python -m venv venv
    ```
    *Aktivieren:*
    *   macOS/Linux: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`

3.  **Abhängigkeiten installieren:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Anwendung starten:**
    ```bash
    python main.py
    ```

**Anwendung selbst bauen:**

Um die ausführbaren Dateien für Ihr Betriebssystem zu erstellen, führen Sie das Build-Skript aus:
```bash
python main.py --build


Die fertigen Pakete finden Sie anschließend im dist-Ordner (und Output für den Windows-Installer).
</details>
⚠️ Hinweis zu Antiviren-Programmen
Da dieses Tool legitime Netzwerk-Scan-Funktionen nutzt, könnten einige Antivirenprogramme eine Warnung (False Positive) anzeigen. Dies ist zu erwarten, da die Anwendung nicht kommerziell signiert ist. Der Quellcode ist vollständig einsehbar und sicher.
📜 Lizenz
Dieses Projekt steht unter der MIT License.
