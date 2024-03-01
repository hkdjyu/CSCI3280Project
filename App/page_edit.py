import tkinter as tk
import librosa
from matplotlib import pyplot as plt
from page import Page
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class EditPage(Page):
    def __init__(self, audio_player, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.config(width=800, height=720, bg="#D4F4CC")

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
        # Add a button

        self.button = tk.Button(
            self,
            text="Test",
            bg="white",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#D4F4CC",
            activeforeground="black",
            command=lambda: print("is audio playing? ", audio_player.is_playing())
        )
        self.button.place(x=200, y=200, width=120, height=20)

        #
        self.audio_visualization = tk.LabelFrame(
            bg= "#FFFFFF",
            bd=0,
        )
        self.audio_visualization.place(
            x=480.0,
            y=100.0,
            width=800.0,
            height=520.0
        )

        def visualize_audio(y, sr):
            fig, ax = plt.subplots(1)
            librosa.display.waveshow(y, sr=sr, ax=ax)
            ax.axis('off')  # Optionally, turn off the axis
            return fig

        def update_visualization(self):
            figure = visualize_audio(y, sr)  # Call the visualization function with your audio data (y and sr)
            canvas = FigureCanvasTkAgg(figure, master=self.audio_visualization)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)