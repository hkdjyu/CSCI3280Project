import tkinter as tk
from page import Page
from window_chat import ChatRoom, start_chat_room

class ChatPage(Page):
    def __init__(self, audio_player, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        self.config(width=1280, height=720, bg="#D4F4CC")
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

        # A text show "Chat Page"
        self.canvas.create_text(
            400,
            360,
            text="Chat Page",
            font=("Arial", 24),
            fill="#792261"
        )

        # A button to open a new tkinter window
        self.open_window_button = tk.Button(
            self,
            text="Open Window",
            font=("Arial", 16),
            command=self.open_window
        )
        self.open_window_button.place(x=300, y=400, width=200, height=50)

    def open_window(self):
        start_chat_room()
        # Create a new tkinter window
        # window = tk.Toplevel(self)
        # window.title("New Window")
        # window.geometry("400x400")
        # window.config(bg="#D4F4CC")

        # # Create a canvas to contain UI elements
        # canvas = tk.Canvas(
        #     window,
        #     width=400,
        #     height=400,
        #     bd=0,
        #     bg="#D4F4CC",
        #     highlightthickness=0,
        #     relief="flat"
        # )
        # canvas.place(x=0, y=0)

        # # A text show "New Window"
        # canvas.create_text(
        #     200,
        #     200,
        #     text="New Window",
        #     font=("Arial", 24),
        #     fill="#792261"
        # )

    