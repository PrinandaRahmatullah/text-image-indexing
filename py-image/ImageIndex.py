import cv2
import pickle
import glob
import argparse

from hist import RGBHist

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True, 
    help="Path to the directory that contains the images to be stored")
ap.add_argument("-i", "--index", required=True,
    help="Path to where the computed index will be stored")
args = vars(ap.parse_args())

index = {}
desc = RGBHist([8, 8, 8])

for imagePath in glob.glob(args["dataset"] + "/*.jpg"):
    k = imagePath[imagePath.rfind("/") + 1:]
    image = cv2.imread(imagePath)
    print(imagePath)
    features = desc.describe(image)
    index[k] = features

f = open(args["index"], "wb")
pickle.dump(index, f)