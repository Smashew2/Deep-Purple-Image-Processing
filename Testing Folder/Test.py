import cv2
import numpy as np
import os
import csv

# Feature Matching Function
def find_feature_in_images(source_image_path, captured_image_path, needs_cleaning_log):
    source_img = cv2.imread(source_image_path, cv2.IMREAD_GRAYSCALE)
    if source_img is None:
        print("Error: Could not load source image.")
        return
    
    orb = cv2.ORB_create()  # Using ORB instead of SURF
    source_keypoints, source_descriptors = orb.detectAndCompute(source_img, None)
    
    captured_img = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)
    if captured_img is None:
        print(f"Error: Could not load captured image at {captured_image_path}.")
        return

    captured_keypoints, captured_descriptors = orb.detectAndCompute(captured_img, None)

    # Check if descriptors are found
    if source_descriptors is None or captured_descriptors is None:
        print("Error: Could not find descriptors in one of the images.")
        return

    # Use FLANN matcher to find matches
    index_params = dict(algorithm=6, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(source_descriptors, captured_descriptors, k=2)

    # Filter good matches
    good_matches = []
    for m in matches:
        if len(m) == 2:  # Ensure we have at least two matches
            if m[0].distance < 0.7 * m[1].distance:
                good_matches.append(m[0])

    hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]  # Get the hole number from the filename

    if len(good_matches) < 4:  # Threshold for a "match"
        print(f"No matches found in image {captured_image_path}. Adding hole {hole_number} to cleaning log.")
        needs_cleaning_log.append(hole_number)
    else:
        print(f"Match found in image {captured_image_path}. Hole {hole_number} does not need cleaning.")

# Main Function
if __name__ == "__main__":
    needs_cleaning_log = []  # List to track holes needing cleaning

    source_image_path = r'C:\Users\smash\Downloads\ImageProcessing Test\Baseline Image\Baseline_Clean_Image.png'  # Path to baseline image
    captured_image_path = r'C:\Users\smash\Downloads\ImageProcessing Test\TestImage.png'  # Path to the test image

    if not os.path.exists(source_image_path):
        print("Source image path does not exist.")
    else:
        print("Source image path exists.")
    
    if os.path.exists(captured_image_path):
        print(f"Processing image: {captured_image_path}")
        find_feature_in_images(source_image_path, captured_image_path, needs_cleaning_log)
    else:
        print("Captured image path does not exist.")

    # Save log to CSV once processing is complete
    with open('holes_needing_cleaning.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Hole Number', 'Needs Cleaning'])
        for hole in needs_cleaning_log:
            writer.writerow([hole, 'Yes'])
    print("Cleaning log saved as 'holes_needing_cleaning.csv'.")
