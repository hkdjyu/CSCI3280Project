# A python voice recorder app using tkinter and pyaudio

import tkinter as tk
from page_record import RecordPage
from page_edit import EditPage
from panel_left import LeftPanel
from navbar import Navbar

from audio_player import AudioPlayer

window_size = "1280x720"

audio_player = AudioPlayer()

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

        self.main_panel = RecordPage(audio_player, self.left_panel, self)
        self.main_panel.grid(row=0, column=1)

        self.edit_panel = EditPage(audio_player, self)
        self.edit_panel.grid(row=0, column=1)

        # Create a dictionary to store the pages
        self.pages = {
            "record": self.main_panel,
            "edit": self.edit_panel
        }

        # Show the record page
        self.show_page("record")

       

    def set_selected_audio_path(self, path):
        self.selected_audio_path = path
        self.main_panel.on_selected_audio_path_changes(path)

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
        self.hide_page("record")
        self.hide_page("edit")
        self.show_page(page_name)
       

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Voice Recorder")
    root.geometry(window_size)
    root.resizable(False, False)

    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry(window_size)
    root.mainloop()
