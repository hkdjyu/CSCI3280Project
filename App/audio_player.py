import wave

# import thread
from threading import Thread

import pyaudio
import time
import numpy as np
from threading import Thread
import librosa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AudioPlayer:
    
    def __init__(self):
        self.play_state = "NOT_PLAYING"
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.filename = ""
        self.speed = 1.0
        self.volume = 0.5
        self.start_time = 0 # from 0 to 1, 0 is the start of the audio, 1 is the end
        self.end_time = None # from 0 to 1, 0 is the start of the audio, 1 is the end
        self.current_time = 0 # from 0 to 1
        self.start_nframes = 0
        self.current_nframes = 0
        self.playingThread = None
        self.data = None
        self.srate = None

    def is_playing(self):
        return self.play_state == "PLAYING"
    
    def is_paused(self):
        return self.play_state == "PAUSED"

    def start_playing(self, filename, start_time=None, end_time=None):
        self.play_state = "PLAYING"
        self.filename = str(filename)

        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time

        # open the sampling audio file
        swf = wave.open(str(filename), 'rb')
        self.srate = swf.getframerate()
        signal = swf.readframes(-1)
        self.stream = self.p.open(format=self.p.get_format_from_width(swf.getsampwidth()),
                                    channels=swf.getnchannels(),
                                    rate=swf.getframerate(),
                                    output=True)
        swf.close()

        # write a new audio file with the new speed
        wf = wave.open("./temp/temp.wav", 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(self.srate * self.speed)
        wf.writeframes(signal)
        wf.close()

        # play the new audio file
        print("Playing started...")
        self.play("./temp/temp.wav")

    def play(self, filename, start_time=None, end_time=None):

        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if self.end_time is None:
            self.end_time = 1


        self.play_state = "PLAYING"

        # open the file
        wf = wave.open(filename, 'rb')

        # open the stream
        self.stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                  channels=wf.getnchannels(),
                                  rate=wf.getframerate(),
                                  output=True)
        # start time
        self.start_nframes = int(wf.getnframes() * self.start_time)
        self.current_nframes = self.start_nframes
        self.end_nframes = int(wf.getnframes() * self.end_time)

        # set the file pointer to the start time
        wf.setpos(self.start_nframes)

        # Read data
        self.data = wf.readframes(1024)

        print("Playing...")

        # Play the file
        while self.data != b'' and (self.play_state == "PLAYING" or self.play_state == "PAUSED"):
            if self.play_state == "PAUSED":
                time.sleep(0.1)
                continue

            if self.stream.is_active() == False or self.stream.is_stopped() == True or self.stream is None:
                break
            
            
            # Set the volume, data *= 0.1
            self.data = np.frombuffer(self.data, dtype=np.int16)
            self.data = (self.volume * self.data).astype(np.int16)
            self.data = self.data.tobytes()

            self.stream.write(self.data) # Write the data to the stream
            self.data = wf.readframes(1024) # Read the next chunk of data
            self.current_nframes += 1024 # Update the current frame
            self.current_time = self.current_nframes / wf.getnframes() # Update the current time
            if self.current_nframes >= wf.getnframes():
                break # reached the end of the file

            if self.current_nframes >= self.end_nframes:
                break # reached the end time

        # Close and terminate the stream
        wf.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        self.play_state = "NOT_PLAYING"
        print("Playing finished...")

    def stop_playing(self):
        if self.play_state == "NOT_PLAYING":
            return
        self.play_state = "NOT_PLAYING"
        print("Playing stopped...")

        # close and terminate the stream
        if self.stream is not None:
            self.stream.stop_stream()

        # join thread if it is still running
        if self.playingThread is not None:
            self.playingThread.join()
            self.playingThread = None
        
        # reset the current time
        self.current_time = 0
        self.start_time = 0
        self.current_nframes = 0
        self.start_nframes = 0            
                

    def pause_playing(self):
        if self.play_state == "PLAYING":
            self.play_state = "PAUSED"
            print("Playing paused...")

    def resume_playing(self):
        if self.play_state == "PAUSED":
            self.play_state = "PLAYING"
            print("Playing resumed...")

    def restart_playing(self, speed, start_time):
        if self.play_state == "PLAYING":
            if self.play_state == "PLAYING":
                self.play_state = "NOT_PLAYING"

                # close and terminate the stream
                if self.stream is not None:
                    self.stream.stop_stream()

                # join thread if it is still running
                if self.playingThread is not None:
                    self.playingThread.join()
                    self.playingThread = None

            elif self.play_state == "PAUSED":
                raise Exception("Cannot stop a paused playback")

        # Start a new playback with updated speed and start time
        self.speed = speed
        self.start_time = start_time
        # start playing the file using a new thread
        self.playingThread = Thread(target=self.start_playing, args=(self.filename,))
        self.playingThread.start()

    def set_speed(self, speed):
        if self.play_state == "NOT_PLAYING":
            self.speed = speed
            print("Speed set to", speed, "x")

        else:
            self.restart_playing(speed, self.current_time)

    def set_volume(self, volume):
        self.volume = volume

            
    def close(self):
        self.p.terminate()

    def get_data(self):
        return self.data
    
    def update_current_time(self, p_canvas, p_text):
        if self.play_state == "PLAYING":
            p_canvas.itemconfigure(p_text, text=self.get_current_time())
            p_canvas.after(1000, self.update_current_time, p_canvas, p_text)

    # return (current time, total time) in seconds, calculate from data
    def get_time(self):
        wf = wave.open(self.filename, 'rb')
        total_time = wf.getnframes() / wf.getframerate()
        current_time = self.current_time * total_time
        wf.close()

        return (current_time, total_time)

    def get_speed(self):
        return self.speed
    
    def seek(self, time): # time is from 0 to 1
        if self.play_state == "PLAYING":
            self.restart_playing(self.speed, time)
    
    def get_sample_rate(self):
        return self.srate
    
    def get_time(self):
        wf = wave.open(self.filename, 'rb')
        total_time = wf.getnframes() / wf.getframerate()
        current_time = self.current_time * total_time
        wf.close()

        return (current_time, total_time)