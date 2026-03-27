import tkinter as tk

class SelectionScreen:
    def __init__(self, parent, on_select_admin, on_select_orchestrating, on_select_cluster):
        self.frame = tk.Frame(parent, bg='#0066cc')
        tk.Label(self.frame, text="NuxClus Setup", font=("Arial", 24, "bold"), bg='#0066cc', fg='white').pack(pady=20)
        tk.Label(self.frame, text="Select Setup Type", font=("Arial", 16), bg='#0066cc', fg='white').pack(pady=10)

        button_style = {'bg': '#ffffff', 'fg': '#0066cc', 'font': ('Arial', 12), 'width': 20, 'height': 2}

        tk.Button(self.frame, text="Admin", command=on_select_admin, **button_style).pack(pady=10)
        tk.Button(self.frame, text="Orchestrating Node", command=on_select_orchestrating, **button_style).pack(pady=10)
        tk.Button(self.frame, text="Cluster Node", command=on_select_cluster, **button_style).pack(pady=10)