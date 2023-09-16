import cv2

def main():
    # Load the video file
    video = cv2.VideoCapture(0)

    # Check if the video is opened successfully
    if not video.isOpened():
        print("Error: Could not open video.")
        return

    # Read the first frame
    ret, frame = video.read()

    # Select the initial bounding box using selectROI
    bbox = cv2.selectROI("Select Object", frame, fromCenter=False, showCrosshair=True)

    # Create a tracker object (choose a tracking algorithm)
    tracker = cv2.legacy.TrackerCSRT_create()

    # Initialize the tracker with the first frame and the initial bounding box
    ret = tracker.init(frame, bbox)

    # Process the video frames
    while True:
        # Read the next frame
        ret, frame = video.read()

        # Break the loop if we reached the end of the video
        if not ret:
            break

        # Update the tracker and get the new bounding box
        ret, bbox = tracker.update(frame)

        if ret:
            # Draw the bounding box on the frame
            x, y, w, h = map(int, bbox)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            # Display a message if tracking fails
            cv2.putText(frame, "Tracking failed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame with the tracked object
        cv2.imshow("Object Tracking", frame)

        # Exit if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the video and destroy all windows
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()