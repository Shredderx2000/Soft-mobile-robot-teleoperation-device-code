# import socket
# 
# # Set up the socket
# s = socket.socket()
# 
# # Set the IP of the Raspberry Pi and port
# ip = '0.0.0.0' # This will listen on all available interfaces
# port = 12345
# 
# # Bind to the IP and port
# s.bind((ip, port))
# 
# # Start listening for connections
# s.listen(5)
# 
# while True:
#     # Accept a connection
#     c, addr = s.accept()
# 
#     # Print a message when connected
#     print('Got connection from', addr)
# 
#     # Receive a message from the client
#     message = c.recv(1024)
#     print('Received: ', message.decode())
# 
#     # Close the connection
#     c.close()
# import socket
# from PIL import Image
# 
# def receive_file(filename, ip, port):
#     with socket.socket() as s:
#         s.bind((ip, port))
#         s.listen(5)
#         while True:
#             conn, addr = s.accept()
#             with conn:
#                 print('Connected by', addr)
#                 with open(filename, 'wb') as f:
#                     while True:
#                         data = conn.recv(1024)
#                         if not data:
#                             break
#                         f.write(data)
#                 print('Received file')
# 
#             # Open and display the image after receiving
#             img = Image.open(filename)
#             img.show()
# 
# # Provide the filename, Raspberry Pi IP and port
# import socket
# from PIL import Image
# import io
# 
# # Set the IP of the Raspberry Pi and port
# ip = '0.0.0.0'
# port = 12345
# 
# # Set up the socket
# s = socket.socket()
# 
# # Bind to the IP and port
# s.bind((ip, port))
# 
# # Start listening for connections
# s.listen(5)
# 
# # A helper function to receive the data in chunks
# def recvall(sock, count):
#     buf = b''
#     while count:
#         newbuf = sock.recv(count)
#         if not newbuf: return None
#         buf += newbuf
#         count -= len(newbuf)
#     return buf
# 
# while True:
#     # Accept a connection
#     clientsocket, addr = s.accept()
# 
#     # Receive the data in small chunks
#     while True:
#         length = recvall(clientsocket,16)
#         stringData = recvall(clientsocket, int(length))
# 
#         # Open the image data as a stream and display it
#         image = Image.open(io.BytesIO(stringData))
#         image.show()
# receive_file('received_picture.jpg', '0.0.0.0', 12345)

#works
# import socket
# import tkinter as tk
# from PIL import Image, ImageTk
# import io
# import threading
# 
# # Set the IP of the Raspberry Pi and port
# ip = '0.0.0.0'
# port = 12345
# 
# # Set up the socket
# s = socket.socket()
# 
# # Bind to the IP and port
# s.bind((ip, port))
# 
# # Start listening for connections
# s.listen(5)
# 
# # Accept a connection
# clientsocket, addr = s.accept()
# print('Connected by', addr)
# 
# # A helper function to receive the data in chunks
# def recvall(sock, count):
#     buf = b''
#     while count:
#         newbuf = sock.recv(count)
#         if not newbuf: return None
#         buf += newbuf
#         count -= len(newbuf)
#     return buf
# 
# root = tk.Tk()
# lbl = tk.Label(root)
# lbl.pack()
# 
# # This function will update the label with new frames
# def update_image():
#     # Receive the data in small chunks
#     length = recvall(clientsocket, 16)
#     stringData = recvall(clientsocket, int(length))
# 
#     # Open the image data as a stream and display it
#     image = Image.open(io.BytesIO(stringData))
#     photo = ImageTk.PhotoImage(image)
#     lbl.config(image=photo)
#     lbl.image = photo
# 
#     # Schedule the function to be called again after 10 milliseconds
#     root.after(10, update_image)
# 
# # Start the update process
# update_image()
# 
# # Start the Tkinter event loop
# root.mainloop()
import socket
import tkinter as tk
from PIL import Image, ImageTk
import io
import time

class Application:
    def __init__(self, ip='0.0.0.0', port=12345):
        self.root = tk.Tk()
        self.lbl = tk.Label(self.root)
        self.lbl.pack()
        self.s = socket.socket()
        self.s.bind((ip, port))
        self.s.listen(5)
        try:
            self.clientsocket, self.addr = self.s.accept()
            print('Connected by', self.addr)
            self.connected = True
        except socket.error:
            print('No connection')
            self.connected = False

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def start(self):
        if self.connected:
            self.update_image()

    def step(self):
        # Run a single step of the Tkinter event loop
        self.root.update()

    def update_image(self):
        if self.connected:
            length = self.recvall(self.clientsocket, 16)
            stringData = self.recvall(self.clientsocket, int(length))
            image = Image.open(io.BytesIO(stringData))
            photo = ImageTk.PhotoImage(image)
            self.lbl.config(image=photo)
            self.lbl.image = photo
            self.start()

    def stop(self):
        if self.connected:
            self.clientsocket.close()
        self.root.quit()
class Controller:
    def __init__(self):
        self.state = 'idle'
        self.app = Application()

    def run(self):
        while True:
            if self.state == 'idle':
                self.idle()
            elif self.state == 'video':
                self.video()
            elif self.state == 'stop':
                self.stop()
            time.sleep(0.1)  # Prevent busy looping

    def idle(self):
        print('State: Idle')
        self.state = 'video'
        #threading.Thread(target=self.app.start, args=()).start()

    def video(self):
        print('State: Video')
        # You can add your code here
        time.sleep(10)  # Stay in this state for 10 seconds for testing purposes
        self.state = 'stop'

    def stop(self):
        print('State: Stop')
        self.app.stop()
        self.state = 'exit'


if __name__ == "__main__":
    c = Controller()
    c.run()
