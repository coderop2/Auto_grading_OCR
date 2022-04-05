# Import libraries and dependencies
from PIL import Image, ImageFilter
import random
import math, sys, random
# import imageio
import numpy as np
import warnings
from Convolution_preprocessing import *
from Edge_detection import *
warnings.filterwarnings('ignore')

# This method is used for getting the votes in the hough space for each and every pixel
# identified by the canny edge detector. I have modified so that each pixel only votes for
# 2 kinds of lines - vertical and horizontal.
def Hough_voter(img, angle, vote_list):
    votes = vote_list
    # Save temp values
    cosValue = np.cos(np.deg2rad(angle))
    sinValue = np.sin(np.deg2rad(angle))
    # Start to vote
    for i in range(img.width):
        for j in range(img.height):
            if img.getpixel((i,j)) == 255:
                # Calculate rho
                rho = i*cosValue + j*sinValue
                votes[abs(int(rho))] += 1
    return votes

# this method is used so that the boxes blurred by the students rae removed for canny edge 
# detection because of the marked boxes there were a lot of false positives in the data.
# so here we are only blackening the pixels is the sum of the surrounding pixels exceed a 
# particular threshold. The threshold was found using trial and error which can ve found
# in the jupyter notebook in the code folder.
def method(image, kernel, summ, stride = 1):
    n = image.shape[0]
    m = image.shape[1]
    
    kernel_h, h = kernel.shape[0], kernel.shape[0]//2
    kernel_w, w = kernel.shape[1], kernel.shape[1]//2

    for x in range(h, image.shape[0]-h, stride):
        for y in range(w, image.shape[1]-w, stride):
            feature_map = image[x-h:x-h+kernel_h, y-w:y-w+kernel_w]
            temp = np.sum(feature_map)
            if temp > summ:
                image[x, y] = 0
    return image

# This method is used to read image, and get locations of boxes by using the horizotal lines
# and vertical lines which is generated by canny edge detection.
def preprocess(img_name):
    # read image using the PIL library and convert to grayscale
    # image = np.array(imageio.imread(img_name,as_gray=True))
    image = np.array(Image.open(img_name).convert("L"))
    if image[0,0] != 0:
        norm_img = np.abs(image - 255.)
    else:
        norm_img = image
        
    # remove the first 600 lines from consideration as they do not contain the boxes
    # marked by the students and may unnecessaryly influence the algorithm.
    norm_img[:600, :] = 0
    
    # Sharpen the image before the edge detection algorithm. the kernel being used is the same
    # as the one shown by professor in the videos because on our experiments that seems to 
    # work the best.
    shrpened = Sharpen(norm_img, sharpen_kernel, -0.2)
    
    # start to canny edge detection
    im = Canny_Edge_Detection(shrpened, 50, 10)
    
    # Remove the marked answers by the students to form the grid around the boxes.
    im = method(im.copy(), np.ones((20, 20)), 20000, stride = 1)
    canny_im = Image.fromarray(im)
    
    # Get vote for 0 degree angle - Vertical lines
    vertical_votes = Hough_voter(canny_im, 0, [0 for i in range(canny_im.width)])
    # Get vote for 90 degree angle - Horizontal lines
    horizontal_votes = Hough_voter(canny_im, 90, [0 for i in range(canny_im.height)])

    # removing first 600 horizontal lines which were voted by the Hough transform
    # from consideration.
    for i in range(600):
        horizontal_votes[i] = 0

    horizontal_pixels = [(idx, i) for idx, i in enumerate(horizontal_votes)]
    vertical_pixels = [(idx, i) for idx, i in enumerate(vertical_votes)]
    
    # As we are missing some question in the 3rd column of the question, which results in 
    # less votes for those lines and might not get choosen because of this issue. So 
    # to overcome this issue we are increasing the vote of any lines present below the
    # pixel number 1950 by 50 votes each. This seems to work well on all the test images.
    arr = []
    for i in horizontal_pixels:
        if i[0]> 1950:
            arr.append((i[0], i[1] + 50))
        else:
            arr.append((i[0], i[1]))
    horizontal_pixels = arr

    # Chose the best 250 and 80 votes horizontal and vertical lines
    horizontal_pixels = sorted(horizontal_pixels, key=lambda x:(x[1], x[0]), reverse = True)[:250]
    vertical_pixels = sorted(vertical_pixels, key=lambda x:(x[1], x[0]), reverse = True)[:80]

    # Sorting back based on the pixels locations and not votes
    horizontal_pixels = sorted(horizontal_pixels, key=lambda x:(x[0], x[1]), reverse = False)
    vertical_pixels = sorted(vertical_pixels, key=lambda x:(x[0], x[1]), reverse = False)
    
    return horizontal_pixels, vertical_pixels, norm_img

