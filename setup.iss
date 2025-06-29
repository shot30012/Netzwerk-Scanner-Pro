; Inno Setup Skript für Netzwerk-Scanner Pro
; Dieses Skript definiert, wie der Windows-Installer erstellt wird.

[Setup]
; App-Informationen
AppName=Netzwerk-Scanner Pro
AppVersion=1.3.0 ; Du kannst dies manuell anpassen oder später automatisieren
AppPublisher=shot30012
AppPublisherURL=https://github.com/shot30012/Netzwerk-Scanner-Pro
AppSupportURL=https://github.com/shot30012/Netzwerk-Scanner-Pro/issues
AppUpdatesURL=https://github.com/shot30012/Netzwerk-Scanner-Pro/releases

; Installationsverzeichnis und Startmenü-Gruppe
DefaultDirName={autopf}\Netzwerk-Scanner Pro
DefaultGroupName=Netzwerk-Scanner Pro

; Kompressionseinstellungen für eine möglichst kleine Datei
Compression=lzma2/ultra
SolidCompression=yes

; Modernes Aussehen des Installers
WizardStyle=modern

; Name der fertigen Installer-Datei (z.B. Netzwerk-Scanner-Pro-Setup.exe)
OutputBaseFilename=Netzwerk-Scanner-Pro-Setup
; Der Installer wird im Unterordner "Output" erstellt
OutputDir=Output

; Admin-Rechte sind für die Installation in "Programme" erforderlich
PrivilegesRequired=admin

[Files]
; Dies ist der wichtigste Teil:
; 1. Nimm den gesamten Inhalt des von PyInstaller erstellten Build-Ordners...
;    (Der Name "Netzwerk-Scanner Pro" muss mit dem Namen in main.py übereinstimmen)
Source: "dist\Netzwerk-Scanner Pro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; 2. (Optional, aber empfohlen) Nimm Nmap aus einem lokalen "dependencies"-Ordner mit auf.
;    Dies macht deine Anwendung komplett unabhängig.
; Source: "dependencies\nmap\*"; DestDir: "{app}\nmap"; Flags: recursesubdirs createallsubdirs

[Icons]
; Erstellt einen Eintrag im Startmenü
Name: "{group}\Netzwerk-Scanner Pro"; Filename: "{app}\Netzwerk-Scanner Pro.exe"
; Erstellt (optional) ein Icon auf dem Desktop
Name: "{autodesktop}\Netzwerk-Scanner Pro"; Filename: "{app}\Netzwerk-Scanner Pro.exe"; Tasks: desktopicon

[Tasks]
; Fügt im Installer eine Checkbox hinzu, um das Desktop-Icon zu erstellen
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Run]
; Option, um das Programm direkt nach der Installation zu starten
Filename: "{app}\Netzwerk-Scanner Pro.exe"; Description: "{cm:LaunchProgram,Netzwerk-Scanner Pro}"; Flags: nowait postinstall skipifsilent
