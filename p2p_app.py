# P2P voice chat system GUI
# Description:
# A simple voice chat system with a GUI that allows users to create a room (run server and run client) or 
# join a room (run client only). 

# Your program should provide function of creating and joining chat rooms. The created chat
# rooms should be visible to other computers in a chat room list. To achieve this, you need to
# implement the following functionalities:
#  Chat room creation: Develop a function that allows users to create a new chat room.
# This function should enable other computers on the same network to discover and
# access the created chat room.
#  Chat room list: Implement a 'chat room list' feature that displays all the created chat
# rooms within the network. This list will help users identify and select the chat room they
# wish to join.
#  Joining chat rooms: Create a function that enables users to join a selected chat room
# from the 'chat room list'. This functionality should establish a connection with the chosen
# chat room, allowing users to participate in real-time communication.
#  Basic GUI for above functions. 

import tkinter as tk
import socket
import pyaudio
from threading import Thread

from p2p_client import VoiceChatClient
from p2p_server import VoiceChatServer

PORT_RANGE = range(3280, 3299) # 20 ports

class VoiceChatApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Voice Chat App")
        
        self.geometry("400x720")
        self.resizable(False, False)

        self.ip_address = "localhost"
        self.port = "3280"
        self.room_name = "server"

        self.mute_status = False
        self.deafen_status = False

        self.server = None
        self.client = None

        self.microphone_list = self.list_microphones()
        self.speaker_list = self.list_speakers()

        self.create_widgets()

        self.refresh()

    def create_widgets(self):

        # settings part

        self.room_name_label = tk.Label(self, text="Room Name: server")
        self.room_name_label.pack(pady=5)

        self.layout1 = tk.Frame(self)
        self.layout1.pack(pady=5)

        self.room_name_entry = tk.Entry(self.layout1)
        self.room_name_entry.pack(side=tk.LEFT)
        self.room_name_entry.insert(0, "server")

        self.room_name_set_button = tk.Button(self.layout1, text="Set", command=self.set_room_name)
        self.room_name_set_button.pack(side=tk.LEFT)

        self.ip_address_label = tk.Label(self, text="IP Address: localhost")
        self.ip_address_label.pack(pady=5)

        self.layout2 = tk.Frame(self)
        self.layout2.pack(pady=5)

        self.ip_address_entry = tk.Entry(self.layout2)
        self.ip_address_entry.pack(side=tk.LEFT)
        self.ip_address_entry.insert(0, "localhost")

        self.ip_address_set_button = tk.Button(self.layout2, text="Set", command=self.set_ip_address)
        self.ip_address_set_button.pack(side=tk.LEFT)

        # self.port_label = tk.Label(self, text="Port: 3280")
        # self.port_label.pack(pady=5)

        # self.layout3 = tk.Frame(self)
        # self.layout3.pack(pady=5)

        # self.port_entry = tk.Entry(self.layout3)
        # self.port_entry.pack(side=tk.LEFT)
        # self.port_entry.insert(0, "3280")

        # self.port_set_button = tk.Button(self.layout3, text="Set", command=self.set_port)
        # self.port_set_button.pack(side=tk.LEFT)


        self.create_room_button = tk.Button(self, text="Create", command=self.create_room)
        self.create_room_button.pack(pady=5)

        self.divider1 = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        self.divider1.pack(fill=tk.X, padx=5, pady=5)

        self.refresh_button = tk.Button(self, text="Refresh", command=self.refresh)
        self.refresh_button.pack(pady=5)

        self.chat_rooms_listbox = tk.Listbox(self, width=30, height=5)
        self.chat_rooms_listbox.pack(pady=5)

        self.join_button = tk.Button(self, text="Join Room", command=self.join_room)
        self.join_button.pack(pady=5)

        self.divider2 = tk.Frame(self, height=2, bd=1, relief=tk.SUNKEN)
        self.divider2.pack(fill=tk.X, padx=5, pady=5)

        # chatting part

        self.layout4 = tk.Frame(self)
        self.layout4.pack(pady=5)

        self.left_col1 = tk.Frame(self.layout4)
        self.left_col1.pack(side=tk.LEFT, padx=5)

        self.right_col1 = tk.Frame(self.layout4)
        self.right_col1.pack(side=tk.LEFT, padx=5)


        self.microphone_option_menu_var = tk.StringVar()
        self.microphone_option_menu_var.set(self.microphone_list[0])
        self.microphone_option_menu = tk.OptionMenu(self.left_col1, self.microphone_option_menu_var, *self.microphone_list)
        self.microphone_option_menu.pack(side=tk.TOP)

        self.speaker_option_menu_var = tk.StringVar()
        self.speaker_option_menu_var.set(self.speaker_list[0])
        self.speaker_option_menu = tk.OptionMenu(self.right_col1, self.speaker_option_menu_var, *self.speaker_list)
        self.speaker_option_menu.pack(side=tk.TOP)

        self.mute_button = tk.Button(self.left_col1, text="Mute", command=self.on_mute_button_click)
        self.mute_button.pack(side=tk.TOP)

        self.deafen_button = tk.Button(self.right_col1, text="Deafen", command=self.on_deafen_button_click)
        self.deafen_button.pack(side=tk.TOP)

    def list_microphones(self):
        p = pyaudio.PyAudio()
        microphone_list = []
        for i in range(p.get_device_count()):
            if p.get_device_info_by_index(i).get('maxInputChannels') > 0:
                microphone_list.append(p.get_device_info_by_index(i).get('name'))
        return microphone_list
    
    def list_speakers(self):
        p = pyaudio.PyAudio()
        speaker_list = []
        for i in range(p.get_device_count()):
            if p.get_device_info_by_index(i).get('maxOutputChannels') > 0:
                speaker_list.append(p.get_device_info_by_index(i).get('name'))
        return speaker_list
        
        
    def set_room_name(self):
        self.room_name = self.room_name_entry.get()
        self.room_name_label.config(text=f"Room Name: {self.room_name}")
        return
    
    def set_ip_address(self):
        self.ip_address = self.ip_address_entry.get()
        self.ip_address_label.config(text=f"IP Address: {self.ip_address}")
        return
    
    def set_port(self):
        self.port = self.port_entry.get()
        self.port_label.config(text=f"Port: {self.port}")
        return
    
    def ping(self, ip, port):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            client_socket.send(b'ping')
            name = client_socket.recv(1024).decode()
            client_socket.send(b'disconnect')
            client_socket.close()
            return True, name
        except:
            return False, None
    
    def check_free_port(self):
        for port in PORT_RANGE:
            status, _ = self.ping(self.ip_address, port)
            if not status:
                return port
        return None

    def create_room(self):
        # start server, then start client
        self.start_server()
        self.start_client(self.ip_address, self.port)
        self.set_settings_enabled(tk.DISABLED)
        return

    def start_server(self):
        if self.server is None:
            port = self.check_free_port()
            if port is not None:
                self.port = port
                self.server = VoiceChatServer(name=self.room_name, host=self.ip_address, port=port)
                server_thread = Thread(target=self.server.start)
                server_thread.start()
            else:
                print("No available ports.")
        return
    
    def start_client(self, host, port):
        p = pyaudio.PyAudio()
        input_device_index = None
        output_device_index = None
        for i in range(p.get_device_count()):
            if p.get_device_info_by_index(i).get('name') == self.microphone_option_menu_var.get() and p.get_device_info_by_index(i).get('maxInputChannels') > 0:
                input_device_index = i
            if p.get_device_info_by_index(i).get('name') == self.speaker_option_menu_var.get() and p.get_device_info_by_index(i).get('maxOutputChannels') > 0:
                output_device_index = i

        
        self.client = VoiceChatClient(host=host, port=port, input_device_index=input_device_index, output_device_index=output_device_index)
        client_thread = Thread(target=self.client.start)
        client_thread.start()
        return

    
    def refresh(self):
        self.chat_rooms_listbox.delete(0, tk.END)
        for port in PORT_RANGE:
            status, name = self.ping(self.ip_address, port)
            if status:
                self.chat_rooms_listbox.insert(tk.END, f"{name} - {self.ip_address}:{port}")
        return
    
    def join_room(self):
        selected = self.chat_rooms_listbox.curselection()
        if selected:
            selected = self.chat_rooms_listbox.get(selected[0])
            selected_name, selected_ip_port = selected.split(" - ")
            selected_ip, selected_port = selected_ip_port.split(":")
            self.start_client(selected_ip, int(selected_port))
            self.set_settings_enabled(tk.DISABLED)
        return
    
    def on_mute_button_click(self):
        if self.mute_status:
            # set unmute
            if self.client is not None:
                self.client.set_mute_status(False)
            self.mute_button.config(text="Mute")
            self.mute_status = False
        else:
            # set mute
            if self.client is not None:
                self.client.set_mute_status(True)
            self.mute_button.config(text="Unmute")
            self.mute_status = True
    
    def on_deafen_button_click(self):
        if self.deafen_status:
            # set undeafen
            if self.client is not None:
                self.client.set_deafen_status(False)
            self.deafen_button.config(text="Deafen")
            self.deafen_status = False
        else:
            # set deafen
            if self.client is not None:
                self.client.set_deafen_status(True)
            self.deafen_button.config(text="Undeafen")
            self.deafen_status = True
    
    def set_settings_enabled(self, status):
        self.room_name_entry.config(state=status)
        self.room_name_set_button.config(state=status)
        self.ip_address_entry.config(state=status)
        self.ip_address_set_button.config(state=status)
        # self.port_entry.config(state=status)
        # self.port_set_button.config(state=status)
        self.create_room_button.config(state=status)
        self.refresh_button.config(state=status)
        self.chat_rooms_listbox.config(state=status)
        self.join_button.config(state=status)
        return
    
    def on_closing(self):
        if self.client is not None:
            self.client.stop()
        if self.server is not None:
            self.server.stop()
        print("Closing app.")
        self.destroy()
        print("App closed.")
        print("press ctrl+c to exit if the program is still running.")
        return

if __name__ == "__main__":
    app = VoiceChatApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()