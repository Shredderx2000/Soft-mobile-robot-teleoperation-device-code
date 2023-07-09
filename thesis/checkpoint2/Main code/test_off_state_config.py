import os
import RPi.GPIO as GPIO
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from adafruit_mcp3xxx.mcp3008 import MCP3008
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import Menu
from button_states import GaitState,func1_OnState, func1_OffState, func2_OnState, func2_OffState, OffState, OnState
class MyOptionMenu(tk.Menubutton):
    def __init__(self, master, variable, *values):
        super().__init__(master, textvariable=variable, relief="raised")
        self.menu = Menu(self, tearoff=False)
        self["menu"] = self.menu
        self.variable = variable
        for value in values:
            self.menu.add_radiobutton(label=value, variable=variable, background='white', activebackground='red')

    def drop_down(self):
        self.menu.post(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())
        
    def clear(self):
        if self.menu is not None:
            self.menu.unpost()
            
class Settings:
    def __init__(self,functions,img):
        os.remove("controller_status.txt")
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(board.D5)
        self.mcp = MCP.MCP3008(self.spi,self.cs)

        self.root = tk.Tk()
        self.root.geometry("380x240")
#         self.root.overrideredirect(True)
        self.root.bind('<q>', self.close_window)
        self.button_pin = 26         
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.current_state = OffState()
        self.current_state.enter()
        # Read the joystick configuration from the file

        self.drop_downs = []
        dropdown_coordinates = [(25, 150), (100, 150), (100, 110), (225, 110), (225, 150), (300, 150)]  # This is just an example. Replace with the actual coordinates
        
        # Load controller image as background
        self.img = img
        self.background = ImageTk.PhotoImage(img)
        self.bg_label = tk.Label(self.root, image=self.background)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.OPTIONS = functions  # List of options to choose from
        self.variables = [tk.StringVar(self.root) for _ in range(6)]
        joystick_config = {}
        with open("controller_status.txt", "r") as file:
                lines = file.readlines()[7:]  # Skip the first 7 lines
                
        self.joystick_label1 = tk.Label(self.root, text="Joystick 1", fg="black")
        self.joystick_label2 = tk.Label(self.root, text="Joystick 2", fg="black")
        self.joystick_label1.place(x=100, y=20)
        self.joystick_label2.place(x=225, y=20)
        for line in lines:
            if "Joystick status" in line:
                joystick_info = line.strip().split(":")
                joystick_channel = int(joystick_info[0].split()[-1])
                joystick_status = joystick_info[1].strip()

                if joystick_status == "Working":
                    joystick_config[joystick_channel] = True
                else:
                    joystick_config[joystick_channel] = False
                    if joystick_channel in [0, 1]:
                        self.joystick_label1.config(fg="red")  # Set joystick 1 label color to red
                    elif joystick_channel in [2, 3]:
                        self.joystick_label2.config(fg="red")  # Set joystick 2 label color to red
        # Assign joystick controls based on the configuration
        if 0 in joystick_config and joystick_config[0]:
            self.joystick_x = AnalogIn(self.mcp, MCP.P0)
        if 1 in joystick_config and joystick_config[1]:
            self.joystick_y = AnalogIn(self.mcp, MCP.P1)        
        if 2 in joystick_config and joystick_config[2]:
            self.joystick_x = AnalogIn(self.mcp, MCP.P2)
        if 3 in joystick_config and joystick_config[3]:
            self.joystick_y = AnalogIn(self.mcp, MCP.P3)        


        self.last_joystick_input = time.time()
        self.last_button_press = time.time()
        self.input_delay = 0.2  # delay in seconds
        # Assign different options to each label
        for i, variable in enumerate(self.variables):
            variable.set(self.OPTIONS[i % len(self.OPTIONS)])  # Assign option based on index

        for i, variable in enumerate(self.variables):
            dropdown = MyOptionMenu(self.root, variable, *self.OPTIONS)
            dropdown.place(x=dropdown_coordinates[i][0], y=dropdown_coordinates[i][1])
            self.drop_downs.append(dropdown)            
        self.confirm_button = tk.Button(self.root, text="Confirm", command=self.confirm_configuration)
        self.confirm_button.place(x=150, y=200) # Update with the actual x and y coordinates
        
        self.selected_dropdown = 0  # initially selected dropdown
        self.is_menu_open = False  # Flag to check if menu is open or not
        self.is_configuration_confirmed = False  # Flag to check if the configuration is confirmed
        self.button_objects = self.drop_downs
        
    def close_window(self):
        self.root.destroy()
        
    def confirm_configuration(self):
        if self.is_configuration_confirmed:
            # Switch to the on state...
            self.write_button_configurations() 
            print("Configuration confirmed.")
            self.close_window()
