import numpy as np

def Convolve(image, kernel, stride = 1):
    img_3d = False if len(image.shape) == 2 else True
    if img_3d:
        return "Only support for 2D images"
    
    n = image.shape[0]
    m = image.shape[1]
    
    kernel_h, h = kernel.shape[0], kernel.shape[0]//2
    kernel_w, w = kernel.shape[1], kernel.shape[1]//2
    
    img = np.zeros((n + 2*h, m + 2*w))
    img[h:h+n, w:w+m] = image
    
    n_out = (n+2*h-kernel_h)//stride
    w_out = (m+2*w-kernel_w)//stride
    img_conv = np.zeros((n_out + 1, 
                         w_out + 1))
    
    i = 0
    for x in range(h, img.shape[0]-h, stride):
        j = 0
        for y in range(w, img.shape[1]-w, stride):
            feature_map = img[x-h:x-h+kernel_h, y-w:y-w+kernel_w]
            img_conv[i, j] = np.sum(feature_map*kernel)
            j+=1
        i+=1
    return img_conv

def Gaussian(shape, sigma = 0.5):
    assert type(shape) != int, "Please send a list/tuple/numpy array of format (h, w)"
    assert len(shape) == 2, "Please send the shape in the format of (h, w)"
    
    h, w = int(shape[0]) // 2, int(shape[1]) // 2
    x, y = np.mgrid[-h:h+1, -w:w+1]
    
    gaus =  np.exp(-((x**2 + y**2) / (2.0*sigma**2)))
    return gaus * (1 / (2.0 * np.pi * sigma**2))

# This kernel was taken from the slides in the 2.7 section video
# As this seems to work better then finding a random kernel
sharpen_kernel = np.array([[0.003, 0.013, 0.022, 0.013, 0.003],
                           [0.013, 0.059, 0.097, 0.059, 0.013],
                           [0.022, 0.097, 0.159, 0.097, 0.022],
                           [0.013, 0.059, 0.097, 0.059, 0.013],
                           [0.003, 0.013, 0.022, 0.013, 0.003]])

def Sharpen(image, kernel, alpha = 0.5):
    return image + alpha * (image - Convolve(image, kernel))
