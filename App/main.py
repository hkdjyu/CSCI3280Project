# A python voice recorder app using tkinter and pyaudio

import tkinter as tk
from page_home import HomePage
from page_edit import EditPage
from panel_left import LeftPanel
from navbar import Navbar

window_size = "1280x720"

class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        # configure the main frame
        self.config(bg="black")
        
        self.navbar = Navbar(self.switch_page, self)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        self.left_panel = LeftPanel(self)
        self.left_panel.grid(row=0, column=0, sticky="s")

        self.main_panel = HomePage(self)
        self.main_panel.grid(row=0, column=1)

        self.edit_panel = EditPage(self)
        self.edit_panel.grid(row=0, column=1)

        # Create a dictionary to store the pages
        self.pages = {
            "home": self.main_panel,
            "edit": self.edit_panel
        }

        # Show the home page
        self.show_page("home")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.show()

    def hide_page(self, page_name):
        page = self.pages[page_name]
        page.hide()

    def switch_page(self, page_name):
        print(f"Switching to {page_name}")
        self.hide_page("home")
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
