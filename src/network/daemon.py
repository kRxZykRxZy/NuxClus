import asyncio
from src.network.tcp import WebsocketServer

class Daemon:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.server = WebsocketServer(host, port)

    def start(self):
        print(f"Starting daemon on {self.host}:{self.port}")
        asyncio.run(self.server.start())