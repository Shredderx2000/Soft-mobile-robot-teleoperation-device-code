import RPi.GPIO as GPIO
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_ssd1306
import board
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import socket
import tkinter as tk
from PIL import Image, ImageTk
import joystick_states
import button_states
class State:
    def enter(self):
        pass
    
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class OffState(State):
    def enter(self):
        print("system is off")
    
    def run(self,machine):
        pass
    
    def exit(self):
        pass
    
class OnState(State):
    def enter(self):
        print("system is on")
        GPIO.output(machine.led_pin, GPIO.HIGH)
        button_states.gait_state = GaitState1()
        self.direction_state = NeutralState()
        self.cam_direction_state = cam_NeutralState()
        button_states.function1_state = func1_OffState()
        button_states.function2_state = func2_OffState()
        button_states.gait_num = 1

    
    def run(self,machine):
        joystick_x_val = machine.joystick_x.value
        joystick_y_val = machine.joystick_y.value
        cam_joystick_x_val = machine.cam_joystick_x.value
        cam_joystick_y_val = machine.cam_joystick_y.value        
        #joystick state logic
        if joystick_x_val < 52000 and joystick_y_val <52000:
            machine.current_state.direction_state = NeutralState()
        elif joystick_x_val > 60000: #and joystick_y_val <1000:
            machine.current_state.direction_state = EastState()
        elif joystick_x_val < 500: #and joystick_y_val <1000:
            machine.current_state.direction_state = WestState()
        elif joystick_y_val > 60000: #and joystick_x_val <1000:
            machine.current_state.direction_state = SouthState()
        elif joystick_y_val < 500: #and joystick_x_val <1000:
            machine.current_state.direction_state = NorthState()
    
    def exit(self):
        GPIO.output(machine.led_pin, GPIO.LOW)
        
 

class Application:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.root = tk.Tk()
        self.lbl = tk.Label(self.root)
        self.lbl.pack()
        self.s = socket.socket()
        self.s.bind((ip, port))
        self.s.listen(5)
        self.s.settimeout(1)  # Set a timeout of 1 second
        try:
            self.clientsocket, self.addr = self.s.accept()
            print('Connected by', self.addr)
            self.connected = True
        except socket.timeout:
            print('No connection')
            self.connected = False
            
    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def start(self):
        if self.connected:
            self.update_image()

    def step(self):
        # Run a single step of the Tkinter event loop
        self.root.update()

    def update_image(self):
        if self.connected:
            length = self.recvall(self.clientsocket, 16)
            stringData = self.recvall(self.clientsocket, int(length))
            image = Image.open(io.BytesIO(stringData))
            photo = ImageTk.PhotoImage(image)
            self.lbl.config(image=photo)
            self.lbl.image = photo
            self.start()

    def stop(self):
        if self.connected:
            self.clientsocket.close()
        self.root.quit()        
