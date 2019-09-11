import cv2
import numpy as np
import imutils
from PIL import Image

def extract_diameter_and_location(curr_drop_trail_mask, pixel_to_mm_ratio_x, prev_plate_BGR, file_name, video_dir):

    method = "--None--"
    adjusted_mask = np.array(curr_drop_trail_mask, dtype=np.uint8)
    int_prev_plate_BGR = prev_plate_BGR
    masked_image = cv2.bitwise_and(int_prev_plate_BGR, int_prev_plate_BGR, mask=adjusted_mask)

    def detect_circular_drops():
        # Detect circles in the images traced by the mask
        img = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
        #img = cv2.medianBlur(img, 3)
        cv2.imshow("Masked Image", img)
        ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        circles = cv2.HoughCircles(thresh, cv2.HOUGH_GRADIENT, 1,20,
                        param1=100,param2=30,minRadius=0,maxRadius=0)
        print(circles)
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:

            diameter = i[2] * 2
            x, y = int(i[0]), int(i[1])
            # draw the outer circle
            cv2.circle(img, (x, y), int(diameter/2), (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(img, (x, y), 2, (0, 0, 255), 3)

        cv2.imshow("Masked Image", img)
        print("complex method circle detection used")

    def detect_drop_by_contours():
        MIN_THRESH = 1
        im = masked_image
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        #ret, thresh = cv2.threshold(imgray, 100, 255, 0)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        ret, thresh = cv2.threshold(blurred,127,255,cv2.THRESH_BINARY)
        #thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 21, 2)

        #edged = cv2.Canny(blurred, 50, 150)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                         cv2.CHAIN_APPROX_SIMPLE)
        #cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                # cv2.CHAIN_APPROX_SIMPLE)
        if len(cnts) == 0:
            empty_array = []
            return empty_array
        else:
            cnts = cnts[0] if imutils.is_cv2() else cnts[1]

            # loop over the contours
            param_list = []
            for c in cnts:
                if cv2.contourArea(c) > MIN_THRESH:
                # Process the contour
                    # Compute the center of the contour
                    M = cv2.moments(c)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])

                    # Get area
                    area = cv2.contourArea(c)

                    # Compute the diameter - area of circle = Pi * r ^2
                    diameter = np.sqrt(area / np.pi) * 2
                    param_list.append([cY, cX, area, diameter])

                    # Draw the contour and center of the shape on the image
                    # cv2.drawContours(int_prev_plate_BGR, [c], -1, (0, 255, 0), 1)
                    # cv2.circle(int_prev_plate_BGR, (cX, cY), int(diameter/2), (255, 0, 0), 1)
            # Write images
            # write_image_file_path = video_dir + str(file_name) + "- MASKED" + ".jpg"
            # image_to_save = Image.fromarray(im)
            # image_to_save.save(write_image_file_path)
            # cv2.imshow("Masked Image", int_prev_plate_BGR)
            # cv2.imshow("Threshold", thresh)
            top_drop = sorted(param_list, key=lambda x: x[0])[0]
            return top_drop

    def detect_drop_based_on_mask():

        # Get simple drop diameter
        refactored_array = [i for i in curr_drop_trail_mask if np.sum(i) > 0]
        g = len(curr_drop_trail_mask) - len(refactored_array)
        n = int(g + 50)
                #len(np.nonzero(refactored_array[20])
                      #))
        diameter = np.average([np.sum(i) for i in refactored_array[0:n]])
        #diameter = diameter*(1/np.sqrt(3))
        diameter_mm =  (diameter)/pixel_to_mm_ratio_x

        # get y coordinates (counting pixels from the top)
        confirm_status = 0
        x, y = 0 ,0
        #for y in mask_array:
        if np.sum(curr_drop_trail_mask) > 0:
            for y_coordinate in curr_drop_trail_mask:
                if np.sum(y_coordinate) == 0:
                    y += 1
                else:
                    # get x coordinates at y coordinates value
                    median_value = 0
                    for x_coordinate in y_coordinate:
                        if x_coordinate == 0:
                            x += 1
                        else: break
                    for x_coordinate in y_coordinate:
                        if x_coordinate > 0:
                            median_value += 1
                    x += median_value/2
                    break
            y += 35

        x, y = int(x), int(y)
        # draw the outer circle
        # img = masked_image
        #cv2.circle(img, (x, y), int(diameter/2), (0, 255, 0), 2)
        # draw the center of the circle
        # cv2.circle(img, (x, y), 2, (0, 0, 255), 3)
        # cv2.imshow("Masked Image", img)
        # Write images
        # write_image_file_path = video_dir + str(file_name)+"-MASKED" + ".jpg"
        # image_to_save = Image.fromarray(img)
        # image_to_save.save(write_image_file_path)
        return x, y, diameter, diameter_mm

    # Get resultant values from the method and set as return values for the parent method
    _y, _x, _area, _diameter = 0 ,0 ,0 ,0

    # try:
    #     _y, _x, _area, _diameter = detect_drop_by_contours()
    try:
        _y, _x, _area, _diameter = detect_drop_based_on_mask()
    except:
        _y, _x, _area, _diameter = 0, 0, 0, 0


    # Convert diameter to mm
    diameter_mm = _diameter

    return [int(_diameter), diameter_mm, int(_x), int(_y), method]

