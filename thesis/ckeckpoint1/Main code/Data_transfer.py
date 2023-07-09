
        
class DataSender:
    def __init__(self, ip='192.168.4.8', port=12346):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.connected = False

    def connect(self):
        try:
            self.sock.connect((self.ip, self.port))
            self.connected = True
        except Exception as e:
            print(f"Could not connect to {self.ip}:{self.port}. Reason: {str(e)}")

    def send_data(self, data):
        if self.connected:
            try:
                data_bytes = str(data).encode()  # Assumes data can be converted to string
                self.sock.sendall(data_bytes)
            except Exception as e:
                print(f"Could not send data. Reason: {str(e)}")

    def close_connection(self):
        if self.connected:
            try:
                self.sock.close()
                self.connected = False
            except Exception as e:
                print(f"Could not close connection. Reason: {str(e)}")