def get_lines(horizontal_pixels, vertical_pixels):
    # This part of the code extracts the vertical lines from the hough space based on the pixel
    # difference of 25 (or whatever was found dynamically) between consecutive lines.
    # This part works in a dynamic setting, where finding the best set of 30 lines/pixel 
    # which will form the vertical lines of the grid. the pixel difference will increase or 
    # decrease based on the number of vertical lines/pixels selected untill the desired 
    # number/set of pixels/lines is reached.
    new_vertical_pixels = []
    pixel_diff = 25
    verti_iter = 0
    min_len = 30
    best_verti_iter = None
    while True:
        verti_iter+=1
        prev = 0
        for i in vertical_pixels:
            i = i[0]
            if prev != 0:
                if i - prev < pixel_diff:
                    continue
            prev = i
            new_vertical_pixels.append(i)

        length = len(new_vertical_pixels)
        if abs(length - 30) < min_len:
            min_len = abs(length - 30)
            best_verti_iter = new_vertical_pixels.copy()

        if length == 30:
            break
        elif length < 30 : 
            pixel_diff -= 1
        else:
            pixel_diff += 1

        if veri_iter > 20:
            break
        # print(pixel_diff, length)
        new_vertical_pixels.clear()

    # This part of the code extracts the Horizontal lines from the hough space based on the 
    # pixel difference of 12 (or whatever was found dynamically) between consecutive lines.
    # This part works in a dynamic setting, where finding the best set of 30 lines/pixel 
    # which will form the horizontal lines of the grid. the pixel difference will increase or 
    # decrease based on the number of horizontal lines/pixels selected untill the desired 
    # number/set of pixels/lines is reached.
    new_horizontal_pixels = []
    pixel_diff = 12
    hori_iter = 0
    min_len = 58
    best_hori_iter = None
    while True:
        hori_iter += 1
        prev = 0
        for i in horizontal_pixels:
            i = i[0]
            if prev != 0:
                if i - prev < pixel_diff:
                    continue
            prev = i
            new_horizontal_pixels.append(i)

        length = len(new_horizontal_pixels)
        if abs(length - 58) < min_len:
            # print("min_len", min_len)
            min_len = abs(length - 58)
            # print("min_len after", min_len)
            best_hori_iter = new_horizontal_pixels.copy()
            # print("best_hori", min_len, len(best_hori_iter))

        if length == 58:
            break
        elif length < 58 : 
            pixel_diff -= 1
        else:
            pixel_diff += 1

        if hori_iter > 20:
            break
        # print(pixel_diff, length)
        new_horizontal_pixels.clear()

    # Here i have added a fall back option for selecting the jorizontal lines as we might have
    # lot of noice in the data or some random horizontal lines. So in order to avoid that 
    # situations i devised a way to find the horizontal lines starting from the last
    # line of the grid as the last line will always be the last lines where there are 
    # last question. So starting from that point i get alternative lines with pixel difference
    # less than 40 and 20, area of the box and the area between the boxes respectively.
    horizontal_pixels2 = horizontal_pixels.copy()
    horizontal_pixels2 = sorted(horizontal_pixels2, key=lambda x:(x[0], x[1]), reverse = True)
    new_arr = [horizontal_pixels2.pop(0)[0]]
    try:
        while True:
            temp = []
            first = new_arr[-1]
            while True and len(horizontal_pixels2) > 0:
                diff = abs(horizontal_pixels2[0][0] - first)
                if diff < 40:
                    temp.append(horizontal_pixels2.pop(0)[0])
                else:
                    break
            if len(horizontal_pixels2) == 0 and len(temp) == 0:
                break
            new_arr.append(min(temp))
            if len(horizontal_pixels2) == 0:
                break

            temp2 = []
            second = new_arr[-1]
            while True and len(horizontal_pixels2) > 0:
                diff = abs(horizontal_pixels2[0][0] - second)
                if diff < 20:
                    temp2.append(horizontal_pixels2.pop(0)[0])
                else:
                    break
            if len(horizontal_pixels2) == 0 and len(temp2) == 0:
                break
            if len(new_arr) == 58:
                break
            new_arr.append(max(temp2))
    except:
        pass
    if len(new_arr) == 58:
        best_hori_iter = new_arr
        
    return best_hori_iter, best_verti_iter

