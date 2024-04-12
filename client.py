# P2P voice chat client using socket programming
# Description: 
# A simple voice chat client that connects to a server.
# It records audio from the microphone and sends it to the server.
# It also receives audio from the server and plays it back.

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

# Function to receive audio from the server
def receive_audio():
    while True:
        try:
            data = client_socket.recv(BUFFERSIZE)
            stream.write(data)
        except ConnectionResetError:
            print("Connection with server closed.")
            break

# Function to send audio to the server
def send_audio():
    while True:
        data = stream.read(CHUNK)
        client_socket.send(data)

# Main function to start the client
def main():
    global client_socket
    global stream

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    output=True,
                    frames_per_buffer=CHUNK)

    receive_thread = threading.Thread(target=receive_audio)
    send_thread = threading.Thread(target=send_audio)

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()

    stream.stop_stream()
    stream.close()
    p.terminate()
    client_socket.close()

if __name__ == "__main__":
    main()
    