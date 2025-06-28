# scanner_engine.py - Plattformübergreifende Version

import socket
import netifaces
import ipaddress
import platform
import subprocess
import xml.etree.ElementTree as ET
import shutil  # Wichtig für die Nmap-Prüfung
from typing import List, Tuple, Optional, Callable

def check_nmap_availability() -> bool:
    """
    Prüft, ob der 'nmap'-Befehl im System-PATH verfügbar ist.
    Gibt True zurück, wenn nmap gefunden wird, sonst False.
    """
    return shutil.which("nmap") is not None

def get_network_info() -> Tuple[Optional[str], Optional[str]]:
    """
    Ermittelt die lokale IP-Adresse und den Netzwerkbereich.
    Diese Funktion ist bereits plattformunabhängig.
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
    Sucht nach aktiven Hosts in einem bestimmten Netzwerkbereich mittels Ping (plattformübergreifend).
    """
    try:
        network = ipaddress.ip_network(network_range, strict=False)
        if network.num_addresses > 1:
            hosts_to_scan = list(network.hosts())
        else:
            hosts_to_scan = [network.network_address]

        total_hosts = len(hosts_to_scan)
        if total_hosts == 0:
            progress_callback.emit("error:Keine gültigen Hosts zum Scannen in diesem Bereich.")
            return

        system = platform.system().lower()

        for i, host in enumerate(hosts_to_scan):
            if is_stopping_func():
                break

            host_str = str(host)
            
            # Plattformspezifische Ping-Befehle
            if system == 'windows':
                command = ['ping', '-n', '1', '-w', '1000', host_str]
            elif system == 'darwin':  # macOS
                command = ['ping', '-c', '1', '-t', '1', host_str]
            else:  # Linux und andere
                command = ['ping', '-c', '1', '-W', '1', host_str]
            
            # startupinfo ist nur für Windows, um das Konsolenfenster zu verstecken
            startupinfo = None
            if system == 'windows':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            try:
                response = subprocess.run(
                    command, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL, 
                    startupinfo=startupinfo, 
                    check=False,
                    timeout=2 # Timeout für den Ping-Befehl
                )
                
                if response.returncode == 0:
                    hostname = ""
                    try:
                        # Reverse-DNS-Lookup
                        data = socket.gethostbyaddr(host_str)
                        hostname = data[0]
                    except (socket.herror, socket.gaierror):
                        hostname = ""
                    progress_callback.emit(f"host_found:{host_str}|||{hostname}")
            except (subprocess.TimeoutExpired, Exception) as e:
                # Fehler oder Timeout einfach ignorieren und weitermachen
                print(f"Fehler oder Timeout bei Ping an {host_str}: {e}")

            progress = int(((i + 1) / total_hosts) * 100)
            progress_callback.emit(f"progress:{progress}")

    except Exception as e:
        progress_callback.emit(f"error:Ein Fehler ist aufgetreten: {e}")

def parse_ports(port_string: str) -> List[int]:
    """ Parst einen String mit Portangaben. Diese Funktion ist plattformunabhängig. """
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
        return []
    return sorted(list(ports))

def scan_single_port(target_ip: str, port: int) -> Optional[dict]:
    """ Scannt einen einzelnen Port mit nmap (plattformübergreifend). """
    try:
        command = ['nmap', '-sV', '-p', str(port), target_ip, '-oX', '-']
        
        system = platform.system().lower()
        startupinfo = None
        if system == 'windows':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
        process = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            startupinfo=startupinfo, 
            timeout=30
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
            result["details"] = details if details else " "
            
        return result
        
    except FileNotFoundError:
        # Dieser Fehler tritt auf, wenn nmap nicht gefunden wird.
        print("Fehler: nmap konnte nicht gefunden werden. Stellen Sie sicher, dass es installiert ist.")
        return None
    except (ET.ParseError, subprocess.TimeoutExpired):
        return None