import cv2
import os

def convert_to(image_path, location, type):
    dirfiles = []
    for root, dirs, files in os.walk(image_path):
        dirs.sort()
        for filename in files:
            #print(filename)
            if filename.endswith(".jpg"):
                dirfiles.append([(os.path.join(root, filename)), filename])
            if filename.endswith(".tif"):
                dirfiles.append([(os.path.join(root, filename)), filename])
            if filename.endswith(".JPG"):
                dirfiles.append([(os.path.join(root, filename)), filename])


    for i in dirfiles:
        print("saving: "+i[1])
        file = cv2.imread(i[0])
        new_name = location+i[1]+".png"
        cv2.imwrite(new_name, file)


image_path = "/Users/illyanayshevskyy/Dropbox/3-Ph.D. Research/0.Hybrid Surfaces/2018 - Soiling Experiments/180815-BG1-BG2/Raw/"
new_location = "/Users/illyanayshevskyy/Dropbox/3-Ph.D. Research/0.Hybrid Surfaces/2018 - Soiling Experiments/180815-BG1-BG2/Processed/"
type = ".png"

convert_to(image_path, new_location, type)