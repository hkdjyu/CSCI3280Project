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
        self.BUFFERSIZE = 2048
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 2048
        self.is_running = False
        self.server_socket = None
        self.client_sockets = []

    def receive_audio(self, client_socket):
        while self.is_running:
            try:
                data = client_socket.recv(self.BUFFERSIZE)
                if data == b'ping':
                    # send name
                    client_socket.send(self.NAME.encode())
                    continue
                if data == b'ping-end':
                    self.client_sockets.remove(client_socket) if client_socket in self.client_sockets else None
                    break
                for socket in self.client_sockets:
                    if socket != client_socket:
                        socket.send(data)
                if data.startswith(b'<disconnect>'):
                        print("Client disconnected.")
                        self.client_sockets.remove(client_socket) if client_socket in self.client_sockets else None
                        break
            except ConnectionResetError:
                print("Connection with client closed.")
                self.client_sockets.remove(client_socket) if client_socket in self.client_sockets else None
                break
        return

    def start(self):
        self.is_running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if self.OS == 'windows':
        #     server_socket.setblocking(False) # set non-blocking on windows for faster response
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen()

        print(f"{self.NAME} listening on {self.HOST}:{self.PORT}")

        p = pyaudio.PyAudio()

        while self.is_running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Connected to {addr}")

                self.client_sockets.append(client_socket)

                receive_thread = threading.Thread(target=self.receive_audio, args=(client_socket,))
                receive_thread.start()
            except KeyboardInterrupt:
                self.stop()
                break
            except OSError:
                break
            except Exception as e:
                print(f"Error: {e}")
                break
    
    def stop(self):
        for client_socket in self.client_sockets:
            client_socket.send(b'<server-stop/>')
            client_socket.close()
        self.client_sockets.clear()
        self.server_socket.close()
        self.is_running = False
        print("Server stopped.")
        return
        

if __name__ == "__main__":
    server = VoiceChatServer()
    server.start()
