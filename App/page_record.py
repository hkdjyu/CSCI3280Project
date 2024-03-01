import time
from threading import Thread
import tkinter as tk
from tkinter import PhotoImage, Button, filedialog, messagebox
from pathlib import Path
from page import Page
from audio_recorder import Recorder
from slider_two_knob import CustomSliderTwoKnob

import math
import wave
import pyaudio

ASSETS_PATH = Path("./assets/frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class RecordPage(Page):
    def __init__(self, audio_player, left_panel, *args, **kwargs):
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
            x=50,
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

        # Trim slider
        self.canvas.create_text(
            85,
            200,
            text="Trim",
            fill="black",
            font=("Arial", 24)
        )
        
        self.trim_slider = CustomSliderTwoKnob(self, width=600, height=30, command=lambda: self.on_trim_change())
        self.trim_slider.config(bg="#F4D6CC")
        self.trim_slider.place(x=100, y=250)
        self.trim_slider.set_enable(False)

        self.start_time_text = self.canvas.create_text(
            110,
            290,
            text="start",
            fill="black",
            font=("Arial", 12)
        )

        self.end_time_text = self.canvas.create_text(
            690,
            290,
            text="end",
            fill="black",
            font=("Arial", 12)
        )

        # preview button
        self.button_preview = Button(
            self,
            text="Preview",
            command=self.preview
        )
        self.button_preview.place(
            x=50,
            y=310,
            width=100,
            height=30
        )

        # Save button
        self.button_save_edited = Button(
            self,
            text="Save",
            command=self.save_trimmed_audio
        )
        self.button_save_edited.place(
            x=600,
            y=310,
            width=100,
            height=30
        )


        # insert new audio
        self.canvas.create_text(
            165,
            380,
            text="Insert/Overwrite",
            fill="black",
            font=("Arial", 24)
        )

        # slider to insert audio
        self.insert_slider = tk.Scale(
            self,
            from_=0,
            to=100,
            resolution=0.1,
            orient="horizontal",
            showvalue=False,
            command=self.on_insert_change
        )
        self.insert_slider.place(x=100, y=420, width=600)

        self.insert_time_text = self.canvas.create_text(
            110,
            460,
            text="00:00:00",
            fill="black",
            font=("Arial", 12)
        )

        # insert audio button (record)
        self.button_insert = Button(
            self,
            text="Insert",
            command=self.insert_audio
        )
        self.button_insert.place(
            x=50,
            y=480,
            width=100,
            height=30
        )

        # overwrite audio button
        self.button_overwrite = Button(
            self,
            text="Overwrite",
            command=self.overwrite_audio
        )
        self.button_overwrite.place(
            x=170,
            y=480,
            width=100,
            height=30
        )



            

        # Initialize the audio recorder and player
        self.recorder = Recorder()
        self.audio_player = audio_player
        self.panel_left = left_panel

        # variables to store the start and end time of the trim
        self.start_time = 0
        self.end_time = 0

        # current editing audio file
        self.editing_audio_path = None

        # insert recoder
        self.insert_recorder = Recorder()
        self.insert_time = 0


    def on_selected_audio_path_changes(self, path):
        if path is None:
            return
        print("Selected audio path changed to", path)
        self.editing_audio_path = path
        self.trim_slider.set_enable(True)
        self.trim_slider.reset()
        self.canvas.itemconfigure(self.start_time_text, text="start")
        self.canvas.itemconfigure(self.end_time_text, text="end")

    def toggle_recording(self):
        # Toggle between starting and stopping the recording
        if self.recorder.is_recording():
            # End the recording
            self.recorder.stop_recording()
            self.recording_thread.join()
            self.timer_thread.join()
            self.button_record.config(text="Start Recording")
            self.trim_slider.set_enable(True)
            self.editing_audio_path = "./temp/record_temp.wav"
            self.save_recording()
        else:
            # Start the recording
            self.recorder.start_recording()
            self.recording_thread = Thread(target=self.recording_task)
            self.timer_thread = Thread(target=self.update_timer)
            self.recording_thread.start()
            self.timer_thread.start()
            self.button_record.config(text="Stop Recording")
            self.trim_slider.set_enable(False)

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
        
        self.editing_audio_path = filename
        self.panel_left.populate_listbox()

    def get_audio_data(self):
        # Return the recorded audio data
        return self.audio_player.get_data()

    def on_trim_change(self):
        # Get the start and end time from the trim slider
        self.start_time, self.end_time = self.trim_slider.get_values()

        total_time = self.get_total_time()
        # update in format, e.g. 01:23:299, MM:SS:MS
        self.canvas.itemconfigure(self.start_time_text, text=f"{int(self.start_time * total_time // 60):02d}:{int(self.start_time * total_time % 60):02d}:{int((self.start_time * total_time * 100) % 100):02d}")
        self.canvas.itemconfigure(self.end_time_text, text=f"{int(self.end_time * total_time // 60):02d}:{int(self.end_time * total_time % 60):02d}:{int((self.end_time * total_time * 100) % 100):02d}")

        


    def get_total_time(self):
        wf = wave.open(str(self.editing_audio_path), 'rb')
        total_time = wf.getnframes() / wf.getframerate()
        wf.close()
        return total_time
    
    def preview(self):
        # Preview the trimmed audio
        self.on_trim_change()
        if self.audio_player.is_playing():
            self.panel_left.play_audio(self.editing_audio_path, self.start_time, self.end_time)

        self.panel_left.play_audio(self.editing_audio_path, self.start_time, self.end_time)
        

    def stop_playing(self):
        # Stop the audio player
        self.audio_player.stop_playing()

    def save_trimmed_audio(self):
        # Save the trimmed audio to a specified file location
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave File", "*.wav")])
        if filename:
            # open the file
            swf = wave.open("./temp/record_temp.wav", 'rb')

            # open the stream
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=self.p.get_format_from_width(swf.getsampwidth()),
                                    channels=swf.getnchannels(),
                                    rate=swf.getframerate(),
                                    output=True)
            # start time
            start_time, end_time = self.trim_slider.get_values()
            self.start_nframes = int(swf.getnframes() * start_time)
            self.end_nframes = int(swf.getnframes() * end_time)



            # write the trimmed audio to the new file
            wf = wave.open(filename, 'wb')
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(swf.getframerate())
            swf.setpos(self.start_nframes)
            wf.writeframes(swf.readframes(self.end_nframes - self.start_nframes))
            wf.close()
            swf.close()

    def on_insert_change(self, value):
        # Get the insert time from the slider
        total_time = self.get_total_time()
        self.insert_time = value
        self.insert_time_for_text = (float(value)) / 100 * total_time
        self.canvas.itemconfigure(self.insert_time_text, text=f"{int(self.insert_time_for_text // 60):02d}:{int(self.insert_time_for_text % 60):02d}:{int((self.insert_time_for_text * 100) % 100):02d}")

    def insert_audio(self):
        if self.recorder.is_recording():
            # pop up a message to stop recording
            messagebox.showinfo("Warning", "Please stop recording first")
            return
        
        if self.insert_recorder.is_recording():
            # stop the recording
            self.insert_recorder.stop_recording(temp_path="./temp/insert_temp.wav")
            self.insert_recording_thread.join()
            self.insert_recording_thread = None
            self.button_insert.config(text="Insert")

            # insert the audio
            self.insert_audio_to_editing_audio()
        else:
            # start the recording
            self.insert_recorder.start_recording()
            self.insert_recording_thread = Thread(target=self.insert_recording_task)
            self.insert_recording_thread.start()
            self.button_insert.config(text="Stop")

    def insert_recording_task(self):
        # Task to continuously record audio while recording is active
        while self.insert_recorder.is_recording():
            self.insert_recorder.record()

    def insert_audio_to_editing_audio(self):
        # Insert the recorded audio to the editing audio
        print("Inserting audio to", self.editing_audio_path)
        self.p = pyaudio.PyAudio()

        frames = []

        print("editing audio path", self.editing_audio_path)
        with wave.open(str(self.editing_audio_path), 'rb') as swf:
            # Open the stream
            self.stream = self.p.open(format=self.p.get_format_from_width(swf.getsampwidth()),
                                    channels=swf.getnchannels(),
                                    rate=swf.getframerate(),
                                    output=True)
            # read frames from start to insert time
            swf.setpos(0)
            frames.append(swf.readframes(int(swf.getframerate() * self.insert_time_for_text)))

        with wave.open("./temp/insert_temp.wav", 'rb') as iwf:
            # read frames from the inserted audio
            frames.append(iwf.readframes(iwf.getnframes()))

        with wave.open(str(self.editing_audio_path), 'rb') as swf:
            # read frames from insert time to end
            swf.setpos(int(swf.getframerate() * self.insert_time_for_text))
            frames.append(swf.readframes(swf.getnframes() - int(swf.getframerate() * self.insert_time_for_text)))

        # select file to save the new audio
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave File", "*.wav")])
        if filename:
            # write the new audio to the new file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(swf.getframerate())
                wf.writeframes(b''.join(frames))
        
        self.panel_left.populate_listbox()

        messagebox.showinfo("Success", "Audio inserted successfully")

    def overwrite_audio(self):
        if self.recorder.is_recording():
            # pop up a message to stop recording
            messagebox.showinfo("Warning", "Please stop recording first")
            return
        
        if self.insert_recorder.is_recording():
            # stop the recording
            self.insert_recorder.stop_recording(temp_path="./temp/insert_temp.wav")
            self.insert_recording_thread.join()
            self.insert_recording_thread = None
            self.button_overwrite.config(text="Overwrite")

            # overwrite the audio
            self.overwrite_audio_to_editing_audio()
        else:
            # start the recording
            self.insert_recorder.start_recording()
            self.insert_recording_thread = Thread(target=self.insert_recording_task)
            self.insert_recording_thread.start()
            self.button_overwrite.config(text="Stop")

    def overwrite_audio_to_editing_audio(self):
        # Overwrite the recorded audio to the editing audio
        print("Overwriting audio to", self.editing_audio_path)
        self.p = pyaudio.PyAudio()

        frames = []

        print("editing audio path", self.editing_audio_path)
        with wave.open(str(self.editing_audio_path), 'rb') as swf:
            # Open the stream
            self.stream = self.p.open(format=self.p.get_format_from_width(swf.getsampwidth()),
                                    channels=swf.getnchannels(),
                                    rate=swf.getframerate(),
                                    output=True)
            # read frames from start to insert time
            swf.setpos(0)
            frames.append(swf.readframes(int(swf.getframerate() * self.insert_time_for_text)))

        with wave.open("./temp/insert_temp.wav", 'rb') as iwf:
            # read frames from the inserted audio
            frames.append(iwf.readframes(iwf.getnframes()))

        length_of_inserted_audio = iwf.getnframes() / iwf.getframerate() # read the length of the inserted audio in seconds

        with wave.open(str(self.editing_audio_path), 'rb') as swf:
            
            # skip the frames of the inserted audio
            swf.setpos(int(swf.getframerate() * (self.insert_time_for_text + length_of_inserted_audio)))
        
            frames.append(swf.readframes(swf.getnframes() - int(swf.getframerate() * self.insert_time_for_text - length_of_inserted_audio)))

        # select file to save the new audio
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("Wave File", "*.wav")])
        if filename:
            # write the new audio to the new file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(swf.getframerate())
                wf.writeframes(b''.join(frames))
        
        self.panel_left.populate_listbox()

        messagebox.showinfo("Success", "Audio overwritten successfully")

        

            
        
            
            

