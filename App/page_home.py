import tkinter as tk
from page import Page

class HomePage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.config(width=800, height=720, bg="#F4D6CC")

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

        self.canvas.create_text(
            400,
            360,
            text="This is home page",
            fill="black",
            font=("Arial", 24)
        )