'''
Image Matching
==============

Takes a query image and image dataset and returns the best
match. A preliminary search by color composition is performed
to narrow the search span, and a SURF match is done on the
best matches.

Usage:
------
    python ImageMatcher.py -q [<query image>] -d [<dataset directory>]
'''


import cv2
import numpy as np
import argparse
import glob
from matplotlib import pyplot as plt

from pano import Panorama
from search import Searcher

class ImageMatcher(object):
    '''
    Class for handling image indexing, color matching, and SURF matching.
    '''

    def __init__(self, img, data, seeColorMatches=False, seeSURFMatches=False):
        self.image = img
        self.dataset = data
        self.index = self.createIndex()
        self.estimates = []
        self.seeColorMatchesFlag = seeColorMatches
        self.seeSURFMatchesFlag = seeSURFMatches

    def createHistogram(self, image, bins=[8, 8, 8]):
        '''
        Creates a flattened 3D histogram.
        '''

        hist = cv2.calcHist([image], [0, 1, 2], None, bins, [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        return hist.flatten()

    def createIndex(self):
        '''
        Creates an dictionary with keys as image names and values as histograms.
        '''

        print("Indexing: " + self.dataset + "...")
        index = {}

        for imagePath in glob.glob(self.dataset + "/*.jpg"):
            filename = imagePath[imagePath.rfind("/") + 1:]
            image = cv2.imread(imagePath)
            print('\t%s' % imagePath)
            features = self.createHistogram(image)
            index[filename] = features

        return index

    def searchByColor(self):
        '''
        Searches query image against index and returns the specified number of matches.
        '''

        MAX_NUMBER_MATCHES = 5

        image = cv2.imread(self.image)
        print("Querying: " + self.image + " ...")
        searcher = Searcher(self.index)
        queryFeatures = self.createHistogram(image)

        results = searcher.search(queryFeatures)[:MAX_NUMBER_MATCHES]

        print("Matches found:")
        for j in range(len(results)):
            (score, imageName) = results[j]
            print("\t%d. %s : %.3f" % (j+1, imageName, score))

        return results

    def showColorResults(self):
        '''
        Displays the results of color matching.
        '''

        results = self.searchByColor()
        cv2.imshow("Query", cv2.imread(self.image))

        for i in range(len(results)):
            match = cv2.imread(self.dataset + "/" + results[i][1])
            cv2.imshow("Match " + str(i+1), match)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def SURFmatch(self, imageName):
        '''
        Performs a SURF image match of a query image against the specified image from 
        the dataset. 
        '''

        print("SURF matching: " + imageName + "...")
        MIN_MATCH_COUNT = 200
        FLANN_INDEX_KDTREE = 0

        query = cv2.imread(self.image)
        training = cv2.imread(self.dataset + "/" + imageName)
        surf = cv2.xfeatures2d.SURF_create()
        kp1, des1 = surf.detectAndCompute(query, None)
        kp2, des2 = surf.detectAndCompute(training, None)

        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)

        matches = flann.knnMatch(des1, des2, k=2)
        filtered = list(filter(lambda x:x[0].distance < 0.7*x[1].distance, matches))
        good = list(map(lambda x: x[0], filtered))

        if len(good) > MIN_MATCH_COUNT:
            print("\tFound %s matches" % (len(good)))
            src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            matchesMask = mask.ravel().tolist()

            h,w = query.shape[:2]
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            dst = cv2.perspectiveTransform(pts,M)

            width = cv2.imread(self.image).shape[1]
            offset = 0.5 * (0.5 * (dst[0][0] + dst[1][0]) + 0.5 * (dst[2][0] - width + dst[3][0] - width))

            self.estimates.append((offset[0] * 60/width + int(imageName[5:8]), len(good)))

            training = cv2.polylines(training,[np.int32(dst)],True,255,3,cv2.LINE_AA)

        else:
            print("\tNot enough matches found - %d/%d" % (len(good), MIN_MATCH_COUNT))

        if self.seeSURFMatchesFlag:
            draw_params = dict(matchColor=(0,255,0), 
                singlePointColor=None, 
                matchesMask=matchesMask, 
                flags=2)

            result = cv2.drawMatches(query,kp1,training,kp2,good,None,**draw_params)
            plt.imshow(result, 'gray'), plt.show()

        return len(good)

    def calculateAngle(self):
        totalMatches = sum(list(map(lambda x: x[1], self.estimates)))
        return sum(map(lambda x: x[0] * x[1]/totalMatches, self.estimates))

    def run(self):
        results = self.searchByColor()

        if self.seeColorMatchesFlag:
            self.showColorResults()

        for match in results:
            self.SURFmatch(match[1])

        angle = self.calculateAngle()
        print("Approximate angle: %0.2f" % angle)

        Panorama(self.dataset, 100, 100, angle).run()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-q', '--query', required=True,
        help='Path to query image')
    ap.add_argument('-d', '--dataset', required=True,
        help='Path to directory of training images')
    args = vars(ap.parse_args())

    print(__doc__)

    ImageMatcher(args['query'], args['dataset']).run()
