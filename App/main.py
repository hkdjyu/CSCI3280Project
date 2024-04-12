# A python voice recorder app using tkinter and pyaudio

import tkinter as tk
from page_record import RecordPage
from page_chat import ChatPage
from page_audio_to_text import AudioToText
from page_noise_removal import NoiseRemoval
from panel_left import LeftPanel
from navbar import Navbar
from audio_player import AudioPlayer
import pyaudio

window_size = "1280x720"

audio_player = AudioPlayer()

audio_input = 0 # default audio input

def set_audio_input(i):
    global audio_input
    audio_input = i


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        # configure the main frame
        self.config(bg="black")

        # selected audio path
        self.selected_audio_path = None
        
        self.navbar = Navbar(self.switch_page, self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.left_panel = LeftPanel(audio_player, self.set_selected_audio_path, self)
        self.left_panel.grid(row=0, column=0, sticky="s")

        self.main_panel = RecordPage(audio_player, self.left_panel, audio_input, self)
        self.main_panel.grid(row=0, column=1)

        self.chat_panel = ChatPage(audio_player, self)
        self.chat_panel.grid(row=0, column=1)

        self.audio_to_text_panel = AudioToText(audio_player, self.left_panel, audio_input, self)
        self.audio_to_text_panel.grid(row=0, column=1)

        # self.noise_removal_panel = NoiseRemoval(audio_player, self.left_panel, audio_input, self)
        # self.noise_removal_panel.grid(row=0, column=1)



        # Create a dictionary to store the pages
        self.pages = {
            "record": self.main_panel,
            "chat": self.chat_panel,
            "audio_to_text": self.audio_to_text_panel,
            # "noise_removal": self.noise_removal_panel
        }

        # Show the record page
        self.show_page("record")

       

    def set_selected_audio_path(self, path):
        self.selected_audio_path = path
        self.main_panel.on_selected_audio_path_changes(path)
        self.audio_to_text_panel.on_selected_audio_path_changes(path)
        self.noise_removal_panel.on_selected_audio_path_changes(path)

    def get_selected_audio_path(self):
        return self.selected_audio_path


    def show_page(self, page_name):
        page = self.pages[page_name]
        page.show()

    def hide_page(self, page_name):
        page = self.pages[page_name]
        page.hide()

    def switch_page(self, page_name):
        print(f"Switching to {page_name}")
        for page in self.pages:
            if page != page_name:
                self.hide_page(page)
        if page_name in self.pages:
            self.show_page(page_name)
        else:
            print(f"Page {page_name} not found")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Voice Recorder")
    root.geometry(window_size)
    root.resizable(False, False)

    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry(window_size)
    
    
    menu_bar = tk.Menu(root)
    device_menu = tk.Menu(menu_bar, tearoff=0)
    
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            device_menu.add_command(label=p.get_device_info_by_host_api_device_index(0, i).get('name'), command=lambda i=i: set_audio_input(i))

    menu_bar.add_cascade(label="Devices", menu=device_menu)
    root.config(menu=menu_bar)

    root.mainloop()
