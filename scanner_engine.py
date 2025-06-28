import socket
import netifaces
import ipaddress
import platform
import subprocess
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional, Callable

def get_network_info() -> Tuple[Optional[str], Optional[str]]:
    """
    Ermittelt die lokale IP-Adresse und den Netzwerkbereich des primären aktiven Adapters.

    Versucht zuerst, den Standard-Gateway zu finden, um die primäre Schnittstelle zu identifizieren.
    Wenn das fehlschlägt, durchläuft es alle Schnittstellen und gibt das erste gefundene
    Nicht-Loopback-Netzwerk zurück.

    Returns:
        Ein Tupel (local_ip, network_range_cidr).
        Beispiel: ('192.168.1.10', '192.168.1.0/24').
        Gibt (None, None) zurück, wenn keine Informationen gefunden werden konnten.
    """
    try:
        # Versuch 1: Über den Standard-Gateway (zuverlässigste Methode)
        gws = netifaces.gateways()
        default_gateway_info = gws.get('default', {}).get(netifaces.AF_INET)
        if default_gateway_info:
            _, interface = default_gateway_info
            if netifaces.AF_INET in netifaces.ifaddresses(interface):
                addr_info = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]
                ip = addr_info.get('addr')
                netmask = addr_info.get('netmask')
                if ip and netmask:
                    ip_obj = ipaddress.IPv4Interface(f"{ip}/{netmask}")
                    return str(ip_obj.ip), str(ip_obj.network)

        # Versuch 2: Fallback - erste gefundene Nicht-Loopback-Schnittstelle
        for interface in netifaces.interfaces():
            ifaddresses = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in ifaddresses:
                addr_info = ifaddresses[netifaces.AF_INET][0]
                ip = addr_info.get('addr')
                netmask = addr_info.get('netmask')
                if ip and netmask and not ip.startswith('127.'):
                    ip_obj = ipaddress.IPv4Interface(f"{ip}/{netmask}")
                    return str(ip_obj.ip), str(ip_obj.network)
                    
    except Exception as e:
        print(f"Fehler bei der Netzwerkerkennung: {e}")
        return None, None
        
    return None, None

def discover_hosts(network_range: str, progress_callback: Callable, is_stopping_func: Callable[[], bool] = lambda: False):
    """
    Sucht nach aktiven Hosts in einem bestimmten Netzwerkbereich mittels Ping.

    Diese Funktion ist so konzipiert, dass sie kooperativ abgebrochen werden kann.

    Args:
        network_range: Der zu scannende Netzwerkbereich in CIDR-Notation (z.B. "192.168.1.0/24").
        progress_callback: Ein Signal-Emitter (z.B. `Signal.emit`), um Updates an die GUI zu senden.
        is_stopping_func: Eine Funktion, die True zurückgibt, wenn der Scan abgebrochen werden soll.
                          Dies ermöglicht ein sauberes Beenden durch die GUI.
    """
    try:
        network = ipaddress.ip_network(network_range, strict=False)
        
        # Bestimme die Liste der zu scannenden Hosts.
        # Für /32-Netze enthält .hosts() nichts, also scannen wir die Adresse selbst.
        if network.num_addresses > 1:
            hosts_to_scan = list(network.hosts())
        else:
            hosts_to_scan = [network.network_address]

        total_hosts = len(hosts_to_scan)
        if total_hosts == 0:
            progress_callback.emit("error:Keine gültigen Hosts zum Scannen in diesem Bereich.")
            return

        for i, host in enumerate(hosts_to_scan):
            # KORREKTUR: Prüfen, ob der Scan vom Benutzer abgebrochen wurde.
            if is_stopping_func():
                print("Host-Scan wurde abgebrochen.")
                break # Die Schleife sicher verlassen.

            host_str = str(host)
            
            # Betriebssystemspezifischer Ping-Befehl
            if platform.system().lower() == 'windows':
                command = ['ping', '-n', '1', '-w', '1000', host_str]
            else:
                command = ['ping', '-c', '1', '-W', '1', host_str]
            
            # Verhindert das Aufpoppen von Konsolenfenstern unter Windows
            startupinfo = None
            if platform.system().lower() == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            try:
                # Führe den Ping-Befehl aus
                response = subprocess.run(
                    command, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL, 
                    startupinfo=startupinfo, 
                    check=False
                )
                
                if response.returncode == 0:
                    hostname = ""
                    try:
                        # Versuche, den Hostnamen via Reverse-DNS-Lookup aufzulösen
                        data = socket.gethostbyaddr(host_str)
                        hostname = data[0]
                    except (socket.herror, socket.gaierror):
                        # Hostname konnte nicht aufgelöst werden, das ist okay.
                        hostname = ""
                    progress_callback.emit(f"host_found:{host_str}|||{hostname}")
            except Exception as e:
                # Unerwarteter Fehler beim Pingen
                print(f"Unerwarteter Fehler bei Ping an {host_str}: {e}")

            # Fortschritt an die GUI senden
            progress = int(((i + 1) / total_hosts) * 100)
            progress_callback.emit(f"progress:{progress}")

    except Exception as e:
        progress_callback.emit(f"error:Ein Fehler ist aufgetreten: {e}")

