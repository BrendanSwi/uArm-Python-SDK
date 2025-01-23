import tkinter as tk
import cv2
import numpy as np
from PIL import Image, ImageTk

# Load Camera Calibration Data (for both cameras)
calibration_data = np.load('stereo_calibration_data.npz')  # Replace with your actual calibration file
camera_matrix_left = calibration_data['camera_matrix_left']
distortion_coefficients_left = calibration_data['distortion_coefficients_left']
camera_matrix_right = calibration_data['camera_matrix_right']
distortion_coefficients_right = calibration_data['distortion_coefficients_right']

# Stereo Calibration Parameters
R = calibration_data['R']  # Rotation matrix between cameras
T = calibration_data['T']  # Translation vector between cameras

# Extract Focal Lengths and Baseline
focal_length = camera_matrix_left[0,0]
baseline = np.linalg.norm(T)

# GStreamer pipeline for NVIDIA Jetson Nano camera modules
GSTREAMER_PIPELINE_LEFT = (
    "nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, "
    "format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, "
    "format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
)

GSTREAMER_PIPELINE_RIGHT = (
    "nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=(int)640, height=(int)480, "
    "format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, "
    "format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
)

# Initialize OpenCV Video Capture
cap_left = cv2.VideoCapture(GSTREAMER_PIPELINE_LEFT, cv2.CAP_GSTREAMER)
cap_right = cv2.VideoCapture(GSTREAMER_PIPELINE_RIGHT, cv2.CAP_GSTREAMER)

# Get the optimal new camera matrices
ret_left, frame_left = cap_left.read()
ret_right, frame_right = cap_right.read()

if ret_left and ret_right:
    h, w = frame_left.shape[:2]
    new_camera_matrix_left, roi_left = cv2.getOptimalNewCameraMatrix(
        camera_matrix_left, distortion_coefficients_left, (w, h), 1, (w, h)
    )
    new_camera_matrix_right, roi_right = cv2.getOptimalNewCameraMatrix(
        camera_matrix_right, distortion_coefficients_right, (w, h), 1, (w, h)
    )

def compute_depth_map(img_left, img_right):
    """Compute the disparity and depth map."""
    # StereoBM or StereoSGBM settings for disparity map calculation
    stereo = cv2.StereoSGBM_create(
        numDisparities=16 * 5,  # Must be divisible by 16
        blockSize=15,
        P1=8 * 3 * 15**2,
        P2=32 * 3 * 15**2,
        mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
    )
    disparity = stereo.compute(img_left, img_right).astype(np.float32) / 16.0
    return disparity

def compute_depth (disparity, focal_length, baseline):
    """"Compute the depth map from the disparity map"""
    disparity [disparity <= 0] = 0.1
    depth = (focal_length * baseline) / disparity

    return depth

def update_camera_feed():
    """Capture frames from both cameras and update the Tkinter Label with disparity map."""
    ret_left, frame_left = cap_left.read()
    ret_right, frame_right = cap_right.read()

    if ret_left and ret_right:
        # Undistort frames using calibration data
        undistorted_left = cv2.undistort (
            frame_left, camera_matrix_left, distortion_coefficients_left, None, new_camera_matrix_left
        )
        undistorted_right = cv2.undistort (
            frame_right, camera_matrix_right, distortion_coefficients_right, None, new_camera_matrix_right
        )

        # Crop based on ROI
        x_left, y_left, w_left, h_left = roi_left
        x_right, y_right, w_right, h_right = roi_right
        undistorted_left = undistorted_left[y_left:y_left + h_left, x_left:x_left + w_left]
        undistorted_right = undistorted_right[y_right:y_right + h_right, x_right:x_right + w_right]

        gray_left = cv2.cvtColor (undistorted_left, cv2.COLOR_BGR2GRAY)
        gray_right = cv2.cvtColor (undistorted_right, cv2.COLOR_BGR2GRAY)

        # Compute Disparity
        disparity = compute_depth_map (gray_left, gray_right)

        # Compute Depth
        depth_map = compute_depth (disparity, focal_length, baseline)

        # Normalize and Display Disparity for Visualization
        disparity_visual = cv2.normalize (disparity, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        disparity_image = Image.fromarray(disparity_visual)
        disparity_tk = ImageTk.PhotoImage(disparity_image)

        camera_label.config(image = disparity_tk)
        camera_label.image = disparity_tk

    root.after(10, update_camera_feed) # Update every 10ms

def start_camera():
    """Starting the camera feed."""
    update_camera_feed()

def stop_camera():
    """Stopping the camera feed."""
    cap_left.release()
    cap_right.release()

# Creating main window
root = tk.Tk()
root.title("Stereo Vision Camera Feed")
root.geometry('640x480')

# Define menu items and their corresponding actions
menu_items = {
    "File": [
        {"label":"New","command":lambda:print("Create a new file")},
        {"label":"Open...", "command":lambda:print("Open an existing file")}
    ],
    "Edit": [
        {"label":"Copy", "command":lambda:print("Copy selected text")},
        {"label":"Paste", "command":lambda:print("Paste copied text")}
    ],
    "Camera": [
        {"label": "Start Camera", "command": start_camera},
        {"label": "Stop Camera", "command": stop_camera}
    ]
}

# Create menu bar
menubar = tk.Menu(root)
root.config(menu = menubar)

# Add menus to the menu bar
for label, items in menu_items.items():
    menu = tk.Menu(menubar, tearoff=False)
    menubar.add_cascade(label=label, menu=menu)
    for item in items:
        menu.add_command(label=item["label"], command=item["command"])

# Add a label for displaying the camera feed
camera_label = tk.Label(root)
camera_label.pack(fill = tk.BOTH, expand=True)

# Start the application
root.mainloop()

# Release the camera resources on exit
cap_left.release()
cap_right.release()