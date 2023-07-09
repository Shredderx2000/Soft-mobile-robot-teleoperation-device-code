import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

pipeline_description = "appsrc name=mysource ! videoconvert ! x264enc speed-preset=ultrafast tune=zerolatency bitrate=500 ! rtph264pay ! udpsink host=192.168.4.1 port=5000"

try:
    pipeline = Gst.parse_launch(pipeline_description)
except GLib.Error as e:
    print("Error creating pipeline: ", e.message)
    pipeline = None

if pipeline is None:
    print("Failed to create pipeline")
else:
    appsrc = pipeline.get_by_name("mysource")
    if appsrc is None:
        print("Failed to get appsrc")
    else:
        print("Got appsrc successfully")
