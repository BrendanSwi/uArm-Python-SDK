import cv2

# GStreamer pipeline for NVIDIA Jetson Nano camera module
GSTREAMER_PIPELINE = (
    "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, "
    "format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, "
    "format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
)

cap = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow("Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
