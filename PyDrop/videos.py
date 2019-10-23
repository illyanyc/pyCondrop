
import csv
import shutil
from os import listdir
import os
from pathlib import Path
import time
from tqdm import tqdm
import cv2
import datetime
import numpy as np

def writevideo(videoname, path, format, csv_file_path, image_directory, startframe):
    # sort all directory files in aphabetical order
    dirfiles = []
    #for root, dirs, files in os.walk(image_directory):
     #   dirs.sort()
      #  for filename in files:
        #    if filename.endswith(".jpg"):
         #       dirfiles.append((os.path.join(root, filename)))

    dirfiles = sorted(listdir(image_directory))
    # print(dirfiles)

    #dirfiles.sort(key=lambda f: int(filter(str.isdigit, f)))

    # Set image size for video
    image = None

    for i_file, file_name in enumerate(dirfiles):
        image = os.path.join(image_directory, file_name)
        if image.endswith(".JPG") or image.endswith(".jpg"):
            print("pass")
        break

    img = cv2.imread(image)
    height, width, channels = img.shape

    # Set up video file name and properties
    videooutput = path + videoname + " - Processed_Video" + format
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (width - int((width * 0.95)), height - 12)
    topLeftCornerOfText = (width - int((width * 0.95)), height - int((height * 0.95)))
    fontScale = 0.8
    fontColor = (255, 255, 255)
    lineType = 1
    video = cv2.VideoWriter(videooutput, 1, 16, (width, height))

    # Set up time tracking
    min = startframe
    hr = 0
    counter = 0

    # Compile video
    # with open(csv_file_path, "r") as csvfile:
    #     csv_file = csv.reader(csvfile, delimiter=',')
    for i_file, file_name in enumerate(dirfiles[(startframe):]):
        #Write frame to video
        print("pass")
        min = min + 1

        if min == 60:
            hr = hr + 1
            min = 0

        printtime = "{:02d}:{:02d}".format(hr, int(min))
        print(printtime)
        text = videoname+ "; Time: " + printtime
               # + "; % Area Cleaned: " + str(csv_file[counter][2]) + " %"

        img = cv2.imread(file_name)

        #cv2.imshow("image",img)
        counter = counter + 1
        cv2.putText(img, text, bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
        video.write(img)
    print ("Complete!")
    cv2.destroyAllWindows()
    video.release()
    #shutil.rmtree(image_directory)

def make_video(dir, videoname, csv_file_path, image_path):

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
    videooutput = os.path.join(image_path, videoname)
    print(videooutput)

    # sert font of test overlay
    font = cv2.FONT_HERSHEY_DUPLEX
    bottomLeftCornerOfText = (width - int((width * 0.72)), height - 12)
    topLeftCornerOfText = (width - int((width * 0.9)), height - int((height * 0.9)))
    fontScale = width/600
    fontColor = (0, 0, 0)
    lineType = 3

    # check if the video file with same name already exists
    my_file = Path(videooutput)
    if my_file.is_file():
        print ("Video file name is already taken! Please chose a different file name...")
        work = False # if yes set work to false and abort

    # Process files
    if work == True:
        print ("Processing, please wait...")
        video = cv2.VideoWriter(videooutput, 1, 16, (width, height))
        min = 0
        hr = 0

        counter = 0
        ref_img_count = 1
        pbar_increment = 1
        pbar = tqdm(total=len(dirfiles))

        for image in dirfiles:
            # count frames for time-stamp in video - convert to hh:mm
            min = min + 1
            if min == 60:
                hr = hr + 1
                min = 0

            printtime = "{:02d}:{:02d}".format(hr, int(min)) # generate time string to print


            # try:
            #     row = data_read[counter]
            #     text = videoname + "; Time: " + printtime + "; % Area Cleaned: " + str(row[2]) + " %"
            # except:
            text = "Time [hh:mm]: " + printtime
                #videoname + \


            img = cv2.imread(image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            # img_raw = cv2.imread(img_raw, cv2.COLOR_BGR2BGRA)
            # get image
            img = cv2.resize(img, None, fx=1, fy=1)

            # write time-string to image
            cv2.putText(img, text , bottomLeftCornerOfText, font, fontScale, fontColor, lineType)
            counter = counter + 1

            video.write(img) # write image to video

            ref_img_count = ref_img_count + 1 # advance refined image counter
            pbar.update(pbar_increment) # update progress bar
        time.sleep(1)
        print ("Complete!")
        pbar.close()
        cv2.destroyAllWindows()
        video.release()
        #shutil.rmtree(image_path)

def timelapse_video(path, name, interval, length_sec, vid_bool,  vid_lenth):
    # get date
    date = datetime.datetime.now()
    # set path dir
    path_dir = path + "/Timelapse photos -"+str(date)
    # create path
    try:
        os.makedirs(path_dir)
    except:
        shutil.rmtree(path_dir)
        os.makedirs(path_dir)

    # get video feed


    if vid_bool:

        time_range = length_sec / interval

        for i in range(time_range):
            start = time.time()
            min = 0

            cap = cv2.VideoCapture(0)
            ret, img = cap.read()
            width = np.size(img, 1)
            height = np.size(img, 0)
            cap.release()

            cam = cv2.VideoCapture(0)
            writer = cv2.VideoWriter(filename= path_dir+name+".mp4",
                                     fourcc=-1,  # this is the codec that works for me
                                     fps=16,  # frames per second, I suggest 15 as a rough initial estimate
                                     frameSize=(width, height))

            t_end = time.time () + vid_lenth
            cap = cv2.VideoCapture(0)

            while time.time() < t_end:
                while True:
                    time_now = time.time()
                    delta = time_now - start
                    if delta > 60:
                        min = min + 1
                        start = time.time()
                        delta = 0

                    print_time = str(min) + ":" + str("%.1f" % delta)

                    ret, img = cam.read()
                    if ret == True:
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

                        x = 12
                        y = height - 12
                        text_color = (0, 0, 220)
                        writer.write(gray)
                        cv2.imshow("Video", gray)

            cv2.destroyAllWindows()
            cv2.VideoCapture(0).release()


    else:
        pass
        # for i in range(time_range):
        #     ret, img = cap.read()
        #     cv2.imwrite(path_dir+str(i).zfill(4)+'.png', img)
        #     time.sleep(interval)

# make_video(dir, videoname, format, csv_file_path, image_path)
# writevideo(videoname, path, format, csv_file_path, width, height, image_directory, startframe)
videoname = "Hybrid_FullLenght.mp4"
path ="/Users/illyanayshevskyy/Dropbox/5.Ph.D.Research/0.HybridSurfaces/Temporary Folder/Hybrid-D17-NaCl"
csv_file_path = path

startframe = 1
dir_image ="/Users/illyanayshevskyy/Dropbox/5.Ph.D.Research/0.HybridSurfaces/Temporary Folder/Hybrid-D17-NaCl"
image_directory = dir_image

make_video(image_directory, videoname, csv_file_path, image_directory)