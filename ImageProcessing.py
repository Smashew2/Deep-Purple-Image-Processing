import cv2
import numpy as np
import os
import csv

def crop_center_template(image_path, center_x, center_y, width, height, x_offset=0, y_offset=0):
    """Crop a specific region around the center from the image."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Image not found at {image_path}")
        return None

    x_start = int(center_x - width / 2 + x_offset)
    y_start = int(center_y - height / 2 + y_offset)

    print(f"Crop Coordinates: x_start = {x_start}, y_start = {y_start}")

    if (x_start < 0 or y_start < 0 or
        x_start + width > img.shape[1] or
        y_start + height > img.shape[0]):
        print("Invalid crop coordinates, outside image bounds.")
        return None

    template = img[y_start:y_start+height, x_start:x_start+width]

    # Optional debugging window
    # cv2.imshow("Cropped Template", template)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return template

def find_center_in_image(template, captured_image_path, needs_cleaning_log, threshold=0.6, method=cv2.TM_CCOEFF_NORMED):
    """Match the template in the captured image using multi-scale template matching."""
    captured_img = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)
    if captured_img is None:
        print(f"Error: Unable to load image at {captured_image_path}")
        return

    best_match_val = -1
    best_match_loc = None
    best_scale = 1.0

    scales = np.linspace(0.8, 1.2, 20)  # Scaling range

    for scale in scales:
        resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        
        if resized_template.shape[0] > captured_img.shape[0] or resized_template.shape[1] > captured_img.shape[1]:
            continue

        result = cv2.matchTemplate(captured_img, resized_template, method)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val > best_match_val:
            best_match_val = max_val
            best_match_loc = max_loc
            best_scale = scale

    match_percentage = best_match_val * 100
    hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]
    is_match = best_match_val >= threshold

    if not is_match:
        print(f"Adding to log: Hole {hole_number}, Match: {match_percentage:.2f}%")
        needs_cleaning_log.append([hole_number, f"{match_percentage:.2f}%"])

# === MAIN PROCESSING ===

if __name__ == "__main__":
    needs_cleaning_log = []
    image_counter = 0
    total_images = 1587

    # File paths
    # source_image_path = "/home/asmluser/Baseline Image/Baseline_Clean_Image.png"
    source_image_path = "/home/asmluser/Baseline Image/A-13.jpg"
    captured_image_folder = "/home/asmluser/ImageStorage"
    image_counter_file = "/home/asmluser/ImageStorage/image_counter.txt"

    # Template crop parameters
    center_x, center_y = 150, 150
    template_width, template_height = 50, 50
    x_offset, y_offset = -15, -45

    # Clear the counter file at the start
    with open(image_counter_file, "w") as f:
        f.write("0")

    # Crop the template
    template = crop_center_template(source_image_path, center_x, center_y, template_width, template_height, x_offset, y_offset)
    if template is None:
        print("Failed to crop the template. Exiting.")
    else:
        if os.path.exists(captured_image_folder):
            for filename in sorted(os.listdir(captured_image_folder)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG')):
                    captured_image_path = os.path.join(captured_image_folder, filename)

                    image_counter += 1
                    print(f"Processing image {image_counter}: {filename}")

                    # Write image_counter for GUI
                    try:
                        with open(image_counter_file, "w") as file:
                            file.write(str(image_counter))
                    except Exception as e:
                        print(f"Error writing image_counter.txt: {e}")

                    # Run template match
                    find_center_in_image(template, captured_image_path, needs_cleaning_log, threshold=0.60)

                    # Optionally update a separate progress file
                    progress_percentage = (image_counter / total_images) * 100
                    try:
                        with open('/home/asmluser/ImageStorage/progress.txt', 'w') as progress_file:
                            progress_file.write(f"{progress_percentage:.2f}")
                    except:
                        pass

    # Write results if needed
    if needs_cleaning_log:
        with open('/home/asmluser/ImageStorage/holes_needing_cleaning.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Hole Number', 'Percent difference from Baseline Image'])
            for entry in needs_cleaning_log:
                writer.writerow(entry)
        print("Cleaning log saved.")
    else:
        print("No holes need cleaning.")
