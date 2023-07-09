import cv2
import socket
import threading
import numpy as np
import queue
import time
#,machine,data_queue
class Application:
    def __init__(self,machine,data_queue, ip='0.0.0.0', port=12345,):
        self.data_queue = data_queue
        self.host = 'localhost'
        self.p = 10000
        self.s = socket.socket()
        self.s.bind((ip, port))
        self.s.listen(2)
        self.s.settimeout(1)  # Set a timeout of 1 second
        self.connected = False
        self.clientsocket = None
        self.addr = None
        self.frame = None
        self.lock = threading.Lock()
        self.message_queue = queue.Queue() # Initialize the message queue
        self.display_time = 1 # Time for each message to display, in seconds
        self.last_display_time = 0 # Time the last message started displaying
        self.current_message = None # Current message being displayed
        self.on_state_event = machine.on_state_event

        self.is_video_window_open = False
    def attempt_connection(self):
        if not self.connected:
            try:
                self.clientsocket, self.addr = self.s.accept()
                print('Connected by', self.addr)
                self.connected = True
            except socket.timeout:
                pass
                print('No connection, retrying...')

    def recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def update_image(self):
        if self.connected:
            length = self.recvall(self.clientsocket, 16)
            stringData = self.recvall(self.clientsocket, int(length))
            nparr = np.frombuffer(stringData, np.uint8)
            self.frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            pass

    def run(self):
        self.on_state_event.wait() 
        while True:
            
            self.attempt_connection()
            self.update_image()

            with self.lock:
                if self.frame is not None:
                    frame_copy = self.frame.copy()
                else:
                    frame_copy = np.zeros((480, 640, 3), np.uint8)

            # If it's time for a new message, get one from the queue
            if (time.time() - self.last_display_time > self.display_time or
                    self.current_message is None):
                try:
                    if not self.data_queue.empty():
                        self.current_message = self.data_queue.get(block=False)
                    self.last_display_time = time.time()
                except queue.Empty:
                    self.current_message = None

            # If there is a message to display, add it to the frame
            if self.current_message is not None:
                cv2.putText(frame_copy, self.current_message, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 2, cv2.LINE_AA)
                

            # If we're in the "on" state and video window is not open, display the video
            if self.on_state_event.is_set() and not self.is_video_window_open:
                cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
                self.is_video_window_open = True

            # If we're not in the "on" state
            elif not self.on_state_event.is_set(): 
                cv2.destroyWindow('Video')
                cv2.destroyAllWindows()
                self.clientsocket.close()
                self.s.close()
                self.is_video_window_open = False

            # If video window is open, show frame
            if self.is_video_window_open:
                cv2.imshow('Video', frame_copy)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            

        cv2.destroyAllWindows()
        self.clientsocket.close()
        self.s.close()
    # Add messages to the queue with this method
#     def add_message(self,self.message_queue):
# #         message = machine.message
#         self.message_queue.put(self)

if __name__ == '__main__':
    app = Application()
    thread = threading.Thread(target=app.run)
    thread.start()
    thread.join()
