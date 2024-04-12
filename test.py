import tkinter as tk
import asyncio
import websockets
import threading

class VoiceChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Voice Chat")
        self.root.geometry("400x720")
        self.root.resizable(False, False)
        
        self.status_label = tk.Label(root, text="Enter the IP address and port of the server")
        self.status_label.pack()

        self.divider = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider.pack(fill=tk.X, padx=5, pady=5)

        self.name_label = tk.Label(root, text="Name:")
        self.name_label.pack()

        self.name_entry = tk.Entry(root)
        self.name_entry.pack()
        self.name_entry.insert(tk.END, "User")

        self.divider2 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider2.pack(fill=tk.X, padx=5, pady=5)

        self.ip_label = tk.Label(root, text="IP Address:")
        self.ip_label.pack()

        self.ip_entry = tk.Entry(root)
        self.ip_entry.pack()
        self.ip_entry.insert(tk.END, "localhost")

        self.port_label = tk.Label(root, text="Port:")
        self.port_label.pack()

        self.port_entry = tk.Entry(root)
        self.port_entry.pack()
        self.port_entry.insert(tk.END, "3280")

        self.start_server_button = tk.Button(root, text="Start Server", command=self.start_server)
        self.start_server_button.pack()

        self.join_server_button = tk.Button(root, text="Join Server", command=self.join_server)
        self.join_server_button.pack()

        self.divider3 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.divider3.pack(fill=tk.X, padx=5, pady=5)

        self.chat_room_listbox = tk.Listbox(root)
        self.chat_room_listbox.pack()
        self.chat_room_listbox.config(width=40, height=10)

        self.chat_textbox = tk.Text(root)
        self.chat_textbox.pack()
        self.chat_textbox.config(width=30, height=1)

        self.send_message_button = tk.Button(root, text="Send Message", command=self.send_message)
        self.send_message_button.pack()

        # Initialize variables
        self.is_running = False
        self.server = None
        self.client = None
        self.server_thread = None
        self.client_thread = None

    def start_server(self):
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
                    await asyncio.sleep(0.1)  # Check every 0.1 second
        except asyncio.CancelledError:
            print("Server stopped.")
        finally:
            self.is_running = False

    async def handle_client(self, websocket, path):
        print("New client connected")
        name = await websocket.recv()
        print(f"Client name: {name}")
        async for message in websocket:
            print(f"Message from {name}: {message}")
            self.chat_textbox.insert(tk.END, f"{name}: {message}\n")

    def join_server(self):
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
                print("Connected to server")
                self.status_label.config(text="Connected to server")

                await websocket.send(self.name_entry.get())

                while self.is_running:
                    await asyncio.sleep(0.1)  # Check every 0.1 second
                    await websocket.send("1")
        except asyncio.CancelledError:
            print("Connection stopped.")
        finally:
            self.is_running = False

    def send_message(self):
        if self.client:
            message = self.chat_textbox.get("1.0", tk.END).strip()
            if message:
                self.client.send(message.encode())
                self.chat_textbox.delete("1.0", tk.END)
                self.chat_textbox.insert(tk.END, f"You: {message}\n")

    def on_close(self):
        self.is_running = False
        self.root.destroy()

def start_app():
    root = tk.Tk()
    app = VoiceChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    start_app()
