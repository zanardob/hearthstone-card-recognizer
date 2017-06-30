import sys
import cv2 as cv
import numpy as np
import matplotlib.pyplot as pl


def recognize_board(screenshot):
    sift = cv.xfeatures2d.SIFT_create()

    boards = [
        {
            'name': 'Gadgetzan',
            'img': "Board/Gadgetzan.png"
        },
        {
            'name': "Karazhan",
            'img': "Board/Karazhan.png"
        },
        {
            'name': "Orgrimmar",
            'img': "Board/Orgrimmar.png"
        },
        {
            'name': "Pandaria",
            'img': "Board/Pandaria.png"
        },
        {
            'name': "Stormwind",
            'img': "Board/Stormwind.png"
        },
        {
            'name': "Stranglethorn",
            'img': "Board/Stranglethorn.png"
        },
        {
            'name': "Un'Goro",
            'img': "Board/Un'Goro.png"
        },
        {
            'name': "Whisper of the Old Gods",
            'img': "Board/Whisper of the Old Gods.png"
        }
    ]

    board_detail = screenshot[720:970, 1256:1600]
    _, des = sift.detectAndCompute(board_detail, None)

    for board in boards:
        board_img = cv.imread(board['img'], 0)[720:970, 1256:1600]
        _, des = sift.detectAndCompute(board_img, None)
        board['des'] = des

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv.FlannBasedMatcher(index_params, search_params)

    # Compares each card of the database with the
    # current card and prints the best match
    match = None
    best = 0
    for board in boards:
        matches = flann.knnMatch(des, board['des'], k=2)

        count = 0
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                count += 1

        if count > best:
            best = count
            match = board

    return match['name']


if __name__ == '__main__':
    screenshot = cv.imread(sys.argv[1])
    screenshot = screenshot[720:970, 1256:1600]

    board = cv.imread(recognize_board(screenshot))
    board = board[720:970, 1256:1600]

    pl.subplot(121)
    pl.axis('off')
    pl.imshow(cv.cvtColor(board, cv.COLOR_BGR2RGB))

    pl.subplot(122)
    pl.axis('off')
    pl.imshow(cv.cvtColor(screenshot, cv.COLOR_BGR2RGB))

    pl.show()
