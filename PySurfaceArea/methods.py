import cv2
import numpy as np
from os import listdir
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets  import RectangleSelector
from matplotlib.path import Path
import time
from scipy.ndimage import imread

# Opens the image
def show(file):
    new_name = file+".png"
    open_file = cv2.imread(file)
    cv2.imwrite(new_name, open_file)
    img = cv2.imshow(new_name)
    return new_name

def pointsInsideShape(tupVerts, img):
    h, w, c = img.shape
    poly = np.zeros((int(h), int(w)), np.int8)
    cv2.fillPoly(poly, tupVerts, (255, 255, 255))
    mask = cv2.bitwise_and(img, img, mask = poly)
    s = np.array(mask)
    mask_nozeroes = s > 0
    if mask_nozeroes.any():
        _mean = int(s[mask_nozeroes].mean())
        _min = int(s[mask_nozeroes].min())
        _max = int(s[mask_nozeroes].max())
        _stdev = int(s[mask_nozeroes].std())
    print(_min, _max, _mean, _stdev)
    return _min, _max, _mean, _stdev

def selectBackground(fileToOpen):
    # Declate a list to take coordiantes of plotted points
    coordinate_list = []

    # mouse callback function to draw points on the image
    def draw_circle(event, x, y, flags, param):
        # sert font of test overlay
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x+10, y)
        fontScale = 0.4
        fontColor = (255, 255, 255)
        lineType = 1

        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(img_resized, (x, y), 5, (0, 0 , 255), -1)
            cv2.putText(img_resized, str(x)+", "+str(y), bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
            coordinate_list.append([x,y])
            cv2.polylines(img_resized, np.array([coordinate_list], np.int32), True, (0,255,255), 2)

    # Write the image to the window canvas and initiate the plotting method
    _min, _max, _mean, _stdev = 255,255,255,255

    img_orig = cv2.imread(fileToOpen)
    h, w, c = img_orig.shape
    sub_x = 400.0/float(w)
    sub_y = 400.0/float(h)
    img_resized = cv2.resize(img_orig, None, fx=sub_x, fy=sub_y)
    img_resized_2 = img_resized.copy()

    cv2.namedWindow('No Dust - Select Area, press Q when done')
    cv2.setMouseCallback('No Dust - Select Area, press Q when done', draw_circle)

    # Keep running the method until boolean conditions are satisfied
    while (1):
        cv2.imshow('No Dust - Select Area, press Q when done', img_resized)
        if (cv2.waitKey(20) & 0xFF == ord('q')):
            cv2.imshow('No Dust - Select Area, press Q when done', img_resized)
            time.sleep(1)
            cv2.destroyAllWindows()
            break

    _min, _max, _mean, _stdev = pointsInsideShape(np.array([coordinate_list], np.int32), img_resized_2)

    return _min, _max, _mean, _stdev


# Takes an image and converts it to binary based on threshold, returns a converted image
def binaryImage(image, slider, zeroes):
    im_gray = cv2.imread(image,0)
    h, w = im_gray.shape

    #min_value = np.min(img_arr)
    min_value = zeroes
    max_value = np.max(im_gray)
    datarange = max_value-min_value

    im_gray[im_gray < zeroes] = 0

    if slider < zeroes:
        slider = zeroes

    def normalize(x):
        norm = (x/float(datarange))
        norm[norm<(zeroes/datarange)]=0
        return norm

    def rgbvalue(x):
        return x * 255

    def sigmoid(x):
        # Change the sigmoid range
        v = (x * 10)-5
        # Apply sigmoid surface area dust coverage correction
        s = 1/(1 + np.exp(-0.5*v))
        return s
    
    # Automatically calculates the bianry image based on auto-threshold function (Otsu Thresh)
    blur = cv2.GaussianBlur(im_gray, (5, 5), 0)
    # cv2.imshow("test", im_gray)
    ret, thresh = cv2.threshold(blur,int(slider),255,cv2.THRESH_BINARY)
    # thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
             # cv2.THRESH_BINARY,11,1)
    # im_bw[im_bw > np.average(datarange)] = 255
    masked_arr = cv2.bitwise_and(blur, blur, mask = thresh)
    # cv2.imshow("test", masked_arr)
    norm_masked_arr = normalize(masked_arr)
    norm_thresh = normalize(thresh)
    coverage, occupied = surfaceAreaCoverage(norm_masked_arr, norm_thresh)

    # final_img = rgbvalue(normalized_arr)

    return masked_arr, thresh, coverage, occupied

    # else:
    #     # Zoeroes out the pixels below threshold based on threshold value provided
    #     thresh = thresh_manual
    #     normalized_arr = normalize(im_gray)
    #     normalized_arr[normalized_arr<(thresh/100)] = 0
    #     normalized_arr[normalized_arr>(thresh/100)] = 1
    #     coverage = surfaceAreaCoverage(normalized_arr)
    #     final_img = rgbvalue(normalized_arr)
    #     return final_img, coverage

# Calculates surface area coverage from the black and white image provided
def surfaceAreaCoverage(image_bw, thresh):
    img_arr = np.array(image_bw) # convert image to numpy array
    total_pixels = img_arr.size  # count total pixels in array

    #Gradient calculation
    soiled_pixels = np.sum(img_arr)
    ratio = float(soiled_pixels)/float(total_pixels)
    percent_soiled = '%.2f'%((ratio)*100) # calculate percent pixels

    #Gradient calculation
    occupied_pixels = np.sum(thresh)
    ratio2 = float(occupied_pixels)/float(total_pixels)
    percent_pixels = '%.2f'%((ratio2)*100) # calculate percent pixels

    return percent_soiled, percent_pixels

def IterateDirectory(fileToOpen):
    file_list = sorted(listdir(fileToOpen))
    return file_list