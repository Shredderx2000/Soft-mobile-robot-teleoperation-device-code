import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from time import sleep
# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
x_channel = AnalogIn(mcp, MCP.P0)
y_channel = AnalogIn(mcp, MCP.P1)

alpha = 0.2 #smoothing factor

x_filtered = 0.0
y_filtered = 0.0
while True:
    x_value = x_channel.value
    y_value = y_channel.value
    
    #converts to range between -1 and 1
    x_scaled = ((x_value - 32767)/32767.0)
    y_scaled = ((y_value - 32767)/32767.0)
    
    x_filtered = (1-alpha)*x_filtered+alpha * x_scaled
    y_filtered = (1-alpha)*y_filtered+alpha * y_scaled
    
    print("x value:",x_filtered)
    print("y value:",y_filtered)
    sleep(.1)

