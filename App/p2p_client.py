import socket
import io
import pyaudio
import wave
import numpy as np
import threading
import librosa

class VoiceChatClient:
    def __init__(self, os='windows', name='user', host='localhost', port=3280, input_device_index=0, output_device_index=0, update_text_listbox=None):
        self.NAME = name
        self.HOST = host
        self.PORT = port
        self.BUFFERSIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.update_text_listbox = update_text_listbox
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # if os == 'windows':
            # self.client_socket.setblocking(False) # set non-blocking on windows for faster response
        self.is_running = False
        self.is_deafened = True
        self.is_muted = True
        self.is_recording = False
        self.recorded_frames = []

        self.pitch_level = 0
        self.pitch_resampler = 'fft'

        self.input_device_index = input_device_index
        self.output_device_index = output_device_index

    def connect(self):
        self.client_socket.connect((self.HOST, self.PORT))
        self.client_socket.send(b'<hi><' + self.NAME.encode() + b'/>' + b'</hi>')
        self.update_text_listbox(f"Connected to {self.HOST}:{self.PORT}")
        print(f"Connected to {self.HOST}:{self.PORT}")
        return

    def disconnect(self):
        # sent disconnect to server
        try:
            self.client_socket.send(b'<disconnect><'+self.NAME.encode()+b'/></disconnect>')
            self.client_socket.close()
            print("Disconnected from server.")
        except OSError:
            print("Error in client disconnect")
        return
    
    def set_mute_status(self, status):
        self.is_muted = status
        return
    
    def set_deafen_status(self, status):
        self.is_deafened = status
        return
    
    def set_record_status(self, status):
        if status == True:
            # start recording
            self.recorded_frames = []
        else:
            # stop recording
            # save recorded frames to a file
            if len(self.recorded_frames) > 0:
                self.save_recorded_audio()
        self.is_recording = status
        return
    
    def set_pitch_level(self, level, resampler):
        self.pitch_level = level
        self.pitch_resampler = resampler
        print(f"Pitch level set to {level}")
        print(f"Resampler set to {resampler}")
        return
    
    def pitch_shift(self, data, level):
        # level: -12 to 12
        if level == 0:
            return data
        
        y = np.frombuffer(data, dtype=np.int16)
        y_float = y.astype(np.float32) / 32767.0  # Convert to floating-point and normalize
        
        # Apply pitch shifting with librosa
        y_shifted = librosa.effects.pitch_shift(y_float, sr=self.RATE, n_steps=level, n_fft=512, bins_per_octave=12, res_type=self.pitch_resampler)
        
        # # Apply overlap-add method for smoother transition
        # hop_length = 512  # Adjust as needed
        # window = 'hann'  # Use Hann window for smoothness
        # stft_matrix = librosa.stft(y_shifted, n_fft=512, hop_length=hop_length, window=window)
        # y_shifted_smooth = librosa.istft(stft_matrix, hop_length=hop_length, window=window)
        
        # # Convert back to 16-bit integer
        y_shifted_int16 = (y_shifted * 32767).astype(np.int16)
        
        return y_shifted_int16.tobytes()
    
    def save_recorded_audio(self):
        print("Saving recorded audio...")
        filename = 'recorded_audio.wav'
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.recorded_frames))
        wf.close()
        print(f"Recorded audio saved as {filename}")
        self.update_text_listbox(f"Recording saved as {filename}")
        return

    def receive_audio(self):
        while self.is_running:
            try:
                data = self.client_socket.recv(self.BUFFERSIZE)
                
                # e.g. b'<hi><username/></hi>'
                if data.startswith(b'<hi>'):
                    username = data.split(b'/')[0].split(b'<')[-1].decode()
                    self.update_text_listbox(f'{username} has joined the chat.')

                # e.g. b'<disconnect><username/></disconnect>'
                elif data.startswith(b'<disconnect>'):
                    username = data.split(b'/')[0].split(b'<')[-1].decode()
                    self.update_text_listbox(f'{username} has left the chat.')

                elif data.startswith(b'<server-stop/>'):
                    self.update_text_listbox(f"Server has stopped.")

                # e.g. b'<text><username/>Hello<text/>'
                elif data.startswith(b'<text>'):
                    username = data.split(b'/>')[0].split(b'<')[-1].decode()
                    text = data.split(b'/>')[-1].split(b'<')[0].decode()
                    self.update_text_listbox(f'{username}: {text}')

                # audio data
                elif not data.endswith(b'<hi/>') and not data.endswith(b'<disconnect/>') and not data.endswith(b'<server-stop/>') and not data.endswith(b'<text/>'):
                    self.stream.write(data) if not self.is_deafened else None

                if self.is_recording:
                    self.recorded_frames.append(data)

            except ConnectionResetError:
                print("Connection with server closed.")
                break
            except IOError:
                print("IOError in client receive_audio")
                break

    def send_audio(self):
        while self.is_running:
            try:
                data = self.stream.read(self.CHUNK)
                if self.pitch_level != 0 and len(data) != 0:
                    data = self.pitch_shift(data, self.pitch_level)
                self.client_socket.send(data) if not self.is_muted else None
                if self.is_recording and not self.is_muted:
                    self.recorded_frames.append(data)
            except ConnectionResetError:
                print("Connection with server closed.")
                break
            except IOError:
                print("IOError in client send_audio")
                break

    def send_text(self, text):
        data = b'<text><' + self.NAME.encode() + b'/>' + text.encode() + b'</text>'
        self.client_socket.send(data)
        return

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
