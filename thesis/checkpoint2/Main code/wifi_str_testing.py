import subprocess
import time
# def get_connected_devices():
#     devices = []
#     try:
#         output = subprocess.check_output(['arp', '-a'])
#         lines = output.decode().split('\n')
#         for line in lines:
#             if ' (incomplete)' not in line:
#                 device_info = line.split(' ')
#                 if len(device_info) >= 2:
#                     ip_address = device_info[1].strip('()')
#                     mac_address = device_info[3]
#                     devices.append((ip_address, mac_address))
#     except subprocess.CalledProcessError:
#         pass
#     return devices
# 
# while True:
#     devices = get_connected_devices()
#     if devices:
#         print("Connected devices:")
#         for device in devices:
#             ip_address, mac_address = device
#             print(f"IP: {ip_address}, MAC: {mac_address}")
#     else:
#         print("No devices connected.")
# 
#     # Delay between each scan
#     time.sleep(5)
import subprocess

def check_rx_bitrate():
    command = "sudo iw dev wlan0 station dump"
    output = subprocess.check_output(command, shell=True, universal_newlines=True)
    lines = output.split("\n")
    
    for line in lines:
        if line.startswith("	rx bitrate:"):
            rx_bitrate = float(line.split()[2])  # Extract the bitrate value as a float
#             print(f"Current RX bitrate: {rx_bitrate} MBit/s")
            
            if rx_bitrate < 5:
                print("Warning: RX bitrate is below 5 MBit/s!")
    return rx_bitrate

if __name__ == "__main__":
    check_rx_bitrate()