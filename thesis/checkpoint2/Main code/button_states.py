from Validation import check_spi_connection, check_button
import RPi.GPIO as GPIO
import time
import busio
import digitalio
import board
import adafruit_ssd1306
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import video_capturing
class State:
    def enter(self):
        pass
    
    def run(self):
        pass
    
    def exit(self):
        pass
    
class OffState(State):
    def enter(self):
        print("system is off")
        self.OLED_on = False
        self.gait_state = GaitState(3)  # You can set the total number of gaits here.
        self.gait_num = 1
        self.function1_state = func1_OffState()  # Initialize function1_state
        self.function2_state = func2_OffState()
        self.bot_speed = 100
        self.cam_speed = 100
        
        self.gait_inc_button_pin = 19 #increases gait
        self.gait_dec_button_pin = 6 #dec gait
        self.joystick_button_pin = 21 
        self.cam_joystick_button_pin = 20 
        self.function_button1_pin = 16 
        self.function_button2_pin = 12 
        self.led_pin = 13 #led to notify if controller is
        self.button_ios = [ 19,6,21,20,16,12,26 ]  # Fill this with your button IO's
        self.spi_channels = [0,1,2,3 ]  # Fill this with your SPI channels        
        # Initialize all buttons         

        GPIO.setup(self.gait_inc_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.gait_dec_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.joystick_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.cam_joystick_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.function_button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.function_button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.led_pin,GPIO.OUT)
        GPIO.output(self.led_pin,GPIO.LOW)
        
        print("Running system check:")
#         app.add_message("Running system check:")
        try:
            #setup OLED
            self.i2c = board.I2C()
            self.disp = adafruit_ssd1306.SSD1306_I2C(128,64,self.i2c)
            self.disp.fill(0)
            self.disp.show()
            self.width = self.disp.width
            self.height = self.disp.height
            self.image = PIL.Image.new("1", (self.width,self.height))
            self.draw = PIL.ImageDraw.Draw(self.image)
            self.font = PIL.ImageFont.load_default()
            self.OLED_on = True
        except ValueError as e:
            print(f"Caught an error: {e}")
            print("No OLED display found at expected address, please check the connection.")
#             app.add_message("No OLED display found at expected address, please check the connection.") 
        for self.button_io in self.button_ios:
            check_button(self,self.button_io)
            
        for self.spi_channel in self.spi_channels:
            check_spi_connection(self,self.spi_channel)
        print("system check complete")
#         app.add_message("system check complete")        
    def run(self):
        pass   
    def exit(self):
        pass
    def write_to_file(self, message):
        with open("controller_status.txt", "a") as file:
            file.write(message + '\n')
            print("Message written to file.")
