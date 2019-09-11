import cv2
from tqdm import tqdm
import os
import imutils
import numpy as np
from pathlib import Path
import shutil

def make_video(path,name):
    img_array = []
    video_name = path+name+'.mp4'

    for root, dirs, files in os.walk(path):
        dirs.sort()
        for filename in files:
            #print(filename)
            if filename.endswith(".jpg"):
                img_array.append((os.path.join(root, filename)))
            if filename.endswith(".tif"):
                img_array.append((os.path.join(root, filename)))
            if filename.endswith(".JPG"):
                img_array.append((os.path.join(root, filename)))

    image = img_array[0]
    img = cv2.imread(image)

    height, width, channels = img.shape
    size = (width, height)

    img_array = sorted(img_array)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_name, fourcc, 15, size)

    pbar_increment = 1
    pbar = tqdm(total=len(img_array)-1)

    for i in range(len(img_array)-1):
        file = img_array[i]
        img = cv2.imread(file)
        out.write(img)
        pbar.update(pbar_increment)
    out.release()
    pbar.close()

def make_video_caption(dir, videoname, format, csv_file_path, image_path, fpm, angle):
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
            if filename.endswith(".jpg"):
                dirfiles.append((os.path.join(root, filename)))
            if filename.endswith(".tif"):
                dirfiles.append((os.path.join(root, filename)))
            if filename.endswith(".JPG"):
                dirfiles.append((os.path.join(root, filename)))

    image = dirfiles[0]
    dirfiles = sorted(dirfiles)

    # set video file name and path
    videooutput = dir + videoname + format
    print(videooutput)

    # check if the video file with same name already exists
    my_file = Path(videooutput)
    if my_file.is_file():
        print ("Video file name is already taken! Please chose a different file name...")
        work = False # if yes set work to false and abort
        cv2.destroyAllWindows()


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
            cv2.circle(frame, (x, y), 10, (0, 0 , 255), -1)
            cv2.putText(frame, str(x)+", "+str(y), bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
            coordinates.append([int(x),int(y)])

    frame = cv2.resize(frame, None, fx=1, fy=1)
    cv2.namedWindow('Set Up The Feature Areas', cv2.WINDOW_NORMAL)
    cv2.imshow('Set Up The Feature Areas', frame)
    cv2.resizeWindow('Set Up The Feature Areas', 600, 600)
    cv2.setMouseCallback('Set Up The Feature Areas', Set_image_bounds)  # Set bounds for video

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
    print("Coordinates: "+ str(coordinates))

    # Process files
    if work == True:
        print ("Processing, please wait...")
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(videooutput, fourcc, 16, (x2-x1, y2-y1))
        sec = 0
        min = 0
        hr = 0

        counter = 0
        ref_img_count = 1
        pbar_increment = 1
        pbar = tqdm(total=len(dirfiles))

        for image in dirfiles:
            y_top, y_bottom, x_left, x_right = coordinates
            # count frames for time-stamp in video - convert to hh:mm:ss


            sec = sec + fpm * 60

            if sec == 60 or sec > 59:
                min = min + 1
                sec = 0

            # min = min + fpm
            if min == 60:
                hr = hr + 1
                min = 0

            printtime = "{:02d}:{:02d}:{:02d}".format(hr, int(min), int(sec)) # generate time string to print

            text = "Time [hh:mm:ss] : " + printtime

            img = cv2.imread(image) # get image
            img = img[y_top:y_bottom, x_left:x_right, :].copy()
            if angle != 0:
                img = imutils.rotate_bound(img, angle)
                cv2.imshow("Rotated", img)

            # set font of test overlay
            x_max = x_right - x_left
            y_max =  y_bottom - y_top

            font = cv2.FONT_HERSHEY_SIMPLEX
            bottomLeftCornerOfText = (x_max - int((x_max * 0.9)), y_max - 25)
            topLeftCornerOfText = (x_max - int((x_max * 0.9)), y_max - int((y_max * 0.85)))
            fontScale = x_max / 600
            fontColor = (255, 255, 255)
            lineType = 3


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

# make_video_caption(dir, videoname, format, csv_file_path, image_path, fpm, set_bounds, angle)
path = "/Users/illyanayshevskyy/Dropbox/5.Ph.D.Research/0.HybridSurfaces/2018 - Soiling Experiments/190823-Full_Lenght_Hybrid/"
name = "190823-Hybrid_FullLenght"
make_video_caption(path, name, ".avi", path, path, 10, 0)

