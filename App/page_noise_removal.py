import time
from threading import Thread
import tkinter as tk
from tkinter import PhotoImage, Button, filedialog, messagebox
from pathlib import Path

import librosa
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from page import Page
from audio_noise_remover import AudioNoiseRemover

import math
import wave
import pyaudio

ASSETS_PATH = Path("./assets/frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class NoiseRemoval(Page):

    @staticmethod
    def on_play_started():
        print("Noise removal page: play started (static)")
        for obj in NoiseRemoval.instatiated_objects:
            obj.on_play_started_obj()
    
    @staticmethod
    def on_play_stopped():
        print("Noise removal page: play stopped (static)")
        for obj in NoiseRemoval.instatiated_objects:
            obj.on_play_stopped_obj()

    @staticmethod
    def on_play_paused():
        print("Noise removal page: play paused (static)")
        for obj in NoiseRemoval.instatiated_objects:
            obj.on_play_paused_obj()

    # static variable to store all the instatiated objects
    instatiated_objects = []


    def __init__(self, audio_player, left_panel, audio_input, *args, **kwargs):
        # Initialize the page with a specified size and background color
        Page.__init__(self, *args, **kwargs)

        self.config(width=1280, height=720, bg="#B5E0E3")
        self.audio_player = audio_player
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
        
        self.fig = plt.figure(figsize=(8, 2))
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.canvas_fig.get_tk_widget().place(x=0, y=500)
        self.ax.set_facecolor('gray')

        NoiseRemoval.instatiated_objects.append(self)

        print(len(NoiseRemoval.instatiated_objects))
        
    def on_selected_audio_path_changes(self, path):
        # if path is too long, display the first 10 and last 30 characters
        if len(str(path)) > 70:
            path = str(path)[:30] + " ... " + str(path)[-40:]
        self.canvas.itemconfig(self.selected_audio_path_text, text=path)
        self.selected_audio_path = path
        if self.audio_player.is_playing():
            self.start_visualization()

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

    def start_visualization(self):
        new_thread = Thread(target=self.update_visualization)
        new_thread.start()

    def update_visualization(self):
        # Load audio file
        audio_player = self.audio_player
        audio_file = "./temp/temp.wav"
        y, sr = librosa.load(audio_file)
        line = None
        annotation = None  # Variable to store the text annotation
        # Clear the previous plot
        self.ax.clear()      
        self.ax.set_facecolor('gray')
        # Plot the waveform
        librosa.display.waveshow(y, sr=sr, ax=self.ax, color='blue')
        
        while True:
            if audio_player.is_playing() or audio_player.is_paused():
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
                line = self.ax.axvline(x=current_time, color='r')

                if annotation:
                    annotation.remove()
                # Add time text annotation
                time_text = f"Time: {current_time_min:02d}:{current_time_sec:02d} / {total_time_min:02d}:{total_time_sec:02d}"
                annotation = self.ax.text(0.5, 0, time_text, transform=self.ax.transAxes, ha='center', va='top')
                
                # Remove axes and labels
                self.ax.axis('off')

                # Update the figure canvas
                self.canvas_fig.draw_idle()

                if not(audio_player.is_playing()) or not (audio_player.is_paused()):
                    break
                # Pause for a short duration
                time.sleep(0.01)

    def on_play_started_obj(self):
        # print("Noise removal page: play started(instance)")
        self.start_visualization()

    def on_play_stopped_obj(self):
        print("Noise removal page: play stopped(instance)")

    def on_play_paused_obj(self):
        print("Noise removal page: play paused(instance)")
    

