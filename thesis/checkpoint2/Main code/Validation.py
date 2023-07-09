import spidev
import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import digitalio
def check_spi_connection(self,channel):
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D5)
    mcp = MCP.MCP3008(spi, cs)
    Analog = AnalogIn(mcp, channel)

    adc_value = Analog.value
    print(f'Channel {channel}: ADC value: {adc_value}')

    # Check the ADC value based on your requirements
    if adc_value > 1000:
        print(f'Channel {channel} is working')
        self.write_to_file(f'Joystick status - Channel {channel}: Working')
        return True
    else:
        self.write_to_file(f'Joystick status - Channel {channel}: Not working')
        return False
   
def check_button(self, io_pin, duration=1):
    start_time = time.time()
    while time.time() - start_time < duration:
        if GPIO.input(io_pin) == GPIO.LOW:
            print(f'Button on IO {io_pin} is stuck pressed')
            self.write_to_file(f'Button status - IO {io_pin}: Stuck pressed')
            return
        time.sleep(0.1)

    print(f'Button on IO {io_pin} is functioning properly')
    self.write_to_file(f'Button status - IO {io_pin}: Functioning properly')

    
if __name__ == "__main__":
#     check_button(26,1)  # replace 18 with your GPIO pin number
    if check_spi_connection(3):  # Replace with your channel
        print("Joystick is connected")
    else:
        print("Joystick is not connected or not responding")
