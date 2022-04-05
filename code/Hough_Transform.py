import math
from PIL import Image
from PIL import ImageFilter
import numpy as np

# This method is used to transform an image into hough space for line detection
def HoughLines(img, lineMax):
    # Range of rhos and thetas
    width, height = img.shape
    diagonal = math.ceil((math.sqrt(math.pow(width, 2) + math.pow(height, 2))))
    ps = np.linspace(-diagonal, diagonal, 2 * diagonal)
    thetas = np.deg2rad(np.arange(0, 180))
    print(len(thetas))
    # Vote in the hough space
    vote = np.zeros((len(ps), len(thetas)))
    y, x = np.nonzero(img)
    print(len(y))
    for i in range(len(x)):
        for t in range(len(thetas)):
            # p = x*cos()+y*sin()
            p = round(x[i] * math.cos(thetas[t]) + y[i] * math.sin(thetas[t]))
            vote[int(p) + diagonal, t] += 1

    voteList = []
    for p in range(len(ps)):
        for t in range(len(thetas)):
            voteList.append((p, t, vote[p,t]))
    voteList = sorted(voteList, reverse=True, key= lambda v: v[2])
    datas = []
    for i in range(lineMax):
        v = voteList[i]
        idx = v[2]
        p = ps[v[0]]
        theta = np.rad2deg(thetas[v[1]])
        datas.append((idx,p,theta))
    return datas
