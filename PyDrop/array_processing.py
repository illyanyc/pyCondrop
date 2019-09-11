from scipy import ndimage  #, signal
import numpy as np
from collections import Counter


def scale_array_max(array, new_max):
    array_max = np.max(array)
    if array_max > 0:
        array = array * (new_max / array_max)
    return array


def scale_array_min_max(img, new_min, new_max):
    old_min = ndimage.minimum(img)
    old_max = ndimage.maximum(img)
    if old_min == old_max:
        return img - old_min + new_min
    return new_min + (img - old_min) * ((new_max - new_min) / (old_max - old_min))


def lift_local_lows(img, low_level_ratio):
    delta = 5
    loc_max = ndimage.maximum_filter(img, size=1+2*delta)
    loc_min = ndimage.minimum_filter(img, size=1+2*delta)
    loc_med = ndimage.median_filter(img, size=1+2*delta)
    loc_lows_mask = (img <= np.round((1-low_level_ratio) * loc_min + low_level_ratio * loc_max))
    new_img = img.copy()
    new_img[loc_lows_mask] = loc_med[loc_lows_mask]
    loc_lows_mask = loc_lows_mask.astype(np.uint8)
    return new_img, loc_lows_mask


def remove_objects_by_size(mask, area_low, area_high):
    labels, n_labels = ndimage.label(ndimage.binary_closing(mask, np.ones((3, 3))), np.ones((3, 3)))
    for lbl, lbl_count in Counter(labels.flatten()).items():
        if lbl > 0 and (lbl_count < area_low or lbl_count > area_high):
            # Eliminate object
            labels[labels == lbl] = 0
    return (labels > 0).astype(np.uint8)
