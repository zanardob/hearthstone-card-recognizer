import sys
import cv2 as cv
import numpy as np
import matplotlib.pyplot as pl


def main():
    if len(sys.argv) != 3:
        print("usage %s object scene" % sys.argv[0])
        sys.exit(1)

    MIN_MATCH_COUNT = 10

    card = cv.imread(sys.argv[1], 0)
    screenshot = cv.imread(sys.argv[2], 0)

    sift = cv.xfeatures2d.SIFT_create()

    kp1, des1 = sift.detectAndCompute(card, None)
    kp2, des2 = sift.detectAndCompute(screenshot, None)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)

    flann = cv.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.8 * n.distance:
            good.append(m)

    if len(good) >= MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        h, w = card.shape
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        dst = cv.perspectiveTransform(pts, M)

        screenshot = cv.polylines(screenshot, [np.int32(dst)], True, 255, 3, cv.LINE_AA)
    else:
        print("Not enough good matches were found - %d/%d" % len(good), MIN_MATCH_COUNT)
        matchesMask = None

    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=None,
                       matchesMask=matchesMask,
                       flags=2)

    result = cv.drawMatches(card, kp1, screenshot, kp2, good, None, **draw_params)
    pl.imshow(result, 'gray')
    pl.show()

if __name__ == '__main__':
    main()
