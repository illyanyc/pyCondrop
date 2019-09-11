
from scipy import ndimage
import numpy as np
import cv2
from array_processing import scale_array_max, scale_array_min_max
from masking import bgr_img_masking
from skimage.feature import peak_local_max
from collections import Counter
from scipy.interpolate import griddata
from PIL import Image
import drops

# drop_location_list = []

prev_plate_name = 'Prev. plate'
curr_plate_name = 'Curr. plate + peaks'
masked_curr_plate_name = 'Masked curr. plate'
masked_prev_plate_name = 'Masked prev. plate'
peak_diff_name = 'Peak profiles ({}, frame {})'
masked_peak_landscape_name = 'Masked peak landscape ({}, frame {})'

def post_process_trail_mask(mask):
    return ndimage.binary_fill_holes(ndimage.binary_dilation(mask.copy()))

def eliminate_floating_blobs(mask):
    y_max = mask.shape[0]
    label_mask, n_blobs = ndimage.label(mask)
    new_mask = np.zeros_like(mask)
    for i_blob in range(1, 1+n_blobs):
        blob_coords = np.nonzero(label_mask == i_blob)
        if max(blob_coords[0]) >= y_max - 3:
            # We keep all blobs within 3 pixels from the bottom of the image
            new_mask[blob_coords] = 1
    return new_mask

def prev_highest_position_on_footprint(seed_pos, prev_drop_trail_masks):
    y_min = prev_drop_trail_masks[0].shape[0] + 1  # Lower than the image, on purpose
    for mask in prev_drop_trail_masks:
        y_positions_filled = np.where(np.any(mask[:, seed_pos], axis=1))
        if y_positions_filled[0].size > 0:
            mask_y_min = np.min(y_positions_filled[0])
            if mask_y_min < y_min:
                y_min = mask_y_min
    return y_min


def create_trail_mask_from_drop_footprint(curr_peaks_landscape,
                                          forbidden_mask,
                                          curr_drop_footprint,
                                          prev_drop_trail_masks,
                                          curr_plate_BW,
                                          prev_plate_BW):
    y_top, y_bottom, x_left, x_right = [0, curr_peaks_landscape.shape[0], 0, curr_peaks_landscape.shape[1]]
    y_top_lowest_part = round(y_bottom * 2 / 3)
    subsample_factor =2
    curr_peaks_landscape[forbidden_mask > 0] = 255
    frame_diff = ndimage.median_filter(np.maximum(0, curr_plate_BW.astype(np.int16) - prev_plate_BW.astype(np.int16)),
                                       size=7)
    # dilation_structure = np.zeros((11, 1))
    # dilation_structure[5:, 0] = 1
    # frame_diff_mask = ndimage.binary_dilation(frame_diff > 30, structure=dilation_structure)
    frame_diff_mask = ndimage.binary_propagation(frame_diff > 60, mask=(frame_diff > 20))
    # cv2.imshow('diff',frame_diff.astype(np.uint8))
    # cv2.imshow('diff mask', 255*frame_diff_mask.astype(np.uint8))
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    drop_trail_mask = np.zeros_like(curr_peaks_landscape)
    if any(curr_drop_footprint.flatten()):
        # Find trail positions for current frame
        seed_pos = np.argwhere(curr_drop_footprint > 0)
        # Extract interpolated peaks for the bottom part of the glass plate
        peaks_interp_cutoff = 40  # Most drop trails have intensity peaks under this value
        low_level_areas_mask = np.zeros_like(curr_peaks_landscape)
        low_level_areas_mask[curr_peaks_landscape <= peaks_interp_cutoff] = 1
        low_level_areas_mask = ndimage.binary_opening(low_level_areas_mask.copy(), iterations=round(20/subsample_factor))
        # low_level_areas_mask = ndimage.binary_dilation(low_level_areas_mask.copy(), iterations=round(7/subsample_factor))
        # Create seed mask at the bottom
        seed_mask = np.zeros_like(curr_peaks_landscape)
        seed_mask[y_top_lowest_part:y_bottom, seed_pos] = 1
        seed_mask[curr_peaks_landscape > peaks_interp_cutoff] = 0
        # Create drop trail mask by propagating the seed within the low level basin
        # cv2.imshow('temp2', 255 * np.logical_or(low_level_areas_mask, frame_diff_mask).astype(np.uint8))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        max_mask_1 = post_process_trail_mask(np.logical_or(low_level_areas_mask, frame_diff_mask))
        drop_trail_mask = ndimage.binary_propagation(seed_mask.copy(), mask=max_mask_1)
        if any(drop_trail_mask.flatten()):
            # We subtract the previous drop trail mask from the current one and propagate again,
            # in order to eliminate areas disconnected from the mask
            max_mask_2 = drop_trail_mask
            drop_trail_min_y = np.min(np.where(np.any(drop_trail_mask[:, seed_pos], axis=1)))
            if prev_highest_position_on_footprint(seed_pos, prev_drop_trail_masks) >= drop_trail_min_y - 10:
                # A new drop is falling from higher above, so current mask must include the footprint column
                # that was also part of the previous masks
                for prev_mask in prev_drop_trail_masks:
                    prev_mask_2 = prev_mask.copy()
                    prev_mask_2[drop_trail_min_y:y_bottom, seed_pos] = 0  # Preserve column profile footprint
                    max_mask_2[prev_mask_2 > 0] = 0
            else:
                # The drop is falling from a lower position than before, so we must protect the current drop trail from
                # overlapping with the previous ones
                for prev_mask in prev_drop_trail_masks:
                    max_mask_2[prev_mask > 0] = 0
            # A new propagation to get rid of unconnected islands
            drop_trail_mask = ndimage.binary_propagation(seed_mask.copy(), mask=max_mask_2)
            # # Add back the column profile footprint
            # drop_trail_mask[:, seed_pos] = np.logical_or(drop_trail_mask[:, seed_pos], column_profile_footprint)
            # Eliminate all blobs that don't touch the bottom and all holes
            drop_trail_mask = ndimage.binary_fill_holes(eliminate_floating_blobs(drop_trail_mask))
    return drop_trail_mask


