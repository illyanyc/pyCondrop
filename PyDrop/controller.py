
# Import dependancies
from trails import *
from os.path import join
from os import listdir
import cv2
import numpy as np
import csv
import os
import shutil
import drops

# Main method to process all the data

def processData(_sample_name, _start_frame, _sample_width, _coordinates, _subsample_factor, _path):
    # Data Input:
    sample_name = _sample_name
    start_frame = _start_frame
    sample_width = _sample_width
    y_top_orig, y_bottom_orig, x_left_orig, x_right_orig = _coordinates
    print (_coordinates)
    subsample_factor = _subsample_factor


    path = _path
    video_dir = path + str("/WashingVideo/")
    try:
        os.makedirs(video_dir)
    except:
        shutil.rmtree(video_dir)
        os.makedirs(video_dir)



    # Initiate data file
    csv_filename = path + "/"+ sample_name + " - Processed_Data_V2" +  ".csv"

    # Set up video file name
    videoname = sample_name + " - Processed VideoV2"
    format = ".mp4"


    # Subsample all parameters
    y_top, y_bottom, x_left, x_right = (round(x/subsample_factor)
                                        for x in [y_top_orig, y_bottom_orig, x_left_orig, x_right_orig])
    # Initialize empty images
    prev_plate_BGR, prev_plate_BW, prev_peak_profile, prev_peak_histogram, prev_peak_landscape, prev_drop_trail_masks = \
        6 * (None,)
    # Find list of files in the given path
    file_list = sorted(listdir(path))

    # Loop through files
    counter = 1
    min = start_frame
    hr = 0
    cleaned_area_sum = 0
    percent_area_cleaned = 0

    for i_file, file_name in enumerate(file_list[(start_frame-1):]):
        print (file_name)
        # Video timing set:
        min = min + 1
        if min == 60:
            hr = hr + 1
            min = 0
        printtime = "{:02d}:{:02d}".format(hr, int(min))

        curr_img_orig_BGR = cv2.imread(join(path, file_name))
        # Subsample image
        curr_img_BGR = cv2.resize(curr_img_orig_BGR, None, fx=1 / subsample_factor, fy=1 / subsample_factor)
        # Convert from color to grayscale
        curr_img_BW = cv2.cvtColor(curr_img_BGR, cv2.COLOR_BGR2GRAY).copy()

        # Set up pixel to mm conversion scale
        height, width = curr_img_BW.shape[:2]
        pixel_to_mm_ratio_x = (width)/ sample_width
        area_1mm_is_n_px = pixel_to_mm_ratio_x * pixel_to_mm_ratio_x

        #curr_img_BW = cv2.cvtColor(curr_img_BGR, cv2.COLOR_BGR2GRAY).copy()
        # Select plate area
        curr_plate_BGR = curr_img_BGR[y_top:y_bottom, x_left:x_right, :].copy()
        curr_plate_BW = curr_img_BW[y_top:y_bottom, x_left:x_right].copy()
        if i_file == 0:
            # Initialize empty images for previous frame
            prev_plate_BGR = np.zeros_like(curr_plate_BGR)
            prev_plate_BW = np.zeros_like(curr_plate_BW)
            prev_peak_profile = np.zeros((4, curr_plate_BW.shape[1]))
            prev_peak_histogram = Counter()
            prev_peak_landscape = np.zeros_like(curr_plate_BW)
            prev_drop_trail_masks = [np.zeros_like(curr_plate_BW)]
        # Find drop trails for current frame
        stop_flag, curr_drop_trail_mask, curr_peak_profile, curr_peak_histogram, curr_peak_landscape, drop_data = \
        find_drop_trails(i_file + start_frame,
                         file_name,
                         curr_plate_BGR,
                         curr_plate_BW,
                         prev_plate_BGR,
                         prev_plate_BW,
                         prev_peak_profile,
                         prev_peak_histogram,
                         prev_peak_landscape,
                         prev_drop_trail_masks,video_dir, pixel_to_mm_ratio_x)

        # Write drop data to list


        if stop_flag:
            break



        # Save current frame data for future use in next frame
        prev_plate_BGR = curr_plate_BGR
        prev_plate_BW = curr_plate_BW
        prev_peak_profile = curr_peak_profile
        prev_peak_histogram = curr_peak_histogram
        prev_peak_landscape = curr_peak_landscape

        counter += 1

        if len(prev_drop_trail_masks) < 4:
            prev_drop_trail_masks.append(curr_drop_trail_mask)

        else:
            prev_drop_trail_masks = prev_drop_trail_masks[1:] + [curr_drop_trail_mask]




        # Calculate total area cleaned
        cleaned_area_sum = cleaned_area_sum + (np.count_nonzero(curr_drop_trail_mask)/area_1mm_is_n_px)
        #print (np.count_nonzero(curr_drop_trail_mask))
        percent_area_cleaned = percent_area_cleaned + (float(np.count_nonzero(curr_drop_trail_mask))/(height*width)*100.0)

        print("Time: " + str(printtime))
        print("Total Area Cleaned: " + str("{0:.2f}".format(cleaned_area_sum)) + " mm^2")
        print("Total Percent Area Cleaned: " + str("{0:.2f}".format(percent_area_cleaned)) + " %")

        # Data that is written to the CSV sheet:

        sum_of_area_cleaned = str("{0:.2f}".format(cleaned_area_sum))
        percent_of_area_cleaned = str("{0:.2f}".format(percent_area_cleaned))
        area_cleaned_at_rolloff_event = str(np.sum(curr_drop_trail_mask)/area_1mm_is_n_px)
        diameter = drop_data[0]
        diameter_mm = drop_data[1]
        x = drop_data[2]
        y = drop_data[3]
        method = drop_data[4]

        _data_to_csv = [ printtime,
                        sum_of_area_cleaned,
                        percent_of_area_cleaned,
                        area_cleaned_at_rolloff_event,
                        diameter_mm,
                        x,
                        y,
                        method]

        with open(csv_filename, 'a') as out:
            w = csv.writer(out)
            w.writerow(_data_to_csv)


    # v.writevideo(videoname, path, format, csv_filename, width, height, "Temp/", start_frame)
    # v.make_video(path, videoname, format, csv_filename, video_dir)




