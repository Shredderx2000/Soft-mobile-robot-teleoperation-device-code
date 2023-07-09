import socket
import tkinter as tk
import io
from PIL import Image, ImageTk

class Application:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.root = tk.Tk()
        self.lbl = tk.Label(self.root)
        self.lbl.pack()
        self.s = socket.socket()
        self.s.bind((ip, port))
        self.s.listen(5)
        self.s.settimeout(1)  # Set a timeout of .1 second
        self.connected = False
        self.clientsocket = None
        self.addr = None
        
    def attempt_connection(self):
        if not self.connected:
            try:
                self.clientsocket, self.addr = self.s.accept()
                print('Connected by', self.addr)
                self.connected = True
            except socket.timeout:
                print('No connection, retrying...')
                
    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def update_image(self):
        if self.connected:
            length = self.recvall(self.clientsocket, 16)
            stringData = self.recvall(self.clientsocket, int(length))
            image = Image.open(io.BytesIO(stringData))
            photo = ImageTk.PhotoImage(image)
            self.lbl.config(image=photo)
            self.lbl.image = photo
    def step(self):
        # Run a single step of the Tkinter event loop
        self.root.update()
        
    def run(self):
        while True:
            self.attempt_connection()
            self.update_image()
            self.root.update_idletasks()
            self.root.update()

# app = Application()
# app.run()
