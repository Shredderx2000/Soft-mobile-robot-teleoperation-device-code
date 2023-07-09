import socket
import tkinter as tk
from PIL import Image, ImageTk
import io

# Set the IP of the Raspberry Pi and port
ip = '0.0.0.0'
port = 12345

# Set up the socket
s = socket.socket()

# Bind to the IP and port
s.bind((ip, port))

# Start listening for connections
s.listen(5)

# Accept a connection
clientsocket, addr = s.accept()
print('Connected by', addr)

# A helper function to receive the data in chunks
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

root = tk.Tk()
lbl = tk.Label(root)
lbl.pack()

# This function will update the label with new frames
def update_image():
    # Receive the data in small chunks
    length = recvall(clientsocket, 16)
    stringData = recvall(clientsocket, int(length))

    # Open the image data as a stream and display it
    image = Image.open(io.BytesIO(stringData))
    photo = ImageTk.PhotoImage(image)
    lbl.config(image=photo)
    lbl.image = photo

    # Schedule the function to be called again after 10 milliseconds
    root.after(10, update_image)

# Start the update process
update_image()

# Start the Tkinter event loop
root.mainloop()
