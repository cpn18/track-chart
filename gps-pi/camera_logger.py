import cv2
from datetime import datetime
import time

def main(port, output_dir):
    # 0 opens the default built-in webcam. Use 1, 2, etc., for external USB cameras.
    cap = cv2.VideoCapture(1)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    image_dir = output_dir + "/images/"

    while True:
        next = time.time() + 1
        # Capture frame-by-frame
        # ret is a boolean (True if frame grabbed successfully), frame is the image array
        ret, frame = cap.read()
    
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting...")
            break

        #print(ret,frame)

        now = datetime.now()
        filename = now.strftime("%Y%m%d_%H%M%S") + ".png"

        cv2.imwrite(image_dir + filename, frame)

        obj = {
            "class": "CAMERA",
            "time": now.isoformat(),
            "filename": filename
        }
        print(obj)

        delay = next - time.time()
        if delay > 0:
            time.sleep(delay)

        #break

        ## Display the resulting frame in a window named 'Webcam Feed'
        #cv2.imshow('Webcam Feed', frame)

        ## Stop the loop if the 'q' key is pressed
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

    # Always release the capture and destroy windows when done to free up hardware
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(int(sys.argv[1]), sys.argv[2])

