"""Occluder masks: point-prompted segmentation (MediaPipe magic_touch) + sky key."""
import os

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions, vision
from mediapipe.tasks.python.components.containers.keypoint import NormalizedKeypoint

MODEL = os.environ.get("MAGIC_TOUCH", "models/magic_touch.tflite")
_seg = None


def _segmenter():
    global _seg
    if _seg is None:
        opts = vision.InteractiveSegmenterLegacyOptions(
            base_options=BaseOptions(model_asset_path=MODEL), output_confidence_masks=True)
        _seg = vision.InteractiveSegmenterLegacy.create_from_options(opts)
    return _seg


def point_mask(rgb, points, box=None, thresh=0.5):
    """Union of masks for each normalized (x, y) click point. Returns float 0..1.

    box = (x0, y0, x1, y1) normalized: segmentation runs on that crop only
    (more pixels on the subject, no bleed into neighbours) and is pasted back.
    """
    H, W = rgb.shape[:2]
    x0, y0, x1, y1 = box or (0, 0, 1, 1)
    px0, py0, px1, py1 = int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)
    crop = np.ascontiguousarray(rgb[py0:py1, px0:px1])
    img = mp.Image(image_format=mp.ImageFormat.SRGB, data=crop)
    Roi = vision.InteractiveSegmenterLegacyRegionOfInterest
    acc = np.zeros(crop.shape[:2], np.float32)
    for x, y in points:
        kx, ky = (x - x0) / (x1 - x0), (y - y0) / (y1 - y0)
        roi = Roi(format=Roi.Format.KEYPOINT, keypoint=NormalizedKeypoint(kx, ky))
        conf = _segmenter().segment(img, roi).confidence_masks[0].numpy_view()
        conf = conf.reshape(crop.shape[:2]) if conf.ndim == 3 else conf
        acc = np.maximum(acc, (conf > thresh).astype(np.float32))
    out = np.zeros((H, W), np.float32)
    out[py0:py1, px0:px1] = acc
    return out


def sky_mask(rgb):
    """Sky = bright, blue-dominant, low-texture pixels connected to the top edge.
    Returns float 0..1 (1 = sky)."""
    f = rgb.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    # deep sky is clearly blue; the hazy band near the horizon is near-white
    # but still bluer than red, while sandstone / cream walls are red-dominant
    blue = ((b > r + 18) & (b > g - 4) & (lum > 120)) | ((b >= r + 6) & (b >= g) & (lum > 160))
    tex = cv2.Laplacian(cv2.GaussianBlur(lum, (3, 3), 0), cv2.CV_32F)
    smooth = cv2.GaussianBlur(np.abs(tex), (5, 5), 0) < 6
    cand = (blue & smooth).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand, connectivity=4)
    top = set(np.unique(lab[: max(2, rgb.shape[0] // 40)])) - {0}
    sky = np.isin(lab, list(top)).astype(np.uint8)
    # close pinholes inside the sky but keep thin poles / wires as occluders
    sky = cv2.morphologyEx(sky, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return sky.astype(np.float32)


def resize_mask(m, size, feather_px=1.5):
    """Upscale a source-res mask to output size and feather by ~1-2 px."""
    m = cv2.resize(m, size, interpolation=cv2.INTER_LINEAR)
    if feather_px:
        m = cv2.GaussianBlur(m, (0, 0), feather_px)
    return np.clip(m, 0, 1)


def find_pole_x(rgb, xr=(0.5, 0.9), rows=(0.02, 0.30)):
    """Normalized x of the most solid vertical non-sky column in the upper frame
    (a utility / light pole crossing the sky)."""
    sky = sky_mask(rgb)
    H, W = sky.shape
    band = 1 - sky[int(rows[0] * H):int(rows[1] * H), int(xr[0] * W):int(xr[1] * W)]
    col = cv2.GaussianBlur(band.mean(axis=0, keepdims=True), (0, 0), 1.5)[0]
    return xr[0] + (int(np.argmax(col)) + 0.5) / W
