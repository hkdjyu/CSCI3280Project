from pathlib import Path
from tkinter import Tk, Canvas, Button, Listbox, Scrollbar, PhotoImage, filedialog
from tkinter import ttk
import tkinter as tk
from threading import Thread
from audio_recorder import Recorder
from audio_player import AudioPlayer
import time

ASSETS_PATH = Path("./assets/frame0")
AUDIO_DIR = Path("./audio")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


class HomeScreen(Tk):
    def __init__(self, screen_size="1280x720"):
        super().__init__()

        self.recorder = Recorder()
        self.audio_player = AudioPlayer()

        self.selected_audio_file = None

        self.title("Voice Recorder")
        self.geometry(screen_size)

        self.style = ttk.Style(self)
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 14))

        self.canvas = Canvas(
            self,
            bg = "#F8DBDE",
            height = 720,
            width = 1280,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.canvas.place(x=0, y=0)


        self.canvas.create_rectangle(
            0.0,
            0.0,
            480.0,
            720.0,
            fill="#CF7793",
            outline="")

        self.canvas.create_rectangle(
            0.0,
            0.0,
            480.0,
            720.0,
            fill="#CF7793",
            outline="")

        self.canvas.create_rectangle(
            480.0,
            620.0,
            1280.0,
            720.0,
            fill="#EFCACE",
            outline="")

        self.canvas.create_rectangle(
            0.0,
            620.0,
            480.0,
            720.0,
            fill="#893271",
            outline="")

        self.canvas.create_rectangle(
            0.0,
            0.0,
            480.0,
            100.0,
            fill="#893271",
            outline="")

        # listbox of audio files
        self.listbox = Listbox(
            self,
            bg="#893271",
            fg="white",
            font=("Arial", 20),
            relief="flat",
            selectbackground="#671B61",
            selectforeground="white"
        )
        self.listbox.place(x=0, y=120, width=460, height=480)
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

        scrollbar = Scrollbar(
            self, orient="vertical", bg="#893271", command=self.listbox.yview)
        scrollbar.place(x=460, y=120, height=480)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.populate_listbox()



        self.button_image_record = PhotoImage(
            file=relative_to_assets("button_record.png"))
        self.button_record = Button(
            image=self.button_image_record,
            borderwidth=0,
            highlightthickness=0,
            command=self.toggle_recording,
            relief="flat"
        )
        self.button_record.place(
            x=810.0,
            y=640.0,
            width=60.0,
            height=60.0
        )

        
        self.timer_text = self.canvas.create_text(
            883.0,
            658.0,
            anchor="nw",
            text="00 : 00",
            fill="#000000",
            font=("Inter", 20 * -1)
        )

        self.button_image_nav0 = PhotoImage(
            file=relative_to_assets("button_nav0.png"))
        self.button_nav0 = Button(
            image=self.button_image_nav0,
            text="Recording",
            font=("Inter", 20 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_2 clicked"),
            relief="flat"
        )
        self.button_nav0.place(
            x=480.0,
            y=0.0,
            width=200.0,
            height=100.0
        )

        self.button_image_nav1 = PhotoImage(
            file=relative_to_assets("button_nav1.png"))
        self.button_nav1 = Button(
            image=self.button_image_nav1,
            text="Editing",
            font=("Inter", 20 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_3 clicked"),
            relief="flat",
        )
        self.button_nav1.place(
            x=680.0,
            y=0.0,
            width=200.0,
            height=100.0
        )

        self.canvas.create_text(
            747.0,
            38.0,
            anchor="nw",
            text="Editing",
            fill="#000000",
            font=("Inter", 20 * -1)
        )

        self.button_image_nav2 = PhotoImage(
            file=relative_to_assets("button_nav2.png"))
        self.button_nav2 = Button(
            image=self.button_image_nav2,
            text="AudioToText",
            font=("Inter", 20 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_4 clicked"),
            relief="flat"
        )
        self.button_nav2.place(
            x=880.0,
            y=0.0,
            width=200.0,
            height=100.0
        )

        self.button_image_nav3 = PhotoImage(
            file=relative_to_assets("button_nav3.png"))
        self.button_nav3 = Button(
            image=self.button_image_nav3,
            text="",
            font=("Inter", 20 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_5 clicked"),
            relief="flat"
        )
        self.button_nav3.place(
            x=1080.0,
            y=0.0,
            width=200.0,
            height=100.0
        )

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

        # verticle slider, for audio volume
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
        self.audio_slider.place(x=370, y=640, width=20, height=60)
        self.audio_slider.set(0.5)

        self.canvas.create_text(
            201.0,
            21.0,
            anchor="nw",
            text="File",
            fill="#FFFFFF",
            font=("Inter", 48 * -1)
        )

        self.button_image_folder = PhotoImage(
            file=relative_to_assets("button_folder.png"))
        self.button_folder = Button(
            image=self.button_image_folder,
            borderwidth=0,
            highlightthickness=0,
            command=self.folder_clicked,
            relief="flat"
        )
        self.button_folder.place(
            x=28.0,
            y=13.0,
            width=60.0,
            height=60.0
        )

        self.button_image_refresh = PhotoImage(
            file=relative_to_assets("button_refresh.png"))
        self.button_refresh = Button(
            image=self.button_image_refresh,
            borderwidth=0,
            highlightthickness=0,
            command=self.populate_listbox,
            relief="flat"
        )
        self.button_refresh.place(
            x=388.0,
            y=13.0,
            width=60.0,
            height=60.0
        )

        self.canvas.create_text(
            398.0,
            73.0,
            anchor="nw",
            text="refresh",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        self.canvas.create_text(
            41.0,
            73.0,
            anchor="nw",
            text="folder",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        self.button_image_speed = PhotoImage(
            file=relative_to_assets("button_speed.png"))
        self.button_speed0 = Button(
            image=self.button_image_speed,
            text="0.5x",
            font=("Inter", 12 * -1),
            compound="center",
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.audio_player.set_speed(0.5),
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
            command=lambda: self.audio_player.set_speed(1.0),
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
            command=lambda: self.audio_player.set_speed(2.0),
            relief="flat"
        )
        self.button_speed2.place(
            x=400.0,
            y=682.0,
            width=60.0,
            height=20.0
        )

        self.canvas.create_text(
            417.0,
            640.0,
            anchor="nw",
            text="0.5x",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        self.canvas.create_text(
            418.0,
            662.0,
            anchor="nw",
            text="1.0x",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        self.canvas.create_text(
            418.0,
            684.0,
            anchor="nw",
            text="2.0x",
            fill="#FFFFFF",
            font=("Inter", 12 * -1)
        )

        self.recording_thread = None
        self.timer_thread = None
        self.audio_player_thread = None
        self.audio_player_state = "NOT_PLAYING"



    def populate_listbox(self):
        self.listbox.delete(0, "end")
        audio_files = sorted(AUDIO_DIR.glob("*.wav"))
        for file in audio_files:
            self.listbox.insert("end", file.stem)

    def on_listbox_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_item = self.listbox.get(selected_index[0])
            self.selected_audio_file = AUDIO_DIR / f"{selected_item}.wav"

    def toggle_recording(self):
        if self.recorder.is_recording():
            # end the recording
            self.recorder.stop_recording()

            self.recording_thread.join()
            self.timer_thread.join()

            self.button_record.config(image=self.button_image_record)
            self.save_recording()

            self.populate_listbox()
        else:
            # start the recording
            self.recorder.start_recording()

            self.recording_thread = Thread(target=self.recording_task)
            self.timer_thread = Thread(target=self.update_timer)
            self.recording_thread.start()
            self.timer_thread.start()

            self.button_record.config(image=self.button_image_stop_old)

    def recording_task(self):
        while self.recorder.is_recording():
            self.recorder.record()

    def update_timer(self):
        start_time = time.time()
        while self.recorder.is_recording():
            elapsed_time = time.time() - start_time
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"{minutes:02d} : {seconds:02d}"
            self.canvas.itemconfigure(self.timer_text, text=time_str)
            time.sleep(1)

    def save_recording(self):
        self.recorder.save_recording()

    def play_audio(self):
        if self.audio_player_state == "NOT_PLAYING" and self.selected_audio_file:
            self.audio_player_state = "PLAYING"
            self.audio_player_thread = Thread(target=self.play_audio_task)
            self.audio_player_thread.start()
            time.sleep(0.12)
            self.button_play.config(image=self.button_image_pause, command=self.pause_audio)
        elif self.audio_player_state == "PAUSED":
            self.audio_player_state = "PLAYING"
            self.audio_player.resume_playing()
            time.sleep(0.12)
            self.button_play.config(image=self.button_image_pause, command=self.pause_audio)



    def play_audio_task(self):
        print("play_audio_task")
        while self.audio_player_state == "PLAYING":
            self.audio_player.start_playing(str(self.selected_audio_file))
            if self.audio_player_state != "PLAYING" or self.audio_player.is_playing() == False:
                self.audio_player_state = "NOT_PLAYING"
                break
            

    def stop_audio(self):
        self.audio_player_state = "NOT_PLAYING"
        self.audio_player.stop_playing()
        self.audio_player_thread.join()

        time.sleep(0.12)

        self.button_play.config(image=self.button_image_play, command=self.play_audio)


    def pause_audio(self):
        if self.audio_player.is_playing() and self.audio_player_state == "NOT_PLAYING":
            self.audio_player_state = "PAUSED"
            self.audio_player.pause_playing()

            time.sleep(0.12)
            self.button_play.config(image=self.button_image_play, command=self.play_audio)

        if self.audio_player_state == "PLAYING":
            self.audio_player_state = "PAUSED"
            self.audio_player.pause_playing()

            time.sleep(0.12)
            self.button_play.config(image=self.button_image_play, command=self.play_audio)

    def set_volume(self, volume):
        self.audio_player.set_volume(float(volume))


    def folder_clicked(self):
        global AUDIO_DIR
        folder_selected = filedialog.askdirectory()
        AUDIO_DIR = Path(folder_selected)




if __name__ == "__main__":
    app = HomeScreen()
    app.mainloop()
