import cv2
import numpy as np
import os
import time
import csv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Function to calculate coverage percentage
def calculate_coverage(source_image_path, captured_image_path):
    source_img = cv2.imread(source_image_path, cv2.IMREAD_GRAYSCALE)
    captured_img = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)

    # Threshold the images to segment the holes
    _, src_thresh = cv2.threshold(source_img, 128, 255, cv2.THRESH_BINARY_INV)
    _, captured_thresh = cv2.threshold(captured_img, 128, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    src_contours, _ = cv2.findContours(src_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    captured_contours, _ = cv2.findContours(captured_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(src_contours) == 0 or len(captured_contours) == 0:
        print("Error: No hole detected in one of the images.")
        return None

    # Calculate areas
    src_area = cv2.contourArea(src_contours[0])  # Area of unobstructed hole
    captured_area = cv2.contourArea(captured_contours[0])  # Area of current hole

    if src_area > 0:
        coverage_percentage = ((src_area - captured_area) / src_area) * 100
        return coverage_percentage
    else:
        return None

# Feature Matching Function
def find_feature_in_images(source_image_path, captured_image_path, needs_cleaning_log):
    source_img = cv2.imread(source_image_path, cv2.IMREAD_GRAYSCALE)
    if source_img is None:
        print("Error: Could not load source image.")
        return
    
    surf = cv2.xfeatures2d.SURF_create(hessianThreshold=400)
    source_keypoints, source_descriptors = surf.detectAndCompute(source_img, None)
    index_params = dict(algorithm=0, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    captured_img = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)
    if captured_img is None:
        print(f"Error: Could not load captured image at {captured_image_path}.")
        return

    captured_keypoints, captured_descriptors = surf.detectAndCompute(captured_img, None)
    matches = flann.knnMatch(source_descriptors, captured_descriptors, k=2)
    
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]

    hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]  # Get the hole number from the filename

    if len(good_matches) < 4:  # Threshold for a "match"
        print(f"No matches found in image {captured_image_path}. Adding hole {hole_number} to cleaning log.")
        coverage = calculate_coverage(source_image_path, captured_image_path)
        if coverage is not None:
            print(f"Coverage for hole {hole_number}: {coverage:.2f}%")
            needs_cleaning_log.append((hole_number, coverage))
        else:
            needs_cleaning_log.append((hole_number, 'Coverage calculation failed'))
    else:
        print(f"Match found in image {captured_image_path}. Hole {hole_number} does not need cleaning.")

# Directory Monitor Class
class ImageHandler(FileSystemEventHandler):
    def __init__(self, source_image_path, needs_cleaning_log):
        self.source_image_path = source_image_path
        self.needs_cleaning_log = needs_cleaning_log

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.jpg', '.png')):
            print(f"New image detected: {event.src_path}")
            time.sleep(1)  # Brief delay to ensure the file is fully written
            find_feature_in_images(self.source_image_path, event.src_path, self.needs_cleaning_log)

# Directory Monitoring and Logging Function
def monitor_folder(folder_path, source_image_path):
    needs_cleaning_log = []  # List to track holes needing cleaning
    event_handler = ImageHandler(source_image_path, needs_cleaning_log)
    observer = Observer()
    observer.schedule(event_handler, path=folder_path, recursive=False)
    observer.start()
    print(f"Monitoring folder: {folder_path} for new images...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        # Save log to CSV once monitoring is stopped
        with open('holes_needing_cleaning.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Hole Number', 'Needs Cleaning', 'Coverage Percentage'])
            for hole in needs_cleaning_log:
                writer.writerow([hole[0], 'Yes', hole[1]])
        print("Cleaning log saved as 'holes_needing_cleaning.csv'.")
    observer.join()

# Usage
source_image_path = 'source_image.jpg'  # Path to feature template
captured_images_folder = '/path/to/captured/images'  # Path to folder containing captured images
monitor_folder(captured_images_folder, source_image_path)
