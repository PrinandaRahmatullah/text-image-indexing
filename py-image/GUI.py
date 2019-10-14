import cv2
import numpy as np 
import math

from Matcher import Matcher

class Circle(object):
    def __init__(self, radius, x, y, folder, color):
        self.r = radius
        self.x = x
        self.y = y
        self.folder = folder
        self.color = color
        self.panoWindow = self.folder + " panorama"
        self.pano = cv2.imread(self.folder + "_panorama.jpg")

    def draw(self, image):
        cv2.circle(image, (self.x, self.y), self.r, self.color, -1)

    def setColor(self, co):
        self.color = co

    def showPanorama(self):
        cv2.imshow(self.panoWindow, self.pano)
        cv2.waitKey(0)
        cv2.destroyWindow(self.panoWindow)

    def inCircle(self, point):
        if (point[0]-self.x)**2 + (point[1]-self.y)**2 < self.r**2:
            return True
        return False

class Arrow(object):
    def __init__(self, Circle, length, angle, size, color):
        self.size = size
        self.color = color
        self.circle = Circle
        self.angle = angle
        self.length = length
        self.x = int(Circle.x + length*math.cos(angle + 3*math.pi/2))
        self.y = int(Circle.y + length*math.sin(angle + 3*math.pi/2))


    def setSize(self, s):
        self.size = s

    def setLength(self, l):
        self.length *= l
        self.x = int(self.circle.x + self.length*math.cos(self.angle + 3*math.pi/2))
        self.y = int(self.circle.y + self.length*math.sin(self.angle + 3*math.pi/2))

    def setColor(self, co):
        self.color = co

    def draw(self, image):
        # print (self.color)
        cv2.arrowedLine(image, (self.circle.x, self.circle.y), (self.x, self.y), self.color, self.size)
        # cv2.arrowedLine(image, (self.circle.x,self.circle.y), (100,100), (50, 50, 50), 10)



def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        for circle in circles:
            if circle.inCircle((x,y)):
                circle.showPanorama()

def getArrows(Cir, intervals):
    '''return a list of arrows pointing in all direction
    intervals defined how many arrows there are in a full circle'''
    angInterval = 2*math.pi/intervals
    center_x = Cir.x
    center_y = Cir.y
    arrowList = []
    for i in range(intervals):
         # print (angleInt*i)
        # print (math.cos(angInterval*i))
        # x = int(center_x + 60*math.cos(angInterval*i + 3*math.pi/2))
        # y = int(center_y + 60*math.sin(angInterval*i + 3*math.pi/2))
        # dist = math.sqrt(x*x + y*y)
        # xnorm = center_x + int(x/dist * 10) 
        # ynorm = center_y + int(y/dist * 10) 
        arrow = Arrow(Cir, 60, angInterval * i, 1, (200,200,200))
        arrowList.append(arrow)
        # angList.append((center_x + center_x*math.cos(angInterval*i), 
        #     center_y + center_y*math.sin(angInterval*i)))
    
    return arrowList

def drawArrows(arrowL):
    ''' this function initialize all the arrows. All grey with length 1'''
    # arrowL = getArrow(Circle, interval)
    for arrow in arrowL:
        arrow.draw(img)

def setArrow(arrowL, index, thickness, color, length):
    ''' this function access an individual arrow and modify its 
    size, color, and magnitude'''
    arrowL[index].setSize(thickness)
    arrowL[index].setColor(color)
    arrowL[index].setLength(length)


def drawCircle(circleL):
    for circle in circleL:
        circle.draw(img) 

def normalize(prob):
    return [float(i)/sum(prob) for i in prob]

def illustrateProb(circle, arrowsL, probsL):
    '''circleL is the list of circles in one region, and arrowsL are the 
    corresponding circles'''
    
    # Let the color range goes from 50 to 255. The higher it is the more
    # likely the robot is there
    minColor = 0
    maxColor = 255
    diff = maxColor - minColor
    totalMatches = sum(list(map(lambda x: x[0],probsL)))
    for circle_ind in range(len(probsL)):
        num_matches, list_of_probs = probsL[circle_ind]
        diffProb = max(list_of_probs) - min(list_of_probs)
        num_probs = len(list_of_probs)
        this_circles_arrows = arrowsL[circle_ind]
        circle[circle_ind].setColor(((num_matches/ totalMatches)*255, (num_matches/ totalMatches)*255,
                                    (num_matches/ totalMatches)*255))
        for j in range(num_probs ):
            this_prob = list_of_probs[j]
            color = (this_prob/diffProb * 255, 50, 50)
            mult = (num_matches/ totalMatches) * this_prob * 20
            setArrow(this_circles_arrows, j, 1, color, mult)

def read(filename):
    file = open(filename,'r')
    content = file.read().split('\n')[:-1]
    newContent = []
    for i in range(len(content))[::2]:
        L = list(map(float, content[i+1].replace('[','').replace(']','').split(',')))
        newContent.append((int(content[i]), L))
    return newContent

# spot_one = imageMatch('query.jpg','spot_one')
# spot_two = imageMatch('query.jpg','spot_two')
# spot_three = imageMatch('query.jpg','spot_three')
# p = [spot_one, spot_two, spot_three]

# p = [ (1000, [0.4]*23 + [0.1]), (1000, [0.4]*23 + [0.1]), (1000, [0.4]*23 + [0.1])]

# print (len(p))
# Initiate Screen
img = np.zeros((540, 960, 3), np.uint8)
cv2.namedWindow('GUI')

# Initiating Circles
circle1 = Circle(50, 200, 200, 'spot_one', [150, 150, 150])
Matcher('query.jpg','spot_one','SURF',320,240).write('out.txt','w')
circle2 = Circle(50, 400, 200, 'spot_two', [150, 150, 150])
Matcher('query.jpg','spot_two','SURF',320,240).write('out.txt','a')
circle3 = Circle(50, 600, 200, 'spot_three', [150, 150, 150])
Matcher('query.jpg','spot_three','SURF',320,240).write('out.txt','a')
circles = [circle1, circle2, circle3]

# Initiating Arrows
arrows1 = getArrows(circle1, 25)
arrows2 = getArrows(circle2, 25)
arrows3 = getArrows(circle3, 25)
Arrows = [arrows1, arrows2, arrows3]

p = read('out.txt')

# Account for possibility
illustrateProb(circles, Arrows, p)

# Constructing Circles and Arrows
drawCircle(circles)
drawArrows(arrows1)
drawArrows(arrows2)
drawArrows(arrows3)


cv2.setMouseCallback('GUI', click)

while True:
    cv2.imshow('GUI', img)



    k = cv2.waitKey(0) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()