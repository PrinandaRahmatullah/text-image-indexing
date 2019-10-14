import cv2
import numpy as np

class RGBHist(object):
    def __init__(self, bins):
        self.bins = bins
    def describe(self, image):
        hist = cv2.calcHist([image], [0, 1, 2], None, self.bins, [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        return hist.flatten()