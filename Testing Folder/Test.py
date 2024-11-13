import cv2
import numpy as np
import os
import csv

# Feature Matching and Homography-based Pattern Check Function
def find_feature_in_images(source_image_path, captured_image_path, needs_cleaning_log):
    source_img = cv2.imread(source_image_path, cv2.IMREAD_GRAYSCALE)
    if source_img is None:
        print("Error: Could not load source image.")
        return

    # Using ORB feature detector on the full image
    orb = cv2.ORB_create(nfeatures=1000, scaleFactor=1.2, nlevels=8)
    source_keypoints, source_descriptors = orb.detectAndCompute(source_img, None)

    captured_img = cv2.imread(captured_image_path, cv2.IMREAD_GRAYSCALE)
    if captured_img is None:
        print(f"Error: Could not load captured image at {captured_image_path}.")
        return
    hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]
    captured_keypoints, captured_descriptors = orb.detectAndCompute(captured_img, None)

    print(f"Source image keypoints: {len(source_keypoints)}")
    print(f"Captured image ({hole_number}) keypoints: {len(captured_keypoints)}")

    # Check if descriptors are found
    if source_descriptors is None or captured_descriptors is None:
        print("Error: Could not find descriptors in one of the images.")
        return

    # Use FLANN matcher to find matches
    index_params = dict(algorithm=6, trees=5)  # Using LSH (Locality Sensitive Hashing) for ORB
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(source_descriptors, captured_descriptors, k=2)

    # Relaxed ratio test: Allow more matches with weaker confidence
    good_matches = []
    for m in matches:
        if len(m) == 2:  # Ensure we have at least two matches
            if m[0].distance < 0.7 * m[1].distance:  # Relaxed ratio test (less strict)
                good_matches.append(m[0])

    hole_number = os.path.splitext(os.path.basename(captured_image_path))[0]  # Get the hole number from the filename

    if len(good_matches) >= 5:  # Reduced threshold for good matches
        print(f"Good matches found in image {captured_image_path}. Checking pattern similarity...")

        # Extract matched points
        src_pts = np.float32([source_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([captured_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Use RANSAC to find homography with more freedom
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)  # Relaxed threshold for RANSAC

        # If a homography matrix is found, it means the pattern is similar
        if M is not None and np.sum(mask) > 3:  # Relaxed inlier condition (less strict)
            print(f"Pattern is similar in image {captured_image_path}. Hole {hole_number} does not need cleaning.")
            # Optionally visualize the matches
            img_matches = cv2.drawMatches(source_img, source_keypoints, captured_img, captured_keypoints, good_matches, None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            cv2.imshow(f"Matches for Hole {hole_number}", img_matches)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print(f"Pattern mismatch detected in image {captured_image_path}. Adding hole {hole_number} to cleaning log.")
            needs_cleaning_log.append(hole_number)
    else:
        print(f"Not enough good matches found in image {captured_image_path}. Adding hole {hole_number} to cleaning log.")
        needs_cleaning_log.append(hole_number)

# Main Function
if __name__ == "__main__":
    needs_cleaning_log = []  # List to track holes needing cleaning

    source_image_path = r'C:\Users\smash\Downloads\ImageProcessing Test\Baseline Image\Baseline_Clean_Image.png'  # Path to baseline image
    captured_image_folder = r'C:\Users\smash\Downloads\ImageProcessing Test'  # Folder with test images

    if not os.path.exists(source_image_path):
        print("Source image path does not exist.")
    else:
        print("Source image path exists.")
    
    if os.path.exists(captured_image_folder):
        print(f"Processing images in folder: {captured_image_folder}")
        
        # Process each image in the folder
        for filename in os.listdir(captured_image_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
                captured_image_path = os.path.join(captured_image_folder, filename)
                find_feature_in_images(source_image_path, captured_image_path, needs_cleaning_log)
    else:
        print("Captured image folder does not exist.")

    # Save log to CSV once processing is complete
    with open('holes_needing_cleaning.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Hole Number', ' Needs Cleaning'])
        for hole in needs_cleaning_log:
            writer.writerow([hole, ' Yes'])
    print("Cleaning log saved as 'holes_needing_cleaning.csv'.")
