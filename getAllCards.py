# These code snippets use an open-source library. http://unirest.io/python
import requests
import json

class mydict(dict):
	def __str__(self):
		return json.dumps(self)

request = requests.get(url="https://omgvamp-hearthstone-v1.p.mashape.com/cards",
  headers={
    "X-Mashape-Key": "55TXAeirFtmshkebdKTpo9Fvrwn2p1QxjyAjsnBVzqijA8Mv5z"
  }
)

with open('all_cards.json', 'w') as cardsfile:
	cardsfile.write(str(mydict(json.loads(request.text))))