

# import cv2
import numpy as np


def bw_img_masking(bw_img, mask, mask_alpha=1.0):
    new_bw_img = bw_img.copy()
    mask_threshold = 1
    mask[np.where(mask >= mask_threshold)] = 255
    mask_positions = np.where(mask >= mask_threshold)
    new_bw_img[mask_positions] = (1 - mask_alpha) * new_bw_img[mask_positions] + mask_alpha * mask[mask_positions]
    return new_bw_img


def bgr_img_masking(bgr_img, mask, layers, mask_alpha=1.0):
    new_bgr_img = bgr_img.copy()
    mask_threshold = 1
    mask[np.where(mask >= mask_threshold)] = 255
    mask_positions = np.where(mask >= mask_threshold)
    for idx_layer in range(3):
        if idx_layer in layers:
            layer = new_bgr_img[:, :, idx_layer].copy()
            layer[mask_positions] = \
                (1 - mask_alpha) * layer[mask_positions] + mask_alpha * mask[mask_positions]
        # else:
        #     layer[mask_positions] = \
        #         (1 - mask_alpha) * layer[mask_positions]
            new_bgr_img[:, :, idx_layer] = layer
    return new_bgr_img