def find_peaks(plate):
    local_max = peak_local_max(plate, min_distance=3, indices=False)
    local_max_idx = np.nonzero(local_max > 0)
    local_med = ndimage.median_filter(plate, size=(5, 9))
    peaks = np.zeros_like(local_med, np.int32)
    peaks[local_max_idx] = plate[local_max_idx] - local_med[local_max_idx]
    y_000 = 0
    y_100 = plate.shape[1]  # 100%
    y_025, y_050, y_075 = [int(y_100 * x) for x in (0.25, 0.50, 0.75)]
    filter_size = 21
    peak_profile = np.concatenate(
        [ndimage.median_filter(np.sum(peaks, axis=0).reshape(1, -1), size=filter_size).astype(np.int32),
         2*ndimage.median_filter(np.sum(peaks[y_000:y_050, :], axis=0).reshape(1, -1), size=filter_size).astype(np.int32),
         2*ndimage.median_filter(np.sum(peaks[y_025:y_075, :], axis=0).reshape(1, -1), size=filter_size).astype(np.int32),
         2*ndimage.median_filter(np.sum(peaks[y_050:y_100, :], axis=0).reshape(1, -1), size=filter_size).astype(np.int32)], axis=0)
    # peak_profile = np.sum(peaks, axis=0).astype(np.int32)
    # peak_count_profile = np.sum(peaks > 0, axis=0).astype(np.int32)
    return local_max, peaks, peak_profile  # , peak_count_profile


def propagate_peaks(peaks):
    peak_idx = np.nonzero(peaks)
    return np.transpose(griddata(np.transpose(peak_idx[::-1]),
                                 peaks[peak_idx],
                                 np.transpose(np.meshgrid(np.arange(peaks.shape[1]),
                                                          np.arange(peaks.shape[0]))),
                                 method='nearest',
                                 fill_value=255))

