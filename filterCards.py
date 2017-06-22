import json
import urllib.request
import os

class mydict(dict):
	def __str__(self):
		return json.dumps(self)


wild = False
downloadCards = False
typeFilteredCards = []

with open('all_cards.json') as allCardsFile:
	allCardsObject = mydict(json.load(allCardsFile))
	allCards = []

	for card in allCardsObject['Basic']:
		allCards.append(card)
	for card in allCardsObject['Classic']:
		allCards.append(card)
	for card in allCardsObject['Whispers of the Old Gods']:
		allCards.append(card)
	for card in allCardsObject['One Night in Karazhan']:
		allCards.append(card)
	for card in allCardsObject['Mean Streets of Gadgetzan']:
		allCards.append(card)
	for card in allCardsObject['Journey to Un\'Goro']:
		allCards.append(card)

	if wild:
		for card in allCardsObject['Goblins vs Gnomes']:
			allCards.append(card)
		for card in allCardsObject['The Grand Tournament']:
			allCards.append(card)
		for card in allCardsObject['The League of Explorers']:
			allCards.append(card)
		for card in allCardsObject['Blackrock Mountain']:
			allCards.append(card)
		for card in allCardsObject['Naxxramas']:
			allCards.append(card)
		for card in allCardsObject['Hall of Fame']:
			allCards.append(card)

	typeList = ['Minion', 'Spell', 'Weapon']

	for card in allCards:
		if card['type'] in typeList:
			typeFilteredCards.append(card)


if downloadCards:
	scriptDir = os.path.dirname(__file__)
	path = ''
	for index, card in enumerate(typeFilteredCards):
		path += card['type'] + '/'
		path += card['playerClass'] + '/'
		path += card['cardId'] + '.png'
		absPath = os.path.join(scriptDir, path)
		path = ''

		request = urllib.request.urlretrieve(card['img'], absPath)

		percentage = int((index / len(typeFilteredCards)) * 100)
		print('Name: ' + card['name'] + ', location: ' + absPath + '\t(' + str(percentage) + '%)')

filteredCardsObject = mydict({'cards': typeFilteredCards})
if wild:
	with open('wild_cards_list.json', 'w') as wildCardsFile:
		wildCardsFile.write(str(filteredCardsObject))
else:
	with open('std_cards_list.json', 'w') as stdCardsFile:
		stdCardsFile.write(str(filteredCardsObject))
