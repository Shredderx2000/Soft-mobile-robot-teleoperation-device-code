import threading
from data_recieving import DataReceiver 
from message_testing import CameraStreamer  

# Create instances of your classes
data_receiver = DataReceiver()
camera_streamer = CameraStreamer()

# Create threads for each class
data_receiver_thread = threading.Thread(target=data_receiver.start_server)
camera_streamer_thread = threading.Thread(target=camera_streamer.start_streaming)

# Start the threads
data_receiver_thread.start()
camera_streamer_thread.start()

# Wait for both threads to complete
data_receiver_thread.join()
camera_streamer_thread.join()