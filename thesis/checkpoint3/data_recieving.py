import socket
import json

class DataReceiver:
    def __init__(self, ip='192.168.4.6', port=12346):
        self.server_address = (ip, port)
        self.matlab_address = ('192.168.4.6', 3333)
        self.sock = None
        self.matsock = None
        self.connected = False
        

    def start_server(self):
#         if self.connected:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.matsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             if self.connected:
#                 self.sock.bind(self.server_address)
#                 self.sock.listen(1)
#             else:
        DataReceiver.receive_data(self)
        
    def receive_data(self):
        if not self.connected:
            print("Waiting for a connection")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(self.server_address)
            self.matsock.bind(self.matlab_address)
            
            self.sock.listen(1)
            print("pi connected")
            msg_m, address_m = self.matsock.recvfrom(1024)
            print("matlab connected")

            self.connected = True
            #print("Connection from", client_address)
            print("Connection from Matlab", address_m)
        try:
            while True:
                connection, client_address = self.sock.accept()
                
                data = connection.recv(1024)
                if data:
                    # Convert bytes to string
                    data_str = data.decode('utf-8')
                    print(data_str)
                    self.matsock.sendto(data, address_m)
                    # Convert string to JSON (Python dict)
                    #data_json = json.loads(data_str)

                    #print("Received:", data_json)
                else:
                    self.connected = False
                    break
        finally:
            #self.connected = False
            pass
#                  connection.close()
    def close_server(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

if __name__ == "__main__":
    data_receiver = DataReceiver()
    #data_receiver.start_server()

    while True:
        data_receiver.start_server()
    data_receiver.close_server()
# import socket
# 
# class DataReceiver:
#     def __init__(self, host='localhost', port=12346):
#         self.host = host
#         self.port = port
# 
#     def start_receiving(self):
#         while True:
#             try:
#                 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#                     s.bind((self.host, self.port))
#                     s.listen()
#                     conn, addr = s.accept()
#                     with conn:
#                         print('Connected by', addr)
#                         while True:
#                             data = conn.recv(1024)
#                             if not data:
#                                 break
#                             print('Received data:', data)
#             except Exception as e:
#                 print(f"Connection error: {e}. Retrying...")
#                 time.sleep(5)  # Wait a bit before retrying