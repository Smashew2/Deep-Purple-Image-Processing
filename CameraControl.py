import pyautogui
import cv2
import numpy as np
import time

# Parameters
blur_threshold = 100   # Threshold for "blurriness"
max_attempts = 3       # Max number of focus adjustment attempts

# Coordinates for Capture and Focus Buttons
capture_button_coords = (200, 300)  # Replace with actual Capture button coordinates
focus_button_coords = (250, 350)    # Replace with actual Focus button coordinates

# Capture Function: Clicks the Capture button in MicroViewer Plus
def capture_image():
    pyautogui.moveTo(capture_button_coords)
    pyautogui.click()
    print("Image captured.")

# Focus Adjustment Function: Clicks the Focus button to adjust focus
def adjust_focus():
    print("Adjusting focus...")
    pyautogui.moveTo(focus_button_coords)
    pyautogui.click()
    time.sleep(1)  # Small delay to let focus adjust

# Blurriness Check: Uses Variance of Laplacian to detect blurriness
def is_blurry(image, threshold=blur_threshold):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    print(f"Laplacian variance: {laplacian_var}")
    return laplacian_var < threshold

# Main Function: Capture with Focus Check
def capture_with_focus_check():
    # Focus MicroViewer Plus window
    pyautogui.click(x=100, y=100)  # Replace with coordinates within the app window
    time.sleep(1)  # Wait for the window to focus

    attempts = 0
    captured = False

    while attempts < max_attempts and not captured:
        # Assume we're capturing a frame from the camera (replace with actual capture code)
        frame = cv2.imread('test_image.jpg')  # Replace with real-time image capture

        if is_blurry(frame):
            print("Image is blurry, adjusting focus...")
            adjust_focus()
            attempts += 1
        else:
            capture_image()  # Capture if not blurry
            captured = True
            print("Image captured successfully.")

        time.sleep(2)  # Delay before next attempt

    if not captured:
        print("Failed to capture a clear image after multiple attempts.")

# Run the capture with focus check
capture_with_focus_check()
