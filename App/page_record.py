import time
from threading import Thread
import tkinter as tk
from tkinter import PhotoImage, Button, filedialog
from pathlib import Path
from page import Page
from audio_recorder import Recorder

ASSETS_PATH = Path("./assets/frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class RecordPage(Page):
    def __init__(self, audio_player, *args, **kwargs):
        # Initialize the page with a specified size and background color
        Page.__init__(self, *args, **kwargs)
        self.config(width=1280, height=720, bg="#F4D6CC")

        # Create a canvas to contain UI elements
        self.canvas = tk.Canvas(
            self,
            width=800,
            height=720,
            bd=0,
            bg="#F4D6CC",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.place(x=0, y=0)

        # Display a text on the canvas
        self.canvas.create_text(
            100,
            60,
            text="Record",
            fill="black",
            font=("Arial", 24)
        )

        # Button to start/stop recording
        self.button_record = Button(
            self,
            text="Start Recording",
            command=self.toggle_recording,
        )
        self.button_record.place(
            x=50+480,
            y=100,
            width=100,
            height=60
        )

        # Button to save recording
        self.button_save = Button(
            self,
            text="Save",
            command=self.save_recording
        )
        self.button_save.place(
            x=600+480,
            y=100,
            width=100,
            height=60
        )

        # Text to display the recording duration
        self.timer_text = self.canvas.create_text(
            160,
            130,
            anchor="nw",
            text="00 : 00",
            fill="#000000",
            font=("Inter", 20 * -1)
        )

        # Initialize the audio recorder
        self.recorder = Recorder()

    def toggle_recording(self):
        # Toggle between starting and stopping the recording
        if self.recorder.is_recording():
            # End the recording
            self.recorder.stop_recording()
            self.recording_thread.join()
            self.timer_thread.join()
            self.button_record.config(text="Start Recording")
        else:
            # Start the recording
            self.recorder.start_recording()
            self.recording_thread = Thread(target=self.recording_task)
            self.timer_thread = Thread(target=self.update_timer)
            self.recording_thread.start()
            self.timer_thread.start()
            self.button_record.config(text="Stop Recording")

    def recording_task(self):
        # Task to continuously record audio while recording is active
        while self.recorder.is_recording():
            self.recorder.record()

    def update_timer(self):
        # Update the timer to display the recording duration
        start_time = time.time()
        while self.recorder.is_recording():
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"{minutes:02d} : {seconds:02d}"
            self.canvas.itemconfigure(self.timer_text, text=time_str)
            time.sleep(1)

    def save_recording(self):
        # Save the recording to a specified file location
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave File", "*.wav")])
        if filename:
            self.recorder.save_recording(filename)