def parse_ports(port_string: str) -> List[int]:
    """
    Parst einen String mit Portangaben in eine sortierte Liste von Integer-Ports.

    Beispiele für gültige Eingaben:
    - "80"
    - "80,443"
    - "8000-8080"
    - "22,80,443,8000-8080"

    Args:
        port_string: Der String mit den Portangaben.

    Returns:
        Eine sortierte Liste von eindeutigen Portnummern.
    """
    ports = set()
    try:
        parts = [p.strip() for p in port_string.split(',')]
        for part in parts:
            if not part:
                continue
            if '-' in part:
                start, end = map(int, part.split('-'))
                if 0 < start <= end < 65536:
                    ports.update(range(start, end + 1))
            else:
                port_num = int(part)
                if 0 < port_num < 65536:
                    ports.add(port_num)
    except ValueError:
        # Bei ungültigen Zeichen (z.B. Buchstaben) wird eine leere Liste zurückgegeben
        return []
    return sorted(list(ports))

def scan_single_port(target_ip: str, port: int) -> Optional[dict]:
    """
    Scannt einen einzelnen Port auf einem Ziel-Host mit nmap zur Diensterkennung.

    Führt 'nmap -sV' aus, um den Dienst und die Version zu ermitteln.
    Der Timeout ist auf 30 Sekunden gesetzt, um zu lange Wartezeiten zu vermeiden.

    Args:
        target_ip: Die IP-Adresse des Ziels.
        port: Die zu scannende Portnummer.

    Returns:
        Ein Dictionary mit den Scan-Ergebnissen, wenn der Port offen ist.
        Beispiel: {'port': 'tcp/80', 'status': 'open', 'service': 'http', 'details': 'Apache httpd 2.4.41'}
        Gibt None zurück, wenn der Port geschlossen ist, nmap nicht gefunden wird oder ein Fehler auftritt.
    """
    try:
        command = ['nmap', '-sV', '-p', str(port), target_ip, '-oX', '-']
        
        startupinfo = None
        if platform.system().lower() == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
        process = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            startupinfo=startupinfo, 
            timeout=30 # Verhindert, dass der Scan ewig hängt
        )

        if process.returncode != 0 or not process.stdout:
            return None

        root = ET.fromstring(process.stdout)
        port_elem = root.find(f".//port[@portid='{port}']")
        if port_elem is None:
            return None
            
        state_elem = port_elem.find('state')
        if state_elem is None or state_elem.get('state') != 'open':
            return None

        result = {
            "port": f"{port_elem.get('protocol')}/{port}",
            "status": "open",
            "service": "unknown",
            "details": ""
        }
        
        service_elem = port_elem.find('service')
        if service_elem is not None:
            result["service"] = service_elem.get('name', 'unknown')
            product = service_elem.get('product', '')
            version = service_elem.get('version', '')
            extra_info = service_elem.get('extrainfo', '')
            details = f"{product} {version} {extra_info}".strip()
            result["details"] = details if details else " " # Leerzeichen um Tabellenzelle zu füllen
            
        return result
        
    except (FileNotFoundError, ET.ParseError, subprocess.TimeoutExpired):
        # FileNotFoundError: nmap ist nicht installiert oder nicht im PATH
        # ET.ParseError: nmap gab eine ungültige XML-Ausgabe zurück
        # TimeoutExpired: Scan dauerte länger als 30 Sekunden
        return None