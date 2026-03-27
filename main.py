import os
import sys
import json
import ctypes

# Check for admin
if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.setup import setup
from src.ui.setup import SetupUI
from src.network.daemon import Daemon
import tkinter as tk

def main():
    # Prompt for config file location
    config_file = input("Enter config file path (e.g., config.json): ").strip()
    if not config_file:
        config_file = 'config.json'

    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump({}, f)

    config_obj = setup(config_file)

    if 'setup_type' not in config_obj.data:
        # Run setup
        root = tk.Tk()
        app = SetupUI(root, config_obj)
        root.mainloop()
        # After quit, reload config
        config_obj = setup(config_file)

    setup_type = config_obj.data.get('setup_type')
    if setup_type in ['orchestrating', 'cluster']:
        if 'server_ip' not in config_obj.data:
            # Assign IP
            import socket
            import subprocess
            port = 8765
            # Same logic as in setup.py
            for host in range(1, 255):
                ip = f"10.0.0.{host}"
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind((ip, port))
                    config_obj.data['server_ip'] = ip
                    config_obj.data['server_port'] = port
                    config_obj.save()
                    break
                except OSError:
                    try:
                        subprocess.run(['netsh', 'interface', 'ipv4', 'add', 'address', 'name="Loopback Pseudo-Interface 1"', ip, '255.255.255.0'], check=True, capture_output=True)
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.bind((ip, port))
                        config_obj.data['server_ip'] = ip
                        config_obj.data['server_port'] = port
                        config_obj.save()
                        break
                    except:
                        continue
            else:
                config_obj.data['server_ip'] = '127.0.0.1'
                config_obj.data['server_port'] = port
                config_obj.save()
        # Start the daemon
        ip = config_obj.data.get('server_ip', '127.0.0.1')
        port = config_obj.data.get('server_port', 8765)
        daemon = Daemon(host=ip, port=port)
        daemon.start()
        print("Daemon started. Press Ctrl+C to stop.")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Stopping daemon...")
    else:
        print("Admin mode: No server started.")

if __name__ == "__main__":
    main()