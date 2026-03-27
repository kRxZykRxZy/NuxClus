import tkinter as tk
from tkinter import filedialog
from .screens.selection_screen import SelectionScreen
from .screens.admin_screen import AdminScreen
from .screens.orchestrating_screen import OrchestratingScreen
from .screens.cluster_screen import ClusterScreen

class SetupUI:
    def __init__(self, root, config_obj):
        self.config_obj = config_obj
        self.root = root
        self.root.title("NuxClus Setup")
        self.root.geometry("600x400")
        self.root.configure(bg='#0066cc')  # Docker-like blue

        self.main_frame = tk.Frame(self.root, bg='#0066cc')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.selection_screen = SelectionScreen(self.main_frame, self.select_admin, self.select_orchestrating, self.select_cluster)
        self.admin_screen = AdminScreen(self.main_frame, self.proceed_admin, self.back_to_selection, self.config_obj)
        self.orchestrating_screen = OrchestratingScreen(self.main_frame, self.proceed_orchestrating, self.back_to_selection)
        self.cluster_screen = ClusterScreen(self.main_frame, self.proceed_cluster, self.back_to_selection)

        self.show_frame(self.selection_screen.frame)

    def show_frame(self, frame):
        for f in [self.selection_screen.frame, self.admin_screen.frame, self.orchestrating_screen.frame, self.cluster_screen.frame]:
            f.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)

    def select_admin(self):
        self.show_frame(self.admin_screen.frame)

    def select_orchestrating(self):
        self.show_frame(self.orchestrating_screen.frame)

    def select_cluster(self):
        self.show_frame(self.cluster_screen.frame)

    def back_to_selection(self):
        self.show_frame(self.selection_screen.frame)

    def proceed_admin(self, vars):
        self.config_obj.update({k: v.get() for k, v in vars.items()})
        self.config_obj.data['setup_type'] = 'admin'
        self.save_config()

    def proceed_orchestrating(self, vars):
        self.config_obj.update({k: v.get() for k, v in vars.items()})
        self.config_obj.data['setup_type'] = 'orchestrating'
        self.assign_ip()
        self.save_config()

    def proceed_cluster(self, vars):
        self.config_obj.update({k: v.get() for k, v in vars.items()})
        self.config_obj.data['setup_type'] = 'cluster'
        self.assign_ip()
        self.save_config()

    def assign_ip(self):
        import socket
        import subprocess
        port = 8765
        # First try 10.0.0.1 to 10.0.0.254
        for host in range(1, 255):
            ip = f"10.0.0.{host}"
            if self.try_assign_ip(ip, port):
                return
        # Then 10.0.1.0 to 10.0.255.254, etc.
        for minor in range(1, 256):
            for host in range(255):
                ip = f"10.0.{minor}.{host}"
                if self.try_assign_ip(ip, port):
                    return
        # Fallback
        self.config_obj.data['server_ip'] = '127.0.0.1'
        self.config_obj.data['server_port'] = port

    def try_assign_ip(self, ip, port):
        import socket
        import subprocess
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((ip, port))
            self.config_obj.data['server_ip'] = ip
            self.config_obj.data['server_port'] = port
            return True
        except OSError:
            # Try to add the IP to loopback
            try:
                subprocess.run(['netsh', 'interface', 'ipv4', 'add', 'address', 'name="Loopback Pseudo-Interface 1"', ip, '255.255.255.0'], check=True, capture_output=True)
                # Try bind again
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((ip, port))
                self.config_obj.data['server_ip'] = ip
                self.config_obj.data['server_port'] = port
                return True
            except:
                return False

    def save_config(self):
        self.config_obj.save()
        self.root.quit()

if __name__ == "__main__":
    from src.config.loader import Config
    config_obj = Config('config.json')
    root = tk.Tk()
    app = SetupUI(root, config_obj)
    root.mainloop()
