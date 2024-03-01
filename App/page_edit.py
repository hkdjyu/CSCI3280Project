import tkinter as tk
import librosa
from matplotlib import pyplot as plt
from page import Page
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import wave

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
            command=lambda: update_visualization(self, audio_player)
            #print("is audio playing? ", audio_player.is_playing(),update_visualization(self, audio_player))
        )
        self.button.place(x=200, y=600, width=120, height=20)

        def update_visualization(self, audio_player):
            # Load audio file
            audio_file = "./temp/temp.wav"
            y, sr = librosa.load(audio_file)

            # Create a matplotlib figure for the audio visualization
            fig = plt.figure(figsize=(6, 4))
            ax = fig.add_subplot(111)

            # Plot the waveform
            librosa.display.waveshow(y, sr=sr, ax=ax, color='r')

            # Create a FigureCanvasTkAgg to embed the figure in the tkinter canvas
            canvas = FigureCanvasTkAgg(fig, master=self.canvas)
            canvas.draw()

            # Place the canvas in the tkinter canvas
            canvas.get_tk_widget().place(x=100, y=100)