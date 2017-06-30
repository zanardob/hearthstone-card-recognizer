import sys
import cv2 as cv
import numpy as np
import json
import json_dict as jd
import card_crops as cc


def hand_counter(board, screenshot):
    mask_names = [
        "masks/mask_0_cards.png",
        "masks/mask_1_cards.png",
        "masks/mask_2_cards.png",
        "masks/mask_3_cards.png",
        "masks/mask_4_cards.png",
        "masks/mask_5_cards.png",
        "masks/mask_6_cards.png",
        "masks/mask_7_cards.png",
        "masks/mask_8_cards.png",
        "masks/mask_9_cards.png",
        "masks/mask_10_cards.png",
    ]

    board = cv.imread(board['img'])
    board = cv.blur(board, (5, 5))
    screenshot = cv.blur(screenshot, (5, 5))
    subtraction = np.subtract(board[930:1080, 584:1240], screenshot[930:1080, 584:1240])

    limit = 40
    for row in subtraction:
        for pixel in row:
            b, g, r = pixel[0], pixel[1], pixel[2]
            if((b < limit) or (b > (255 - limit))):
                pixel[0] = 0
                b = 0
            if((g < limit) or (g > (255 - limit))):
                pixel[1] = 0
                g = 0
            if((r < limit) or (r > (255 - limit))):
                pixel[2] = 0
                r = 0

            sum = int(b) + int(g) + int(r)
            if sum < limit*3:
                pixel[0], pixel[1], pixel[2] = 0, 0, 0
            else:
                pixel[0], pixel[1], pixel[2] = 255, 255, 255

    hits = [0] * 11
    for maskid, mask_name in enumerate(mask_names):
        mask = cv.imread(mask_name, 0)

        for rowid, row in enumerate(subtraction):
            for pixelid, pixel in enumerate(row):
                if pixel[0] == mask[rowid][pixelid]:
                    hits[maskid] += 1;
        print(mask_name + ' hits: ' + str(hits[maskid]))

    maxHit = 0
    bestHit = 0
    for i, hit in enumerate(hits):
        if hit > maxHit:
            bestHit = i
            maxHit = hit

    return bestHit


def minion_counter(board, screenshot):
    # Subtract the board from the screenshot to remove background
    subtracted = cv.imread(board['img'], 0)
    subtracted = np.subtract(screenshot, subtracted)

    # Blur the image to remove small imperfections
    thresh_img = cv.medianBlur(subtracted, 5)

    # Threshold the image to isolate minions
    _, thresh_img = cv.threshold(thresh_img, 1, 255, cv.THRESH_BINARY)

    # Crop the scene and threshold according to possible minion positions
    candidates = cc.crops(screenshot).get_minion_crop()
    thresh_imgs = cc.crops(thresh_img).get_minion_crop()

    # Setup kernel for the upcoming erosion
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (100, 100))

    minion_imgs = []
    for index, img in enumerate(thresh_imgs):
        # Erode the image to distinguish good matches against mismatches
        erosion = cv.erode(img, kernel, iterations=1)
        w, h = img.shape

        # If the central pixel on the image is not black, it is a match
        if erosion[int(w/2)][int(h/2)] != 0:
            minion_imgs.append(candidates[index])

    return minion_imgs


def board_recognizer(screenshot):
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
    _, current_des = sift.detectAndCompute(board_detail, None)

    for board in boards:
        board_img = cv.imread(board['img'], 0)[720:970, 1256:1600]
        _, des = sift.detectAndCompute(board_img, None)
        board['des'] = des

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv.FlannBasedMatcher(index_params, search_params)

    # Compares each board of the database with the current
    # board and returns the name of the best match
    match = None
    best = 0
    for board in boards:
        matches = flann.knnMatch(current_des, board['des'], k=2)

        count = 0
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                count += 1

        if count > best:
            best = count
            match = board

    return match


def card_recognizer(cards_imgs, cards_json, minions_only=False):
    cards_des = []
    sift = cv.xfeatures2d.SIFT_create()
    for card in cards_imgs:
        _, des = sift.detectAndCompute(card, None)
        cards_des.append(des)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv.FlannBasedMatcher(index_params, search_params)

    # Compares each card of the database with the
    # current card and returns the best match
    results = []
    for index, card in enumerate(cards_imgs):
        match = None
        best = 0
        for obj in cards_json['cards']:
            if minions_only:
                if obj['type'] != 'Minion':
                    continue

            db_des = np.load(obj['descriptors'])
            matches = flann.knnMatch(cards_des[index], db_des, k=2)

            count = 0
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    count += 1

            if count > best:
                best = count
                match = obj

        results.append(match)

    return results


def main():
    if len(sys.argv) != 3:
        print("usage %s scene number_of_cards" % sys.argv[0])
        sys.exit(1)

    with open('std_cards_list_descriptors.json', 'r') as cards_file:
        cards_json = jd.jdict(json.load(cards_file))

    # Read the scene passed
    screenshot = cv.imread(sys.argv[1], 0)

    # Recognizing the board being played on
    board = board_recognizer(screenshot)

    # Cropping the scene to get the cards at hand
    card_count = hand_counter(board, screenshot)
    hand_imgs = cc.crops(screenshot).get_hand_crop(card_count)
    # hand_imgs = cc.crops(screenshot).get_hand_crop(int(sys.argv[2]))

    # Getting the minions in play
    minion_imgs = minion_counter(board, screenshot)

    # Recognizing each card on the hand of the player
    hand = card_recognizer(hand_imgs, cards_json)

    # Recognizing each minion in play
    minions = card_recognizer(minion_imgs, cards_json, True)

    print('The current board is ' + board['name'] + '.')
    print('Cards currently at hand:')
    for card in hand:
        print('\t(' + card['cardId'] + ') ' + card['name'])
    print('Minions currently on the board:')
    for minion in minions:
        print('\t(' + minion['cardId'] + ') ' + minion['name'])


if __name__ == '__main__':
    main()
