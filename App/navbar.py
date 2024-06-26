import tkinter as tk
from page import Page

class Navbar(tk.Frame):
    def __init__(self, switch_page, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.config(width=480, height=120, bg="#792261")

        self.canvas = tk.Canvas(
            self,
            width=480,
            height=120,
            bd=0,
            bg="#792261",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.place(x=0, y=0)

        self.record_button = tk.Button(
            self,
            text="Record",
            bg="lightgrey",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.record_button.place(x=0, y=0, width=120, height=20)

        self.chat_button = tk.Button(
            self,
            text="Voice Chat",
            bg="lightgrey",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.chat_button.place(x=120, y=0, width=120, height=20)

        self.audioToText_button = tk.Button(
            self,
            text="Audio to Text",
            bg="lightgrey",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.audioToText_button.place(x=240, y=0, width=120, height=20)

        self.noiseRemoval_button = tk.Button(
            self,
            text="Noise Removal",
            bg="lightgrey",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.noiseRemoval_button.place(x=360, y=0, width=120, height=20)

        self.record_button.bind("<Button-1>", lambda e: switch_page("record"))
        self.chat_button.bind("<Button-1>", lambda e: switch_page("chat"))
        self.audioToText_button.bind("<Button-1>", lambda e: switch_page("audio_to_text"))
        self.noiseRemoval_button.bind("<Button-1>", lambda e: switch_page("noise_removal"))