# this method helps dynamically find the threshold of the boxes which are marked by the 
# students as answers. The total intensity values are taken as an average over first 29 questions.
def find_threshold(norm_img, hori_arr, vl, error = False):
    min_sum = 0
    max_sum = 0
    for x in range(0, 58, 2):
        x1 = hori_arr[x]
        if error:
            x2 = x1+35 
        else:
            x2 = hori_arr[x+1]
        block_a = norm_img[x1:x2, vl[0]:vl[1]]
        block_b = norm_img[x1:x2, vl[2]:vl[3]]
        block_c = norm_img[x1:x2, vl[4]:vl[5]]
        block_d = norm_img[x1:x2, vl[6]:vl[7]]
        block_e = norm_img[x1:x2, vl[8]:vl[9]]
        arr = [np.sum(block_a), np.sum(block_b), np.sum(block_c),np.sum(block_d), np.sum(block_e)]
        min_sum+=min(arr)
        max_sum+=max(arr)
    # threshold = np.mean([min_sum/29, max_sum/29])
    return np.mean([min_sum/29, max_sum/29])
    # Deal with two cases: all boxes are unpainted and all boxes are smeared
    # if threshold < 100000 or threshold > 155000:
    #     threshold = 100000
    # return threshold

# Here we check if the student has marked the answers to some question in a handwritten format
# i am simply checking based on a threshold that if something has been marked and not just noise.
def check_marks(img, y1, y2, x1, x2):
    block = img[y1:y2, x1-120:x1-60]
    if np.sum(block)>10000:
        return True 
    else:
        return False

# This method identify the answers by block, which is used in the get_answers function
def get_answers_by_block(ques_ans, i, norm_img, best_hori_iter, 
                         best_verti_iter, size, f, e, threshold, error = False):
    vl = best_verti_iter[f:e]
    for x in range(0, size, 2):
        ans = ''
        x1 = best_hori_iter[x]
        if error:
            x2 = x1 + 35
        else:
            x2 = best_hori_iter[x + 1]
        # read the image by block
        block_a = norm_img[x1:x2, vl[0]:vl[1]]
        block_b = norm_img[x1:x2, vl[2]:vl[3]]
        block_c = norm_img[x1:x2, vl[4]:vl[5]]
        block_d = norm_img[x1:x2, vl[6]:vl[7]]
        block_e = norm_img[x1:x2, vl[8]:vl[9]]
        # identify the answers in a block
        if np.sum(block_a) > threshold:
            ans = ans + "A"
        if np.sum(block_b) > threshold:
            ans = ans + "B"
        if np.sum(block_c) > threshold:
            ans = ans + "C"
        if np.sum(block_d) > threshold:
            ans = ans + "D"
        if np.sum(block_e) > threshold:
            ans = ans + "E"
        # identify the written answer
        if check_marks(norm_img, x1, x2, vl[0], vl[1]):
            ans += " x"
        ques_ans[i] = ans
        i += 1
    return ques_ans, i

# Loop through all the boxes formed by the grid of vertical and horizontal lines and find the
# marked box based on the threshold and output it.
def get_answers(best_hori_iter, best_verti_iter, norm_img, error = False):
    if best_hori_iter[-1] < 800:
        best_hori_iter = best_hori_iter[::-1]
        
    ques_ans = {}
    vl = best_verti_iter[:10]
    threshold = find_threshold(norm_img, best_hori_iter, vl, error)
    i = 1
    ques_ans, i = get_answers_by_block(ques_ans, i, norm_img, best_hori_iter, best_verti_iter, 58, 0, 10, threshold, error)
    ques_ans, i = get_answers_by_block(ques_ans, i, norm_img, best_hori_iter, best_verti_iter, 58, 10, 20, threshold, error)
    ques_ans, i = get_answers_by_block(ques_ans, i, norm_img, best_hori_iter, best_verti_iter, 54, 20, len(best_verti_iter), threshold, error)
    return ques_ans

if __name__ == '__main__':
    # Load the scanned image
    # Read the image and preprocess it into grid
    # Output vertical and horizontal lines based on best votes
    horizontal_pixels, vertical_pixels, norm_img = preprocess(sys.argv[1])
    
    # id and match filled in boxes to questions
    # Best 30 and 58 set of vertical and horizontal lines resp.
    best_hori_iter, best_verti_iter = get_lines(horizontal_pixels, vertical_pixels)
    
    # id hand written answers
    # Try and catch to catch any exception and if nothing works then just output a 
    # hardcoded answer.
    try:
        ques_ans = get_answers(best_hori_iter, best_verti_iter, norm_img)
    except:
        try:
            ques_ans = get_answers(best_hori_iter, best_verti_iter, norm_img, True)
        except:
            ques_ans = {i:"A" for i in range(1, 86)}
            
    # generate final output of answers
    # print answers on form
    # combine and save in argv2
    string_answers=[]
    for key,val in ques_ans.items():
        string_answer = ""
        string_answers.append(str(key)+ " "+val+"\n")
    with open(sys.argv[2], 'w') as f:
        f.writelines(string_answers)
        f.close