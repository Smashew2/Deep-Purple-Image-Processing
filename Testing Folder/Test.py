import cv2
import numpy as np
import os
import csv

def crop_center_template(image_path, center_x, center_y, width, height, x_offset=0, y_offset=0, show_template=False):
    """Crop a specific region around the center from the image and optionally display it."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read image in grayscale
    if img is None:
        print(f"Error: Could not load image at {image_path}.")
        return None
    
    # Apply the offset to center_x and center_y
    x_start = int(center_x - width / 2 + x_offset)
    y_start = int(center_y - height / 2 + y_offset)
    
    # Check that the crop coordinates are within the image dimensions
    if (x_start < 0 or y_start < 0 or
        x_start + width > img.shape[1] or
        y_start + height > img.shape[0]):
        print("Error: Crop area is out of bounds.")
        return None
    
    template = img[y_start:y_start+height, x_start:x_start+width]
    
    # Display the cropped template area if requested
    if show_template:
        cv2.imshow("Template Area", template)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return template

def find_center_in_image(template, captured_image_path, needs_cleaning_log, threshold=0.2, method=cv2.TM_SQDIFF_NORMED):
    """Match the template in the captured image using cv2.TM_SQDIFF_NORMED."""
    captured_img = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)  # Read captured image in grayscale
    if captured_img is None:
        print(f"Error: Could not load captured image at {captured_image_path}.")
        return
    
    # Perform template matching
    result = cv2.matchTemplate(captured_img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]
    
    # `cv2.TM_SQDIFF_NORMED` - lower values indicate better matches
    is_match = min_val <= threshold  # Consider it a match if it's 80% or more similar

    # Determine the coordinates of the rectangle to draw on the image
    top_left = min_loc
    bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

    # If a match is found, draw a green rectangle around the matched area
    if is_match:
        cv2.rectangle(captured_img, top_left, bottom_right, (0, 255, 0), 2)  # Green rectangle
        print(f"Center feature found in image {captured_image_path} with match score {min_val:.2f}. Hole {hole_number} does not need cleaning.")
    else:
        # If no match is found, draw a red rectangle and log it
        cv2.rectangle(captured_img, top_left, bottom_right, (0, 0, 255), 2)  # Red rectangle
        print(f"Center feature not found in image {captured_image_path}. Adding hole {hole_number} to cleaning log.")
        needs_cleaning_log.append(hole_number)

    # Show the image with the rectangle drawn (for debugging and visual confirmation)
    cv2.imshow(f"Matching: {hole_number}", captured_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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

    # Crop the center template from the baseline image with an offset and display it
    template = crop_center_template(source_image_path, center_x, center_y, template_width, template_height, x_offset, y_offset, show_template=True)
    if template is None:
        print("Failed to crop the template. Exiting.")
    else:
        # Process each captured image if template cropping was successful
        if os.path.exists(captured_image_folder):
            print(f"Processing images in folder: {captured_image_folder}")
            for filename in os.listdir(captured_image_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
                    captured_image_path = os.path.join(captured_image_folder, filename)
                    
                    # Use `cv2.TM_SQDIFF_NORMED` method with a threshold for best matching (80% similarity)
                    find_center_in_image(template, captured_image_path, needs_cleaning_log, threshold=0.2, method=cv2.TM_SQDIFF_NORMED)
        else:
            print("Captured image folder does not exist.")

    # Save log to CSV once processing is complete
    with open('holes_needing_cleaning.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Hole Number', 'Needs Cleaning'])
        for hole in needs_cleaning_log:
            writer.writerow([hole, 'Yes'])
    print("Cleaning log saved as 'holes_needing_cleaning.csv'.")
