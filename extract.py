from PIL import Image
from PIL import ImageFilter
import random
import math
import numpy as np
import sys

# function to straighten and return top straight lines
def hough_straighten(im, straighten): 
    # convert to gray and find edges
    im = im.convert("L")
    gray_im = im.filter(ImageFilter.FIND_EDGES)

    # range of p and theta
    degree_increments = 5
    theta = np.deg2rad(np.arange(0, 180, 1/degree_increments))
    diagonal = math.ceil(np.sqrt(np.square(gray_im.width)+np.square(gray_im.height)))
    rs = np.linspace(-diagonal, diagonal, 2*diagonal+1)

    #theta x rhos array
    hough_space=np.zeros((len(rs), len(theta)))
    #vote for locations in hough space
    for i in range(10,gray_im.width-10):
        for j in range(10,gray_im.height-10):
            pixel = gray_im.getpixel((i,j))
            #for each edge pixel find each possible theta and rho
            if pixel > 100:
                if straighten == False:
                    for k in list(range(degree_increments * 1)) + list(range(degree_increments*89,degree_increments*91)) + list(range(degree_increments*179,degree_increments*180)):                
                        p = round(i*math.cos(theta[k]) + j*math.sin(theta[k]))
                        hough_space[int(p)+diagonal,k] += 1
                else:
                    for k in list(range(degree_increments*10)) + list(range(degree_increments*80,degree_increments*100)) + list(range(degree_increments*170,degree_increments*180)):                 
                        p = round(i*math.cos(theta[k]) + j*math.sin(theta[k]))
                        hough_space[int(p)+diagonal,k] += 1

    #find top straight lines
    hough_rho, hough_theta = hough_space.shape
    min_step = 20
    values = []
    for i in range(hough_rho):
        for j in range(hough_theta):
            values.append((i,j, hough_space[i,j]))
    values = sorted(values, reverse=True, key=lambda x: x[2])
    top_6 = top_x(6, values)
    if straighten == False:
        return [im,values]
    # list of angles of striaght lines
    angles = [i[1]/degree_increments for i in top_6]

    #get the longest line near 90 degrees and calculate amount needed to adjust
    angle_adjust = [i for i in angles if (i>45) & (i<135)]
    if len(angle_adjust) >= 3:
        current_angle = sum(angle_adjust)/len(angle_adjust)
        adjust_amount = 90-current_angle
    else:
        angle_adjust = [(180-i)*-1 if i >= 135 else i for i in angles]
        current_angle = sum(angle_adjust)/len(angle_adjust)
        adjust_amount = 0-current_angle
    #rotate image  
    im_rotate = im.rotate(-adjust_amount)
    return im_rotate

# function to calculate two best straight lines
def top_x(x, values):
    top_x = []
    for i in range(len(values)):
        if len(top_x) == x:
            break
        if len(top_x) == 0:
            top_x.append(values[i])
            continue
        for top in top_x:
            if (abs(values[i][0]-top[0]) < 100) & (abs(values[i][1]-top[1]) < 5):
                break
            else:
                top_x.append(values[i])
                break
    return top_x

