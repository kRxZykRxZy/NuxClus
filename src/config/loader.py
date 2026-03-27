import json

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.data = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, d):
        self.data.update(d)

    def save(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.data, f, indent=4)