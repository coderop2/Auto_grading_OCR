#Import the Image and ImageFilter classes
from PIL import Image
from PIL import ImageFilter
import sys
import random
import math

if __name__ == '__main__':
    # Load the form
    im = Image.open(sys.argv[1])
    # convert to grayscale
    gray_im = im.convert("L")
    
    # get correct answers and place in dict
    answers = {}
    with open(sys.argv[2]) as file:
        answer_list = file.readlines()
        for answer in answer_list:
            answer = answer.strip('\n').split(" ")
            answers[int(answer[0])] = answer[1]
                
    # shuffled order of 85 questions
    question_order_key = [51,66,53,64,59,47,78,20,21,57,40,26,24,69,68,60,35,85,52,79,8,76,73,44,81,36,38,23,33,75,58,13,22,4,14,25,80,30,67,1,9,45,27,15,77,70,61,84,62,63,18,46,41,6,82,32,50,12,72,19,11,37,56,39,49,71,34,29,28,31,43,65,48,10,3,7,16,17,42,83,74,54,2,5,55]
    
    # % length of each answer and segment (% of box height)
    answer_length = {'A':0.05,'B':0.10,'C':0.25,'D':0.20,'E':0.15}
    
    # draw box for print area
    top = 325
    bottom = 590
    left = 200
    right = 1450
    for i in range((right-left)+10):
        for j in range(10):
            gray_im.putpixel((left+i,top+j), 0)
            gray_im.putpixel((left+i,bottom+j), 0)
    for i in range(bottom-top):
        for j in range(10):
            gray_im.putpixel((left+j,top+i), 0)
            gray_im.putpixel((right+j,top+i), 0)
            
    # max height and length pixels available for printing answers with border of 10
    max_height = bottom-top-10
    max_width = right-left-10

    # spaces and widths for an 85 question exam
    num_questions = 85
    spaces = num_questions + 1
    bar_width = math.floor(max_width / (spaces + num_questions))
    
    # print answer bar codes in order of the question_order_key
    current_pos_horiz = left+10
    for q in question_order_key:
        current_pos_horiz+=bar_width
        current_pos_vert = top+10
        current_answer = [char for char in answers[q]]
        # randomize to get different order
        random.shuffle(current_answer)
        # calculate space allowed in between for mulitple answers
        space_taken = 1.0
        for c in current_answer:
            space_taken -= answer_length[c]
        in_between = math.floor(space_taken/(len(current_answer)+1)*max_height)
        # print bar codes
        for i in current_answer:
            current_pos_vert+=random.randint(math.floor(in_between/4), in_between)
            current_answer_length = math.floor(answer_length[i]*max_height)
            for j in range(current_answer_length):
                for k in range(bar_width):
                    gray_im.putpixel((current_pos_horiz+k,current_pos_vert+j), 0)
            current_pos_vert+=j
        current_pos_horiz+=bar_width
    
    # save answer sheet with coded answers
    gray_im.save(sys.argv[3])
