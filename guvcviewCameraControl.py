import serial
import subprocess

# Set up serial connection
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust based on your port

def capture_image():
    image_path = "/home/pi/captured_image.jpg"  # Set your desired path
    subprocess.run(["guvcview", "--capture-image", image_path])


while True:
    try:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            print("Received:", data)
            
            if data == "capture":
                print("Capturing Image...")
                capture_image()
    except Exception as e:
        print("Error:", e)
