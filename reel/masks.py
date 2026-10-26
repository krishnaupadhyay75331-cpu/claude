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
    # bridge thin wires for connectivity only, so sky between wires still counts
    bridged = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab = cv2.connectedComponents(bridged, connectivity=4)
    top = set(np.unique(lab[: max(2, rgb.shape[0] // 20)])) - {0}
    sky = (np.isin(lab, list(top)) & (cand > 0)).astype(np.uint8)
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


def foliage_mask(rgb):
    """Leaves / trees: green-to-olive hue with texture. Returns float 0..1 (1 = foliage)."""
    hsv = cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    g = ((h > 45) & (h < 170) & (s > 0.15) & (v > 0.08)).astype(np.uint8)
    g = cv2.morphologyEx(g, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    g = cv2.morphologyEx(g, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return g.astype(np.float32)


def track_points(grays, i0, pts):
    """Lucas-Kanade track normalized points from frame i0 to every frame.
    Returns list (per frame) of normalized point lists."""
    H, W = grays[0].shape
    p0 = np.float32([[x * W, y * H] for x, y in pts]).reshape(-1, 1, 2)
    out = [None] * len(grays)
    out[i0] = p0
    lk = dict(winSize=(31, 31), maxLevel=3,
              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
    for rng in (range(i0 + 1, len(grays)), range(i0 - 1, -1, -1)):
        prev = i0
        for i in rng:
            p, st, _ = cv2.calcOpticalFlowPyrLK(grays[prev], grays[i], out[prev], None, **lk)
            # keep a lost point where it was
            out[i] = np.where(st.reshape(-1, 1, 1) == 1, p, out[prev])
            prev = i
    return [[(float(q[0][0]) / W, float(q[0][1]) / H) for q in o] for o in out]


def sky_occluder(rgb):
    """Things that poke up into the sky (poles, wires, roofs, branches, bunting).

    Per column the skyline is the lowest sky pixel, widened over neighbouring
    columns so a pole with sky on both sides still counts as in front. Below the
    skyline nothing occludes, so a hero that dips under the roofline stays legible.
    Returns float 0..1 (1 = occluder)."""
    sky = sky_mask(rgb) > 0
    H, W = sky.shape
    has = sky.any(axis=0)
    last = np.where(has, H - 1 - np.argmax(sky[::-1], axis=0), -1).astype(np.float32)
    skyline = cv2.dilate(last.reshape(1, -1), np.ones((1, 25), np.uint8)).ravel()
    rows = np.arange(H, dtype=np.float32)[:, None]
    return ((~sky) & (rows < skyline[None, :])).astype(np.float32)
