# Netzwerk-Scanner Pro

Ein einfacher, aber leistungsstarker grafischer Netzwerk-Scanner für Windows, geschrieben in Python mit PySide6.

![Screenshot Ihrer Anwendung](link_zum_screenshot.png) <!-- Ersetzen Sie dies später durch einen echten Screenshot -->

## Funktionen

*   **Host Discovery:** Findet aktive Hosts in einem bestimmten Netzwerkbereich mittels Ping.
*   **Port-Scanner:** Scannt ausgewählte Hosts auf offene Ports mit verschiedenen Scan-Tiefen (Schnell, Standard, Intensiv, Benutzerdefiniert).
*   **Diensterkennung:** Nutzt Nmap, um Dienste und Versionen auf offenen Ports zu identifizieren.
*   **Export-Funktion:** Speichert Scan-Ergebnisse als CSV-Datei.
*   **Installer:** Kommt mit einem einfachen Installer, der die Nmap-Abhängigkeit automatisch mitinstalliert.

## Download & Installation

1.  Gehen Sie zur **[Releases-Seite](link_zu_den_releases)**. <!-- Den Link fügen wir in Schritt 4 ein -->
2.  Laden Sie die `Netzwerk-Scanner-Pro-Setup.exe` der neuesten Version herunter.
3.  Führen Sie die Setup-Datei aus und folgen Sie den Anweisungen. Nmap wird automatisch mitinstalliert.

## Hinweis zu Antiviren-Programmen

Da dieses Tool Netzwerk-Scan-Funktionen (wie Nmap) nutzt, die auch für bösartige Zwecke verwendet werden können, könnten einige Antivirenprogramme eine Warnung (False Positive) anzeigen. Dies ist zu erwarten. Die Anwendung ist sicher und Open Source – Sie können den Quellcode in diesem Repository jederzeit überprüfen.

## Lizenz

Dieses Projekt steht unter der [MIT License](LICENSE).
