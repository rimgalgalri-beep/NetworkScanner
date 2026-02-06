import subprocess
import json
import sqlite3
import platform
import re
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Try to import supabase, but fall back to requests-based API if it fails
try:
    from supabase import create_client, Client
    SUPABASE_SDK_AVAILABLE = True
except Exception:
    SUPABASE_SDK_AVAILABLE = False

SUPABASE_AVAILABLE = REQUESTS_AVAILABLE


class NetworkScanner:
    def __init__(self, db_name="tinklo_vardas_irenginiai_data.db", use_supabase=None):
        """
        Initialize NetworkScanner with SQLite or Supabase backend.
        
        Args:
            db_name: SQLite database filename (ignored if use_supabase=True)
            use_supabase: Force Supabase backend (True/False/None for auto-detect from env)
        """
        self.db_name = db_name
        self.devices = []
        
        # Auto-detect Supabase from environment if not explicitly set
        if use_supabase is None:
            use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
        
        self.use_supabase = use_supabase and SUPABASE_AVAILABLE
        
        if self.use_supabase:
            self.supabase_url = os.getenv("SUPABASE_URL")
            self.supabase_key = os.getenv("SUPABASE_KEY")
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")
            # Use REST API instead of SDK
            if SUPABASE_SDK_AVAILABLE:
                self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            self.supabase_headers = {
                "Authorization": f"Bearer {self.supabase_key}",
                "Content-Type": "application/json",
                "apikey": self.supabase_key
            }
        
        self.init_database()

    def init_database(self):
        """Initialize SQLite database or verify Supabase table schema."""
        if self.use_supabase:
            # Verify Supabase table exists via REST API
            try:
                url = f"{self.supabase_url}/rest/v1/irenginiai?limit=1"
                response = requests.get(url, headers=self.supabase_headers)
                if response.status_code == 200:
                    pass  # Table exists
            except Exception as e:
                print(f"Note: Could not verify Supabase table, will try to insert anyway: {e}")
        else:
            # Create SQLite table
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS irenginiai (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip_adresas TEXT UNIQUE NOT NULL,
                    mac_adresas TEXT,
                    host_name TEXT,
                    duomenu_perdavimo_greitis TEXT,
                    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()

    def scan_network(self):
        """Scan network devices based on OS."""
        if platform.system() == "Windows":
            self._scan_windows()
        elif platform.system() == "Linux":
            self._scan_linux()
        elif platform.system() == "Darwin":
            self._scan_macos()

    def _scan_windows(self):
        """Scan network devices on Windows using ARP."""
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if 'dynamic' in line or 'static' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        mac = parts[1].replace('-', ':')
                        hostname = self._resolve_hostname(ip)
                        transfer_rate = self._get_transfer_rate_windows(ip)
                        
                        self.devices.append({
                            'ip_adresas': ip,
                            'mac_adresas': mac,
                            'host_name': hostname,
                            'duomenu_perdavimo_greitis': transfer_rate
                        })
        except Exception as e:
            print(f"Error scanning network on Windows: {e}")

    def _scan_linux(self):
        """Scan network devices on Linux using ARP and nmap."""
        try:
            result = subprocess.run(
                ["arp-scan", "-l"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 2 and ':' in parts[1]:
                    ip = parts[0].strip()
                    mac = parts[1].strip()
                    hostname = self._resolve_hostname(ip)
                    transfer_rate = self._get_transfer_rate_linux(ip)
                    
                    self.devices.append({
                        'ip_adresas': ip,
                        'mac_adresas': mac,
                        'host_name': hostname,
                        'duomenu_perdavimo_greitis': transfer_rate
                    })
        except Exception as e:
            print(f"Error scanning network on Linux: {e}")
            self._scan_linux_fallback()

    def _scan_linux_fallback(self):
        """Fallback method for Linux using standard arp-scan."""
        try:
            result = subprocess.run(
                ["cat", "/proc/net/arp"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')[1:]
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 4:
                        ip = parts[0]
                        mac = parts[3]
                        hostname = self._resolve_hostname(ip)
                        transfer_rate = self._get_transfer_rate_linux(ip)
                        
                        self.devices.append({
                            'ip_adresas': ip,
                            'mac_adresas': mac,
                            'host_name': hostname,
                            'duomenu_perdavimo_greitis': transfer_rate
                        })
        except Exception as e:
            print(f"Error in Linux fallback scan: {e}")

    def _scan_macos(self):
        """Scan network devices on macOS using arp."""
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.split('\n')
            for line in lines:
                if ':' in line:
                    match = re.search(r'(\S+)\s+\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([a-f0-9:]+)', line)
                    if match:
                        hostname = match.group(1)
                        ip = match.group(2)
                        mac = match.group(3)
                        transfer_rate = self._get_transfer_rate_macos(ip)
                        
                        self.devices.append({
                            'ip_adresas': ip,
                            'mac_adresas': mac,
                            'host_name': hostname,
                            'duomenu_perdavimo_greitis': transfer_rate
                        })
        except Exception as e:
            print(f"Error scanning network on macOS: {e}")

    def _resolve_hostname(self, ip):
        """Resolve IP address to hostname."""
        try:
            result = subprocess.run(
                ["ping", "-n", "1"] if platform.system() == "Windows" else ["ping", "-c", "1"],
                args=[ip],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            import socket
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return "Unknown"

    def _get_transfer_rate_windows(self, ip):
        """Get data transfer rate on Windows (simulated)."""
        try:
            result = subprocess.run(
                ["ping", "-n", "2", "-w", "1000", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if "average" in result.stdout:
                match = re.search(r'Average = (\d+)ms', result.stdout)
                if match:
                    return f"{match.group(1)}ms response time"
            return "Not available"
        except Exception:
            return "Not available"

    def _get_transfer_rate_linux(self, ip):
        """Get data transfer rate on Linux (simulated)."""
        try:
            result = subprocess.run(
                ["ping", "-c", "2", "-W", "1", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if "min/avg/max" in result.stdout:
                match = re.search(r'min/avg/max[/\w]+ = ([\d.]+)/([\d.]+)/([\d.]+)', result.stdout)
                if match:
                    return f"avg: {match.group(2)}ms"
            return "Not available"
        except Exception:
            return "Not available"

    def _get_transfer_rate_macos(self, ip):
        """Get data transfer rate on macOS (simulated)."""
        try:
            result = subprocess.run(
                ["ping", "-c", "2", "-W", "1000", ip],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if "min/avg/max" in result.stdout:
                match = re.search(r'min/avg/max/stddev = ([\d.]+)/([\d.]+)/([\d.]+)', result.stdout)
                if match:
                    return f"avg: {match.group(2)}ms"
            return "Not available"
        except Exception:
            return "Not available"

    def save_to_database(self):
        """Save scanned devices to SQLite or Supabase."""
        if self.use_supabase:
            self._save_to_supabase()
        else:
            self._save_to_sqlite()

    def _save_to_sqlite(self):
        """Save scanned devices to SQLite database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for device in self.devices:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO irenginiai 
                    (ip_adresas, mac_adresas, host_name, duomenu_perdavimo_greitis)
                    VALUES (?, ?, ?, ?)
                ''', (
                    device['ip_adresas'],
                    device['mac_adresas'],
                    device['host_name'],
                    device['duomenu_perdavimo_greitis']
                ))
            except sqlite3.IntegrityError:
                cursor.execute('''
                    UPDATE irenginiai 
                    SET mac_adresas=?, host_name=?, duomenu_perdavimo_greitis=?, scan_time=CURRENT_TIMESTAMP
                    WHERE ip_adresas=?
                ''', (
                    device['mac_adresas'],
                    device['host_name'],
                    device['duomenu_perdavimo_greitis'],
                    device['ip_adresas']
                ))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(self.devices)} devices to SQLite database")

    def _save_to_supabase(self):
        """Save scanned devices to Supabase PostgreSQL via REST API."""
        try:
            for device in self.devices:
                # Use Supabase REST API - try insert, then update on conflict
                url = f"{self.supabase_url}/rest/v1/irenginiai"
                payload = {
                    'ip_adresas': device['ip_adresas'],
                    'mac_adresas': device['mac_adresas'],
                    'host_name': device['host_name'],
                    'duomenu_perdavimo_greitis': device['duomenu_perdavimo_greitis'],
                    'scan_time': datetime.now().isoformat()
                }
                
                # Try insert with merge-duplicates preference
                response = requests.post(
                    url,
                    json=payload,
                    headers={**self.supabase_headers, 'Prefer': 'resolution=merge-duplicates'}
                )
                
                # If conflict (409), try update
                if response.status_code == 409:
                    # URL encode the IP address for the query
                    ip_encoded = quote(device['ip_adresas'], safe='')
                    update_url = f"{url}?ip_adresas=eq.{ip_encoded}"
                    update_payload = {
                        'mac_adresas': device['mac_adresas'],
                        'host_name': device['host_name'],
                        'duomenu_perdavimo_greitis': device['duomenu_perdavimo_greitis'],
                        'scan_time': datetime.now().isoformat()
                    }
                    try:
                        update_response = requests.patch(update_url, json=update_payload, headers=self.supabase_headers, timeout=10)
                        if update_response.status_code not in [200, 204]:
                            print(f"Warning: Update failed {update_response.status_code}: {update_response.text}")
                    except requests.exceptions.RequestException as e:
                        print(f"Warning: Update request failed: {e}")
                elif response.status_code not in [200, 201]:
                    print(f"Warning: Insert failed {response.status_code}: {response.text}")
            
            print(f"Saved {len(self.devices)} devices to Supabase")
        except Exception as e:
            print(f"Error saving to Supabase: {e}")

    def get_all_devices(self):
        """Retrieve all devices from SQLite or Supabase."""
        if self.use_supabase:
            return self._get_all_devices_supabase()
        else:
            return self._get_all_devices_sqlite()

    def _get_all_devices_sqlite(self):
        """Retrieve all devices from SQLite database."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM irenginiai ORDER BY scan_time DESC')
        rows = cursor.fetchall()
        conn.close()
        
        devices = []
        for row in rows:
            devices.append({
                'id': row[0],
                'ip_adresas': row[1],
                'mac_adresas': row[2],
                'host_name': row[3],
                'duomenu_perdavimo_greitis': row[4],
                'scan_time': row[5]
            })
        
        return devices

    def _get_all_devices_supabase(self):
        """Retrieve all devices from Supabase PostgreSQL via REST API."""
        try:
            url = f"{self.supabase_url}/rest/v1/irenginiai?order=scan_time.desc"
            response = requests.get(url, headers=self.supabase_headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error retrieving devices from Supabase: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error retrieving devices from Supabase: {e}")
            return []

    def print_results(self):
        """Print scan results in a formatted table."""
        print("\n" + "="*100)
        print("Tinklo irenginiai / Network Devices")
        print("="*100)
        
        devices = self.get_all_devices()
        
        if not devices:
            print("No devices found")
            return
        
        print(f"{'IP Adresas':<15} {'MAC Adresas':<20} {'Host Name':<25} {'Duomenu Greitis':<20} {'Scan Time':<20}")
        print("-"*100)
        
        for device in devices:
            print(f"{device['ip_adresas']:<15} {device['mac_adresas']:<20} {device['host_name']:<25} {device['duomenu_perdavimo_greitis']:<20} {device['scan_time']:<20}")
        
        print("="*100 + "\n")


def main():
    # Auto-detect Supabase from environment variables
    use_supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"))
    
    scanner = NetworkScanner(use_supabase=use_supabase)
    
    backend = "Supabase" if use_supabase else "SQLite"
    print(f"Starting network scan (backend: {backend})...")
    scanner.scan_network()
    
    if scanner.devices:
        scanner.save_to_database()
        scanner.print_results()
    else:
        print("No devices found during scan")


if __name__ == "__main__":
    main()
