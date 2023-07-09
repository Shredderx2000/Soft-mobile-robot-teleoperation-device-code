import cv2
import socket
import struct
import pickle

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.4.1', 8000))  # replace with the IP of your Raspberry Pi

camera = cv2.VideoCapture(0)  # 0 stands for the first webcam on your system. Modify if needed.
payload_size = struct.calcsize("Q")

while True:
    ret, frame = camera.read()
    if not ret:
        break
    data = pickle.dumps(frame)
    message_size = struct.pack("Q", len(data))
    client_socket.sendall(message_size + data)
    print(data)
camera.release()
client_socket.close()
