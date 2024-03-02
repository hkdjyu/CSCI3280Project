import time
from threading import Thread
import tkinter as tk
from tkinter import Listbox, Scrollbar, Button, PhotoImage, filedialog, Canvas
from pathlib import Path
from page import Page
from page_noise_removal import NoiseRemoval

ASSETS_PATH = Path("./assets/frame0")
AUDIO_DIR = Path("./audio")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class LeftPanel(Page):
    def __init__(self, audio_player, set_selected_audio_path, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.config(width=480, height=600, bg="#893271")
    
        # Canvas setup
        self.canvas = Canvas(
            self,
            height=720,
            width=480,
            bd=0,
            bg="#893271",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.place(x=0, y=0)

        # Display current folder path
        self.file_path_text = self.canvas.create_text(
            85.0,
            3.0,
            anchor="nw",
            text=AUDIO_DIR,
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        # Button to select folder
        self.button_folder = Button(
            text="Select Folder",
            font=("Inter", 12 * -1),
            bg="white",
            fg="black",
            command=self.folder_clicked,
            relief="flat",
        )
        self.button_folder.place(
            x=0.0,
            y=120.0,
            width=80.0,
            height=20.0
        )

        # Refresh button
        self.button_refresh = Button(
            text="Refresh",
            font=("Inter", 12 * -1),
            bg="white",
            fg="black",
            command=self.populate_listbox,
            relief="flat",
        )
        self.button_refresh.place(
            x=400.0,
            y=120.0,
            width=80.0,
            height=20.0
        )

        # Listbox for audio files
        self.listbox = Listbox(
            self,
            bg="#893271",
            fg="white",
            font=("Arial", 20),
            relief="flat",
            selectbackground="#671B61",
            selectforeground="white",
            highlightthickness=1,
            highlightcolor="white",
        )
        self.listbox.place(x=0, y=20, width=460, height=480)
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        # Scrollbar for the listbox
        scrollbar = Scrollbar(
            self, orient="vertical", bg="#893271", command=self.listbox.yview)
        scrollbar.place(x=460, y=20, height=480)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Initialize audio player
        self.audio_player = audio_player
        self.current_audio_path = None
        self.selected_audio_file_path = None
        self.audio_player_thread = None
        self.audio_player_state = "NOT_PLAYING"

        # Add play, stop, and volume buttons
        self.add_audio_buttons()

        # Populate listbox with audio files
        self.populate_listbox()

        # slider control
        self.is_holding_slider = False
        self.slider_value = 0

        # Set the selected audio path
        self.set_selected_audio_path = set_selected_audio_path
       


    def on_listbox_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_item = self.listbox.get(selected_index[0])
            self.selected_audio_file_path = AUDIO_DIR / f"{selected_item}.wav"
            self.set_selected_audio_path(self.selected_audio_file_path)

    def add_audio_buttons(self):
        # Play button
        self.button_image_play = PhotoImage(
            file=relative_to_assets("button_play.png"))
        self.button_play = Button(
            image=self.button_image_play,
            borderwidth=0,
            highlightthickness=0,
            command=self.play_audio,
            relief="flat"
        )
        self.button_play.place(
            x=13.0,
            y=625.0,
            width=90.0,
            height=90.0
        )

        # Stop button
        self.button_image_pause = PhotoImage(
            file=relative_to_assets("button_pause.png"))
        self.button_image_stop = PhotoImage(
            file=relative_to_assets("button_stop.png"))
        self.button_image_stop_old = PhotoImage(
            file=relative_to_assets("button_stop_old.png"))
        
        self.button_stop = Button(
            image=self.button_image_stop,
            borderwidth=0,
            highlightthickness=0,
            command=self.stop_audio,
            relief="flat"
        )
        self.button_stop.place(
            x=103.0,
            y=647.0,
            width=45.0,
            height=45.0
        )

        # Audio volume slider
        self.audio_slider = tk.Scale(
            self,
            from_=1.0,
            to=0.0,
            resolution=0.01,
            orient="vertical",
            bd=1,
            font=("inter", 12),
            bg="#EFCACE",
            relief="flat",
            showvalue=False,
            troughcolor="#EFCACE",
            activebackground="#EFCACE",
            command=self.set_volume,
            highlightthickness=0
        )
        self.audio_slider.place(x=370, y=510, width=20, height=80)
        self.audio_slider.set(0.5)

        # Speed buttons
        self.add_speed_buttons()

        # Add a text to display the current time of the audio
        self.current_time_text = self.canvas.create_text(
            260.0,
            570.0,
            anchor="nw",
            text="00:00:00 / 00:00:00",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )
        
        # Add audio slider
        self.audio_slider = tk.Scale(
            self,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            bg="#FFFFFF",
            length=200,
            highlightthickness=0,
            showvalue=False,
        )
        self.audio_slider.place(x=160.0, y=540.0)
        self.audio_slider.bind("<ButtonPress>", lambda e: self.set_holding_slider(True))
        self.audio_slider.bind("<ButtonRelease>", lambda e: self.seek_audio(self.audio_slider.get()))


    def add_speed_buttons(self):
        self.button_image_speed = PhotoImage(
            file=relative_to_assets("button_speed.png"))
        self.button_speed0 = Button(
            image=self.button_image_speed,
            text="0.5x",
            font=("Inter", 12 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.set_speed(0.5),
            relief="flat"
        )
        self.button_speed0.place(
            x=400.0,
            y=638.0,
            width=60.0,
            height=20.0
        )

        self.button_speed1 = Button(
            image=self.button_image_speed,
            text="1.0x",
            font=("Inter", 12 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.set_speed(1.0),
            relief="flat"
        )
        self.button_speed1.place(
            x=400.0,
            y=660.0,
            width=60.0,
            height=20.0
        )

        self.button_speed2 = Button(
            image=self.button_image_speed,
            text="2.0x",
            font=("Inter", 12 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.set_speed(2.0),
            relief="flat"
        )
        self.button_speed2.place(
            x=400.0,
            y=682.0,
            width=60.0,
            height=20.0
        )

    def play_audio(self, path=None, start_time=None, end_time=None):
        path = str(self.selected_audio_file_path) if path is None else path
        if self.audio_player_state == "NOT_PLAYING" and path:
            self.audio_player_state = "PLAYING"
            self.audio_player_thread = Thread(target=self.play_audio_task, args=(path, start_time, end_time))
            self.audio_player_thread.start()
            time.sleep(0.12)
            self.button_play.config(image=self.button_image_pause, command=self.pause_audio)

            # Update the current time of the audio, a new thread is created to update the time
            self.current_time_thread = Thread(target=self.update_current_time)
            self.current_time_thread.start()

            NoiseRemoval.on_play_started(None)

        elif self.audio_player_state == "PAUSED" and path == self.current_audio_path:
            self.audio_player_state = "PLAYING"
            self.audio_player.resume_playing()
            time.sleep(0.12)
            self.button_play.config(image=self.button_image_pause, command=self.pause_audio)
            self.current_time_thread = Thread(target=self.update_current_time)
            self.current_time_thread.start()

            NoiseRemoval.on_play_started(None)
            
        elif self.audio_player_state == "PAUSED" and path != self.current_audio_path:

            # stop the current audio
            self.stop_audio()

            self.audio_player_state = "PLAYING"
            self.audio_player_thread = Thread(target=self.play_audio_task, args=(path, start_time, end_time))
            self.audio_player_thread.start()
            time.sleep(0.12)
            self.button_play.config(image=self.button_image_pause, command=self.pause_audio)
            self.current_time_thread = Thread(target=self.update_current_time)
            self.current_time_thread.start()

            NoiseRemoval.on_play_started(None)

    def update_current_time(self):
        print("Updating current time")
        while self.audio_player.is_playing():
            current_time, total_time = self.audio_player.get_time()  # in seconds

            # Convert total time to MM:SS format
            total_minutes = total_time // 60
            total_seconds = total_time % 60
            total_milliseconds = int((total_time - int(total_time)) * 1000)
            total_milliseconds_str = f"{total_milliseconds:02d}"[:2]  # Ensure milliseconds have two digits
            total_time_str = f"{int(total_minutes):02d}:{int(total_seconds):02d}:{total_milliseconds_str}"

            # Convert current time to MM:SS:MS format
            minutes = current_time // 60
            seconds = current_time % 60
            milliseconds = int((current_time - int(current_time)) * 1000)
            milliseconds_str = f"{milliseconds:02d}"[:2]  # Ensure milliseconds have two digits
            current_time_str = f"{int(minutes):02d}:{int(seconds):02d}:{milliseconds_str}"

            # update audio slider
            self.audio_slider.set(current_time / total_time)

            self.canvas.itemconfig(self.current_time_text, text=f"{current_time_str} / {total_time_str}")
            time.sleep(0.1)



    def play_audio_task(self, path=None, start_time=None, end_time=None):
        path = str(self.selected_audio_file_path) if path is None else path
        print("panel left:",path)
        while self.audio_player_state == "PLAYING":
            # self.audio_player.start_playing(str(path))
            if start_time is not None and end_time is not None:
                self.audio_player.start_playing(str(path), start_time, end_time)
            else:
                self.audio_player.start_playing(str(path))
            if self.audio_player_state != "PLAYING" or self.audio_player.is_playing() == False:
                self.audio_player_state = "NOT_PLAYING"
                break

    def stop_audio(self):
        self.audio_player_state = "NOT_PLAYING"
        self.audio_player.stop_playing()
        self.audio_player_thread.join()

        time.sleep(0.12)
        self.button_play.config(image=self.button_image_play, command=self.play_audio)

        self.canvas.itemconfig(self.current_time_text, text="00:00:00 / 00:00:00")
        self.audio_slider.set(0)

        NoiseRemoval.on_play_stopped(None)

    def pause_audio(self):
        if self.audio_player.is_playing() and self.audio_player_state == "NOT_PLAYING":
            self.audio_player_state = "PAUSED"
            self.audio_player.pause_playing()

            time.sleep(0.12)
            self.button_play.config(image=self.button_image_play, command=self.play_audio)
            NoiseRemoval.on_play_paused(None)

        if self.audio_player_state == "PLAYING":
            self.audio_player_state = "PAUSED"
            self.audio_player.pause_playing()

            time.sleep(0.12)
            self.button_play.config(image=self.button_image_play, command=self.play_audio)
            NoiseRemoval.on_play_paused(None)

    def set_volume(self, volume):
        self.audio_player.set_volume(float(volume))

    def folder_clicked(self):
        global AUDIO_DIR
        folder_selected = filedialog.askdirectory()
        AUDIO_DIR = Path(folder_selected)
        self.populate_listbox()

    def populate_listbox(self):
        self.listbox.delete(0, "end")
        audio_files = sorted(AUDIO_DIR.glob("*.wav"))
        for file in audio_files:
            self.listbox.insert("end", file.stem)
        
        path = Path(AUDIO_DIR)
        # if path is too long, display the first 10 and last 30 characters
        if len(str(path)) > 20:
            path = str(path)[:20] + " ... " + str(path)[-30:]
        self.canvas.itemconfig(self.file_path_text, text=path)

    def set_speed(self, speed):
        self.audio_player.set_speed(float(speed))
        self.current_time_thread = Thread(target=self.update_current_time)
        time.sleep(1)
        self.current_time_thread.start()

    def set_holding_slider(self, value):
        self.is_holding_slider = value

    def seek_audio(self, value):
        if self.is_holding_slider:
            self.audio_player.seek(float(value))
            
            time.sleep(1)
            self.current_time_thread = Thread(target=self.update_current_time)
            self.current_time_thread.start()

        self.set_holding_slider(False)

    def get_selected_audio_file_path(self):
        return self.selected_audio_file_path

    
        