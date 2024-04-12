# P2P voice chat client
# It is a client that captures the voice data from the microphone and sends it to the server.
# Meanwhile, it receives voice data from the server and plays it through the speakers.

import asyncio
import websockets
import pyaudio

class VoiceChatClient:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, output=True, frames_per_buffer=1024)
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect("ws://localhost:8765")

    async def send_voice_data(self):
        while True:
            data = self.stream.read(1024)
            await self.websocket.send(data)

    async def receive_voice_data(self):
        while True:
            data = await self.websocket.recv()
            self.stream.write(data)

    async def start(self):
        await self.connect()
        await asyncio.gather(self.send_voice_data(), self.receive_voice_data())

if __name__ == "__main__":
    client = VoiceChatClient()
    asyncio.run(client.start())