class StateMachine:
    def __init__(self):
        self.button_pin = 26 #on/off button
        self.gait_inc_button_pin = 19 #increases gait
        self.gait_dec_button_pin = 6 #increases gait
        self.joystick_button_pin = 21 #increases gait
        self.cam_joystick_button_pin = 20 #increases gait
        self.function_button1_pin = 16 #increases gait
        self.function_button2_pin = 12 #increases gait
        self.led_pin = 13 #led to notify if controller is on
        self.spi = busio.SPI(clock=board.SCK, MISO = board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(board.D5)
        self.mcp = MCP.MCP3008(self.spi,self.cs)
        self.joystick_x = AnalogIn(self.mcp, MCP.P0)
        self.joystick_y = AnalogIn(self.mcp, MCP.P1)
        self.cam_joystick_x = AnalogIn(self.mcp, MCP.P2)
        self.cam_joystick_y = AnalogIn(self.mcp, MCP.P3)
        self.current_state = OffState()
        self.gait_num = 1
        
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
        
        # Initialize all buttons         
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.gait_inc_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.gait_dec_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.joystick_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.cam_joystick_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.function_button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.function_button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.led_pin,GPIO.OUT)
        GPIO.output(self.led_pin,GPIO.LOW)
        
        self.bot_speed = 100
        self.cam_speed = 100
        print("got to here")        
        self.app = Application()
        print("got to here")        
    def run(self):
        while True:
            if GPIO.input(self.button_pin) == GPIO.LOW: #on/off button
                if isinstance(self.current_state, OffState):
                    self.current_state = OnState()
                    self.current_state.enter()
                elif isinstance(self.current_state, OnState):
                    self.current_state = OffState()
                    self.current_state.enter()
                    
            elif GPIO.input(self.gait_inc_button_pin) == GPIO.LOW: #inc gait button 
                if isinstance(self.current_state, OnState):
                    self.current_state.gait_state.increment(self)
                    self.current_state.gait_state.enter()
                    self.gait_num = self.current_state.gait_num
            elif GPIO.input(self.gait_dec_button_pin) == GPIO.LOW: #dec gait button
                if isinstance(self.current_state, OnState):
                    self.current_state.gait_state.decrement(self)
                    self.current_state.gait_state.enter()
                    self.gait_num = self.current_state.gait_num
                    
            elif GPIO.input(self.joystick_button_pin) == GPIO.LOW: #joystick button
                if isinstance(self.current_state, OnState):
                    self.bot_speed = self.bot_speed-25
                    if self.bot_speed == 0:
                        self.bot_speed = 100                    
            elif GPIO.input(self.cam_joystick_button_pin) == GPIO.LOW: #cam joystick button
                if isinstance(self.current_state, OnState):
                    self.cam_speed = self.cam_speed-25
                    if self.cam_speed == 0:
                        self.cam_speed = 100
                        
            elif GPIO.input(self.function_button1_pin) == GPIO.LOW: #function1 button
                if isinstance(self.current_state, OnState):
                    if isinstance(self.current_state.function1_state, func1_OffState):
                        self.current_state.function1_state = func1_OnState()
                        self.current_state.function1_state.enter()
                    elif isinstance(self.current_state.function1_state, func1_OnState):
                        self.current_state.function1_state = func1_OffState()
                        self.current_state.function1_state.enter()
            elif GPIO.input(self.function_button2_pin) == GPIO.LOW: #function2 button
                if isinstance(self.current_state, OnState):
                    if isinstance(self.current_state.function2_state, func2_OffState):
                        self.current_state.function2_state = func2_OnState()
                        self.current_state.function2_state.enter()
                    elif isinstance(self.current_state.function2_state, func2_OnState):
                        self.current_state.function2_state = func2_OffState()
                        self.current_state.function2_state.enter()
            self.app.step()                   
            #update OLED
            self.draw.rectangle((0,0,self.width,self.height), outline=0,fill=0)
            self.draw.text((0,0), "Gait:{}".format(self.gait_num),font=self.font, fill=255)
            self.draw.text((0,15), "bot speed:{}".format(self.bot_speed),font=self.font, fill=255)
            self.draw.text((0,30), "cam speed:{}".format(self.cam_speed),font=self.font, fill=255)
            self.disp.image(self.image)
            self.disp.show()
            
            #powerLED
            if isinstance(self.current_state,OnState):
                GPIO.output(self.led_pin,GPIO.HIGH)
            else:
                GPIO.output(self.led_pin,GPIO.LOW)
                
            #updating joystick direction
            joystick_x_val = self.joystick_x.value
            joystick_y_val = self.joystick_y.value
            
            if isinstance(self.current_state, OnState):            
                if joystick_x_val < 52000 and joystick_y_val <52000:
                    machine.current_state.direction_state = NeutralState()
                    machine.current_state.direction_state.enter()
                elif joystick_x_val > 60000 and joystick_y_val <1000:
                    machine.current_state.direction_state = EastState()
                    machine.current_state.direction_state.enter()
                elif joystick_x_val < 500 and joystick_y_val <1000:
                    machine.current_state.direction_state = WestState()
                    machine.current_state.direction_state.enter()
                elif joystick_y_val > 60000 and joystick_x_val <1000:
                    machine.current_state.direction_state = SouthState()
                    machine.current_state.direction_state.enter()
                elif joystick_y_val < 500 and joystick_x_val <1000:
                    machine.current_state.direction_state = NorthState()
                    machine.current_state.direction_state.enter()
            else:
                pass
            #updating joystick direction
            cam_joystick_x_val = self.cam_joystick_x.value
            cam_joystick_y_val = self.cam_joystick_y.value
            
            if isinstance(self.current_state, OnState):            
                if cam_joystick_x_val < 52000 and cam_joystick_y_val <52000:
                    machine.current_state.cam_direction_state = cam_NeutralState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_x_val > 60000 and cam_joystick_y_val <1000:
                    machine.current_state.cam_direction_state = cam_EastState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_x_val < 500 and cam_joystick_y_val <1000:
                    machine.current_state.cam_direction_state = cam_WestState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_y_val > 60000 and cam_joystick_x_val <1000:
                    machine.current_state.cam_direction_state = cam_SouthState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_y_val < 500 and cam_joystick_x_val <1000:
                    machine.current_state.cam_direction_state = cam_NorthState()
                    machine.current_state.cam_direction_state.enter()
            else:
                pass
#             print("x value:",joystick_x_val)
#             print("y value:",joystick_y_val)            
                
            time.sleep(0.1)                
            self.current_state.run(self)            
            
if __name__ == '__main__':
    print("running")
    machine = StateMachine()
    machine.run()
 