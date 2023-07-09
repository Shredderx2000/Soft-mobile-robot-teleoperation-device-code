#modules
import RPi.GPIO as GPIO
import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import cv2
import socket
import threading
from threading import Event
import numpy as np
import json
import sys
#import files
from Validation import check_spi_connection, check_button
import joystick_states
from button_states import GaitState,func1_OnState, func1_OffState, func2_OnState, func2_OffState, OffState, OnState
import video_capturing
#import joystick_calibration
from test_data_sending import DataSender
import queue
from wifi_str_testing import check_rx_bitrate


class StateMachine:
    def __init__(self,data_queue):
        print("initilizing")
        self.data_queue = data_queue        
        self.message = None
        self.host = "localhost"
        self.port = 10000
        self.connected = False

        self.on_state_event = Event()
        self.spi = busio.SPI(clock=board.SCK, MISO = board.MISO, MOSI=board.MOSI)
        self.cs = digitalio.DigitalInOut(board.D5)
        self.mcp = MCP.MCP3008(self.spi,self.cs)
        self.bitrate_flag = 0
        self.data_sender = DataSender()  # Initialize DataSender with default IP and port

        
        # Read the joystick configuration from the file
        joystick_config = {}
        with open("controller_status.txt", "r") as file:
                lines = file.readlines()[7:]  # Skip the first 7 lines
        working_channels = []  # List to hold the indices of working channels
        for line in lines:
            if "Joystick status" in line:
                joystick_info = line.strip().split(":")
                joystick_channel = int(joystick_info[0].split()[-1])
                joystick_status = joystick_info[1].strip()

                if joystick_status == "Working":
                    joystick_config[joystick_channel] = True
                    working_channels.append(joystick_channel)
                else:
                    joystick_config[joystick_channel] = False

                # Assign joystick controls based on the configuration
        if len(working_channels) < 4:
            if 0 in joystick_config and joystick_config[0]:
                self.joystick_x = AnalogIn(self.mcp, MCP.P0)
                self.cam_joystick_x = AnalogIn(self.mcp, MCP.P2)
            if 1 in joystick_config and joystick_config[1]:
                self.joystick_y = AnalogIn(self.mcp, MCP.P1)
                self.cam_joystick_y = AnalogIn(self.mcp, MCP.P3)
            if 2 in joystick_config and joystick_config[2]:
                self.cam_joystick_x = AnalogIn(self.mcp, MCP.P0)
                self.joystick_x = AnalogIn(self.mcp, MCP.P2)
            if 3 in joystick_config and joystick_config[3]:
                self.joystick_y = AnalogIn(self.mcp, MCP.P3)
                self.cam_joystick_y = AnalogIn(self.mcp, MCP.P1)
        else:
            self.joystick_x = AnalogIn(self.mcp, MCP.P0)            
            self.joystick_y = AnalogIn(self.mcp, MCP.P1)
            self.cam_joystick_x = AnalogIn(self.mcp, MCP.P2)
            self.cam_joystick_y = AnalogIn(self.mcp, MCP.P3)
        self.button_pin = 26 #on/off button 
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
 
        self.current_state = OnState()
        self.current_state.enter()        
        self.on_state_event.set()                  
        self.current_state.run()
        print("initilizing complete")
        
    def run(self):

        while True:
            if GPIO.input(self.button_pin) == GPIO.LOW: #on/off button
                self.on_state_event.clear()
                sys.exit(0)  # Exit the program with a success code                
            #run loop of on/off state
            cam_speed, bot_speed, gait_num, func1_state, func2_state  = self.current_state.run()                        
            #updating joystick direction
            joystick_x_val = self.joystick_x.value
            joystick_y_val = self.joystick_y.value
            
            if isinstance(self.current_state, OnState):            
                if (self.joystick_x.value < 52000 and self.joystick_x.value > 46000) and (self.joystick_y.value < 52000 and self.joystick_y.value > 46000):
                    self.current_state.direction_state = joystick_states.NeutralState()
                    self.current_state.direction_state.enter()
                elif self.joystick_x.value > 60000 and (self.joystick_y.value < 65000 and self. joystick_y.value > 46000):
                    self.current_state.direction_state = joystick_states.EastState()
                    self.current_state.direction_state.enter()
                elif self.joystick_x.value < 500 and(self.joystick_y.value < 52000 and self.joystick_y.value > 46000) :
                    self.current_state.direction_state = joystick_states.WestState()
                    self.current_state.direction_state.enter()
                elif self.joystick_y.value > 64000 and (self.joystick_x.value < 61000 and self.joystick_x.value > 55000):
                    self.current_state.direction_state = joystick_states.SouthState()
                    self.current_state.direction_state.enter()
                elif self.joystick_y.value < 1000 and (self.joystick_x.value < 52000 and self.joystick_x.value > 46000):
                    self.current_state.direction_state = joystick_states.NorthState()
                    self.current_state.direction_state.enter()
            else:
                pass

            #updating joystick direction
            cam_joystick_x_val = self.cam_joystick_x.value
            cam_joystick_y_val = self.cam_joystick_y.value
        
            if isinstance(self.current_state, OnState):            
                if cam_joystick_x_val < 52000 and cam_joystick_y_val < 52000:
                    self.current_state.cam_direction_state = joystick_states.cam_NeutralState()
                    self.current_state.cam_direction_state.enter()
                elif cam_joystick_x_val > 60000 and cam_joystick_y_val <1000:
                    self.current_state.cam_direction_state = joystick_states.cam_EastState()
                    self.current_state.cam_direction_state.enter()
                elif cam_joystick_x_val < 500 and cam_joystick_y_val <1000:
                    self.current_state.cam_direction_state = joystick_states.cam_WestState()
                    self.current_state.cam_direction_state.enter()
                elif cam_joystick_y_val > 60000 and cam_joystick_x_val <1000:
                    self.current_state.cam_direction_state = joystick_states.cam_SouthState()
                    self.current_state.cam_direction_state.enter()
                elif cam_joystick_y_val < 500 and cam_joystick_x_val <1000:
                    self.current_state.cam_direction_state = joystick_states.cam_NorthState()
                    self.current_state.cam_direction_state.enter()
            else:
                pass
            #testing data out
