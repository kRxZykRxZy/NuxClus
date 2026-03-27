import asyncio
import websockets
import json
from src.network.handler import handle

class WebsocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = set()

    async def handler(self, websocket, path):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                print(f"Received message: {message}")
                handle(json.loads(message), websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)

    async def start(self):
        server = await websockets.serve(self.handler, self.host, self.port)
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        await server.wait_closed()