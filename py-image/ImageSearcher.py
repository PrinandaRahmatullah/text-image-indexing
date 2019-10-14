import numpy as np 
import argparse
import pickle
import cv2

from Searcher import Searcher
from hist import RGBHist

ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True,
    help="Path to the query image")
ap.add_argument("-d", "--dataset", required=True,
    help="Path to the dataset")
ap.add_argument("-i", "--index", required=True,
    help="Path to the index")
args = vars(ap.parse_args())

index = pickle.load(open(args["index"], 'rb'))
searcher = Searcher(index)

path = args["query"]
queryImage = cv2.imread(path)
cv2.imshow("Query", queryImage)
print("query: %s" % path)

desc = RGBHist([8,8,8])
queryFeatures = desc.describe(queryImage)

results = searcher.search(queryFeatures)

for j in range(10):
    (score, imageName) = results[j]
    print("\t%d. %s : %.3f" % (j + 1, imageName, score))

matchPath = args["dataset"] + "/%s" % (results[0][1])
match = cv2.imread(matchPath)
cv2.imshow("Match", match)
cv2.waitKey(0)