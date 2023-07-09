import cv2
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# Set up the GStreamer pipeline
gst_str = (
"appsrc name=mysource ! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency bitrate=500 ! rtph264pay ! udpsink host=192.168.4.1 port=5000"
)
pipeline = Gst.parse_launch(gst_str)

# Get the appsrc element
appsrc = pipeline.get_child_by_name("mysource")

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Open the camera using OpenCV
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Get the frame's bytes and create a GStreamer buffer from them
    frame_bytes = frame.tobytes()
    gst_buffer = Gst.Buffer.new_wrapped(frame_bytes)

    # Push the buffer into the pipeline
    appsrc.emit("push-buffer", gst_buffer)

# Clean up
cap.release()
pipeline.set_state(Gst.State.NULL)