class OnState(State):
    def enter(self):
        self.OLED_on = False
        self.gait_state = GaitState(3)  # You can set the total number of gaits here.
        self.gait_num = 1
        self.func1_state = 0
        self.func2_state = 0
        self.function1_state = func1_OffState()  # Initialize function1_state
        self.function2_state = func2_OffState()
        self.bot_speed = 100
        self.cam_speed = 100

        button_config = {}
        with open("button_configuration.txt", "r") as file:
            for line in file:
                if "Dropdown" in line:
                    dropdown_info = line.strip().split(":")
                    dropdown_num = int(dropdown_info[0].split()[-1])
                    function_name = dropdown_info[1].strip()
                    button_config[function_name] = dropdown_num

        # Map dropdown numbers to pin numbers
        dropdown_pin_mapping = {
            1: 19,
            2: 6,
            3: 21,
            4: 20,
            5: 16,
            6: 12,
        }

        # Set up GPIO mode and initialize all buttons
        GPIO.setmode(GPIO.BCM)
        for function_name, dropdown_num in button_config.items():
            if dropdown_num in dropdown_pin_mapping:
                button_pin = dropdown_pin_mapping[dropdown_num]
                GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.led_pin = 13  # led to notify if controller is on
        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.output(self.led_pin, GPIO.LOW)

    def run(self):
        dropdown_pin_mapping = {
            1: 19,
            2: 6,
            3: 21,
            4: 20,
            5: 16,
            6: 12,
        }

        button_config = {}
        with open("button_configuration.txt", "r") as file:
            for line in file:
                if "Dropdown" in line:
                    dropdown_info = line.strip().split(":")
                    dropdown_num = int(dropdown_info[0].split()[-1])
                    function_name = dropdown_info[1].strip()
                    button_config[function_name] = dropdown_num

        for function_name, dropdown_num in button_config.items():
            if GPIO.input(dropdown_pin_mapping[dropdown_num]) == GPIO.LOW:
                if function_name == 'GaitInc':
                    self.gait_state.increment()
                    self.gait_num = self.gait_state.current_gait
                    
                elif function_name == 'GaitDec':
                    self.gait_state.decrement()
                    self.gait_num = self.gait_state.current_gait
                elif function_name == 'MovSpeed':
                    self.bot_speed = self.bot_speed - 25
                    if self.bot_speed == 0:
                        self.bot_speed = 100
                elif function_name == 'CamSpeed':
                    self.cam_speed = self.cam_speed - 25
                    if self.cam_speed == 0:
                        self.cam_speed = 100
                elif function_name == 'Func1':
                    if isinstance(self.function1_state, func1_OffState):
                        self.function1_state = func1_OnState()
                        self.function1_state.enter()
                        self.func1_state = 1
                    elif isinstance(self.function1_state, func1_OnState):
                        self.function1_state = func1_OffState()
                        self.function1_state.enter()
                        self.func1_state = 0
                elif function_name == 'Func2':
                    if isinstance(self.function2_state, func2_OffState):
                        self.function2_state = func2_OnState()
                        self.function2_state.enter()
                        self.func2_state = 1
                    elif isinstance(self.function2_state, func2_OnState):
                        self.function2_state = func2_OffState()
                        self.function2_state.enter()
                        self.func2_state = 0
            return self.cam_speed, self.bot_speed, self.gait_num, self.func1_state, self.func2_state                  
#             #update OLED
#             self.draw.rectangle((0,0,self.width,self.height), outline=0,fill=0)
#             self.draw.text((0,0), "Gait:{}".format(self.gait_num),font=self.font, fill=255)
#             self.draw.text((0,15), "bot speed:{}".format(self.bot_speed),font=self.font, fill=255)
#             self.draw.text((0,30), "cam speed:{}".format(self.cam_speed),font=self.font, fill=255)
#             self.disp.image(self.image)
#             self.disp.show()
#         else:
#             pass        
#             
    def exit(self):
        pass

class GaitState(State):
    def __init__(self,machine, num_gaits=3, current_gait=1):
        self.num_gaits = num_gaits
        self.current_gait = current_gait
        self.machine = machine
    
    def enter(self):
        print(f"Gait state {self.current_gait}")
#         self.machine.message = f"Gait state {self.current_gait}"        
    def run(self):
        pass	
    
    def exit(self):
        pass
    
    def increment(self):
        self.current_gait += 1
        message = "increment pressed"
        #self.data_queue.put(message)
        if self.current_gait > self.num_gaits:
            self.current_gait = 1
        self.gait_state = GaitState(self.num_gaits, self.current_gait)
        self.gait_state.enter()
        
    def decrement(self):
        message = "decrement pressed"
        #self.data_queue.put(message)
        self.current_gait -= 1
        if self.current_gait < 1:
            self.current_gait = self.num_gaits
        self.gait_state = GaitState(self.num_gaits, self.current_gait)
        self.gait_state.enter()
            
class func1_OnState(State):
    def enter(self):
        print("function 1 on")
#         app.add_message("function 1 on")        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class func1_OffState(State):
    def enter(self):
        print("function 1 off")
#         app.add_message("function 1 off")        
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class func2_OnState(State):
    def enter(self):
        print("function 2 on")
#         app.add_message("function 2 on")        
    def run(self):
        pass
    
    def exit(self):
        pass
    
class func2_OffState(State):
    def enter(self):
        print("function 2 off")
#         app.add_message("function 2 off")        
    def run(self):
        pass
    
    def exit(self):
        pass
    
class ButtonStates:
    def __init__(self):
        self.gait_state = None
        self.function1_state = None
        self.function2_state = None
        self.gait_num = 1

    def reset(self):
        self.gait_state = GaitState1()
        self.function1_state = func1_OffState()
        self.function2_state = func2_OffState()