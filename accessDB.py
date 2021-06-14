import pymongo, json, unicodedata, json, certifi
from pymongo import MongoClient

# connection = MongoClient('localhost', 27017)

# db = connection['wicket-wiz-db']
# document = db['test']

# post = {"_id":0, "name": "foo", "age":50}

# document.insert_one(post)

# connection = MongoClient('localhost', 27017)
connection = MongoClient('mongodb+srv://admin:21441@cluster0.7y5hx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())

def addRow(rows, switch, infoRows):
	# print(rows)
	db = connection['cricmanagerrecent']
	document = db[infoRows]
	if(switch == 'odi'):
		document = db['infoRowsCPLRedone']

	with open("count.json") as f:
		data_ = json.load(f)

	post = {"_id": data_['count'], "_data": rows}
	document.insert_one(post)
	data_['count'] += 1
	print(data_['count'])
	with open("count.json", "w") as outp:
		json.dump(data_, outp)


def addPlayerInit(playerID):
	# pass #remove and uncomment below lines
	db = connection['cricmanagerrecent']
	document = db['playerInit']

	post = {"_id": playerID['_id'], "playerInitials": playerID['playerInitials'], "displayName": playerID['displayName'], "batStyle": playerID['batStyle'], "bowlStyle": playerID['bowlStyle']}
	document.insert_one(post)

def checkPlayer(_id):
	db = connection['cricmanagerrecent']
	document = db['playerInit']

	fetch = document.find_one({"_id":  _id})
	if fetch != None:
		return True
	else:
		return False

def receivePlayer(_id):
	db = connection['cricmanagerrecent']
	document = db['playerInit']

	fetch = document.find_one({"_id": _id})
	return fetch

def addNewMatch(matchID, matchTracker):
	print(matchID)
	db = connection['cricmanagerrecent']
	document = db[matchTracker]

	post = {"_id": matchID}
	document.insert_one(post)

def addPlayerMatchInfo(info):
	db = connection['cricmanagerrecent']
	document = db['playerInfo']

	for key in info:
		p = info[key]
		p['captained'], p['wicketkeeper'] = 0, 0
		fetch = document.find_one({"_id": p["_id"]})
		if(p['isCaptain']):
			p['captained'] = 1
		if(p['isWK']):
			p['wicketkeeper'] = 1

		p['matches'] = 1
		del p['isCaptain']
		del p['isWK']

		if fetch == None:
			post = p
			document.insert_one(post)
		else:
			document.delete_one(fetch)
			fetch['matches'] += 1
			fetch['position'] += p['position']
			fetch['captained'] += p['captained']
			fetch['wicketkeeper'] += p['wicketkeeper']
			fetch['batRunsTotal'] += p['batRunsTotal']
			fetch['batBallsTotal'] += p['batBallsTotal']
			fetch['bowlRunsTotal'] += p['bowlRunsTotal']
			fetch['bowlBallsTotal'] += p['bowlBallsTotal']
			fetch['batOutsTotal'] += p['batOutsTotal']
			fetch['bowlOutsTotal'] += p['bowlOutsTotal']
			fetch['bowlNoballs'] += p['bowlNoballs']
			fetch['bowlWides'] += p['bowlWides']
			fetch['catches'] += p['catches']

			if(p['playerInitials'] == "SR Watson"):
				print(fetch['batOutTypes'], p['batOutTypes'])

			for outType in p['batOutTypes']:
				fetch['batOutTypes'][outType] += p['batOutTypes'][outType]

			for outType in p['bowlOutTypes']:
				fetch['bowlOutTypes'][outType] += p['bowlOutTypes'][outType]

			for outType in p['batRunDenominations']:
				fetch['batRunDenominations'][outType] += p['batRunDenominations'][outType]

			for outType in p['bowlRunDenominations']:
				fetch['bowlRunDenominations'][outType] += p['bowlRunDenominations'][outType]

			fetch['overNumbers'] += p['overNumbers']
			fetch['runnedOut'] += p['runnedOut']

			for style in p['byBatsman']:
				if style in fetch['byBatsman']:
					fetch['byBatsman'][style]['bowlRunsTotal'] +=  p['byBatsman'][style]['bowlRunsTotal']
					fetch['byBatsman'][style]['bowlBallsTotal'] += p['byBatsman'][style]['bowlBallsTotal']
					fetch['byBatsman'][style]['bowlOutsTotal'] += p['byBatsman'][style]['bowlOutsTotal']

					for outType in fetch['byBatsman'][style]['bowlOutTypes']:	
						fetch['byBatsman'][style]['bowlOutTypes'][outType] += p['byBatsman'][style]['bowlOutTypes'][outType]
					
					for outType in fetch['byBatsman'][style]['bowlRunDenominations']:	
						fetch['byBatsman'][style]['bowlRunDenominations'][outType] += p['byBatsman'][style]['bowlRunDenominations'][outType]

				else:
					fetch['byBatsman'][style] = p['byBatsman'][style]

			for style in p['byBowler']:
				if style in fetch['byBowler']:
					fetch['byBowler'][style]['batRunsTotal'] +=  p['byBowler'][style]['batRunsTotal']
					fetch['byBowler'][style]['batBallsTotal'] += p['byBowler'][style]['batBallsTotal']
					fetch['byBowler'][style]['batOutsTotal'] += p['byBowler'][style]['batOutsTotal']
					
					for outType in fetch['byBowler'][style]['batOutTypes']:	
						fetch['byBowler'][style]['batOutTypes'][outType] += p['byBowler'][style]['batOutTypes'][outType]
					
					for outType in fetch['byBowler'][style]['batRunDenominations']:	
						fetch['byBowler'][style]['batRunDenominations'][outType] += p['byBowler'][style]['batRunDenominations'][outType]

				else:
					fetch['byBowler'][style] = p['byBowler'][style]	

			post = fetch
			document.insert_one(post)


