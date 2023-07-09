# import json
# import socket
# import time
# 
# class DataSender:
#     def __init__(self, ip='192.168.4.8', port=12346):
#         self.server_address = (ip, port)
#         self.sock = None
# 
#     def connect(self):
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.sock.connect(self.server_address)
# 
#     def send_data(self, data):
#         # Convert your data to a JSON string
#         data_json = json.dumps(data)
# 
#         # Then convert that string to bytes
#         data_bytes = data_json.encode('utf-8')
# 
#         # Now you can send it
#         self.sock.sendall(data_bytes)
# 
#     def close_connection(self):
#         if self.sock is not None:
#             self.sock.close()
#             self.sock = None
# 
# if __name__ == "__main__":
#     data_sender = DataSender()
#     data_sender.connect()
# 
#     while True:
#         # Put your joystick data here
#         data = {
#             'joystick_x': 1234,
#             'joystick_y': 5678,
#         }
#         data_sender.send_data(data)
# 
#         # Delay to keep the loop from running too fast
#         time.sleep(0.1)
# 
#     data_sender.close_connection()
# # 
import json
import socket
import time

class DataSender:
    def __init__(self, ip='192.168.4.8', port=12346):
        self.server_address = (ip, port)
        self.sock = None
        self.is_sending = True  # A flag to control the sending loop
        self.connected = False
    def connect(self):
        if not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(self.server_address)
                self.connected = True
            except Exception as e:
                print(f"Connection error: {e}. Retrying...")
                #time.sleep(3)

    def send_data(self, data):
        # Convert your data to a JSON string
        data_json = json.dumps(data)

        # Then convert that string to bytes
        data_bytes = data_json.encode('utf-8')

        # Now you can send it
        self.sock.sendall(data_bytes)

    def close_connection(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def start_sending(self):
        self.connect()

        while self.is_sending:
            # Put your joystick data here
            data = {
                'joystick_x': 1234,
                'joystick_y': 5678,
            }
            self.send_data(data)

            # Delay to keep the loop from running too fast
            #time.sleep(0.1)

        self.close_connection()

    def stop_sending(self):
        self.is_sending = False