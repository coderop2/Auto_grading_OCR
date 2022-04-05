import numpy as np
from Convolution_preprocessing import *

# sobel filters 
sobel_x = np.array([[-1,0,1],[-2,0,2],[-1,0,1]])*(1/8)
sobel_y = np.array([[1,2,1],[0,0,0],[-1,-2,-1]])*(1/8)

# Calculate magnitude and gradient
def Sobel_edge_detection(image, calculate_angles = False):
    # apply the sobel filters to the image
    new_image_x = Convolve(image, sobel_x)
    new_image_y = Convolve(image, sobel_y)
    
    grad_mag = np.sqrt(np.square(new_image_x) + np.square(new_image_y))
    grad_mag *= 255.0 / grad_mag.max()
    # Calculate the gradient
    if calculate_angles:
        theta = np.arctan2(new_image_y, new_image_x)
        theta = theta * 180. / np.pi
        theta[theta < 0] += 180
        return grad_mag, np.round(theta, 2)
    
    return grad_mag

# This method is used to thin out the edges
def Non_Max_Suppression(img, theta):
    # Create a matrix for output image
    n, m = img.shape[0], img.shape[1]
    img_out = np.zeros((n,m), dtype=np.int32)
    # Find the direction of edge by using theta
    for i in range(1,n-1):
        for j in range(1,m-1):
            # 0 angle
            if (theta[i,j] < 22.5 and theta[i,j] >= 0) or (theta[i,j] <=180 and theta[i,j] >= 157.5):
                p, r = img[i, j+1], img[i, j-1]
            # 45 angle
            elif theta[i,j] < 67.5 and theta[i,j] >= 22.5:
                p, r = img[i+1, j-1], img[i-1, j+1]
            # 90 angle
            elif theta[i,j] < 112.5 and theta[i,j] >= 67.5:
                p, r = img[i+1, j], img[i-1, j]
            # 135 angle
            elif theta[i,j]< 157.5 and theta[i,j] >= 112.5:
                p, r = img[i-1, j-1], img[i+1, j+1]
            else:
                p, r = 255, 255

            if img[i,j] >= p and img[i,j] >= r:
                img_out[i,j] = img[i,j]

    return img_out
# This method is used to identify strong pixels and non-relevant pixels. 
# The high_threshold is used to identify the strong pixels
# The low_threshold is used to identify the non-relevant pixels.
# Others are the weak pixels
def Thresholding(image, high_threshold, low_threshold, set_particular_val = True,
                 high_threshold_val = 255, low_threshold_val = 0):
    n, m = image.shape[0], image.shape[1]
    
    img = image.copy()
    # Find the non-relevant pixels
    img[np.where(img < low_threshold)] = low_threshold_val
    if set_particular_val:
        img[np.where(img >= high_threshold)] = high_threshold_val
    
    directions = [(-1,-1), (-1,0), (-1,1), (0,)]
    for i in range(1, n-1):
        for j in range(1, m-1):
            if img[i,j] < high_threshold and img[i,j] > low_threshold:
                set_edge = False
                for pixel_x in [-1,0,1]:
                    for pixel_y in [-1,0,1]:
                        # Find the strong pixels
                        if img[i+pixel_x, j+pixel_y] >= high_threshold:
                            set_edge = True
                if not set_edge:
                    img[i, j] = 0

        return img

# This method is used to detect the edge, 
# which uses a multi-stage algorithm to detect edges of an image.
def Canny_Edge_Detection(image, high_threshold, low_threshold, 
                         set_particular_val = True,
                         high_threshold_val = 255, 
                         low_threshold_val = 0):
    # Gradient calculation
    grad_mag, theta = Sobel_edge_detection(image, True)
    # Non-maximum suppression
    non_max_img = Non_Max_Suppression(grad_mag, theta)
    # Double threshold
    output = Thresholding(non_max_img, high_threshold, 
                          low_threshold, set_particular_val = True,
                          high_threshold_val = 255, low_threshold_val = 0)
    return output

# cannny_edge_img = Canny_Edge_Detection(image, 75, 25)
