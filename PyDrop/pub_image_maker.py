import cv2
import pandas as pd
from PIL import Image
import numpy as np

# set intake parameters
csv_file_path = "/Users/illyanayshevskyy/Dropbox/3-Ph.D. Research/0.Hybrid Surfaces/Software Developement/" \
                  "a.python Condensation-DropAnalyzer/PyCondrop/source/DropMeasurements_all.csv"
image_file_path = "/Users/illyanayshevskyy/Dropbox/3-Ph.D. Research/0.Hybrid Surfaces/Abrasive Method(restored)/" \
                  "180505-HS2mm4mm3row-T4/Timeline Images/101INTVLWashingVideoCaculationsV2/DSCN0004.JPG.jpg"
key_term = "HS"
write_image_file_path = image_file_path+"-PROCESSED.jpg"

# load image
img = cv2.imread(image_file_path)
cv2.imshow("img",img)
height, width, channels = img.shape

# load csv data
csvdata = pd.read_csv(csv_file_path, header=0)
folder = list(csvdata.folder)
image = list(csvdata.image)
diameter = list(csvdata.diameter)
roiPos_X = list(csvdata.roiPos_X)
roiPos_Y = list(csvdata.roiPos_Y)


# Make a data frame with dots to show on the map
data = pd.DataFrame({
    'folder': folder,
    'image': image,
    'diameter': diameter,
    'roiPos_X': roiPos_X,
    'roiPos_Y': roiPos_Y
})
data

# get list of image names
processed_img = img.copy()
image_names = data["folder"]
counter = 0
diameter = []
for i in image_names:
    if str(i).find(key_term) > 0:
        x = data["roiPos_X"][counter]
        y = data["roiPos_Y"][counter]
        d = data["diameter"][counter]

        counter += 1

        if x > 0:
            diameter.append(d)
            if x > width:
                x = width
            if y > height:
                y = height
        try:
            cv2.circle(img, (int(x), int(y)), int(d / 2), (0, 0, 255), 1)
            cv2.circle(img, (int(x), int(y)), int(3), (255, 0, 0), -1)
            print(x,y,d)
        except:
            None
print(np.average(diameter),np.std(diameter))
cv2.imshow("Processed Image", img)
image_to_save = Image.fromarray(img)
image_to_save.save(write_image_file_path)




