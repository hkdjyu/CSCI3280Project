import wave
import pyaudio
from threading import Thread

chunk = 1024
sample_format = pyaudio.paInt16
channels = 2
fs = 44100
filename = "./audio/output.wav"

class Recorder:

    def __init__(self):
        self.record_state = "NOT_RECORDING"
        self.p = pyaudio.PyAudio()

    def is_recording(self):
        return self.record_state == "RECORDING"
    
    def is_playing(self):
        return self.record_state == "PLAYING"

    def start_recording(self):
        if self.record_state == "NOT_RECORDING":
            self.stream = self.p.open(format=sample_format,
                                      channels=channels,
                                      rate=fs,
                                      frames_per_buffer=chunk,
                                      input=True)
            self.frames = []
            self.record_state = "RECORDING"
            print("Recording started...")

    def stop_recording(self):
        if self.record_state == "RECORDING":
            self.record_state = "NOT_RECORDING"
            print("Recording stopped...")
            # self.save_recording() # Save the recording

            # Stop and close the stream
            self.stream.stop_stream()
            self.stream.close()
            
            # Terminate the PortAudio interface
            # self.p.terminate()


    def record(self):
        while self.record_state == "RECORDING":
            data = self.stream.read(chunk)
            self.frames.append(data)

    def save_recording(self):
        if self.frames:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(self.p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            print("Recording saved to", filename)
        else:
            print("No recording to save.")



# chunk = 1024
# sample_format = pyaudio.paInt16
# channels = 2
# fs = 44100
# seconds = 3 # Record for 3 seconds
# filename = "output.wav"

# p = pyaudio.PyAudio() # Create an interface to PortAudio

# print('Recording')

# stream = p.open(format=sample_format,
#                 channels=channels,
#                 rate=fs,
#                 frames_per_buffer=chunk,
#                 input=True)

# frames = [] # Initialize array to store frames

# # Store data in chunks for 3 seconds
# for i in range(0, int(fs / chunk * seconds)):
#     data = stream.read(chunk)
#     frames.append(data)

# # Stop and close the stream
# stream.stop_stream()
# stream.close()
# # Terminate the PortAudio interface
# p.terminate()

# print('Finished recording')

# # Save the recorded data as a WAV file
# wf = wave.open(filename, 'wb')
# wf.setnchannels(channels)
# wf.setsampwidth(p.get_sample_size(sample_format))
# wf.setframerate(fs)
# wf.writeframes(b''.join(frames))
# wf.close()
