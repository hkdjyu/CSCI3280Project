import tkinter as tk
from page import Page

class EditPage(Page):
    def __init__(self, audio_player, *args, **kwargs):
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

        # Add a button

        self.button = tk.Button(
            self,
            text="Test",
            bg="white",
            fg="black",
            font=("Arial", 12),
            relief="flat",
            activebackground="#D4F4CC",
            activeforeground="black",
            command=lambda: print("is audio playing? ", audio_player.is_playing())
        )
        self.button.place(x=200, y=200, width=120, height=20)