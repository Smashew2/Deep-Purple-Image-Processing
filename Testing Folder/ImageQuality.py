import cv2
import numpy as np
import serial
import time

# Set up serial communication
# serial_port = 'COM3'  # Change to your Arduino's serial port (e.g., 'COM3' for Windows or '/dev/ttyACM0' for Linux/Mac)
# baud_rate = 9600  # Match the baud rate to the one set in Arduino code

# ser = serial.Serial(serial_port, baud_rate)
# time.sleep(2)  # Wait for the serial connection to initialize

def detect_circle(image, min_radius=50, max_radius=200):
    """Detect the center of the circle in an image using Canny and HoughCircles."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 1: Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    edges_inv = cv2.bitwise_not(edges)  # Invert edges to detect white on black
    cv2.imshow('Inverted Edges', edges_inv)  # Debugging visualization
    cv2.waitKey(0)

    # Step 2: Use HoughCircles to detect circles
    circles = cv2.HoughCircles(edges_inv, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50, 
                               param1=50, param2=30, minRadius=min_radius, maxRadius=max_radius)
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # Draw the center of the circle (ignoring radius)
            cv2.circle(image, (i[0], i[1]), 2, (0, 0, 255), 3)  # Red center
            return (i[0], i[1])  # Return center

    return None

def calculate_x_distance(circle_center, img_shape):
    """Calculate the horizontal distance between the circle center and the image center."""
    img_center_x = img_shape[1] // 2  # X-coordinate of the image center
    offset_x = circle_center[0] - img_center_x  # Horizontal distance
    return offset_x

# Load Image
image_path = r"C:\Users\smash\Downloads\ImageProcessing Test\Baseline Image\Baseline_Clean_Image.png"
# image_path = r"C:\Users\smash\Downloads\ImageProcessing Test\KS030.JPG"
frame = cv2.imread(image_path)

if frame is None:
    print(f"Error: Could not read image {image_path}")
else:
    # Detect circle center
    circle_center = detect_circle(frame)
    if circle_center:
        # Calculate the horizontal distance from the center of the image to the circle's center
        x_distance = calculate_x_distance(circle_center, frame.shape)
        cv2.putText(frame, f"Center X: {circle_center[0]} X Distance: {x_distance}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        print(f"Circle center detected at {circle_center}")
        print(f"X Distance from center: {x_distance:.2f} pixels")

        # Send the x_distance to Arduino over serial
        # ser.write(f"{x_distance}\n".encode())  # Send the value as a string

    # Display final image
    cv2.imshow('Final Result', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# # Close the serial communication when done
# ser.close()