def img_is_flat(hist):
    sum_all = sum(hist.values())
    sum_low = sum([hist[x] for x in range(1, 32)])
    if sum_low > 0.65 * sum_all:
        return True
    return False


def visualize_img_and_drop_profiles(i_frame, file_name,
                                    curr_plate_BGR, prev_plate_BGR,
                                    curr_peaks, curr_peak_landscape, curr_drop_footprints, curr_drop_trail_mask,
                                    curr_peak_profile, prev_peak_profile, diff_peak_profile,
                                    curr_local_max, max_peak_diff_idx,video_dir, pixel_to_mm_ratio_x):
    y_max, x_max = curr_plate_BGR.shape[:2]
    max_profile_level = 255

    # Drop trails histogram
    curr_drop_trail_idx = np.nonzero(curr_drop_footprints)
    curr_drop_trail_hist = Counter(curr_peaks[0:y_max, curr_drop_trail_idx].flatten())
    curr_drop_trail_hist[0] = 0
    curr_drop_trail_hist[255] = 0

    # Prepare scaling parameters for the column profiles to fit inside the windows
    prev_max_peak = max(prev_peak_profile[0, :])
    curr_max_peak = max(curr_peak_profile[0, :])
    diff_max_peak = np.array([diff_peak_profile[i_p, max_peak_diff_idx[i_p][0]] for i_p in range(4)]).reshape(-1, 1)
    max_interframe_peak = max(prev_max_peak, curr_max_peak)
    prev_scale_level = max_profile_level * prev_max_peak / max_interframe_peak
    curr_scale_level = max_profile_level * curr_max_peak / max_interframe_peak
    diff_scale_level = max_profile_level * diff_max_peak / max_interframe_peak

    # Prepare polylines representing the various column profiles
    x_idx = [x for x in range(x_max)]
    curr_polyline = np.array([list(z) for z in zip(x_idx,
                                                   y_max - scale_array_max(curr_peak_profile[0, :].flatten(), curr_scale_level).astype(
                                                       np.uint8))],
                             np.int32).reshape((-1, 1, 2))
    prev_polyline = np.array([list(z) for z in zip(x_idx,
                                                   y_max - scale_array_max(prev_peak_profile[0, :].flatten(), prev_scale_level).astype(
                                                       np.uint8))],
                             np.int32).reshape((-1, 1, 2))

    diff_polyline = np.array([list(z)
                              for z in zip(x_idx,
                                           y_max - scale_array_min_max(diff_peak_profile[0, :].flatten(),
                                                                       0,
                                                                       diff_scale_level[0]).astype(np.uint8))],
                             np.int32).reshape((-1, 1, 2))
    drop_trails_polyline = np.array([list(z)
                                     for z in zip(x_idx,
                                                  y_max - scale_array_min_max(curr_drop_footprints,
                                                                              0,
                                                                              max_profile_level).astype(np.uint8))],
                                    np.int32).reshape((-1, 1, 2))

    # Prepare the display of images
    # prev_plate_name = 'Prev. plate ({}, frame {})'.format(file_name, i_frame-1)
    # curr_plate_name = 'Curr. plate + peaks ({}, frame {})'.format(file_name, i_frame)
    # masked_curr_plate_name = 'Masked curr. plate ({}, frame {})'.format(file_name, i_frame)
    # masked_prev_plate_name = 'Masked prev. plate ({}, frame {})'.format(file_name, i_frame-1)
    # peak_diff_name = 'Peak profiles ({}, frame {})'.format(file_name, i_frame)
    # masked_peak_landscape_name = 'Masked peak landscape ({}, frame {})'.format(file_name, i_frame)

    # Calculate the drop diameter and location
    method = "--None--"
    if np.sum(curr_drop_trail_mask) > 0:
        diameter, diameter_mm, x, y , method= drops.extract_diameter_and_location(curr_drop_trail_mask, pixel_to_mm_ratio_x, prev_plate_BGR, file_name, video_dir)
    else: diameter, diameter_mm, x, y, method = 0 ,0 ,0 ,0, "--None--"

    # Show images
    cv2.imshow(prev_plate_name, prev_plate_BGR)
    cv2.imshow(curr_plate_name,
               bgr_img_masking(curr_plate_BGR, curr_local_max, [1], 1))
    # Show masked images
    past_frame  = bgr_img_masking(prev_plate_BGR, curr_drop_trail_mask, [1], 1)
    cv2.imshow(masked_prev_plate_name,
               past_frame)
    # Current frame
    current_frame = bgr_img_masking(curr_plate_BGR, curr_drop_trail_mask, [1], 1)
    cv2.imshow(masked_curr_plate_name,
               current_frame)
    # Write images
    write_image_file_path = video_dir + str(file_name)+".jpg"
    image_to_save = Image.fromarray(current_frame)
    image_to_save.save(write_image_file_path)
    # Adding peak profiles to the peak image
    peak_diff_img = cv2.cvtColor(cv2.equalizeHist(scale_array_min_max(curr_peaks,
                                                                      0,
                                                                      max_profile_level).astype(np.uint8)),
                                 cv2.COLOR_GRAY2BGR)
    # peak_diff_img = cv2.polylines(peak_diff_img, [hist_polyline], False, (255, 255, 0), 2)
    peak_diff_img = cv2.polylines(peak_diff_img, [drop_trails_polyline], False, (255, 255, 255), 4)
    peak_diff_img = cv2.polylines(peak_diff_img, [prev_polyline], False, (255, 0, 0), 2)
    peak_diff_img = cv2.polylines(peak_diff_img, [curr_polyline], False, (0, 0, 255), 2)
    peak_diff_img = cv2.polylines(peak_diff_img, [diff_polyline], False, (0, 255, 0), 2)
    # text_pos = (min(max_peak_diff_idx[0][0], x_max - 70), max(30, min(y_max - diff_scale_level[0], max_profile_level - 10)))
    # peak_diff_img = cv2.putText(peak_diff_img, str(diff_max_peak[0][0]),
    #                             text_pos, cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow(masked_peak_landscape_name,
               bgr_img_masking(cv2.cvtColor(scale_array_min_max(curr_peak_landscape,
                                                                0,
                                                                max_profile_level).astype(np.uint8),
                                            cv2.COLOR_GRAY2BGR), curr_drop_trail_mask, [1], 1))
    # cv2.imshow(masked_peak_landscape_name,
    #            scale_array_min_max(curr_peak_landscape,
    #                                0,
    #                                max_profile_level).astype(np.uint8))
    cv2.imshow(peak_diff_name, peak_diff_img)
    # Move images on the screen
    dy = 0
    dx = 0
    cv2.moveWindow(prev_plate_name, dx, dy + prev_plate_BGR.shape[0])
    cv2.moveWindow(curr_plate_name, dx, dy)
    cv2.moveWindow(masked_prev_plate_name, dx + prev_plate_BGR.shape[1], dy + prev_plate_BGR.shape[0])
    cv2.moveWindow(masked_curr_plate_name, dx + prev_plate_BGR.shape[1], dy)
    cv2.moveWindow(masked_peak_landscape_name, dx + 2*prev_plate_BGR.shape[1], dy + prev_plate_BGR.shape[0])
    cv2.moveWindow(peak_diff_name, dx + 2*prev_plate_BGR.shape[1], dy)

    # Wait for a key press
    # key = cv2.waitKey(0)
    #
    # if key in [ord('q'), ord('Q')]:
    #     return True

    # cv2.destroyAllWindows()
    cv2.waitKey(1)
    return False, [diameter, diameter_mm, x, y, method]

