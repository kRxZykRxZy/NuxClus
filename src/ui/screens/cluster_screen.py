import tkinter as tk

class ClusterScreen:
    def __init__(self, parent, on_proceed, on_back):
        self.frame = tk.Frame(parent, bg='#0066cc')
        tk.Label(self.frame, text="Cluster Node Setup Options", font=("Arial", 18, "bold"), bg='#0066cc', fg='white').pack(pady=20)

        self.vars = {
            'enable_proxy': tk.BooleanVar(),
            'enable_commands': tk.BooleanVar(),
            'enable_docker': tk.BooleanVar(),
            'enable_storage': tk.BooleanVar(),
        }

        options = [
            ("Enable Proxy", 'enable_proxy'),
            ("Enable Command Execution", 'enable_commands'),
            ("Enable Docker", 'enable_docker'),
            ("Enable Storage", 'enable_storage'),
        ]

        for text, var in options:
            tk.Checkbutton(self.frame, text=text, variable=self.vars[var], bg='#0066cc', fg='white', selectcolor='#004499', font=('Arial', 12)).pack(anchor=tk.W, padx=50, pady=5)

        tk.Button(self.frame, text="Proceed", command=lambda: on_proceed(self.vars), bg='#ffffff', fg='#0066cc', font=('Arial', 12)).pack(pady=20)
        tk.Button(self.frame, text="Back", command=on_back, bg='#cccccc', fg='#000000', font=('Arial', 12)).pack()