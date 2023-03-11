import os
import cv2
import numpy as np
try:
    from .config import *
except ImportError:
    from config import *


def blend_image(mask_name, color, reverse=False, p=1):
    mask_path = os.path.join(PATH_ASSETS, mask_name)
    image_path = mask_path + ".blended.png"
    mask = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)
    mask2 = cv2.cvtColor(mask, cv2.COLOR_BGR2HLS)
    mask2[:, :, 0] = color.hslHue() / 2
    mask2[:, :, 2] = color.hslSaturation()
    if reverse:
        mask2[:, :, 1] = (
            255 * ((7 / 8) - (6 / 8) * (mask[:, :, 1] / 255.0)**p)).astype(np.uint8)
    else:
        mask2[:, :, 1] = (255 * (mask[:, :, 1] / 255.0)**p).astype(np.uint8)
    mask2 = cv2.cvtColor(mask2, cv2.COLOR_HLS2BGR)
    mask[:, :, 0:3] = mask2
    cv2.imwrite(image_path, mask)
    return image_path
