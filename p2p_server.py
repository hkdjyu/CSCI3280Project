import sys
import socket
import pyaudio
import threading

class VoiceChatServer:
    def __init__(self, os='windows', name='server', host='localhost', port=3280):
        self.OS = os
        self.NAME = name
        self.HOST = host
        self.PORT = port
        self.BUFFERSIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.is_running = False
        self.client_sockets = []

    def receive_audio(self, client_socket):
        while self.is_running:
            try:
                data = client_socket.recv(self.BUFFERSIZE)

                if data == b'ping':
                    # send name
                    client_socket.send(self.NAME.encode())
                    continue

                if data == b'disconnect':
                    print("Client disconnected.")
                    self.client_sockets.remove(client_socket) if client_socket in self.client_sockets else None
                    break
                for socket in self.client_sockets:
                    if socket != client_socket:
                        socket.send(data)
            except ConnectionResetError:
                print("Connection with client closed.")
                self.client_sockets.remove(client_socket)
                break

    def start(self):
        self.is_running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if self.OS == 'windows':
        #     server_socket.setblocking(False) # set non-blocking on windows for faster response
        server_socket.bind((self.HOST, self.PORT))
        server_socket.listen()

        print(f"{self.NAME} listening on {self.HOST}:{self.PORT}")

        p = pyaudio.PyAudio()

        while self.is_running:
            client_socket, addr = server_socket.accept()
            print(f"Connected to {addr}")

            self.client_sockets.append(client_socket)

            receive_thread = threading.Thread(target=self.receive_audio, args=(client_socket,))
            receive_thread.start()
    
    def stop(self):
        for client_socket in self.client_sockets:
            client_socket.send(b'disconnect')
            client_socket.close()
        self.client_sockets.clear()
        self.is_running = False
        print("Server stopped.")
        return
        

if __name__ == "__main__":
    server = VoiceChatServer()
    server.start()
