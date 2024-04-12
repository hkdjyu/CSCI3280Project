import tkinter as tk
import websockets
import asyncio
import threading
from voice_chat_server import VoiceChatServer
from voice_chat_client import VoiceChatClient

class VoiceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Voice Chat")
        self.root.geometry("400x720")
        self.root.resizable(False, False)

        # variables

        self.username = "User"
        self.ip_address = "localhost"
        self.port = 3280
        
        self.server = None
        self.server_thread = None

        self.is_muted = True
        
        self.create_widgets(self.root)

    def create_widgets(self, root):
        # status label

        self.status_label = tk.Label(root, text="Enter the IP address and port of the server")
        self.status_label.pack()

        self.divider = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider.pack(fill=tk.X, padx=5, pady=5)

        # input fields for name

        self.name_label = tk.Label(root, text="Username: User")
        self.name_label.pack()

        self.layout_frame_0 = tk.Frame(root)
        self.layout_frame_0.pack()

        self.name_entry = tk.Entry(self.layout_frame_0)
        self.name_entry.pack(side=tk.LEFT)
        self.name_entry.insert(tk.END, "User")

        self.name_entry_button = tk.Button(self.layout_frame_0, text="Set", command=lambda: self.on_name_change())
        self.name_entry_button.pack(side=tk.RIGHT, padx=5)


        self.divider2 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider2.pack(fill=tk.X, padx=5, pady=5)

        # input fields for IP and port, for creating server

        self.ip_label = tk.Label(root, text="IP Address: localhost")
        self.ip_label.pack()

        self.layout_frame_1 = tk.Frame(root)
        self.layout_frame_1.pack()

        self.ip_entry = tk.Entry(self.layout_frame_1)
        self.ip_entry.pack(side=tk.LEFT)
        self.ip_entry.insert(tk.END, "localhost")

        self.ip_entry_button = tk.Button(self.layout_frame_1, text="Set", command=lambda: self.on_ip_change())
        self.ip_entry_button.pack(side=tk.RIGHT, padx=5)

        self.port_label = tk.Label(root, text="Port: 3280")
        self.port_label.pack()

        self.layout_frame_2 = tk.Frame(root)
        self.layout_frame_2.pack()

        self.port_entry = tk.Entry(self.layout_frame_2)
        self.port_entry.pack(side=tk.LEFT)
        self.port_entry.insert(tk.END, "3280")

        self.port_entry_button = tk.Button(self.layout_frame_2, text="Set", command=lambda: self.on_port_change())
        self.port_entry_button.pack(side=tk.RIGHT, padx=5)

        self.start_server_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_server_button.pack()

        self.join_server_button = tk.Button(root, text="Join Server", command=self.join_server)
        self.join_server_button.pack()

        self.divider3 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider3.pack(fill=tk.X, padx=5, pady=5)

        # a listbox showing available chat rooms, for joining server

        self.chat_room_label = tk.Label(root, text="Chat Rooms:")
        self.chat_room_label.pack()

        self.chat_room_listbox = tk.Listbox(root)
        self.chat_room_listbox.pack()
        self.chat_room_listbox.config(width=20, height=5)
        self.chat_room_listbox.bind("<<ListboxSelect>>", self.on_room_select)

        # layout of two columns
        # column: refresh button, join button

        self.layout_frame = tk.Frame(root)
        self.layout_frame.pack()

        self.refresh_button = tk.Button(self.layout_frame, text="Refresh", command=self.on_refresh_room_click)
        self.refresh_button.pack(side=tk.LEFT)

        self.join_chat_room_button = tk.Button(self.layout_frame, text="Join Chat Room", command=self.join_chat_room)
        self.join_chat_room_button.pack(side=tk.RIGHT)
        self.join_chat_room_button.config(state=tk.DISABLED)

        self.divider4 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider4.pack(fill=tk.X, padx=5, pady=5)

        self.chat_listbox = tk.Listbox(root)
        self.chat_listbox.pack()
        self.chat_listbox.config(width=40, height=10)

        self.chat_textbox = tk.Text(root)
        self.chat_textbox.pack()
        self.chat_textbox.config(width=30, height=1)
        self.chat_textbox.bind("<Return>", lambda e: self.send_message())

        self.send_message_button = tk.Button(root, text="Send Message", command=self.send_message)
        self.send_message_button.pack()

        self.divder5 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divder5.pack(fill=tk.X, padx=5, pady=5)

        self.mute_button = tk.Button(root, text="Unmute", command=self.on_mute_click)
        self.mute_button.pack()

        self.divider6 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider6.pack(fill=tk.X, padx=5, pady=5)


    def on_name_change(self):
        self.username = self.name_entry.get()
        self.name_label.config(text="Username: " + self.username)

    def on_ip_change(self):
        self.ip_address = self.ip_entry.get()
        self.ip_label.config(text="IP Address: " + self.ip_address)

    def on_port_change(self):
        self.port = int(self.port_entry.get())
        self.port_label.config(text="Port: " + str(self.port))

    def start_server(self):
        self.status_label.config(text="Server started at " + self.ip_address + ":" + str(self.port))
        self.start_server_button.config(state=tk.DISABLED)
        # self.server = VoiceChatServer(self.ip_address, self.port)
        # self.server_thread = threading.Thread(target=self.server.start_server)
        # self.server_thread.start()
        threading.Thread(target=self.start_server_thread).start()

    
    def start_server_thread(self):
        self.server = VoiceChatServer(self.ip_address, self.port)
        asyncio.run(self.start_server_async())

    async def start_server_async(self):
        await self.server.run_server()


    def join_server(self):
        self.status_label.config(text="Joining server at " + self.ip_address + ":" + str(self.port))
        self.join_server_button.config(state=tk.DISABLED)
        self.client = VoiceChatClient(self.ip_address, self.port)
        self.client_thread = threading.Thread(target=self.client.connect_to_server)
        self.client_thread.start()

    def on_room_select(self, event):
        pass

    def on_refresh_room_click(self):
        pass

    def join_chat_room(self):
        pass

    def send_message(self):
        pass

    def on_mute_click(self):
        if self.is_muted:
            # set to unmuted
            self.is_muted = False
            self.mute_button.config(text="Mute")
            if self.client is not None:
                self.client.is_muted = False
                threading.Thread(target=self.client.send_audio_data).start()
        else:
            # set to muted
            self.is_muted = True
            self.mute_button.config(text="Unmute")
            if self.client is not None:
                self.client.is_muted = True

            # if self.client is not None:
            #     threading.Thread(target=self.client.send_audio_data).start()

    def on_close(self):
        self.is_running = False
        self.root.destroy()

        if self.server:
            asyncio.run(self.server.close())


def start_app():
    root = tk.Tk()
    app = VoiceChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    start_app()