#             sys.exit(0)  # Exit the program with a success code
        else:
            pass
        
    def write_button_configurations(self):
        button_configurations = []

        # Add button configurations to the list
        for dropdown, variable in enumerate(self.variables):
            button_configurations.append(f"Dropdown {dropdown + 1}: {variable.get()}")

        # Write button configurations to a text file
        with open("button_configuration.txt", "w") as file:
            file.write("\n".join(button_configurations))
            print("Button configurations written to file.")

    def update_labels(self):
        # Read the button status from the file
        with open("controller_status.txt", "r") as file:
            lines = file.readlines()
        # Split the list of buttons into good and bad buttons
        good_buttons = []
        bad_buttons = []

        # Iterate through the lines and check button statuses
        for index, line in enumerate(lines[:-5]):
            if "Button status" in line:
                button_info = line.split(":")
                button_io = button_info[0].split()[-1].strip()
                button_status = button_info[1].strip()

                # Check if button is working or not
                if button_status == "Stuck pressed":
                    bad_buttons.append(self.button_objects[index])
                else:
                    good_buttons.append(self.button_objects[index])

        # Set the background color for good buttons to white
        for button in good_buttons:
            button.config(bg="white")

        # Set the background color for bad buttons to red
        for button in bad_buttons:
            button.config(bg="red")

        self.confirm_button.config(bg="white")

        # Color the selected button
        if self.selected_dropdown >= 0 and self.selected_dropdown < len(self.button_objects):
            selected_button = self.button_objects[self.selected_dropdown]
            if selected_button in bad_buttons:
                selected_button.config(bg="yellow")
            elif selected_button in good_buttons:
                selected_button.config(bg="green")
        else:
            self.confirm_button.config(bg="green")
                        
    def run(self):
        last_y = self.joystick_y.value
        while True:



            # Check for joystick action
            DEADZONE = 17000  # Define the dead zone
            THRESHOLD = 28000  # Define the threshold for detecting movement
            CENTER = 35767  # The center value for the joystick
            last_non_center_y = CENTER  # Initialize last non-center y position

            # Check for joystick action
            if abs(self.joystick_y.value - CENTER) > DEADZONE:  # If the joystick is out of the dead zone
                if time.time() - self.last_joystick_input >= self.input_delay:  # Only if enough time has passed since the last input
                    self.last_joystick_input = time.time()  # Update the time of the last input
                    if abs(last_non_center_y - self.joystick_y.value) > THRESHOLD:  # Threshold to filter minor movements
                        if self.joystick_y.value > last_non_center_y:  # If the joystick is moved up
                            if self.is_menu_open:
                                self.variables[self.selected_dropdown].set(self.OPTIONS[(self.OPTIONS.index(self.variables[self.selected_dropdown].get()) - 1) % len(self.OPTIONS)])
                            else:
                                self.selected_dropdown = (self.selected_dropdown - 1) % 7
                        elif self.joystick_y.value < last_non_center_y:  # If the joystick is moved down
                            if self.is_menu_open:
                                self.variables[self.selected_dropdown].set(self.OPTIONS[(self.OPTIONS.index(self.variables[self.selected_dropdown].get()) + 1) % len(self.OPTIONS)])
                            else:
                                self.selected_dropdown = (self.selected_dropdown + 1) % 7
                        last_non_center_y = self.joystick_y.value  # Update the last non-center y position
            self.root.update()                        
            self.update_labels() 
            # Here you should read the button state, if button is pressed:
            if GPIO.input(self.button_pin) == GPIO.LOW: #on/off button
                if self.selected_dropdown == 6:  # Confirm button is selected
                    self.is_configuration_confirmed = True
                    self.confirm_configuration()
                    break
                elif self.is_menu_open:
                    selected_option = self.variables[self.selected_dropdown].get()
                    print(f"Selected option for dropdown {self.selected_dropdown + 1}: {selected_option}")
                    self.variables[self.selected_dropdown].set(selected_option)
                    self.is_menu_open = False
                    self.drop_downs[self.selected_dropdown].clear()
                else:
                    self.is_menu_open = True
                    self.drop_downs[self.selected_dropdown].drop_down()



            time.sleep(0.1)
            
if __name__ == '__main__':
    img = Image.open("/home/pi/Documents/thesis/Controller.jpeg") 
    functions = ['GaitInc','MovSpeed', 'GaitDec','Func1','CamSpeed','Func2']
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D5)
    app = Settings(functions,img)
    app.run()
