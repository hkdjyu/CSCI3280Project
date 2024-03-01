import tkinter as tk

class CustomSliderTwoKnob(tk.Canvas):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg="#FFFFFF", bd=0, highlightthickness=0, relief="flat", width=600, height=30)

        self.enable = True  # Enable/Disable the slider

        # a lambda function to call the command
        self.command = command if command else None

        self.width = 600  # Width of the slider

        self.create_line(5, 10, self.width - 5, 10, fill="#000000", width=2) # x0 means 

        self.knob1_pos = 0  # Initial position of knob 1 (leftmost)
        self.knob2_pos = 1  # Initial position of knob 2 (rightmost)
        self.knob1 = self.create_oval(5, 5, 15, 15, fill="#00FF00", outline="#000000", width=1)
        self.knob2 = self.create_oval(self.width - 10, 5, self.width, 15, fill="#FF0000", outline="#000000", width=1)  # Knob 2
        self.bind("<B1-Motion>", self.move_knob)  # Bind mouse drag event to move knobs

        self.update_knobs()

    def move_knob(self, event):
        if not self.enable:
            return
        knob = event.widget.find_closest(event.x, event.y)[0]    
        if knob == self.knob1:
            # Ensure knob1 does not cross knob2
            self.knob1_pos = max(0, min((event.x - 5) / (self.width - 10), self.knob2_pos - 0.02))

        elif knob == self.knob2:
            # Ensure knob2 does not cross knob1
            self.knob2_pos = min(1, max((event.x + 5) / (self.width - 10), self.knob1_pos + 0.02))

        self.update_knobs()

        if self.command:
            self.command()

        
        

    def update_knobs(self):
        if self.enable:
            self.itemconfig(self.knob1, fill="#00FF00")
            self.itemconfig(self.knob2, fill="#FF0000")
        else:
            self.itemconfig(self.knob1, fill="#A0A0A0")
            self.itemconfig(self.knob2, fill="#A0A0A0")
        self.coords(self.knob1, self.knob1_pos * (self.width - 10), 5,
                    self.knob1_pos * (self.width - 10) + 10, 15)
        self.coords(self.knob2, self.knob2_pos * (self.width - 10) - 10, 5,
                    self.knob2_pos * (self.width - 10), 15)
        
    def get_knob1_pos(self):
        return self.knob1_pos
    
    def get_knob2_pos(self):
        return self.knob2_pos
    
    def get_values(self):
        return self.knob1_pos, self.knob2_pos
    
    def set_enable(self, enable):
        self.enable = enable
        self.update_knobs()

    def reset(self):
        self.knob1_pos = 0
        self.knob2_pos = 1
        self.update_knobs()
    
    

# Example usage
# root = tk.Tk()
# slider = CustomSliderTwoKnob(root, width=400, height=30)
# slider.pack()

# print(slider.get_knob1_pos())
# print(slider.get_knob2_pos())


# root.mainloop()
