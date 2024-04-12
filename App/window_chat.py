import tkinter as tk
import asyncio
import websockets

class ChatRoom:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Room Application")
        self.master.geometry("800x720")
        self.master.resizable(False, False)

        # Create GUI elements

        
        # Create a button to create a chat room
        self.create_room_button = tk.Button(self.master, text="Create Chat Room", command=self.create_room)
        self.create_room_button.pack()

        # Create a button to join a chat room
        self.join_room_button = tk.Button(self.master, text="Join Chat Room", command=self.join_room)
        self.join_room_button.pack()

        # Create a text box to send messages
        self.chat_room_listbox = tk.Listbox(self.master)
        self.chat_room_listbox.pack()

        # Create a text box to receive messages
        self.chat_textbox = tk.Text(self.master)
        self.chat_textbox.pack()

        # Initialize variables
        self.chat_rooms = []

    def create_room(self):
        # Implement function to create a chat room
        # This involves setting up a server and broadcasting its existence
        pass

    def join_room(self):
        # Implement function to join a chat room
        # This involves connecting to the server and establishing communication
        pass

    async def send_message(self, message):
        # Implement function to send a message to the chat room
        pass

    async def receive_message(self):
        # Implement function to receive messages from the chat room
        pass

async def main():
    # Initialize asyncio event loop
    loop = asyncio.get_running_loop()

    # Create the tkinter GUI
    root = tk.Tk()
    app = ChatRoom(root)

    # Run the GUI event loop
    root.mainloop()

def start_chat_room():
    asyncio.run(main())

# if __name__ == "__main__":
#     asyncio.run(main())
