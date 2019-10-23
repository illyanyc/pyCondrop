import csv
import shutil
import os
from pathlib import Path
from tqdm import tqdm
import cv2
import numpy as np
import imutils
import pyglet
import time

global location

def setLocation(_filename):
    global location
    location = _filename

def MakeVideo(dir, videoname, format, csv_file_path, image_path, fpm, set_bounds, angle):

    # Print init text
    print ("Making video: " + str(videoname))
    print ("File path: " + str(image_path))

    # set process to work
    work = True

    # sort all directory files in aphabetical order
    dirfiles = []
    for root, dirs, files in os.walk(image_path):
        dirs.sort()
        for filename in files:
            #print(filename)
            if filename.endswith(".jpg"):
                dirfiles.append((os.path.join(root, filename)))
            if filename.endswith(".tif"):
                dirfiles.append((os.path.join(root, filename)))
            if filename.endswith(".JPG"):
                dirfiles.append((os.path.join(root, filename)))
    #print(dirfiles)
    # set video window frame size
    image = dirfiles[0]
    #print image
    img = cv2.imread(image)

    height, width, channels = img.shape

    dirfiles = sorted(dirfiles)

    # set video file name and path
    videooutput = dir + videoname + format

    # check if the video file with same name already exists
    my_file = Path(videooutput)
    if my_file.is_file():
        print ("Video file name is already taken! Please chose a different file name...")
        work = False # if yes set work to false and abort

    # set dir for refined image output
    ref_img_path = image_path
    ref_img_dir = ref_img_path+ str("/Refined Images/")

    try:
        os.makedirs(ref_img_dir)
    except:
        shutil.rmtree(ref_img_dir)
        os.makedirs(ref_img_dir)


    frame = cv2.imread(dirfiles[1])
    coordinates = []
    def Set_image_bounds(event, x, y, flags, param): # method that splits the screen into areas for analysis
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x+10, y)
        fontScale = 0.4
        fontColor = (255, 255, 255)
        lineType = 1

        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(frame, (x, y), 5, (0, 0 , 255), -1)
            cv2.putText(frame, str(x)+", "+str(y), bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
            coordinates.append([int(x*2),int(y*2)])

    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
    cv2.imshow('Set Up The Feature Areas', frame)
    cv2.setMouseCallback('Set Up The Feature Areas', Set_image_bounds)  # Set bounds for video

    if set_bounds == True:

        while (1):
            cv2.imshow('Set Up The Feature Areas', frame) # show frame
            if cv2.waitKey(20) in [ord('p'), ord('P')]: # if P is pressed close
                cv2.imshow('Set Up The Feature Areas', frame)
                cv2.destroyAllWindows()
                break

    x_list = []
    y_list = []
    for i in coordinates:
        x_list.append(i[0])
        y_list.append(i[1])

    y1 = np.min(y_list)
    y2 = np.max(y_list)
    x1 = np.min(x_list)
    x2 = np.max(x_list)

    coordinates = y1, y2, x1, x2

    # Process files
    if work == True:
        print ("Processing, please wait...")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(videooutput, fourcc, 20.0, (x2-x1, y2-y1))

        count = 0
        sec = 0
        min = 0
        hr = 0
        total = len(dirfiles)
        #printProgressBar(0, total, prefix='Progress:', suffix='Complete', length=50)
        data_read = []

        # with open(csv_file_path, "r") as csvfile:
        #     csv_file = csv.reader(csvfile, delimiter=',')
        #     data_read = [row for row in csv_file]

        counter = 0
        ref_img_count = 1
        pbar_increment = 1
        pbar = tqdm(total=len(dirfiles))

        for image in dirfiles:
            y_top, y_bottom, x_left, x_right = coordinates
            # count frames for time-stamp in video - convert to hh:mm:ss


            sec = sec + fpm*60

            if sec == 60 or sec > 59:
                min = min + 1
                sec = 0

            # min = min + fpm
            if min == 60:
                hr = hr + 1
                min = 0

            printtime = "{:02d}:{:02d}:{:02d}".format(hr, int(min), int(sec)) # generate time string to print


            # try:
            #     row = data_read[counter]
            #     text = videoname + "; Time: " + printtime + "; % Area Cleaned: " + str(row[2]) + " %"
            # except:
            text = "Time [hh:mm:ss] : " + printtime

            img = cv2.imread(image) # get image

            if angle != 0:
                img = imutils.rotate(img, angle)
                #img = imutils.rotate_bound(rotated, angle)
                #cv2.imshow("Rotated", img)



            img = img[y_top:y_bottom, x_left:x_right, :].copy()

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

            # set font of test overlay
            x_max = x_right - x_left
            y_max =  y_bottom - y_top

            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = (x_max - int((x_max * 0.9)), y_max - 25)
            topLeftCornerOfText = (x_max - int((x_max * 0.9)), y_max - int((y_max * 0.85)))
            fontScale = x_max / 1000
            fontColor = (0,0,0)
            lineType = 1


            # write time-string to image
            cv2.putText(img, text , bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
            counter = counter + 1

            video.write(img) # write image to video
            ref_img_name = "None"
            if ref_img_count >999:
                ref_img_name = "Time-" + str(ref_img_count) + "-min.jpg"  # refined image name
            elif ref_img_count >99:
                ref_img_name = "Time-0" + str(ref_img_count) + "-min.jpg"  # refined image name
            elif ref_img_count < 10:
                ref_img_name = "Time-000"+str(ref_img_count)+"-min.jpg" # refined image name
            else:
                ref_img_name = "Time-00" + str(ref_img_count) + "-min.jpg"  # refined image name

            cv2.imwrite(ref_img_dir+ref_img_name, img) # write refined image
            ref_img_count = ref_img_count + 1 # advance refined image counter
            pbar.update(pbar_increment) # update progress bar

        print ("Complete!")
        pbar.close()
        cv2.destroyAllWindows()
        video.release()
        #shutil.rmtree(image_path)

def MakeVideo_withCaption(dir, videoname, format, csv_file_path, image_path, locations_of_tag):

    # Print init text
    print("Making video: " + str(videoname))
    print("File path: " + str(image_path))

    # set process to work
    work = True

    # sort all directory files in aphabetical order
    dirfiles = []
    for root, dirs, files in os.walk(image_path):
        dirs.sort()
        for filename in files:
            # print(filename)
            if filename.endswith(".jpg"):
                dirfiles.append((os.path.join(root, filename)))
            if filename.endswith(".tif"):
                dirfiles.append((os.path.join(root, filename)))
            if filename.endswith(".TIFF"):
                dirfiles.append((os.path.join(root, filename)))
            if filename.endswith(".JPG"):
                dirfiles.append((os.path.join(root, filename)))
    # print(dirfiles)
    # set video window frame size
    image = dirfiles[0]
    # print image
    img = cv2.imread(image)

    height, width, channels = img.shape

    dirfiles = sorted(dirfiles)

    # set video file name and path
    videooutput = dir + videoname + format

    # sert font of test overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (width - int((width * 0.9)), height - 12)
    topLeftCornerOfText = (width - int((width * 0.9)), height - int((height * 0.9)))
    fontScale = 2
    fontColor = (0, 0, 255)
    lineType = 2

    # check if the video file with same name already exists
    my_file = Path(videooutput)
    if my_file.is_file():
        print("Video file name is already taken! Please chose a different file name...")
        work = False  # if yes set work to false and abort

    # set dir for refined image output
    ref_img_path = image_path
    ref_img_dir = ref_img_path + str("/Refined Images/")

    try:
        os.makedirs(ref_img_dir)
    except:
        shutil.rmtree(ref_img_dir)
        os.makedirs(ref_img_dir)

    # Process files
    if work == True:
        print("Processing, please wait...")

        video = cv2.VideoWriter(videooutput, 1, 16, (width, height)) # init the video

        # read the csv file with data
        with open(csv_file_path, "r") as csvfile:
            csv_file = csv.reader(csvfile, delimiter=',')
            data_read = [row for row in csv_file]

        counter = 1 # frame counter
        pbar_increment = 1 # progress bar inrement init
        pbar = tqdm(total=len(dirfiles)) # progress bar lenght init

        number_of_areas = len(locations_of_tag) # get number of hydrophilic areas
        drop_counter_dict = {} # declare dictionary to kee track of the counter

        # init the dictionary with number of hydrophilic areas
        for i in range(1,number_of_areas+1):
            drop_counter_dict[str(i)]=0

        for image in dirfiles:
            img = cv2.imread(image)  # get image
            area_counter = 1
            try:
                for i in locations_of_tag:
                    loc = i

                    # read the csv and get the data for the notations on the video
                    row = data_read[counter]
                    csv_value = row[area_counter]

                    calculated_value = None # init calcualted value parameter

                    # identify if new drop slide off event has occured
                    if None == csv_value or csv_value == "" or csv_value == 0:
                        calculated_value = drop_counter_dict[str(area_counter)]
                    else:
                        past_value = drop_counter_dict[str(area_counter)]
                        new_value = past_value + int(csv_value)
                        drop_counter_dict[str(area_counter)] = new_value
                        calculated_value = new_value

                    text = str(calculated_value)
                    # write counter of right drop
                    cv2.putText(img, text, loc, font, fontScale, fontColor, lineType)
                    area_counter = area_counter + 1

                video.write(img)  # write image to video

                pbar.update(pbar_increment)  # update progress bar

                counter = counter + 1
            except:
                pass

        print("Complete!")
        pbar.close()
        cv2.destroyAllWindows()
        video.release()
        # shutil.rmtree(image_path)

def MakeVideo_wScaleBar(file_to_find, form, um500, sb_height, mu, scale, view, pic):

    file = dict[file_to_find][0]+file_to_find+form

    # set up video capture
    vidcap = cv2.VideoCapture(file)
    success,image = vidcap.read()
    frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    vidtime = vidcap.get(cv2.CAP_PROP_POS_MSEC)
    print(frames, fps, vidtime)

    # get frame parameters
    width = np.size(image, 1)
    height = np.size(image, 0)

    # set up video output
    writer = cv2.VideoWriter(filename=dict[file_to_find][0] + file_to_find + "_SECFRAME" + form,
                             fourcc=-1,  # this is the codec that works for me
                             fps=30,  # frames per second, I suggest 15 as a rough initial estimate
                             frameSize=(width, height))

    # set up scale parameters
    scale_bar_width = height*um500
    scale_bar_height = height*sb_height
    scale_bar_pt1 = (int(width-scale_bar_width-170),int(height-scale_bar_height-38))
    scale_bar_pt2 = (int(width-170),int(height-38))
    text_loc = (int(width-170-scale_bar_width*0.9),int(height-7))
    print(str(width),str(height))

    count = 0
    counttime = 0
    start = 0
    min = 0

    while success:

        time_now = counttime
        delta = time_now - start
        if delta > 60:
            min = min + 1
            start = start+60
            delta = 0

        counttime = counttime + 1/fps

        print_time = str(min) + ":" + str("%.1f" % delta)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # cv2.rectangle(image, (0, int(height-scale_bar_height-45)), (width, height), (0,0,0), cv2.FILLED)
        # cv2.rectangle(image, scale_bar_pt1, scale_bar_pt2, (255,255,255), cv2.FILLED)
        # font = cv2.FONT_HERSHEY_DUPLEX  # color
        #
        # cv2.putText(image, scale, text_loc, font, 1, (255,255,255), 2)
        # cv2.putText(image, print_time, (180,int(height-15)), font, 1, (255,255,255), 2)


        writer.write(image)

        if view:
            cv2.imshow("Output", image)

        if pic:
            cv2.imwrite("frame%d.jpg" % count, image)



        success,image = vidcap.read()

        # print("Read frame: "+ str(count))
        count += 1

        if cv2.waitKey(1) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()
    cv2.VideoCapture(0).release()
    writer.release()

def CountDrops(videofile, csv_dir, name, path):
    # declare all the frames
    current_frame_w = 'Current'
    previous_frame_mask_w = 'Previous Mask'
    two_frames_frame_mask_w = 'Two Frames Before Mask'
    video_w = 'Video'
    difference_w = 'Difference'

    # create folders for video process files
    video_dir = path + "/" + str(name) + str("-StillImages/")
    video_dir_circle = video_dir + str("/OutlinesCircles/")
    video_dir_trace = video_dir + str("/TracedImages/")
    video_dir_difference = video_dir + str("/Difference/")
    init_csv(str(name) + str("-DropAreas"), path)
    path_arr = [video_dir, video_dir_circle, video_dir_trace, video_dir_difference]
    try:
        for i in path_arr:
            os.makedirs(i)
    except:
        shutil.rmtree(path_arr[0])
        for i in path_arr:
            os.makedirs(i)


    # init all the params
    #region
    set_csv = csv_dir+name+".csv"
    boundaries_list = []
    cap = cv2.VideoCapture(videofile)
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    flag, fr = cap.read()
    frame = cv2.resize(fr, None, fx=0.8, fy=0.8)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    cv2.imshow('Set Up The Feature Areas', frame)
    temp_list = []
    #endregion
    # method to id the hydrophilic region areas
    def set_feature_areas(event, x, y, flags, param): # method that splits the screen into areas for analysis
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x+10, y)
        fontScale = 0.4
        fontColor = (255, 255, 255)
        lineType = 1

        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(frame, (x, y), 5, (0, 0 , 255), -1)
            cv2.putText(frame, str(x)+", "+str(y), bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
            boundaries_list.append(x)

    # method to record the slide event (drop roll off event)
    def record_drop(event, x, y, flags, param): # record the position of drop
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (x + 10, y)
        fontScale = 0.6
        fontColor = (0,0,0)
        lineType = 2

        if event == cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(frame, (x, y), 8, (0, 0, 255), 3)
            # cv2.putText(frame, str(x) + ", " + str(y), bottomLeftCornerOfText, font, fontScale, (0, 0, 255), lineType)
            temp_list.append([x,"Jump",y])

        if event == cv2.EVENT_RBUTTONDBLCLK:
            cv2.circle(frame, (x, y), 8, (255, 0 , 0), 3)
            # cv2.putText(frame, str(x)+", "+str(y), bottomLeftCornerOfText, font, fontScale, (255, 0 , 0), lineType)
            temp_list.append([x,"Slide",y])

    cv2.setMouseCallback('Set Up The Feature Areas', set_feature_areas) # Write the image to the window canvas and initiate the plotting method

    # run the method to id the feature regions
    while (1):

        cv2.imshow('Set Up The Feature Areas', frame) # show frame

        if cv2.waitKey(20) in [ord('p'), ord('P')]: # if P is pressed close
            cv2.imshow(video_w, frame)

            cv2.destroyAllWindows()
            break

    boundaries_list.append(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # add last point to boudaries list which is same a frame width
    boundaries_list = sorted(boundaries_list) # sort boundaries_list descending

    # get difference between two frames
    def diff(frame, last_frame):
        result = cv2.absdiff(frame,last_frame)
        return result

    # instatiate the csv file
    with open(set_csv, 'a') as out:
        counter = 0
        line = ["Frame Number"]
        for i in range(0,len(boundaries_list)):
            line.append("Area: "+str(i))
            counter += 1
        w = csv.writer(out)
        w.writerow(line)


    # write point(s) to csv file
    def WritePointToCSV(point_list, frame_number):
        point_list = sorted(point_list) # sort the point list
        number_or_rows = len(boundaries_list) #  set number of setions
        # print(number_or_rows)
        # print(boundaries_list)
        print(point_list) # print the list for verification

        #build dictionary
        dict = {}
        for i in range(0,number_or_rows):
            dict[i]={"Jump":0,"Slide":0,"JumpLoc":[(0,0)],"SlideLoc":[(0,0)]}

        # add values to dictionary comparing them to the boudaries
        for j in point_list:
            point_location = j[0]
            point_type = j[1]

            p_x = j[0]
            p_y = j[2]
            for i in range(0,len(boundaries_list)):

                low_thresh = 0
                if i > 0:
                    low_thresh = boundaries_list[i-1]
                high_thresh = boundaries_list[i]

                if  point_location <= high_thresh and point_location > low_thresh:

                    if point_type == "Jump":
                        current = dict[i]["Jump"]
                        dict[i]["Jump"] = current + 1
                        arr = dict[i]["JumpLoc"]
                        arr.append((p_x, p_y))
                        dict[i]["JumpLoc"] = arr



                    if point_type == "Slide":
                        current = dict[i]["Slide"]
                        dict[i]["Slide"] = current + 1
                        arr = dict[i]["SlideLoc"]
                        arr.append((p_x, p_y))
                        dict[i]["SlideLoc"] = arr

                    # point_list.remove(j)
        print(dict)

        # build string from dictionary
        counter_for_string_builder = 1
        line = [str(frame_number)]
        for i in range(0,number_or_rows):
            line.append(str(dict[i]))

        with open(set_csv, 'a') as out:
            w = csv.writer(out)
            w.writerow(line)

    # iterate through frames and id slide-off events
    frame_number = 2
    last_frame = None
    two_frames_ago = None
    last_frame_bool = False
    two_frames_ago_bool = False
    contours_twoframes = None
    contours_oneframe = None
    difference_frame = None
    print_fps = True
    area_list = []
    while True:
        flag, frame = cap.read()
        fps = cap.get(cv2.CAP_PROP_FPS)
        if print_fps:
            print("FPS: "+str(fps))
            print_fps = False

        frame = cv2.resize(frame, None, fx=0.8, fy=0.8)

        if flag:
            temp_list.clear()
            # The frame is ready and already captured
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5)

            if last_frame_bool:
                if two_frames_ago_bool:
                    # difference between two frames - current and two frame ago
                    difference = diff(two_frames_ago, frame)
                    difference = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)
                    difference = np.array(difference)
                    difference[difference < 25] = 0
                    difference[difference > 210] = 255
                    thresh_difference = difference
                    blur = cv2.GaussianBlur(difference, (5, 5), 0)
                    ret2, thresh2 = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
                    # thresh3 = cv2.adaptiveThreshold(thresh_difference,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
                    im2, contours_twoframes, hierarchy2 = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    # hull = cv2.convexHull(contours_twoframes)
                    # contours_a = contours_twoframes
                    difference = cv2.cvtColor(difference, cv2.COLOR_GRAY2BGR)
                    cv2.drawContours(difference, contours_twoframes, -1, (0, 255, 0), 1)

                    # difference between two frames - current and one frame ago
                    difference2 = diff(last_frame, frame)
                    difference2 = cv2.cvtColor(difference2, cv2.COLOR_BGR2GRAY)
                    difference2 = np.array(difference2)
                    difference2[difference2 < 40] = 0
                    difference2[difference2 > 150] = 255
                    thresh_difference = difference2
                    blur2 = cv2.GaussianBlur(difference2, (5, 5), 0)
                    ret3, thresh3 = cv2.threshold(blur2, 40, 255, cv2.THRESH_BINARY)
                    # thresh3 = cv2.adaptiveThreshold(thresh_difference,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
                    im3, contours_oneframe, hierarchy3 = cv2.findContours(thresh3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    # hull2 = cv2.convexHull(contours_oneframe)
                    # contours_b = contours_oneframe
                    cv2.drawContours(difference, contours_oneframe, -1, (0,0,255), 1)

                    # get contours areas: https://docs.opencv.org/3.1.0/dd/d49/tutorial_py_contour_features.html
                    feature_count = 0
                    for i in contours_oneframe:
                        area = cv2.contourArea(i)
                        perimeter = cv2.arcLength(i, True)
                        area_arr = [str(frame_number), str(feature_count), str(area), str(perimeter)]
                        # area_join = ",".join(area_arr)
                        # area_list.append(area_join)
                        feature_count += 1
                        write_data_to_csv(area_arr)
                        # area_list.clear()


                    cv2.imshow(difference_w, difference)
                    difference_frame = difference
                    # cv2.moveWindow(difference_w, dx, dy + difference.shape[0] + 50)
                    difference = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

                    #get overlay
                    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # frame_gray = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR)
                    ret, mask = cv2.threshold(difference,10,255, cv2.THRESH_BINARY)
                    mask_inv = cv2.bitwise_not(mask)
                    frame_gray_mask = cv2.addWeighted(frame_gray,0.7,mask_inv,0.3,0)

                    # last frame
                    last_frame_gray = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
                    last_frame_gray_col = cv2.cvtColor(last_frame_gray, cv2.COLOR_GRAY2RGB)
                    last_frame_gray_mask = cv2.drawContours(last_frame_gray_col, contours_twoframes, -1, (0, 255, 0), 1)
                    last_frame_gray_mask = cv2.drawContours(last_frame_gray_mask, contours_oneframe, -1, (0, 0, 255), 1)
                        # = cv2.addWeighted(last_frame_gray, 0.7, mask_inv, 0.3, 0)
                    # cv2.imshow(previous_frame_w, last_frame_gray)
                    cv2.imshow(previous_frame_mask_w, last_frame_gray_mask)

                    # cv2.moveWindow(previous_frame_mask_w, dx + last_frame_gray_mask.shape[1]+50, dy)
                    # cv2.imwrite(name+str(frame_number)+".jpg",last_frame)

                    # two frmes ago
                    two_frames_ago_gray = cv2.cvtColor(two_frames_ago, cv2.COLOR_BGR2GRAY)
                    two_frames_ago_gray_col = cv2.cvtColor(two_frames_ago_gray, cv2.COLOR_GRAY2RGB)
                    two_frames_ago_gray_mask = cv2.drawContours(two_frames_ago_gray_col, contours_twoframes, -1, (0, 255, 0), 1)
                    two_frames_ago_gray_mask = cv2.drawContours(two_frames_ago_gray_mask, contours_oneframe, -1, (0, 0, 255), 1)
                        # = cv2.addWeighted(two_frames_ago_gray, 0.7, mask_inv, 0.3, 0)
                    # cv2.imshow(two_frames_frame_w,  two_frames_ago_gray)
                    cv2.imshow(two_frames_frame_mask_w, two_frames_ago_gray_mask)
                    # cv2.moveWindow(two_frames_frame_mask_w, dx + 2 * two_frames_ago_gray_mask.shape[1]+120, dy)

                two_frames_ago_bool = True
                two_frames_ago = last_frame



            else:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow(current_frame_w, frame_gray)
                frame_gray_col = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2RGB)
                frame_gray_col_mask = cv2.drawContours(frame_gray_col, contours_twoframes, -1, (0, 255, 0), 1)
                frame_gray_col_mask = cv2.drawContours(frame_gray_col_mask, contours_oneframe, -1, (0, 0, 255), 1)

                cv2.imshow(video_w, frame_gray_col_mask)
                # cv2.moveWindow(video_w, dx, dy)

            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

            frame_gray_col = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2RGB)
            last_frame_bool = True
            last_frame = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2RGB)

            cv2.setMouseCallback(video_w, record_drop)

            while (1):
                # frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                cv2.imshow(current_frame_w, frame)
                frame_gray_col_mask = cv2.drawContours(frame_gray_col, contours_twoframes, -1, (0, 255, 0), 1)
                frame_gray_col_mask = cv2.drawContours(frame_gray_col_mask, contours_twoframes, -1, (0, 0, 255), 1)
                cv2.imshow(video_w, frame_gray_col_mask)
                # cv2.moveWindow(video_w, dx, dy)



                k = cv2.waitKey(20)
                if k == 32:  # if Space is pressed close
                    cv2.imshow("Video", frame_gray_col)
                    try:
                        print("Frame: "+str(frame_number))
                        frame_gray_col_mask_rev = frame_gray_col
                        frame_gray_col_mask_rev = cv2.drawContours(frame_gray_col_mask_rev, contours_b, -1, (0, 255, 0), 1)
                        cv2.imwrite(video_dir_circle + name + "-" + "Trace-"+str(frame_number) + ".jpg",frame_gray_col_mask_rev )
                        cv2.imwrite(video_dir_trace + name + "-" + "Original-" + str(frame_number) + ".jpg", frame)
                        cv2.imwrite(video_dir_difference + name + "-" + "Difference-" + str(frame_number) + ".jpg", difference_frame)
                    except:
                        pass
                    break

            WritePointToCSV(temp_list, frame_number) # call method to write slide events to csv
            frame_number += 1 # iterate frame number

        else:
            # The next frame is not ready, so we try to read it again
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)

            "frame is not ready"
            # It is better to wait for a while for the next frame to be ready
            cv2.waitKey(1000)

        if cv2.waitKey(10) == 27:
            break

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT): # If the number of captured frames is equal to the total number of frames, we stop
            break

