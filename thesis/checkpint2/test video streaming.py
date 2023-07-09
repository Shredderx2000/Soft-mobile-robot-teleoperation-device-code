import cv2

def stream_video():
    cap = cv2.VideoCapture('/dev/video0')

    # Check if the camera was successfully opened
    if not cap.isOpened():
        print("Failed to open the camera")
        return

    # Set the video resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Create a video writer to stream video to v4l2loopback
    writer = cv2.VideoWriter('/dev/video1', cv2.CAP_V4L2, 0, (640, 480))

    # Read and stream frames from the camera until the user interrupts
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Check if the frame was successfully read
        if not ret:
            print("Failed to read a frame from the camera")
            break

        # Write the frame to the video writer
        writer.write(frame)

        # Display the frame
        cv2.imshow('Video Stream', frame)

        # Check for user interrupt (press 'q' to quit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the resources
    cap.release()
    writer.release()
    cv2.destroyAllWindows()

# Call the stream_video() function to start streaming
stream_video()
