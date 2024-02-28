# A python voice recorder app using tkinter and pyaudio

import tkinter as tk
import wave
import pyaudio
from screen_home import HomeScreen

screen_size = "1280x720"

if __name__ == "__main__":
    app = HomeScreen(screen_size)
    app.mainloop()