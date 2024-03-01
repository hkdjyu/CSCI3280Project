import tkinter as tk
import librosa
from matplotlib import pyplot as plt
from page import Page
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from threading import Thread
import wave
import time
import noisereduce as nr
import pyaudio

sample_format = pyaudio.paInt16
channels = 2
fs = 44100
file = "./audio/output_noise_removal.wav"

class EditPage(Page):
    def __init__(self, audio_player, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.config(width=1280, height=720, bg="#D4F4CC")

        self.canvas = tk.Canvas(
            self,
            width=800,
            height=720,
            bd=0,
            bg="#D4F4CC",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.place(x=0, y=0)

        self.canvas.create_text(
            400,
            360,
            text="This is edit page",
            fill="black",
            font=("Arial", 24)
        )

        self.button = tk.Button(
            self,
            text="Test",
            bg="white",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#D4F4CC",
            activeforeground="black",
            command= lambda: noise_removal()
            #command= lambda: start_visualization(self, audio_player)
        )
        self.button.place(x=200, y=600, width=120, height=20)

        self.fig = plt.figure(figsize=(8, 2))
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.canvas_fig.get_tk_widget().place(x=0, y=100)

        def start_visualization(self, audio_player):
            new_thread = Thread(target=update_visualization, args=(self, audio_player))
            new_thread.start()

        def update_visualization(self, audio_player):
            # Load audio file
            audio_file = "./temp/temp.wav"
            y, sr = librosa.load(audio_file)
            line = None
            annotation = None  # Variable to store the text annotation
            # Clear the previous plot
            self.ax.clear()      
            
            # Plot the waveform
            librosa.display.waveshow(y, sr=sr, ax=self.ax, color='r')
            
            while audio_player.is_playing():
                # Get the current progress of the audio
                current_time, total_time = audio_player.get_time()  # Adjust this line based on your audio player implementation
                 # Convert time to minutes and seconds
                current_time_min = int(current_time // 60)
                current_time_sec = int(current_time % 60)
                total_time_min = int(total_time // 60)
                total_time_sec = int(total_time % 60)


                if line:
                    line.remove()
                # Plot a line to represent the current progress
                line = self.ax.axvline(x=current_time, color='g')

                if annotation:
                    annotation.remove()
                 # Add time text annotation
                time_text = f"Time: {current_time_min:02d}:{current_time_sec:02d} / {total_time_min:02d}:{total_time_sec:02d}"
                annotation = self.ax.text(0.5, 0, time_text, transform=self.ax.transAxes, ha='center', va='top')
                
                # Remove axes and labels
                self.ax.axis('off')

                # Update the figure canvas
                self.canvas_fig.draw_idle()

                # Pause for a short duration
                time.sleep(0.01)

        def noise_removal():
            global file  # Declare file as a global variable
            #y, sr = librosa.load("./audio/output.wav")
            rf = wave.open("./audio/output.wav", 'rb')
            params = rf.getparams()
            nchannels, sampwidth, framerate, nframes = params[:4]
            data = rf.readframes(nframes)
            
            reduced_noise = nr.reduce_noise(y=data, sr=framerate)
            
            if file == "":
                file = "./output_noise_removal.wav"
            if not file.endswith(".wav"):
                file = file + ".wav"

            if reduced_noise.any():
                wf = wave.open(file, 'wb')
                wf.setnchannels(nchannels)
                wf.setsampwidth(sampwidth)
                wf.setframerate(framerate)
                wf.writeframes(reduced_noise.tobytes())
                wf.close()
                print("Recording saved to", file)
            else:
                print("No recording to save.")     

            