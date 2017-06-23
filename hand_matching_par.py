import sys
import cv2 as cv
import numpy as np
import matplotlib.pyplot as pl
import json
import json_dict as jd
import card_crops as cc
from joblib import Parallel, delayed
import multiprocessing


FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)


def detect_card(index, json, hand_des):
    flann = cv.FlannBasedMatcher(index_params, search_params)
    match = None
    best = 0
    for obj in json['cards']:
        db_des = np.load(obj['descriptors'])
        matches = flann.knnMatch(hand_des[index], db_des, k=2)

        count = 0
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                count += 1

        if count > best:
            best = count
            match = obj

    print('I believe card number ' + str(index+1) + ' is ' + match['name'] + ' (cardId: ' + match['cardId'] + ')')


def main():
    if len(sys.argv) != 3:
        print("usage %s scene number_of_cards" % sys.argv[0])
        sys.exit(1)

    with open('std_cards_list_descriptors.json', 'r') as cards_file:
        cards_json = jd.jdict(json.load(cards_file))

    # MIN_MATCH_COUNT = 10
    cores = multiprocessing.cpu_count()
    sift = cv.xfeatures2d.SIFT_create()

    # Read the scene passed
    screenshot = cv.imread(sys.argv[1], 0)

    # Cropping the scene to get the cards at hand
    hand = cc.crops(screenshot).get_crop(int(sys.argv[2]))

    # Computing the descriptors for each card
    hand_des = []
    for card in hand:
        _, des = sift.detectAndCompute(card, None)
        hand_des.append(des)

    # FLANN_INDEX_KDTREE = 0
    # index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    # search_params = dict(checks=50)
    # flann = cv.FlannBasedMatcher(index_params, search_params)

    # Tries to match each card in hand with the database cards
    inputs = int(sys.argv[2])

    Parallel(n_jobs=cores)(delayed(detect_card)(index, cards_json, hand_des) for index in range(len(hand)))
    # for index, card in enumerate(hand):
    #     match = None
    #     best = 0
    #     for obj in cards_json['cards']:
    #         db_des = np.load(obj['descriptors'])
    #         matches = flann.knnMatch(hand_des[index], db_des, k=2)
    #
    #         count = 0
    #         for m, n in matches:
    #             if m.distance < 0.7 * n.distance:
    #                 count += 1
    #
    #         if count > best:
    #             best = count
    #             match = obj
    #
    #     print('I believe card number ' + str(index+1) + ' is ' + match['name'] + ' (cardId: ' + match['cardId'] + ')')

    # if len(good) >= MIN_MATCH_COUNT:
    # Matched the card


if __name__ == '__main__':
    main()
