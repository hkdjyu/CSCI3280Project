import time
from threading import Thread
import tkinter as tk
from tkinter import PhotoImage, Button, filedialog, messagebox
from pathlib import Path
from page import Page
from audio_recorder import Recorder
from slider_two_knob import CustomSliderTwoKnob
from audio_text_converter import AudioTextConverter

import math
import wave
import pyaudio

ASSETS_PATH = Path("./assets/frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class AudioToText(Page):
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
            text="Audio To Text",
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

        # Create a button to convert the audio to text
        self.convert_button = Button(
            self,
            text="Convert",
            font=("Arial", 16),
            command=self.on_convert_button_click
        )
        self.convert_button.place(x=300, y=150, width=200, height=50)

        # Create a input field to show the converted text
        self.converted_textbox = tk.Text(
            self,
            font=("Arial", 12),
            wrap="word"
        )
        self.converted_textbox.place(x=100, y=250, width=600, height=400)

        self.audio_text_converter = AudioTextConverter()
        
        



    def on_selected_audio_path_changes(self, path):
        # if path is too long, display the first 10 and last 30 characters
        if len(str(path)) > 70:
            path = str(path)[:30] + " ... " + str(path)[-40:]
        self.canvas.itemconfig(self.selected_audio_path_text, text=path)

    def on_convert_button_click(self):
        # Get the selected audio path
        selected_audio_path = self.canvas.itemcget(self.selected_audio_path_text, "text")

        # Check if the audio path is empty
        if selected_audio_path == "No audio selected":
            messagebox.showerror("Error", "Please select an audio file")
            return

        # Clear the converted text
        self.converted_textbox.delete(1.0, "end")
        
        # Convert the audio to text
        self.convert_audio_to_text(selected_audio_path)

    def convert_audio_to_text(self, audio_path):
        # Simulate the conversion process
        self.canvas.itemconfig(self.selected_audio_path_text, text="Calculating...")
        
        self.audio_text_converter.get_large_audio_transcription_on_silence(str(audio_path), self.on_audio_converted, self.on_audio_chunk_converted)

    def on_audio_converted(self, text):
        self.converted_textbox.delete(1.0, "end")
        self.converted_textbox.insert("end", text)
        self.canvas.itemconfig(self.selected_audio_path_text, text="Audio converted")

    def on_audio_chunk_converted(self, text, i, total):
        print(f"Chunk {i}/{total}:", text)
        self.canvas.itemconfig(self.selected_audio_path_text, text=f"Converting... {i}/{total}")




