import pyautogui
import pygetwindow as gw
import time
import subprocess

def bring_window_to_front(window_title):
    """Bring the camera software window to the foreground."""
    try:
        # Get the window by title and bring it to the front
        window = gw.getWindowsWithTitle(window_title)
        if window:
            window[0].activate()  # Focus the window
            return True
        else:
            print(f"Window '{window_title}' not found.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def open_camera_software():
    """Open the camera software in non-blocking mode"""
    return subprocess.Popen(["C:\\MicroViewer_DMC-1213\\VSVC3EM.EXE"])

def wait_for_software_to_load(timeout=60):
    """Wait for the camera software window to appear"""
    start_time = time.time()
    while True:
        # Check if the software window is present by its title
        window_title = "MicroScope"  # Replace with the exact or partial window title
        window = gw.getWindowsWithTitle(window_title)
        if window:
            return True
        if time.time() - start_time > timeout:
            print("Timeout: Software did not load in time.")
            return False
        time.sleep(1)  # Wait for 1 second before checking again

def capture_image():
    """Capture the image by pressing the key combination Ctrl + Insert"""
    pyautogui.hotkey('ctrl', 'insert')
    print("Image captured!")

# 1. Open the camera software in non-blocking mode
process = open_camera_software()

# 2. Wait for the software to load completely
if wait_for_software_to_load(timeout=60):  # Adjust the timeout as necessary
    # 3. Wait a longer time before interacting with the software
    time.sleep(20)  # Wait for 45 seconds 

    # 4. Bring the software window into focus (use the window title or part of it)
    window_title = "MicroScope"  # Adjust based on the software window title
    if bring_window_to_front(window_title):
        # 5. Simulate pressing Enter to dismiss the popup (if detected)
        time.sleep(10)  # Wait for 3 seconds (adjust as necessary)
        pyautogui.press('enter')

        # 6. Capture the image by pressing Ctrl + Insert
        time.sleep(5)  # Wait for 3 seconds (adjust as necessary)
        capture_image()
else:
    print("Camera software did not load in time.")

# Optionally, wait for the software to close before exiting the script
process.wait()  # This ensures the script waits until the camera software closes
