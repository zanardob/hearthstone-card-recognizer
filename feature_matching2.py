import sys
import cv2 as cv
import numpy as np
import matplotlib.pyplot as pl


def main():
    if len(sys.argv) != 2:
        print("usage %s scene" % sys.argv[0])
        sys.exit(1)

    MIN_MATCH_COUNT = 10
    sift = cv.xfeatures2d.SIFT_create()

    # Read the scene passed
    screenshot = cv.imread(sys.argv[2])

    # Cropping the scene to get the cards at hand
    hand = []
    hand.append(screenshot[1001:1079,  586:674])
    hand.append(screenshot[993:1079,   643:733])
    hand.append(screenshot[961:1079,   702:789])
    hand.append(screenshot[951:1079,   760:839])
    hand.append(screenshot[938:1079,   820:889])
    hand.append(screenshot[929:1079,   881:944])
    hand.append(screenshot[930:1079,  932:1008])
    hand.append(screenshot[937:1079,  990:1063])
    hand.append(screenshot[949:1079, 1044:1125])
    hand.append(screenshot[976:1079, 1110:1234])

    # Computing the descriptors for each card
    hand_des = []
    for card in hand:
        _, des = sift.detectAndCompute(card, None)
        hand_des.append(des)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    # Tries to match each card in hand with the database cards
    for card in hand:
        # Load the descriptors of the cards in the database
        # For each set of descriptors, do:
            flann = cv.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(desFROMTHEDATABASE, desFROMTHECARDATHAND, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    if len(good) >= MIN_MATCH_COUNT:
        # Matched the card

if __name__ == '__main__':
    main()
