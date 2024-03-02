import time
from threading import Thread
import tkinter as tk
from tkinter import PhotoImage, Button, filedialog, messagebox
from pathlib import Path
from page import Page
from audio_noise_remover import AudioNoiseRemover

import math
import wave
import pyaudio

ASSETS_PATH = Path("./assets/frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class NoiseRemoval(Page):
    def __init__(self, audio_player, left_panel, audio_input, *args, **kwargs):
        # Initialize the page with a specified size and background color
        Page.__init__(self, *args, **kwargs)
        self.config(width=1280, height=720, bg="#B5E0E3")

        # Create a canvas to contain UI elements
        self.canvas = tk.Canvas(
            self,
            width=800,
            height=720,
            bd=0,
            bg="#B5E0E3",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.place(x=0, y=0)

        # Display a text on the canvas
        self.canvas.create_text(
            400,
            60,
            text="Noise Removal",
            fill="black",
            font=("Arial", 24)
        )

        # Create a text to show the selected audio path
        self.selected_audio_path_text = self.canvas.create_text(
            400,
            100,
            text="No audio selected",
            fill="black",
            font=("Arial", 12)
        )

        # Create a button to remove noise from the audio
        self.remove_noise_button = Button(
            self,
            text="Remove Noise",
            font=("Arial", 16),
            command=self.on_remove_noise_clicked
        )
        self.remove_noise_button.place(x=300, y=140, width=200, height=40)

        self.noise_remover = AudioNoiseRemover()
        self.selected_audio_path= None

        # Create a slider to adjust the noise level
        self.noise_level_slider = tk.Scale(
            self,
            from_=1,
            to=0,
            resolution=0.1,
            orient="vertical",
            label="Noise Removal Percentage",
            font=("Arial", 12),
            command=self.on_noise_level_changed
        )
        self.noise_level_slider.place(x=280, y=200)

        self.noise_remover_level = 1
        
        
    def on_selected_audio_path_changes(self, path):
        # if path is too long, display the first 10 and last 30 characters
        if len(str(path)) > 70:
            path = str(path)[:30] + " ... " + str(path)[-40:]
        self.canvas.itemconfig(self.selected_audio_path_text, text=path)
        self.selected_audio_path = path

    def on_remove_noise_clicked(self):
        if self.selected_audio_path is None:
            messagebox.showerror("Error", "No audio selected")
            return

        self.remove_noise_button.config(state="disabled")

        # Create a new thread to remove noise
        new_thread = Thread(target=self.remove_noise_thread)
        new_thread.start()

    def remove_noise_thread(self):

        output_path = str(self.selected_audio_path).replace(".wav", "_noise_removed.wav")

        # Remove noise from the audio
        self.noise_remover.remove_noise(str(self.selected_audio_path), output_path, self.noise_remover_level)

        # Enable the remove noise button
        self.remove_noise_button.config(state="normal")

        # Message box to show the completion of noise removal
        messagebox.showinfo("Success", "Noise removed successfully and saved as " + str(output_path))

    def on_noise_level_changed(self, level):
        self.noise_remover_level = float(level)

        


