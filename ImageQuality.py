import cv2
import numpy as np
import os
import serial
import time

# Initialize the serial connection to the Arduino
def init_serial_connection(port, baud_rate=9600):
 #   """Initialize serial connection to Arduino."""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)  # Adjust the timeout as needed
        print(f"Connected to Arduino on {port} at {baud_rate} baud.")
        time.sleep(2)  # Give Arduino time to reset
        return ser
    except Exception as e:
        print(f"Error connecting to Arduino: {e}")
        return None

def send_x_distance_to_arduino(ser, x_distance):
    """Send the X distance to the Arduino."""
    if ser:
        try:
            # Send the distance to the Arduino
            sec = "P"
            if x_distance < 0:
                sec = "N"
                x_distance = abs(x_distance)
                
            x_distance_str = str(x_distance)
            if x_distance < 100 and x_distance >= 10:
                x_distance_str = "0" + x_distance_str
            elif x_distance < 10:
                x_distance_str = "00" + x_distance_str
            x_distance_str = "T" + sec + x_distance_str
            message = f"{x_distance_str}\n"  # Send as a string with newline for easy parsing
            ser.write(message.encode())  # Encode and send the message
            print(f"Sent X Distance: {x_distance_str} to Arduino.")
        except Exception as e:
            print(f"Error sending data to Arduino: {e}")

def detect_circle(image, min_radius=50, max_radius=200):
    """Detect the center of the circle in an image using Canny and HoughCircles."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Step 1: Canny edge detection
    edges = cv2.Canny(gray, 50, 150)
    edges_inv = cv2.bitwise_not(edges)  # Invert edges to detect white on black
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

def process_latest_image_in_folder(folder_path, ser):
    """Process the most recent image in a folder and detect the circle center."""
    # Get all image files in the folder (assuming jpg, png, etc.)
    valid_image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    # List all files in the folder and filter for valid images
    images = [f for f in os.listdir(folder_path) if any(f.lower().endswith(ext) for ext in valid_image_extensions)]
    
    if not images:
        print("No images found in the folder.")
        return

    # Sort images by modification time (latest first)
    images.sort(key=lambda f: os.path.getmtime(os.path.join(folder_path, f)), reverse=True)

    # Select the latest image
    latest_image_path = os.path.join(folder_path, images[0])
    print(f"Processing the latest image: {latest_image_path}")
    
    frame = cv2.imread(latest_image_path)

    if frame is None:
        print(f"Error: Could not read image {latest_image_path}")
    else:
        # Detect circle center
        circle_center = detect_circle(frame)
        if circle_center:
            # Calculate the horizontal distance from the center of the image to the circle's center
            x_distance_degrees = calculate_x_distance(circle_center, frame.shape) / 248.1111
            x_distance = round(x_distance_degrees * 100) 
            cv2.putText(frame, f"Center X: {circle_center[0]} X Distance: {x_distance}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            print(f"Circle center detected at {circle_center}")
            print(f"X Distance from center: {x_distance:.2f}")
            
            # Send the X distance to the Arduino
            send_x_distance_to_arduino(ser, x_distance)

        # Display final image (Only for debugging purposes)
        #cv2.imshow(f'Processed Image - {images[0]}', frame)
        #cv2.waitKey(0)  # Wait for a key press to move to the next image
        cv2.destroyAllWindows()


if __name__ == "__main__":
        ## Main script execution
    folder_path = "/home/asmluser/ImageStorage"  # Change to your image folder path
    arduino_port = '/dev/ttyACM0' 

    # Initialize serial connection
    ser = init_serial_connection(arduino_port)

    if ser:
        process_latest_image_in_folder(folder_path, ser)
        ser.close()  # Close the serial connection after use
