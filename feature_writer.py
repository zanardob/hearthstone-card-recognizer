import os
import cv2 as cv
import numpy as np


def main():
    sift = cv.xfeatures2d.SIFT_create()

    i = 0
    keypoints = dict()
    descriptors = dict()
    for filename in os.listdir('db'):
        if i < 100:
            card = cv.imread('db/' + filename, 0)
            kp, des = sift.detectAndCompute(card, None)

            card_name = filename.split(".")[0]
            keypoints[card_name] = kp
            descriptors[card_name] = des

            i += 1
            print(card_name)

    np.savez('card_features', keypoints=keypoints, descriptors=descriptors)


if __name__ == '__main__':
    main()
