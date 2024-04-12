import tkinter as tk
import asyncio
import websockets
import threading
import pyaudio

class VoiceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Voice Chat")
        self.root.geometry("400x720")
        self.root.resizable(False, False)
        
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

        # Initialize variables
        self.username = self.name_entry.get()
        self.ip_address = self.ip_entry.get()
        self.port = self.port_entry.get()
        self.selected_chat_room = None
        self.is_running = False
        self.server = None
        self.connected_client_ports = []
        self.client = None
        self.connected_server_port = None
        self.server_thread = None
        self.client_thread = None
        self.refresh_room_thread = None
        self.is_refreshing = False
        self.available_chat_rooms = []

        self.is_muted = True
        self.pyaudio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self.audio_input_thread = None
        self.audio_output_thread = None

    def on_name_change(self):
        self.username = self.name_entry.get()
        self.name_label.config(text=f"Username: {self.username}")

    def on_ip_change(self):
        self.ip_address = self.ip_entry.get()
        self.ip_label.config(text=f"IP Address: {self.ip_address}")

    def on_port_change(self):
        self.port = int(self.port_entry.get())
        self.port_label.config(text=f"Port: {self.port}")

    def on_room_select(self, event):
        if self.available_chat_rooms.__len__() == 0:
            return
        self.join_chat_room_button.config(state=tk.NORMAL)
        try:
            self.selected_chat_room = self.chat_room_listbox.get(self.chat_room_listbox.curselection())
            print(f"Selected chat room: {self.selected_chat_room}")
        except Exception as e:
            self.selected_chat_room = None
        return
    
    def on_refresh_room_click(self):
        if self.is_refreshing is False:
            self.is_refreshing = True
            self.join_chat_room_button.config(state=tk.DISABLED)
            self.refresh_button.config(text=" Stop ")
            self.refresh_room_thread = threading.Thread(target=self.update_chat_rooms)
            self.refresh_room_thread.start()
        else:
            self.is_refreshing = False
            self.join_chat_room_button.config(state=tk.NORMAL)
            self.refresh_button.config(text="Refresh")
        return

    def update_chat_rooms(self):
        # check available chat rooms, port 3280-3289
        self.chat_room_listbox.delete(0, tk.END)
        self.status_label.config(text="Updating chat rooms ...")
        for i in range(10):
            if self.is_refreshing is False:
                self.status_label.config(text="Chat rooms update stopped.")
                return
            self.status_label.config(text="Updating chat rooms ... checking port " + str(3280 + i))
            try:
                uri = f"ws://{self.ip_entry.get()}:{3280 + i}"
                hostname, port = asyncio.run(self.check_chat_room(uri))
                if port and hostname:
                    print(f"Found chat room {hostname} at port {port}")
                    self.chat_room_listbox.insert(tk.END, f"{hostname}'s Room ({port})")
                    print(f"Updated chat room listbox")
                    self.available_chat_rooms.append(f"{hostname}'s Room ({port})")
            except WindowsError as e:
                print(f"Unable to connect to {uri}")
            except Exception as e:
                print(e)
        self.status_label.config(text="Chat rooms updated.")
        return
    
    async def check_chat_room(self, uri):
        async with websockets.connect(uri) as websocket:
            send_msg = self.encode_string_message(str(self.username), "search-ask", str(self.username))
            await websocket.send(send_msg)
            print(f"Sent search ask to {uri}")
            print(send_msg)
            recv_msg = await websocket.recv()
            print(f"Received search reply from {uri}")
            print(recv_msg)
            recv_msg_name, recv_msg_type, recv_msg_string = self.decode_string_message(recv_msg)
            if recv_msg_type == "search-reply":
                return recv_msg_name, recv_msg_string
        return None, None

    def set_enable_settings(self, enable):
        self.name_entry.config(state=enable)
        self.ip_entry.config(state=enable)
        self.port_entry.config(state=enable)
        self.name_entry_button.config(state=enable)
        self.ip_entry_button.config(state=enable)
        self.port_entry_button.config(state=enable)
        self.start_server_button.config(state=enable)
        self.join_server_button.config(state=enable)
        self.refresh_button.config(state=enable)
        self.join_chat_room_button.config(state=enable)

    def start_server(self):
        self.set_enable_settings(tk.DISABLED)
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        self.server_thread = threading.Thread(target=self.start_server_thread, args=(ip, port))
        self.server_thread.start()

    def start_server_thread(self, ip, port):
        asyncio.run(self.start_server_async(ip, port))

    async def start_server_async(self, ip, port):
        self.is_running = True
        try:
            async with websockets.serve(self.handle_client, ip, port) as websocket:
                print(f"Server started at ws://{ip}:{port}")
                self.status_label.config(text=f"Server started at ws://{ip}:{port}")
                while self.is_running:
                    await asyncio.sleep(0.01)  # Check every 0.1 second
        except asyncio.CancelledError:
            print("Server stopped.")
        finally:
            self.is_running = False

    async def handle_client(self, websocket, path):
        self.server = websocket
        msg = await websocket.recv()
        print(f"Received message: \n{msg}\n")
        # if msg is string, it always start with <username/><type/><string=""/>
        msg_username = None
        msg_type = None
        msg_string = None
        
        if msg and isinstance(msg, str):
            msg_username, msg_type, msg_string = self.decode_string_message(msg)

        if msg_username and msg_type and msg_string:
            if msg_type == "search-ask":
                # search chat rooms
                port = self.port
                send_msg = self.encode_string_message(self.name_entry.get(), "search-reply", str(port))
                await websocket.send(send_msg)

            if msg_type == "client-info":
                print(f"Client connected, {msg_username}: {msg_string}")
                self.chat_listbox.insert(tk.END, f"New client connected: {msg_username}\n")
                # self.chat_listbox.see(tk.END)
                uri = f"ws://{str(self.ip_address)}:{str(self.port)}"
                print(f"Sending server info to {msg_username}: {uri}")
                send_msg = self.encode_string_message(str(self.username), "server-info", uri)
                await websocket.send(send_msg)

                # listen for messages
                while self.is_running:
                    try:
                        msg = await websocket.recv()
                    except websockets.exceptions.ConnectionClosedError:
                        print("Error: Connection closed.")
                        break
                    if isinstance(msg, str):
                        print(f"Received message: \n{msg}\n")
                        msg_username, msg_type, msg_string = self.decode_string_message(msg)
                        if msg_username and msg_type and msg_string:
                            if msg_type == "text-message":
                                self.chat_listbox.insert(tk.END, f"{msg_username}: {msg_string}\n")
                                # self.chat_listbox.see(tk.END)
                    elif isinstance(msg, bytes):
                        print(f"Received audio message.")
                        # play audio

                        if self.output_stream is None:
                            self.output_stream = self.pyaudio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
                        self.output_stream.write(msg)

                    await asyncio.sleep(0.01)
        
        # print(f"Client name: {msg_username}\nmsg_type: {msg_type}\nmsg_string: {msg_string}")

        print()
            
    def decode_string_message(self, msg):
        msg_username = None
        msg_type = None
        msg_string = None
        if msg.startswith("<") and msg.endswith("/>"):
            msg = msg[1:-2]
            msg_list = msg.split("/><")
            if len(msg_list) == 3:
                msg_username, msg_type, msg_string = msg_list
        return msg_username, msg_type, msg_string
    
    def encode_string_message(self, username, msg_type, msg_string):
        return f"<{username}/><{msg_type}/><{msg_string}/>"

    def join_server(self):
        self.set_enable_settings(tk.DISABLED)
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        self.client_thread = threading.Thread(target=self.connect_to_server, args=(ip, port))
        self.client_thread.start()

    def connect_to_server(self, ip, port):
        asyncio.run(self.connect_to_server_async(ip, port))

    async def connect_to_server_async(self, ip, port):
        self.is_running = True
        uri = f"ws://{ip}:{port}"
        print(f"Connecting to {uri} ...")
        self.status_label.config(text=f"Connecting to {uri} ...")
        try:
            async with websockets.connect(uri) as websocket:
                self.client = websocket
                print("Connected to server")
                self.status_label.config(text="Connected to server")
                send_msg = self.encode_string_message(str(self.username), "client-info", str(self.username))
                await websocket.send(send_msg)
                print(f"Sent client info, waiting for server info ...")
                recv_msg = await websocket.recv()
                print(f"Received server info: {recv_msg}")
                recv_msg_name, recv_msg_type, recv_msg_string = self.decode_string_message(recv_msg)
                if recv_msg_type == "server-info":
                    print(f"Received server info: {recv_msg_string}")
                    # self.client = websocket
                    self.chat_listbox.insert(tk.END, f"Connected to {recv_msg_name}'s Room\n")
                    # self.chat_listbox.see(tk.END)

                    self.connected_server_port = int(recv_msg_string.split(":")[2])

                    # listen for messages
                    while self.is_running:
                        msg = await websocket.recv()
                        if isinstance(msg, str):
                            print(f"Received message: \n{msg}\n")
                            msg_username, msg_type, msg_string = self.decode_string_message(msg)
                            if msg_username and msg_type and msg_string:
                                if msg_type == "text-message":
                                    self.chat_listbox.insert(tk.END, f"{msg_username}: {msg_string}\n")
                                    # self.chat_listbox.see(tk.END)
                        elif isinstance(msg, bytes):
                            print(f"Received audio message.")
                            # play audio

                            if self.output_stream is None:
                                self.output_stream = self.pyaudio.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)
                            self.output_stream.write(msg)

                        await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            print("Connection stopped.")
        except websockets.exceptions.ConnectionClosedError:
            print("Error: Connection closed.")
        finally:
            self.is_running = False

    def join_chat_room(self):
        if self.selected_chat_room:
            if self.is_refreshing:
                self.on_refresh_room_click()
            self.set_enable_settings(tk.DISABLED)
            chat_room_port = int(self.selected_chat_room.split("(")[1].split(")")[0])
            print(f"Joining chat room {chat_room_port}")
            self.client_thread = threading.Thread(target=self.connect_to_server, args=(self.ip_address, chat_room_port))
            self.client_thread.start()
        return

    def send_message(self):
        if self.client:
            msg = self.chat_textbox.get("1.0", tk.END)
            self.chat_textbox.delete("1.0", tk.END)
            msg = self.encode_string_message(self.username, "text-message", msg)
            print(f"Sending message: {msg}")
            asyncio.run(self.send_message_async(msg))
        elif self.server:
            msg = self.chat_textbox.get("1.0", tk.END)
            self.chat_textbox.delete("1.0", tk.END)
            msg = self.encode_string_message(self.username, "text-message", msg)
            print(f"Sending message: {msg}")
            asyncio.run(self.send_message_async(msg))
        return

    async def send_message_async(self, msg):
        msg_username, msg_type, msg_string = self.decode_string_message(msg)
        if self.client:
            self.chat_listbox.insert(tk.END, f"{self.username}: {msg_string}\n")
            # self.chat_listbox.see(tk.END)
            await self.client.send(msg)
        elif self.server:
            self.chat_listbox.insert(tk.END, f"{self.username}: {msg_string}\n")
            # self.chat_listbox.see(tk.END)
            await self.server.send(msg)
        return
    
    def on_mute_click(self):
        if self.is_muted:
            # unmute and start keep sending audio
            self.is_muted = False
            self.mute_button.config(text="Mute")
            
            if self.client:
                self.audio_input_thread = threading.Thread(target=lambda: asyncio.run(self.send_audio()))
                self.audio_input_thread.start()

            elif self.server:
                self.audio_input_thread = threading.Thread(target=lambda: asyncio.run(self.send_audio()))
                self.audio_input_thread.start()

        else:
            # mute and stop sending audio
            self.is_muted = True
            self.mute_button.config(text="Unmute")
            if self.input_stream:
                self.input_stream.stop_stream()
                self.input_stream.close()
                self.input_stream = None
        return
    
    async def send_audio(self):
        if self.is_muted:
            return
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        if self.output_stream is None:
            self.output_stream = self.pyaudio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        print("Audio sending started . . ", end="")
        if self.client:
            # send audio
            while self.is_running and not self.is_muted:
                data = self.output_stream.read(CHUNK)
                await self.client.send(data)
                print (f"Sent audio data.")

                # DEBUG
                # await self.client.send(self.encode_string_message(self.username, "text-message", "Hello, world!"))
                # await asyncio.sleep(1)
            
        elif self.server:
            # send audio
            while self.is_running and not self.is_muted:
                data = self.output_stream.read(CHUNK)
                await self.server.send(data)   
                print (f"Sent audio data.")

        print(". . Audio sending stopped.")  
        return


    def on_close(self):
        self.is_running = False
        # if self.input_stream:
        #     self.input_stream.stop_stream()
        #     self.input_stream.close()
        # if self.output_stream:
        #     self.output_stream.stop_stream()
        #     self.output_stream.close()
        # if self.pyaudio:
        #     self.pyaudio.terminate()

        self.root.destroy()

        # if self.server:
        #     self.server.close()

        # if self.client:
        #     self.client.close()

        if self.server_thread:
            self.server_thread.join()
        if self.client_thread:
            self.client_thread.join()
        if self.refresh_room_thread:
            self.refresh_room_thread.join()

def start_app():
    root = tk.Tk()
    app = VoiceChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    start_app()
