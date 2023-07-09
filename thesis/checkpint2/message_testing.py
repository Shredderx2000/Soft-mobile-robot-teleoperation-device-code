#works
# import socket
# 
# # Set up the socket
# s = socket.socket()
# 
# # Set the IP of the Raspberry Pi and port
# ip = '192.168.4.1' # Replace this with your Raspberry Pi's IP
# port = 12345
# 
# # Connect to the Raspberry Pi
# s.connect((ip, port))
# 
# # Send a message
# s.send(b'Hello, Raspberry Pi!')
# 
# # Close the socket
# s.close()


#works
# import socket
# 
# def send_file(filename, ip, port):
#     with socket.socket() as s:
#         s.connect((ip, port))
#         with open(filename, 'rb') as f:
#             while True:
#                 bytes_read = f.read(1024)
#                 if not bytes_read:
#                     # File transmitting is done
#                     break
#                 s.sendall(bytes_read)
# 
# # Provide the filename, Raspberry Pi IP and port
# send_file('tree.jpg', '192.168.4.1', 12345)
import time
import socket
import cv2
import numpy as np

class CameraStreamer:
    def __init__(self, ip='192.168.4.1', port=12345):
        self.server_address = (ip, port)
        self.sock = None
        self.cap = cv2.VideoCapture('/dev/video0')

        if not self.cap.isOpened():
            raise Exception("Failed to open the camera")
        
    def start_streaming(self):
        while True:
            try:
                self.sock = socket.socket()
                # Connect to the Raspberry Pi
                self.sock.connect(self.server_address)
                
                while self.cap.isOpened():
                    # Capture frame-by-frame
                    ret, frame = self.cap.read()

                    # If the frame was captured correctly
                    if ret == True:
                        # Lower the resolution
#                         frame = cv2.resize(frame, (320, 240))

                        # Convert the frame to grayscale
#                         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                        result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                        
                        # Convert the frame to bytes and send
                        data = np.array(frame)
                        string_data = data.tobytes()

                        self.sock.sendall((str(len(string_data))).encode().ljust(16) + string_data)
                break  # If the capture isn't open, break out of the outer while loop
            except Exception as e:
                print(f"Connection error: {e}. Retrying...")
                time.sleep(5)  # Wait a bit before retrying
            
    def stop_streaming(self):
        self.cap.release()
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    streamer = CameraStreamer()
    streamer.start_streaming()