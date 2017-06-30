import json
import requests
import json_dict as jd # This is a modified JSON dictionary handler, as described in json_dict.py.

# This script simply downloads a JSON file containing description for all cards in the game.
# With the downloaded JSON file it's possible to access the cards' images links, to download them.

request = requests.get(url=
                       "https://omgvamp-hearthstone-v1.p.mashape.com/cards",
                       headers={
                           "X-Mashape-Key":
                           "55TXAeirFtmshkebdKTpo9Fvrwn2p1QxjyAjsnBVzqijA8Mv5z"
                       }
                       )

with open('all_cards.json', 'w') as cardsfile:
    cardsfile.write(str(jd.jdict(json.loads(request.text))))