def widen_drop_trail_footprints(drop_footprint, peak_profile, diff_peak_profile, min_diff_peak_profile):
    drop_labels, n_labels = ndimage.label(drop_footprint)
    new_footprint = drop_footprint.copy()
    for i_p in range(4):
        for i_label in range(1, 1+n_labels):
            label_idx = np.where(drop_labels == i_label)
            expansion_areas = np.logical_and(peak_profile[i_p, :] <= np.median(peak_profile[i_p, :][label_idx]),
                                             diff_peak_profile[i_p, :] >= min_diff_peak_profile)
            expanded_footprint = ndimage.binary_propagation(drop_labels == i_label, mask=expansion_areas)
            new_footprint |= expanded_footprint
    return new_footprint.astype(np.uint8)


def find_drop_trails(i_frame, file_name, curr_plate_BGR, curr_plate_BW,
                     prev_plate_BGR, prev_plate_BW, prev_peak_profile, prev_peak_histogram, prev_peak_landscape,
                     prev_drop_trail_masks, video_dir, pixel_to_mm_ratio_x):
    # Calculate column profiles on the plate
    curr_local_max, curr_peaks, curr_peak_profile = find_peaks(curr_plate_BW)

    diff_peak_profile = ndimage.median_filter(np.maximum(0, prev_peak_profile - curr_peak_profile), size=(1, 17))
    max_peak_diff_idx = [np.where(diff_peak_profile[i_p, :] == max(diff_peak_profile[i_p, :]))[0] for i_p in range(4)]
    curr_peak_histogram = Counter(curr_peaks[curr_peaks > 0].flatten())
    min_diff_peak_profile = 50
    if all([diff_peak_profile[i_p, max_peak_diff_idx[i_p][0]] < 175 for i_p in range(4)]) or \
            (img_is_flat(curr_peak_histogram) and img_is_flat(prev_peak_histogram)):
        # We should not detect anything in images that when the maximum cummulative peak difference per column is low
        # or when both current and previous images are flat (so before drops start accumulating)
        curr_drop_footprints = np.zeros((1, curr_peak_profile.shape[1]))
    else:
        # prev_peak_median = np.median(prev_peak_profile)
        # curr_drop_footprints = np.logical_and(diff_peak_profile > prev_peak_profile / 3,
        #                              prev_peak_profile > prev_peak_median / 3).astype(np.int32)
        curr_drop_footprints = np.max(np.logical_and(diff_peak_profile >= 0.75 * prev_peak_profile,
                                                     diff_peak_profile >= min_diff_peak_profile),
                                      axis=0)
        # Get rid of thin spikes
        curr_drop_footprints = widen_drop_trail_footprints(ndimage.median_filter(curr_drop_footprints, size=3),
                                                           curr_peak_profile,
                                                           diff_peak_profile,
                                                           min_diff_peak_profile)
    # Create a mask of forbidden areas
    curr_relaxed_drop_footprints = ndimage.binary_propagation(curr_drop_footprints.reshape(1, -1),
                                                              mask=(diff_peak_profile[0, :] < min_diff_peak_profile / 2).reshape(1,-1))
    forbidden_mask = np.ones_like(curr_plate_BW)
    forbidden_mask[:, np.where(curr_relaxed_drop_footprints > 0)] = 0
    # Interpolate trail landscape based on the detected peaks
    curr_peak_landscape = propagate_peaks(curr_peaks)
    # Build droplet trail mask starting from the footprint on the bottom
    curr_drop_trail_mask = create_trail_mask_from_drop_footprint(curr_peak_landscape.copy(),
                                                                 forbidden_mask,
                                                                 curr_drop_footprints,
                                                                 prev_drop_trail_masks,
                                                                 curr_plate_BW,
                                                                 prev_plate_BW)


    # Visualize results
    stop_flag, drop_data = visualize_img_and_drop_profiles(i_frame, file_name,
                                                curr_plate_BGR, prev_plate_BGR,
                                                curr_peaks, curr_peak_landscape, curr_drop_footprints.flatten(), curr_drop_trail_mask,
                                                curr_peak_profile, prev_peak_profile, diff_peak_profile,
                                                curr_local_max, max_peak_diff_idx,video_dir, pixel_to_mm_ratio_x)

    return stop_flag, curr_drop_trail_mask, curr_peak_profile, curr_peak_histogram, curr_peak_landscape, drop_data



