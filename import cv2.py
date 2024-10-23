import cv2 
import numpy as np

# Read the image
img = cv2.imread('your_image.jpg', cv2.IMREAD_GRAYSCALE)

# Create SURF object
surf = cv2.xfeatures2d.SURF_create(400)  # 400 is the Hessian threshold

# Find keypoints and descriptors
kp, des = surf.detectAndCompute(img, None)

# Draw keypoints on the image
img_with_keypoints = cv2.drawKeypoints(img, kp, None, (255,0,0), 4)

# Show the image
cv2.imshow('Keypoints', img_with_keypoints)
cv2.waitKey(0)
cv2.destroyAllWindows()