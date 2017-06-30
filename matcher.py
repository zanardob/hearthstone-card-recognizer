import sys
import cv2 as cv
import numpy as np
import json
import json_dict as jd
import card_crops as cc


def hand_counter(board, screenshot):
    # This is a list of masks representing each possible number of cards in the player's hand.
    # Check the Mask folder for a visual idea of what they look like
    mask_names = [
        "Mask/0cards.png",
        "Mask/1card.png",
        "Mask/2cards.png",
        "Mask/3cards.png",
        "Mask/4cards.png",
        "Mask/5cards.png",
        "Mask/6cards.png",
        "Mask/7cards.png",
        "Mask/8cards.png",
        "Mask/9cards.png",
        "Mask/10cards.png"
    ]

    board = cv.imread(board['img']) # RGB

    # Blurring the images so that some small differences disappear in the subtraction
    board = cv.blur(board, (5, 5))
    screenshot = cv.blur(screenshot, (5, 5))

    # Subtracting the slice of the hand's player with the empty board template to count cards
    subtraction = np.subtract(board[930:1080, 584:1240], screenshot[930:1080, 584:1240])

    limit = 40

    for row in subtraction:
        for pixel in row:
            # Apply a threshold in each individual RGB value, needed after the subtraction
            b, g, r = pixel[0], pixel[1], pixel[2]
            if b < limit or b > 255 - limit:
                pixel[0] = 0
                b = 0
            if g < limit or g > 255 - limit:
                pixel[1] = 0
                g = 0
            if r < limit or r > 255 - limit:
                pixel[2] = 0
                r = 0

            # If the pixel is no longer relevant, make it black. Otherwise, make it white
            sum = int(b) + int(g) + int(r)
            if sum < limit*3:
                pixel[0], pixel[1], pixel[2] = 0, 0, 0
            else:
                pixel[0], pixel[1], pixel[2] = 255, 255, 255

    # Now, each mask will be tested with the processed hand image
    # If a pixel is equal in both images, it's a hit, otherwise it's not
    hits = [0] * 11
    for maskid, mask_name in enumerate(mask_names):
        mask = cv.imread(mask_name, 0)
        for rowid, row in enumerate(subtraction):
            for pixelid, pixel in enumerate(row):
                if pixel[0] == mask[rowid][pixelid]:
                    hits[maskid] += 1

    # The mask that best describes the processed hand image
    # should tell us how many cards are in the player's hand
    maxHit = 0
    bestHit = 0
    for i, hit in enumerate(hits):
        if hit > maxHit:
            bestHit = i
            maxHit = hit

    return bestHit


def minion_counter(board, screenshot, opponent_minions=False):
    # Subtract the board from the screenshot to remove background
    subtracted = cv.imread(board['img'], 0)
    subtracted = np.subtract(screenshot, subtracted)

    # Blur the image to remove small imperfections
    thresh_img = cv.medianBlur(subtracted, 5)

    # Threshold the image to isolate minions
    _, thresh_img = cv.threshold(thresh_img, 1, 255, cv.THRESH_BINARY)

    # Crop the scene and threshold according to possible minion positions
    if not opponent_minions:
        candidates = cc.crops(screenshot).get_minion_crop(cc.crops.MINE)
        thresh_imgs = cc.crops(thresh_img).get_minion_crop(cc.crops.MINE)
    else:
        candidates = cc.crops(screenshot).get_minion_crop(cc.crops.OPPONENT)
        thresh_imgs = cc.crops(thresh_img).get_minion_crop(cc.crops.OPPONENT)

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
    if len(sys.argv) != 2:
        print("usage: %s scene" % sys.argv[0])
        sys.exit(1)

    with open('JSON/std_cards_list_descriptors.json', 'r') as cards_file:
        cards_json = jd.jdict(json.load(cards_file))

    # Read the scene passed
    screenshot = cv.imread(sys.argv[1], 0)
    screenshot_color = cv.imread(sys.argv[1])

    # Recognizing the board being played on
    print('Now trying to recognize the board...')
    board = board_recognizer(screenshot)
    print('The current board is ' + board['name'] + '.')

    # Cropping the scene to get the cards at hand
    print('Now counting cards in the player\'s hand...')
    card_count = hand_counter(board, screenshot_color)
    print('There are ' + str(card_count) + ' cards in the player\'s hand.')
    hand_imgs = cc.crops(screenshot).get_hand_crop(card_count)

    # Getting the minions in play
    my_minion_imgs = minion_counter(board, screenshot)
    opponent_minion_imgs = minion_counter(board, screenshot, True)

    # # Recognizing each card on the hand of the player
    # print('Now recognizing cards in player\'s hand...')
    # hand = card_recognizer(hand_imgs, cards_json)
    # print('Cards currently at hand:')
    # for card in hand:
    #     print('\t(' + card['cardId'] + ') ' + card['name'])

    # Recognizing each minion in play
    print('Now recognizing minions on the player\'s board...')
    minions = card_recognizer(my_minion_imgs, cards_json, True)
    print('There are ' + str(len(minions)) + ' minions on the player\'s board.')
    print('Minions on the player\'s board:')
    for minion in minions:
        print('\t(' + minion['cardId'] + ') ' + minion['name'])

    print('Now recognizing minions on the opponent\'s board...')
    print('There are ' + str(len(minions)) + ' minions on the opponent\'s board.')
    minions = card_recognizer(opponent_minion_imgs, cards_json, True)
    print('Minions on the opponent\'s board:')
    for minion in minions:
        print('\t(' + minion['cardId'] + ') ' + minion['name'])


if __name__ == '__main__':
    main()
