from .loader import Config

config = None

def setup(config_file):
    global config
    config = Config(config_file)
    return config