import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import asyncio
import websockets

class AdminManagementUI:
    def __init__(self, parent, config_obj):
        self.config_obj = config_obj
        self.window = tk.Toplevel(parent)
        self.window.title("Admin - Manage Servers")
        self.window.geometry("500x400")
        self.window.configure(bg='#0066cc')

        tk.Label(self.window, text="Manage Orchestrating and Cluster Servers", font=("Arial", 16, "bold"), bg='#0066cc', fg='white').pack(pady=10)

        self.server_listbox = tk.Listbox(self.window, bg='#ffffff', fg='#000000', font=('Arial', 12))
        self.server_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.load_servers()

        button_frame = tk.Frame(self.window, bg='#0066cc')
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(button_frame, text="Discover", command=self.discover_servers, bg='#ffffff', fg='#0066cc').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Add Server", command=self.add_server, bg='#ffffff', fg='#0066cc').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit Server", command=self.edit_server, bg='#ffffff', fg='#0066cc').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Remove Server", command=self.remove_server, bg='#ffffff', fg='#0066cc').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Send Command", command=self.send_command, bg='#ffffff', fg='#0066cc').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Get Stats", command=self.get_stats, bg='#ffffff', fg='#0066cc').pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=self.window.destroy, bg='#cccccc', fg='#000000').pack(side=tk.RIGHT, padx=5)

    def load_servers(self):
        self.server_listbox.delete(0, tk.END)
        servers = self.config_obj.data.get('servers', [])
        for server in servers:
            self.server_listbox.insert(tk.END, f"{server['ip']} - {server['type']}")

    async def discover_async(self):
        port = 8765
        found = []
        for i in range(1, 255):
            ip = f"10.0.0.{i}"
            try:
                uri = f"ws://{ip}:{port}"
                async with websockets.connect(uri) as websocket:
                    await websocket.send('{"type": "ping"}')
                    response = await websocket.recv()
                    if response:
                        found.append({'ip': ip, 'type': 'unknown'})  # Could parse response for type
            except:
                pass
        return found

    def discover_servers(self):
        def run():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            found = loop.run_until_complete(self.discover_async())
            loop.close()
            servers = self.config_obj.data.get('servers', [])
            for server in found:
                if not any(s['ip'] == server['ip'] for s in servers):
                    servers.append(server)
            self.config_obj.data['servers'] = servers
            self.config_obj.save()
            self.load_servers()
        threading.Thread(target=run).start()

    def add_server(self):
        ip = simpledialog.askstring("Add Server", "Enter server IP:")
        if ip:
            type_ = simpledialog.askstring("Add Server", "Enter type (orchestrating/cluster):")
            if type_ in ['orchestrating', 'cluster']:
                servers = self.config_obj.data.get('servers', [])
                servers.append({'ip': ip, 'type': type_})
                self.config_obj.data['servers'] = servers
                self.config_obj.save()
                self.load_servers()
            else:
                messagebox.showerror("Error", "Invalid type")

    def edit_server(self):
        selected = self.server_listbox.curselection()
        if selected:
            index = selected[0]
            servers = self.config_obj.data.get('servers', [])
            server = servers[index]
            new_ip = simpledialog.askstring("Edit Server", "Enter new IP:", initialvalue=server['ip'])
            if new_ip:
                server['ip'] = new_ip
                self.config_obj.save()
                self.load_servers()

    def remove_server(self):
        selected = self.server_listbox.curselection()
        if selected:
            index = selected[0]
            servers = self.config_obj.data.get('servers', [])
            del servers[index]
            self.config_obj.data['servers'] = servers
            self.config_obj.save()
            self.load_servers()

    def send_command(self):
        selected = self.server_listbox.curselection()
        if selected:
            index = selected[0]
            servers = self.config_obj.data.get('servers', [])
            server = servers[index]
            cmd = simpledialog.askstring("Send Command", "Enter command:")
            if cmd:
                # Send via WebSocket
                def run():
                    async def send():
                        try:
                            uri = f"ws://{server['ip']}:8765"
                            async with websockets.connect(uri) as websocket:
                                await websocket.send(f'{{"type": "command", "command": "{cmd}"}}')
                                # Could receive response
                        except Exception as e:
                            messagebox.showerror("Error", str(e))
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(send())
                    loop.close()
                threading.Thread(target=run).start()

    def get_stats(self):
        selected = self.server_listbox.curselection()
        if selected:
            index = selected[0]
            servers = self.config_obj.data.get('servers', [])
            server = servers[index]
            # Get stats and show graph
            def run():
                async def get():
                    try:
                        uri = f"ws://{server['ip']}:8765"
                        async with websockets.connect(uri) as websocket:
                            await websocket.send('{"type": "stats"}')
                            response = await websocket.recv()
                            stats = eval(response)  # Unsafe, but for demo
                            # Show graph, e.g., CPU usage
                            import matplotlib.pyplot as plt
                            plt.bar(['CPU', 'Memory', 'Disk'], [stats['cpu']['usage_percent'], stats['memory']['percent'], stats['disks'][0]['percent']])
                            plt.show()
                    except Exception as e:
                        messagebox.showerror("Error", str(e))
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(get())
                loop.close()
            threading.Thread(target=run).start()