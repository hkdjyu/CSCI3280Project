import pyaudio
import struct
import numpy as np
import tkinter as tk

# Constants
CHUNK = 1024 * 2             # Samples per frame
FORMAT = pyaudio.paInt16     # Audio format (bytes per sample)
CHANNELS = 1                 # Single channel for microphone
RATE = 44100                 # Samples per second

# Create tkinter window
root = tk.Tk()
root.title("Audio Waveform")
canvas = tk.Canvas(root, width=800, height=400, bg="black")
canvas.pack()

# Create line for waveform
line = canvas.create_line(0, 200, 0, 200, fill="white")

# PyAudio instance
p = pyaudio.PyAudio()

# Get list of available inputs
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

# Select input
audio_input = input("\n\nSelect input by Device id: ")

# Stream object to get data from microphone
stream = p.open(
    input_device_index=int(audio_input),
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

print('stream started')

# For measuring frame rate
frame_count = 0

while True:
    try:
        # Binary data
        data = stream.read(CHUNK)

        # Convert data to integers
        data_int = struct.unpack(str(CHUNK) + 'h', data)  # Use 'h' format instead of 'B'

        # Create np array
        data_np = np.array(data_int, dtype=np.int16)  # Use np.int16 as dtype

        # Scale the waveform to fit in canvas height
        scaled_data = np.interp(data_np, (data_np.min(), data_np.max()), (-200, 200))

        # Draw waveform on canvas
        canvas.delete(line)  # Delete previous waveform
        line = canvas.create_line([(i, 200 + scaled_data[i]) for i in range(len(scaled_data))], fill="white")

        root.update()  # Update tkinter window

        frame_count += 1

    except KeyboardInterrupt:
        # Stop stream and terminate PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Calculate average frame rate
        frame_rate = frame_count / (time.time() - start_time)

        print('Stream stopped')
        print('Average frame rate = {:.0f} FPS'.format(frame_rate))
        break

root.mainloop()
