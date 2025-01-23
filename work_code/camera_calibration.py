import numpy as np
import cv2
import glob


def calibrate_camera (camera_id, image_path, output_file):
    """Calibrating a single camera using chessboard images"""
    # Define Chestboard Size
    chessboard_size = (9, 7) # Inner corners per a chessboard's row and column
    square_size = 0.025  # Size of a square in meters 

    # Termination criteria for corner refinement
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Prepare object points (3D points in the real-world space)
    objp = np.zeros ((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape (-1,2)
    objp *= square_size

    # Arrays to store object points and image points from all the images
    objpoints = []
    imgpoints = []

    # Load all the calibration images
    images = glob.glob(f'{image_path}/*.jpg') 

    for image_file in images:
        img = cv2.imread (image_file)
        gray = cv2.cvtColor (img, cv2.COLOR_BGR2GRAY)

        # Find chessboard corners
        ret, corners = cv2.findChessboardCorners (gray, chessboard_size, None)

        if ret:
            objpoints.append (objp)

            # Refine corner locations
            corners2 = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), criteria
            )
            imgpoints.append (corners2)

            # Draw and display the corners
            cv2.drawChessboardCorners (img, chessboard_size, corners2, ret)
            cv2.imshow('Chessboard', img)
            cv2.waitKey (500)

    cv2.destroyAllWindows

    # Perform Camera Calibration
    ret, camera_matrix, distortion_coefficients, rvecs, tvecs = cv2.calibrateCamera (objpoints, imgpoints, gray.shape[::-1], None, None)

    # Save Calibration Data
    np.savez(output_file, camera_matrix = camera_matrix, distortion_coefficients = distortion_coefficients)

    # Print Calibration Results
    print (f"Camera Matrix: \n", camera_matrix)
    print (f"Distortion Coefficient: \n", distortion_coefficients)

    # Test Undistortion 
    for image_file in images:
        img = cv2.imread (image_file)
        h, w = img.shape [:2]
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix (
            camera_matrix, distortion_coefficients, (w, h), 1, (w, h)
        )

        # Undistort the Image
        dst = cv2.undistort (img, camera_matrix, distortion_coefficients, None, new_camera_matrix)

        # Cropping the Image
        x, y, w, h = roi
        dst = dst [y:y+h, x:x+h]

        # Display the results
        cv2.imshow ('Original', img)
        cv2.imshow ('Undistorted', dst)
        cv2.waitKey(500)

    cv2.destroyAllWindows

calibrate_camera (1, 'camera1_calibration_images', 'camera1_calibration_data.npz')
calibrate_camera (2, 'camera2_calibration_images', 'camera2_calibration_data.npz')