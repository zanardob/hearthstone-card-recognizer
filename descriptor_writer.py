import json
import cv2 as cv
import numpy as np
import json_dict as jd


def main():
    sift = cv.xfeatures2d.SIFT_create()

    with open('JSON/std_cards_list.json', 'r') as cards_file:
        cards_json = jd.jdict(json.load(cards_file))

    total = len(cards_json['cards'])
    for index, card in enumerate(cards_json['cards']):
        path = card['type'] + '/' + card['playerClass'] + '/' + card['cardId']

        img = cv.imread(path + '.png', 0)
        _, descriptors = sift.detectAndCompute(img, None)
        np.save(path + '.npy', descriptors)

        new_field = {'descriptors': path + '.npy'}
        card.update(new_field)

        percentage = int((index / total * 100))
        print('(' + str(percentage) + '%) ' + card['name'])

    with open('JSON/std_cards_list_descriptors.json', 'w') as cards_file:
        cards_file.write(str(cards_json))


if __name__ == '__main__':
    main()
