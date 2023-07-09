import RPi.GPIO as GPIO
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import adafruit_ssd1306
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import threading
import cv2
import socket
import threading
import numpy as np

import joystick_states
from button_states import GaitState,func1_OnState, func1_OffState, func2_OnState, func2_OffState, OffState, OnState
import video_capturing
#import joystick_calibration
from test_data_sending import DataSender
import socket
import json


class StateMachine:
    def __init__(self):
        self.button_pin = 26 #on/off button
        self.gait_inc_button_pin = 19 #increases gait
        self.gait_dec_button_pin = 6 #dec gait
        self.joystick_button_pin = 21 
        self.cam_joystick_button_pin = 20 
        self.function_button1_pin = 16 
        self.function_button2_pin = 12 
        self.led_pin = 13 #led to notify if controller is on
        self.spi = busio.SPI(clock=board.SCK, MISO = board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(board.D5)
        self.mcp = MCP.MCP3008(self.spi,self.cs)
        self.joystick_x = AnalogIn(self.mcp, MCP.P0)
        self.joystick_y = AnalogIn(self.mcp, MCP.P1)
        self.cam_joystick_x = AnalogIn(self.mcp, MCP.P2)
        self.cam_joystick_y = AnalogIn(self.mcp, MCP.P3)
        self.current_state = OffState()
        self.gait_state = GaitState(3)  # You can set the total number of gaits here.
        self.gait_num = 1
        self.function1_state = func1_OffState()  # Initialize function1_state
        self.function2_state = func2_OffState()
        
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


    def run(self):
        while True:
            if GPIO.input(self.button_pin) == GPIO.LOW: #on/off button
                if isinstance(self.current_state, OffState):
                    self.current_state = OnState()
                    self.current_state.enter()
                elif isinstance(self.current_state, OnState):
                    self.current_state = OffState()
                    self.current_state.enter()
                    
            elif GPIO.input(self.gait_inc_button_pin) == GPIO.LOW:  # inc gait button 
                if isinstance(self.current_state, OnState):
                    self.gait_state.increment(self)
                    self.gait_num = self.gait_state.current_gait

            elif GPIO.input(self.gait_dec_button_pin) == GPIO.LOW:  # dec gait button
                if isinstance(self.current_state, OnState):
                    self.gait_state.decrement(self)
                    self.gait_num = self.gait_state.current_gait
                    
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
                    if isinstance(self.function1_state, func1_OffState):
                        self.function1_state = func1_OnState()
                        self.function1_state.enter()
                    elif isinstance(self.function1_state, func1_OnState):
                        self.function1_state = func1_OffState()
                        self.function1_state.enter()
            elif GPIO.input(self.function_button2_pin) == GPIO.LOW: #function2 button
                if isinstance(self.current_state, OnState):
                    if isinstance(self.function2_state, func2_OffState):
                        self.function2_state = func2_OnState()
                        self.function2_state.enter()
                    elif isinstance(self.function2_state, func2_OnState):
                        self.function2_state = func2_OffState()
                        self.function2_state.enter()
#             self.app.attempt_connection()
#             self.app.update_image()
#             self.app.step()  # Update UI
#             self.app.root.update()
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
                    machine.current_state.direction_state = joystick_states.NeutralState()
                    machine.current_state.direction_state.enter()
                elif joystick_x_val > 60000 and joystick_y_val <1000:
                    machine.current_state.direction_state = joystick_states.EastState()
                    machine.current_state.direction_state.enter()
                elif joystick_x_val < 500 and joystick_y_val <1000:
                    machine.current_state.direction_state = joystick_states.WestState()
                    machine.current_state.direction_state.enter()
                elif joystick_y_val > 60000 and joystick_x_val <1000:
                    machine.current_state.direction_state = joystick_states.SouthState()
                    machine.current_state.direction_state.enter()
                elif joystick_y_val < 500 and joystick_x_val <1000:
                    machine.current_state.direction_state = joystick_states.NorthState()
                    machine.current_state.direction_state.enter()
            else:
                pass
            #updating joystick direction
            cam_joystick_x_val = self.cam_joystick_x.value
            cam_joystick_y_val = self.cam_joystick_y.value
            
            if isinstance(self.current_state, OnState):            
                if cam_joystick_x_val < 52000 and cam_joystick_y_val <52000:
                    machine.current_state.cam_direction_state = joystick_states.cam_NeutralState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_x_val > 60000 and cam_joystick_y_val <1000:
                    machine.current_state.cam_direction_state = joystick_states.cam_EastState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_x_val < 500 and cam_joystick_y_val <1000:
                    machine.current_state.cam_direction_state = joystick_states.cam_WestState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_y_val > 60000 and cam_joystick_x_val <1000:
                    machine.current_state.cam_direction_state = joystick_states.cam_SouthState()
                    machine.current_state.cam_direction_state.enter()
                elif cam_joystick_y_val < 500 and cam_joystick_x_val <1000:
                    machine.current_state.cam_direction_state = joystick_states.cam_NorthState()
                    machine.current_state.cam_direction_state.enter()
            else:
                pass
            #print("x value:",joystick_x_val)
            #print("y value:",joystick_y_val)
            #data sending
            data_sender = DataSender()  # Initialize DataSender with default IP and port
            data_sender.connect()  # Connect to the server 

            data = joystick_x_val  # Replace this with your actual data gathering code
            if data_sender.connected:
                data_sender.send_data(data)  # Send the data
                data_sender.close_connection()  # Close the connection                
#             time.sleep(0.1)                
            self.current_state.run(self)

if __name__ == '__main__':
    print("running")
    app = video_capturing.Application()    
    machine = StateMachine()


    machine_thread = threading.Thread(target=machine.run)
    app_thread = threading.Thread(target=app.run)

    machine_thread.start()
    app_thread.start()

    machine_thread.join()
    app_thread.join()
    