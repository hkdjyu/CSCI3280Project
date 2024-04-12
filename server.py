# P2P voice chat server using socket programming
# Description: 
# A simple voice chat server that listens for incoming connections from clients.
# It receives audio from clients and plays it back to all connected clients except the sender.

import socket
import pyaudio
import wave
import threading
import time

# Global variables
HOST = 'localhost'
PORT = 5555
BUFFERSIZE = 1024
FORMAT = pyaudio.paInt16    
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# List to store client sockets
client_sockets = []

# Function to receive audio from a client and broadcast it to all clients
def receive_audio(client_socket):
    while True:
        try:
            data = client_socket.recv(BUFFERSIZE)
            for socket in client_sockets:
                if socket != client_socket:
                    socket.send(data)
        except ConnectionResetError:
            print("Connection with client closed.")
            client_sockets.remove(client_socket)
            break

# Main function to start the server
def main():
    global client_sockets

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server listening on {HOST}:{PORT}")

    p = pyaudio.PyAudio()

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")

        client_sockets.append(client_socket)

        receive_thread = threading.Thread(target=receive_audio, args=(client_socket,))
        receive_thread.start()

if __name__ == "__main__":
    main()