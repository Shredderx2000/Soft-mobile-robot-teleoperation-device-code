import time
import busio
import board
import RPi.GPIO as GPIO
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import digitalio

class Joystick:
    def __init__(self, x_channel, y_channel, calibration_button_pin):
        self.x_channel = x_channel
        self.y_channel = y_channel
        self.calibration_button_pin = calibration_button_pin
        self.x_min = 1023
        self.x_max = 0
        self.y_min = 1023
        self.y_max = 0
        GPIO.setup(self.calibration_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read(self):
        x_value = self.x_channel.value
        y_value = self.y_channel.value
        self.x_min = min(self.x_min, x_value)
        self.x_max = max(self.x_max, x_value)
        self.y_min = min(self.y_min, y_value)
        self.y_max = max(self.y_max, y_value)
        return x_value, y_value

    def calibrate(self):
        print("Calibrating. Move joystick to full extents and press button when done...")
        while GPIO.input(self.calibration_button_pin) == GPIO.HIGH:
            self.read()
            time.sleep(0.01)
        print("Calibration complete.")
        print("X min:", self.x_min, "max:", self.x_max)
        print("Y min:", self.y_min, "max:", self.y_max)

    def get_normalized(self):
        x, y = self.read()
        x = (x - self.x_min) / (self.x_max - self.x_min) * 20 - 10
        y = (y - self.y_min) / (self.y_max - self.y_min) * 20 - 10
        return x, y

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D22)
mcp = MCP.MCP3008(spi, cs)

x_channel = AnalogIn(mcp, MCP.P0)  # Modify as needed
y_channel = AnalogIn(mcp, MCP.P1)  # Modify as needed

calibration_button_pin = 26  # Modify as needed

joystick = Joystick(x_channel, y_channel, calibration_button_pin)
joystick.calibrate()

while True:
    x, y = joystick.get_normalized()
    print("Normalized X:", x, " Y:", y)
    time.sleep(0.1)
