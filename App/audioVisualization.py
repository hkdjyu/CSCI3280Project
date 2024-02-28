import pyaudio
import os
import struct
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError

# constants
CHUNK = 1024 * 2             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second

# create matplotlib figure and axes
fig, ax = plt.subplots(1, figsize=(15, 7))

# pyaudio class instance
p = pyaudio.PyAudio()

# get list of available inputs
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

# select input
audio_input = input("\n\nSelect input by Device id: ")

# stream object to get data from microphone
stream = p.open(
    input_device_index=int(audio_input),
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

# variable for plotting
x = np.arange(0, 2 * CHUNK, 2)

# create a line object with random data
line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=1)

# basic formatting for the axes
ax.set_title('AUDIO WAVEFORM')
ax.set_xlabel('samples')
ax.set_ylabel('volume')
ax.set_ylim(-1024, 1024)
ax.set_xlim(0, 2 * CHUNK)
plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[-1024, 0, 1024])

# show the plot
plt.show(block=False)

print('stream started')

# for measuring frame rate
frame_count = 0
start_time = time.time()

while True:
    try:
        # binary data
        data = stream.read(CHUNK)

        # convert data to integers
        data_int = struct.unpack(str(CHUNK) + 'h', data)  # Use 'h' format instead of 'B'

        # create np array
        data_np = np.array(data_int, dtype=np.int16)  # Use np.int16 as dtype

        line.set_ydata(data_np)

        # update figure canvas
        fig.canvas.draw()
        fig.canvas.flush_events()
        frame_count += 1

    except KeyboardInterrupt:
        # Calculate average frame rate
        frame_rate = frame_count / (time.time() - start_time)

        print('Stream stopped')
        print('Average frame rate = {:.0f} FPS'.format(frame_rate))
        break