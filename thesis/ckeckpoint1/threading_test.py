import threading
from test_data_sending import DataSender  # Assuming the DataSender class is in data_sender.py
from video_capturing import Application  # Assuming the CameraFeedReceiver class is in camera_feed_receiver.py

# Create instances of your classes
data_sender = DataSender()
camera_feed_receiver = Application()

# Create threads for each class
camera_feed_receiver_thread = threading.Thread(target=camera_feed_receiver.run)
data_sender_thread = threading.Thread(target=data_sender.start_sending)


# Start the threads
camera_feed_receiver_thread.start()
data_sender_thread.start()


# Wait for both threads to complete
data_sender_thread.join()
camera_feed_receiver_thread.join()