def VideoToFrames(path, video_name, first_frame, last_frame):
    video_file = path + video_name
    image_path = path+"/"+video_name+"-Frames/"

    try:
        os.makedirs(image_path)
    except:
        shutil.rmtree(image_path)
        os.makedirs(image_path)

    cap = cv2.VideoCapture(video_file)
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)

    frame_number = 1
    pbar = tqdm(total=int(last_frame))

    while frame_number <= int(last_frame):
        flag, frame = cap.read()
        if flag:
            if int(first_frame) < int(frame_number) < int(last_frame):
                image_name = str(frame_number) +"-"+ video_name
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # cv2.imshow("Frame",frame_gray)
                cv2.imwrite(image_path + image_name + ".jpg", frame_gray)

            pbar.update(1)
            frame_number += 1  # iterate frame number
        else:
            # The next frame is not ready, so we try to read it again
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
            # It is better to wait for a while for the next frame to be ready
            cv2.waitKey(1000)

        if cv2.waitKey(10) == 27:
            break

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(
                cv2.CAP_PROP_FRAME_COUNT):  # If the number of captured frames is equal to the total number of frames, we stop
            break

    pbar.close()
    cv2.destroyAllWindows()
    cap.release()

def GetVariableFrameRate(path, filename, filetype=".mp4"):
    video_path = path + "/" + filename + filetype
    csv_path = path + "/" + filename + ".csv"
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    timestamps = [cap.get(cv2.CAP_PROP_POS_MSEC)]
    calc_timestamps = [0.0]
    start = time.time()
    pbar = tqdm(total=cap.get(cv2.CAP_PROP_FRAME_COUNT))
    while (cap.isOpened()):
        frame_exists, curr_frame = cap.read()
        if frame_exists:
            pbar.update(1)
            now = time.time()
            elapsed_time = now-start
            timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
            calc_timestamps.append(elapsed_time
                # calc_timestamps[-1] + 1000 / fps
            )
        else:
            break

    cap.release()
    pbar.close()

    with open(csv_path, 'a') as out:
        w = csv.writer(out)
        for i, (ts, cts) in enumerate(zip(timestamps, calc_timestamps)):
            line = [str(i),str(cts*0.001)]
            w.writerow(line)

def CheckFrames(path, video_name):
    video_file = path + video_name
    cap = cv2.VideoCapture(video_file)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps =  cap.get(cv2.CAP_PROP_FPS)
    cv2.destroyAllWindows()
    cap.release()
    return frame_count, fps

def init_csv(_name, loc):
    filename = _name + ".csv"
    path = loc + filename
    print(path)
    headers = ["Frame", "Datapoint", "Area", "Perimeter"]
    setLocation(path)
    headers = ",".join(headers)
    with open(path, "w") as path:
        path.write(headers)
        path.close()

def write_data_to_csv(_list):
    global location
    with open(location, 'a') as out:
        w = csv.writer(out)
        w.writerow(_list)

# Make Video
dir = "/Users/illyanayshevskyy/Dropbox/5.Ph.D.Research/0.HybridSurfaces/2019 - Soiling Experiments/2019 - Soiling - Jordan/Data/Hydroscopic Soilant Analysis/Experiment Videos/Hybrid-E1-ARD/"
image_path = dir
csv_file_path = ""
videoname = "Hybrid-E1-ARD"
fpm = 1
angle = -2
set_bounds = True
format = ".mp4"

MakeVideo(dir, videoname, format, csv_file_path, image_path, fpm, set_bounds, angle)
