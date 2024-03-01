import tkinter as tk
from page import Page

class EditPage(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.config(width=800, height=720, bg="#D4F4CC")

        self.canvas = tk.Canvas(
            self,
            width=800,
            height=720,
            bd=0,
            bg="#D4F4CC",
            highlightthickness=0,
            relief="flat"
        )
        self.canvas.place(x=0, y=0)

        self.canvas.create_text(
            400,
            360,
            text="This is edit page",
            fill="black",
            font=("Arial", 24)
        )