#             print("mov x value:",joystick_x_val)
#             print("mov y value:",joystick_y_val)
#             print("cam x value:",cam_joystick_x_val)
#             print("cam y value:",cam_joystick_y_val)
#             print("cam speed:", cam_speed)
#             print("bot speed:", bot_speed)
#             print("Gait:", gait_num)
#             print("Func1 state:", func1_state)
#             print("Func2 state:", func2_state)

            #data sending 

            self.bitrate = check_rx_bitrate()
            if self.bitrate is not None:
                if self.bitrate < 5.0:
                    self.bitrate_flag = 1
                    data = [joystick_x_val,joystick_y_val,cam_speed,0,self.bitrate_flag]  # Replace this with some default value
                    message = "Warning: poor connection detected!"
                    self.data_queue.put(message)
                else:
                    self.bitrate_flag = 0
                    data = [joystick_x_val, joystick_y_val,
                            cam_joystick_x_val, cam_joystick_y_val,
                            bot_speed, cam_speed, gait_num, func1_state, func2_state, self.bitrate_flag]  # Replace this with your actual data gathering code
                    print(data)


            else:
                pass
                #print("Error: Failed to retrieve RX bitrate.")
            self.data_sender.connect()
            if self.data_sender.connected:
                self.data_sender.send_data(data)  # Send the data
                self.data_sender.close_connection()
            else:
                self.data_sender.connect()


            
            #message for display
            if self.message is not None:
                self.data_queue.put(self.message)
                        
#             time.sleep(0.1)                

if __name__ == '__main__':
    print("running")
    # Create the shared queue
    data_queue = queue.Queue()
    
    machine = StateMachine(data_queue)
    app = video_capturing.Application(machine,data_queue)    

    app_thread = threading.Thread(target=app.run)
    machine_thread = threading.Thread(target=machine.run)
    
    app_thread.start()
    machine_thread.start()

    app_thread.join()
    machine_thread.join()