if __name__ == '__main__':
    # Load the form
    im = Image.open(sys.argv[1])
    
    # name for output file
    new_file_name = sys.argv[2]
    
    #get top third of sheet
    im = im.crop((0, 0, im.width, int(im.height / 3)))
    
    # straighten the image and crop out edges from rotation
    im=im.filter(ImageFilter.SHARPEN)
    gray_im = hough_straighten(im, straighten=True)
    gray_im = gray_im.crop((50, 50, gray_im.width-50, gray_im.height-50))
    
    # get top lines
    crop_data = hough_straighten(gray_im, straighten=False)
    gray_im,crop_lines = crop_data[0], crop_data[1]
    
    # get hypotenuse length and increments for converting vertical and horizontal line locations
    hyp_len = math.ceil(np.sqrt(np.square(gray_im.width)+np.square(gray_im.height)))
    degree_increments = 5
    
    # get top two strongest lines in both directions
    vert_limits = top_x(2, [i for i in crop_lines if i[1] < (90*degree_increments) + degree_increments and i[1] > (90*degree_increments) - degree_increments])[:2]
    horiz_limits = top_x(2, [i for i in crop_lines if i[1] < 0 + degree_increments or i[1] > (180*degree_increments) - degree_increments])

    # crop to the best lines
    gray_im=gray_im.crop((min(i[0] for i in horiz_limits) - hyp_len, min(i[0] for i in vert_limits) - hyp_len, max(i[0] for i in horiz_limits) - hyp_len, (max(i[0] for i in vert_limits) - hyp_len)))
    
    # remove black outline - if any
    start_min_vert = False
    min_vert = 0
    for i in range(30):
        count=0
        for j in range(gray_im.width):
            if gray_im.getpixel((j,i))<150:
                count+=1
        if count > gray_im.width*0.5:
            start_min_vert = True
            min_vert = i
        elif start_min_vert == True:
            break

    start_max_vert = False
    max_vert = gray_im.height
    for i in reversed(range(gray_im.height-30, gray_im.height)):
        count=0
        for j in range(gray_im.width):
            if gray_im.getpixel((j,i))<150:
                count+=1
        if count > gray_im.width*0.5:
            start_max_vert = True
            max_vert = i
        elif start_max_vert == True:
            break

    start_min_horiz = False
    min_horiz = 0
    for i in range(30):
        count=0
        for j in range(gray_im.height):
            if gray_im.getpixel((i,j))<150:
                count+=1
        if count > gray_im.height*0.8:
            start_min_horiz = True
            min_horiz = i
        elif start_min_horiz == True:
            break
    
    start_max_horiz = False
    max_horiz = gray_im.width
    for i in reversed(range(gray_im.width-30, gray_im.width)):
        count=0
        for j in range(gray_im.height):
            if gray_im.getpixel((i,j))<150:
                count+=1
        if count > gray_im.height*0.8:
            start_max_horiz = True
            max_horiz = i
        elif start_max_horiz == True:
            break

    gray_im = gray_im.crop((min_horiz+3, min_vert+3, max_horiz-3, max_vert-3)) 
    
    # for an 85 question exam
    max_height = gray_im.height
    max_width = gray_im.width
    num_questions = 85
    spaces = num_questions + 1
    min_inbetween = math.floor((.25/6)*max_height)
    # % length of each answer and segment (% of box height)
    answer_length = {'A':0.05,'B':0.10,'C':0.25,'D':0.20,'E':0.15}
    # answer key
    question_order_key = [51,66,53,64,59,47,78,20,21,57,40,26,24,69,68,60,35,85,52,79,8,76,73,44,81,36,38,23,33,75,58,13,22,4,14,25,80,30,67,1,9,45,27,15,77,70,61,84,62,63,18,46,41,6,82,32,50,12,72,19,11,37,56,39,49,71,34,29,28,31,43,65,48,10,3,7,16,17,42,83,74,54,2,5,55]

    #calculate bar lengths
    region_size=3
    questions = np.arange(1,86)
    current_pos_horiz = 0
    final_answers = {}
    current_pos_horiz = 0
    total=[]
    while current_pos_horiz < gray_im.width-region_size:
        current_pos_vert = min_inbetween
        current_bar = []
        for i in range(0,gray_im.height):
            values=[]
            for j in range(region_size):
                values.append(gray_im.getpixel((current_pos_horiz+j,i)))
            avg_value = sum(values)/len(values)
            current_bar.append(avg_value)
        ranges = []
        k=0
        while k < len(current_bar)-region_size:
            mean_region = sum(current_bar[k:k+region_size])/region_size
            if mean_region > 150:
                ranges.append((k,0))
            else:
                ranges.append((k,1))
            k+=1
        answer_percent=[]
        l=1
        while l < len(ranges):
            if (ranges[l][1] == 1) & (ranges[l-1][1] == 0):
                start = 1
            elif (ranges[l][1] == 1) & (ranges[l-1][1] == 1):
                start += 1
            elif (ranges[l][1] == 0) & (ranges[l-1][1] == 1):
                percent_of_height = start/(max_height-20)
                answer_percent.append(percent_of_height)
                start=0
            l+=1
        total.append(answer_percent)
        current_pos_horiz+=1
 

    #determine best bar lengths for each bar group
    first = 0
    start = 0
    end = 0
    final_lengths = []
    total[0]=[]
    x=0
    while x < len(total):
        if first == 0:
            if len(total[x]) == 0:
                first=1
                x+=1
            continue
        if len(total[x]) > 0:
            if start == 0:
                start=x
        else:
            if start > 0:
                end = x-1
                diff = np.floor((end-start)/2)
                middle = int(end-diff)
                question_len=total[middle]
                if min(question_len) < 0.04:
                    x+=1
                    continue
                final_lengths.append(question_len)
                start=0
                end=0
        # determine letter grades for each bar
        x+=1
    question=1
    for m_list in final_lengths:
        letter_answers = []
        for m in m_list:
            if (m < answer_length['A'] + 0.025) & (m > answer_length['A'] - 0.025):
                letter_answers.append("A")
            elif (m < answer_length['B'] + 0.025) & (m > answer_length['B'] - 0.025):
                letter_answers.append("B")
            elif (m < answer_length['C'] + 0.025) & (m > answer_length['C'] - 0.025):
                letter_answers.append("C")
            elif (m < answer_length['D'] + 0.025) & (m > answer_length['D'] - 0.025):
                letter_answers.append("D")
            elif (m < answer_length['E'] + 0.025) & (m > answer_length['E'] - 0.025):
                letter_answers.append("E")
        letter_answers = sorted(letter_answers)
        cur_number = question_order_key[question-1]
        final_answers[cur_number] = letter_answers
        question+=1
        
    # save answers to file
    string_answers=[]
    for i in range(1,86):
        string_answer = ""
        for j in final_answers[int(i)]:
            string_answer=string_answer + j
        string_answers.append(str(i)+ " "+string_answer+"\n")
    
    with open(new_file_name, 'w') as f:
        f.writelines(string_answers)
        f.close
