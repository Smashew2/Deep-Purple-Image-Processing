import cv2
import numpy as np
import os
import csv

def crop_center_template(image_path, center_x, center_y, width, height, x_offset=0, y_offset=0):
    """Crop a specific region around the center from the image."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read image in grayscale
    if img is None:
        return None
    
    # Apply the offset to center_x and center_y
    x_start = int(center_x - width / 2 + x_offset)
    y_start = int(center_y - height / 2 + y_offset)
    
    # Check that the crop coordinates are within the image dimensions
    if (x_start < 0 or y_start < 0 or
        x_start + width > img.shape[1] or
        y_start + height > img.shape[0]):
        return None
    
    template = img[y_start:y_start+height, x_start:x_start+width]
    
    return template

# def is_image_blurry(image_path, blur_threshold=100.0):
#     """Check if the image is too blurry using Laplacian variance."""
#     img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
#     if img is None:
#         return False
    
#     # Compute the Laplacian of the image and then compute its variance
#     laplacian = cv2.Laplacian(img, cv2.CV_64F)
#     variance = laplacian.var()
    
#     # If variance is below the threshold, consider the image blurry
#     return variance < blur_threshold

def find_center_in_image(template, captured_image_path, needs_cleaning_log, threshold=0.6, method=cv2.TM_CCOEFF_NORMED, blur_threshold=100.0):
    """Match the template in the captured image using multi-scale cv2.TM_CCOEFF_NORMED."""
    # # Check if the image is too blurry
    # if is_image_blurry(captured_image_path, blur_threshold):
    #     hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]
    #     needs_cleaning_log.append([hole_number, "Image unable to be used, please retake"])
    #     return
    
    captured_img = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)  # Read captured image in grayscale
    if captured_img is None:
        return
    
    # Initialize variables for best match
    best_match_val = -1
    best_match_loc = None
    best_scale = 1.0

    # Define scales to search over (adjust range and step as needed)
    scales = np.linspace(0.8, 1.2, 20)  # Try scaling from 80% to 120%

    for scale in scales:
        # Resize template
        resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        
        # Ensure the template size is smaller than the captured image
        if resized_template.shape[0] > captured_img.shape[0] or resized_template.shape[1] > captured_img.shape[1]:
            continue

        # Perform template matching
        result = cv2.matchTemplate(captured_img, resized_template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Use max_val for cv2.TM_CCOEFF_NORMED, higher values indicate better match
        if max_val > best_match_val:
            best_match_val = max_val
            best_match_loc = max_loc
            best_scale = scale

    # Calculate match percentage as a percentage of the best match score
    match_percentage = best_match_val * 100

    # Determine if the match is good enough
    hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]
    is_match = best_match_val >= threshold

    # Only add to the log if the match score is below the threshold (cleaning needed)
    if not is_match:
        needs_cleaning_log.append([hole_number, f"{match_percentage:.2f}%"])

# Main Function
if __name__ == "__main__":
    needs_cleaning_log = []  # List to track holes needing cleaning

    source_image_path = r'C:\Users\smash\Downloads\ImageProcessing Test\Baseline Image\Baseline_Clean_Image.png'  # Path to baseline image
    captured_image_folder = r'C:\Users\smash\Downloads\ImageProcessing Test'  # Folder with test images

    # Coordinates and size for the center template
    center_x, center_y = 150, 150  # Example coordinates (adjust based on your image)
    template_width, template_height = 50, 50  # Example size (adjust as needed)

    # Offset values to shift the template slightly left and up
    x_offset, y_offset = -15, -45  # Adjust these values as needed

    # Crop the center template from the baseline image with an offset
    template = crop_center_template(source_image_path, center_x, center_y, template_width, template_height, x_offset, y_offset)
    if template is None:
        print("Failed to crop the template. Exiting.")
    else:
        # Process each captured image if template cropping was successful
        if os.path.exists(captured_image_folder):
            for filename in os.listdir(captured_image_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg','.JPG')):  # Check for image files
                    captured_image_path = os.path.join(captured_image_folder, filename)
                    
                    # Use `cv2.TM_CCOEFF_NORMED` method with a threshold of 0.6 for cleaning determination
                    find_center_in_image(template, captured_image_path, needs_cleaning_log, threshold=0.65, method=cv2.TM_CCOEFF_NORMED)

    # Save log to CSV once processing is complete
    if needs_cleaning_log:
        with open('holes_needing_cleaning.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Hole Number', 'Percent difference from Baseline Image'])
            for entry in needs_cleaning_log:
                writer.writerow(entry)
        print("Cleaning log saved as 'holes_needing_cleaning.csv'.")
    else:
        print("No holes need cleaning.")
