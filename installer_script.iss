; Inno Setup Skript für Netzwerk-Scanner Pro
; Erstellt von: Dir
; Version: 1.0

[Setup]
AppId={{60e2ad3d-5fac-4aa9-bec5-ff6c56d1e26a}}
AppName=Netzwerk-Scanner Pro
AppVersion=1.0
AppPublisher=Dein Name oder Firmenname
AppPublisherURL=
AppSupportURL=
DefaultDirName={autopf}\Netzwerk-Scanner Pro
OutputBaseFilename=Netzwerk-Scanner-Pro-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
; 1. Die Hauptanwendung (.exe)
Source: "dist\Netzwerk-Scanner Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

; KORREKTUR: Wir kopieren die Nmap-Datei mit Wildcard, aber OHNE DestName.
; Sie wird mit ihrem Originalnamen ins Temp-Verzeichnis kopiert.
Source: "nmap-*-setup.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Icons]
Name: "{autoprograms}\Netzwerk-Scanner Pro"; Filename: "{app}\Netzwerk-Scanner Pro.exe"
Name: "{autodesktop}\Netzwerk-Scanner Pro"; Filename: "{app}\Netzwerk-Scanner Pro.exe"; Tasks: desktopicon

[Run]
; KORREKTUR: Wir verwenden eine "scripted constant" ({code:...}), um unsere Funktion
; im [Code]-Abschnitt aufzurufen und den exakten Pfad zur Laufzeit zu erhalten.
Filename: "{code:GetNmapPath}"; Parameters: "/S"; StatusMsg: "Installiere Nmap (notwendige Komponente)...";

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

; ====================================================================
; KORREKTUR: Der [Code]-Block wird verwendet, um den genauen Pfad zur Nmap-Datei
; zur Laufzeit zu finden.
; ====================================================================
[Code]
var
  FoundNmapPath: String; // Dient als Cache, um nicht mehrmals suchen zu müssen

// Diese Funktion sucht im Temp-Verzeichnis nach der Nmap-Datei und gibt den vollen Pfad zurück.
function GetNmapPath(Param: String): String;
var
  FindRec: TFindRec;
begin
  // Nur einmal suchen, um effizient zu sein
  if FoundNmapPath = '' then
  begin
    // FindFirst sucht nach der ersten Datei, die dem Muster entspricht
    if FindFirst(ExpandConstant('{tmp}\nmap-*-setup.exe'), FindRec) then
    begin
      try
        // Speichere den vollen Pfad in unserer globalen Variable
        FoundNmapPath := ExpandConstant('{tmp}\' + FindRec.Name);
      finally
        // Wichtig: Die Suche immer schließen
        FindClose(FindRec);
      end;
    end;
  end;
  // Gib den gefundenen Pfad zurück
  Result := FoundNmapPath;
end;