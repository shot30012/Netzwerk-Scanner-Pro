; Inno Setup Skript für Netzwerk-Scanner Pro
; ============================================
; Dieses Skript definiert, wie der Windows-Installer erstellt wird.

[Setup]
; --- Grundlegende App-Informationen ---
AppName=Netzwerk-Scanner Pro
; WICHTIG: Passe die Version hier für jedes neue Release manuell an!
AppVersion=1.4.0 
AppPublisher=shot30012
AppPublisherURL=https://github.com/shot30012/Netzwerk-Scanner-Pro
AppSupportURL=https://github.com/shot30012/Netzwerk-Scanner-Pro/issues
AppUpdatesURL=https://github.com/shot30012/Netzwerk-Scanner-Pro/releases

; --- Installations-Einstellungen ---
; Standardverzeichnis für die Installation (z.B. C:\Programme\Netzwerk-Scanner Pro)
DefaultDirName={autopf}\Netzwerk-Scanner Pro
; Name der Gruppe im Startmenü
DefaultGroupName=Netzwerk-Scanner Pro
; Admin-Rechte sind für die Installation in "Programme" erforderlich
PrivilegesRequired=admin

; --- Kompression (für eine möglichst kleine Setup-Datei) ---
Compression=lzma2/ultra
SolidCompression=yes

; --- Installer-Aussehen und -Ausgabe ---
; Modernes Aussehen für den Installations-Assistenten
WizardStyle=modern
; Name der fertigen Installer-Datei (z.B. Netzwerk-Scanner-Pro-Setup.exe)
OutputBaseFilename=Netzwerk-Scanner-Pro-Setup
; Der Installer wird im Unterordner "Output" erstellt
OutputDir=Output


[Files]
; Dies ist der wichtigste Abschnitt. Er legt fest, welche Dateien in den Installer gepackt werden.

; 1. Nimm den gesamten Inhalt des von PyInstaller erstellten Build-Ordners.
;    Der Ordnername "Netzwerk-Scanner Pro" muss exakt mit dem 'app_name' in main.py übereinstimmen.
Source: "dist\Netzwerk-Scanner Pro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. Nimm die Nmap-Dateien, die der GitHub Workflow im Schritt zuvor vorbereitet hat.
;    Diese werden in einen Unterordner "nmap" innerhalb des App-Verzeichnisses installiert.
Source: "dependencies\nmap_unpacked\*"; DestDir: "{app}\nmap"; Flags: recursesubdirs createallsubdirs


[Icons]
; Erstellt die Verknüpfungen im System.

; Eintrag im Startmenü
Name: "{group}\Netzwerk-Scanner Pro"; Filename: "{app}\Netzwerk-Scanner Pro.exe"
; Optionales Icon auf dem Desktop (siehe [Tasks])
Name: "{autodesktop}\Netzwerk-Scanner Pro"; Filename: "{app}\Netzwerk-Scanner Pro.exe"; Tasks: desktopicon


[Tasks]
; Fügt im Installer eine Checkbox hinzu, mit der der Benutzer entscheiden kann,
; ob ein Desktop-Icon erstellt werden soll.
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";


[Run]
; Fügt auf der letzten Seite des Installers eine Checkbox hinzu, um das Programm
; direkt nach der Installation zu starten.
Filename: "{app}\Netzwerk-Scanner Pro.exe"; Description: "{cm:LaunchProgram,Netzwerk-Scanner Pro}"; Flags: nowait postinstall skipifsilent
