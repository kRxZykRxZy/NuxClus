import tkinter as tk
from ..admin_management import AdminManagementUI

class AdminScreen:
    def __init__(self, parent, on_proceed, on_back, config_obj):
        self.config_obj = config_obj
        self.frame = tk.Frame(parent, bg='#0066cc')
        tk.Label(self.frame, text="Admin Setup Options", font=("Arial", 18, "bold"), bg='#0066cc', fg='white').pack(pady=20)

        self.vars = {
            'enable_api_server': tk.BooleanVar(),
            'enable_etcd': tk.BooleanVar(),
            'enable_commands': tk.BooleanVar(),
            'enable_docker': tk.BooleanVar(),
            'enable_networking': tk.BooleanVar(),
        }

        options = [
            ("Enable API Server", 'enable_api_server'),
            ("Enable etcd", 'enable_etcd'),
            ("Enable Command Execution", 'enable_commands'),
            ("Enable Docker", 'enable_docker'),
            ("Enable Networking", 'enable_networking'),
        ]

        for text, var in options:
            tk.Checkbutton(self.frame, text=text, variable=self.vars[var], bg='#0066cc', fg='white', selectcolor='#004499', font=('Arial', 12)).pack(anchor=tk.W, padx=50, pady=5)

        tk.Button(self.frame, text="Manage Servers", command=self.manage_servers, bg='#ffffff', fg='#0066cc', font=('Arial', 12)).pack(pady=10)
        tk.Button(self.frame, text="Proceed", command=lambda: on_proceed(self.vars), bg='#ffffff', fg='#0066cc', font=('Arial', 12)).pack(pady=20)
        tk.Button(self.frame, text="Back", command=on_back, bg='#cccccc', fg='#000000', font=('Arial', 12)).pack()

    def manage_servers(self):
        AdminManagementUI(self.frame, self.config_obj)