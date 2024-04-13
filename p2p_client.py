import socket
import pyaudio
import threading

class VoiceChatClient:
    def __init__(self, os='windows', host='localhost', port=3280, input_device_index=0, output_device_index=0):
        self.HOST = host
        self.PORT = port
        self.BUFFERSIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os == 'windows':
            self.client_socket.setblocking(False) # set non-blocking on windows for faster response
        self.is_running = False
        self.is_deafened = False
        self.is_muted = False

        self.input_device_index = input_device_index
        self.output_device_index = output_device_index

    def connect(self):
        self.client_socket.connect((self.HOST, self.PORT))
        print(f"Connected to {self.HOST}:{self.PORT}")
        return

    def disconnect(self):
        # sent b'disconnect' to server
        self.client_socket.send(b'disconnect')
        self.client_socket.close()
        print("Disconnected from server.")
        return
    
    def set_mute_status(self, status):
        self.is_muted = status
        return
    
    def set_deafen_status(self, status):
        self.is_deafened = status
        return

    def receive_audio(self):
        while self.is_running:
            try:
                data = self.client_socket.recv(self.BUFFERSIZE)
                self.stream.write(data) if not self.is_deafened else None
            except ConnectionResetError:
                print("Connection with server closed.")
                break
            except IOError:
                print("IOError")
                break

    def send_audio(self):
        while self.is_running:
            try:
                data = self.stream.read(self.CHUNK)
                self.client_socket.send(data) if not self.is_muted else None
            except ConnectionResetError:
                print("Connection with server closed.")
                break
            except IOError:
                print("IOError")
                break

    def start(self):
        self.is_running = True
        self.connect()

        p = pyaudio.PyAudio()
        input_channels= p.get_device_info_by_index(self.input_device_index).get('maxInputChannels')
        output_channels = p.get_device_info_by_index(self.output_device_index).get('maxOutputChannels')

        # print(f'input_channels: {input_channels}')
        # print(f'output_channels: {output_channels}')
        # print(f'input_device_index: {self.input_device_index}')
        # print(f'output_device_index: {self.output_device_index}')
        # print(f'Input Device: {p.get_device_info_by_index(self.input_device_index)["name"]}')
        # print(f'Output Device: {p.get_device_info_by_index(self.output_device_index)["name"]}')
        self.stream = p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             input_device_index=self.input_device_index,
                             output=True,
                             output_device_index=self.output_device_index,
                             frames_per_buffer=self.CHUNK)

        receive_thread = threading.Thread(target=self.receive_audio)
        send_thread = threading.Thread(target=self.send_audio)

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

        self.stream.stop_stream()
        self.stream.close()
        p.terminate()
        self.client_socket.close()

    def stop(self):
        self.disconnect()
        self.is_running = False
        return

if __name__ == "__main__":
    client = VoiceChatClient()
    try:
        client.start()
    except KeyboardInterrupt:
        client.disconnect()
        exit()
