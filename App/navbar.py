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
            bg="white",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.record_button.place(x=0, y=0, width=120, height=20)

        self.edit_button = tk.Button(
            self,
            text="Edit",
            bg="white",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.edit_button.place(x=120, y=0, width=120, height=20)

        self.delete_button = tk.Button(
            self,
            text="",
            bg="white",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.delete_button.place(x=240, y=0, width=120, height=20)

        self.add_button = tk.Button(
            self,
            text="",
            bg="white",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#792261",
            activeforeground="white"
        )
        self.add_button.place(x=360, y=0, width=120, height=20)

        self.record_button.bind("<Button-1>", lambda e: switch_page("record"))
        self.edit_button.bind("<Button-1>", lambda e: switch_page("edit"))

