import cv2
import numpy as np

def find_feature_in_images(source_image_path, captured_images_paths):
    # Load the source image and detect its keypoints and descriptors
    source_img = cv2.imread(source_image_path, cv2.IMREAD_GRAYSCALE)
    if source_img is None:
        print("Error: Could not load source image.")
        return
    
    # Initialize SURF detector
    surf = cv2.xfeatures2d.SURF_create(hessianThreshold=400)
    
    # Detect keypoints and compute descriptors for the source image
    source_keypoints, source_descriptors = surf.detectAndCompute(source_img, None)

    # FLANN parameters for feature matching
    index_params = dict(algorithm=0, trees=5)  # Algorithm 0 is KDTree
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    # List to keep track of images needing cleaning
    images_needing_cleaning = []

    for img_path in captured_images_paths:
        # Load each captured image
        captured_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if captured_img is None:
            print(f"Error: Could not load captured image at {img_path}.")
            continue
        
        # Detect keypoints and descriptors in the captured image
        captured_keypoints, captured_descriptors = surf.detectAndCompute(captured_img, None)

        # Use FLANN-based matcher to find matching features
        matches = flann.knnMatch(source_descriptors, captured_descriptors, k=2)

        # Filter out good matches using Lowe's ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)

        # Check if any good matches are found
        if len(good_matches) > 0:
            # Get the matched keypoints
            src_pts = np.float32([source_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([captured_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

            # Calculate the homography matrix to find the bounding box of the matched feature
            if len(good_matches) >= 4:  # Minimum points to find a homography
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
                
                # Get the bounding box around the source image feature
                h, w = source_img.shape
                box = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
                projected_box = cv2.perspectiveTransform(box, M)

                # Draw the bounding box on the captured image
                captured_img_with_box = cv2.polylines(captured_img, [np.int32(projected_box)], isClosed=True, color=(255, 0, 0), thickness=3)

                # Show the matched image with bounding box
                cv2.imshow('Matched Feature', captured_img_with_box)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                # Save the matched image with the bounding box overlay
                matched_image_path = f'matched_{img_path}'
                cv2.imwrite(matched_image_path, captured_img_with_box)
                print(f"Match found and saved as {matched_image_path}")
            else:
                print(f"Not enough matches found in image {img_path}.")
                images_needing_cleaning.append(img_path)  # Add image to cleaning list
        else:
            print(f"No matches found in image {img_path}.")
            images_needing_cleaning.append(img_path)  # Add image to cleaning list

    # Print the list of images needing cleaning
    if images_needing_cleaning:
        print("Images that need to be cleaned:")
        for img in images_needing_cleaning:
            print(f"- {img}")
    else:
        print("All captured images contain the feature.")

# Example usage
source_image_path = 'source_image.jpg'  # Path to the feature template image
captured_images_paths = ['captured1.jpg', 'captured2.jpg']  # Paths to captured images
find_feature_in_images(source_image_path, captured_images_paths)

