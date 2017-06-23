import json
import requests
import json_dict as jd

request = requests.get(url=
                       "https://omgvamp-hearthstone-v1.p.mashape.com/cards",
                       headers={
                           "X-Mashape-Key":
                           "55TXAeirFtmshkebdKTpo9Fvrwn2p1QxjyAjsnBVzqijA8Mv5z"
                       }
                       )

with open('all_cards.json', 'w') as cardsfile:
    cardsfile.write(str(jd.jdict(json.loads(request.text))))
