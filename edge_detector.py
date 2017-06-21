import sys
import cv2 as cv
import numpy as np
import matplotlib.pyplot as pl

def main():
    if len(sys.argv) != 2:
        print("usage %s screenshot" % sys.argv[0])
        sys.exit(1)

    # Pre-processing: Convert frame to standard size, 1024x768
    screenshot = cv.imread(sys.argv[1], 0)
    # screenshot = cv.medianBlur(screenshot, 9)

    kernelGauss = np.array([[0.0625, 0.125, 0.0625], [0.125, 0.25, 0.125], [0.0625, 0.125, 0.0625]])
    kernelLaplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])

    result = cv.filter2D(screenshot, -1, kernelGauss)
    result = cv.filter2D(result, -1, kernelLaplacian)

    edges = cv.Canny(result, 75, 100)
    # _, contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    #
    # for c in contours:
    #     rect = cv.minAreaRect(c)
    #     box = cv.boxPoints(rect)
    #     area = cv.contourArea(box)
    #     if area < 50:
    #         continue
    #     screenshot = cv.polylines(screenshot, [np.int32(box)], True, 255, 3, cv.LINE_AA)

    # pl.subplot(121)
    # pl.axis('off')
    # pl.imshow(screenshot, cmap='gray')
    #
    # pl.subplot(122)
    pl.axis('off')
    pl.imshow(edges, cmap='gray')

    pl.show()

if __name__ == '__main__':
    main()
