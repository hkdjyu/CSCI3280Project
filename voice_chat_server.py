# P2P voice chat server
# It is a server that listens for incoming connections from clients and forwards the voice data to all connected clients except the sender.
# The server is implemented using websockets, asyncio, and pyaudio.

import asyncio
import websockets
import pyaudio

class VoiceChatServer:
    def __init__(self):
        self.clients = set()

    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        try:
            while True:
                data = await websocket.recv()
                for client in self.clients:
                    if client != websocket:
                        await client.send(data)
        except websockets.exceptions.ConnectionClosedError:
            pass
        finally:
            self.clients.remove(websocket)

    async def start(self):
        server = await websockets.serve(self.handle_client, "localhost", 8765)
        await server.wait_closed()

if __name__ == "__main__":
    server = VoiceChatServer()
    asyncio.run(server.start())
