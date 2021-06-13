import requests, re, xl, balls, time, traceback, balls_via_API
from espncricinfo.match import Match

detailsPattern = re.compile(r"(http:\/\/.+?(?=details\?)details\?)")
athletePattern = re.compile(r"http:\/\/core\..+?(?=\/\d)\/.+?(?=\/)\/athletes\/(\d.+)")

def doMatch(match, cilink, matchTracker, infoRows, matchData, update):
	try:

		m = Match(match)
		log = []
		response = requests.get(m.json_url)
		# response2 = requests.get(m.details_url)
		response3 = requests.get(m.event_url)
		print(m.details_url)

		respMatch = response.json()
		# respDetails = response2.json()
		respEvent = response3.json()

		city = respMatch['match']['town_name']
		tossDecision = respMatch['match']['toss_decision_name'].capitalize() if respMatch['match']['toss_decision_name'] == "bat" else "Field"
		competition = respEvent['name']
		matchType = matchData['matchType']
		method = 0
		neutral_venue = respMatch['match']['neutral_match']
		numberOfOvers = matchData['overs']
		inningsMetaPrep = respMatch['innings']
		inningsMeta = []
		for im in inningsMetaPrep:
			if(im['balls'] > 0):
				inningsMeta.append(im)



		winnerMsg = respMatch['live']['status'].capitalize()
		teamsString = f"{respMatch['match']['team1_name']}, {respMatch['match']['team2_name']}".upper()
		umpires = []
		for i in respMatch['official']:
			if(i['player_type_name'] == "umpire"):
				umpires.append(i['card_long'].upper())

		teams = {respMatch['match']['team1_id']: respMatch['match']['team1_name'].upper(), 
			respMatch['match']['team2_id']: respMatch['match']['team2_name'].upper()}

		teamsAbb = {respMatch['match']['team1_abbreviation']: respMatch['match']['team1_name'].upper(),
					respMatch['match']['team2_abbreviation']: respMatch['match']['team2_name'].upper()	}

		umpiresString = ", ".join(umpires)
		winner = ""

		try:
			if(str(respMatch['match']['winner_team_id']) == str(0)):
				winner = teams[respMatch['match']['tiebreaker_team_id']].upper()
			else:
				teams[respMatch['match']['winner_team_id']].upper()
		except:
			winner = ""

		venue = respMatch['match']['ground_name']
		tossWinner = teams[respMatch['match']['toss_winner_team_id']].upper()
		dateIN = respMatch['match']['start_date_raw']
		date = f"{dateIN.split('-')[2]}/{dateIN.split('-')[1]}/{dateIN.split('-')[0]}"
		season = dateIN.split('-')[0]

		batFirst = "None"
		batSecond = "None"

		numberOfInnings = len(inningsMeta)

		if(tossDecision == "Bat"):
			batFirst = tossWinner
			for n in teamsString.split(", "):
				if(n != tossWinner):
					batSecond = n
		else:
			batSecond = tossWinner
			for n in teamsString.split(", "):
				if(n != tossWinner):
					batFirst = n

		players = {}
		playersByID = {}
		playersByApiID = {}
		teamACaptain = ""
		teamBCaptain = ""
		teamAKeeper = ""
		teamBKeeper = ""

		teamA = ""
		teamB = ""

		if('substitute' in respMatch):
			for j in respMatch['substitute']:
				fragment = {'init': j['card_long'], 'short': j['mobile_name'], 'display': j['known_as'], 
							'bowlStyle': "" if j['bowling_style_long'] == None else j['bowling_style_long'].strip(), 'batStyle': j['batting_style_long'], 'team': "",
							'keeper': j['keeper'], 'captain': j['captain'], '_id': j['object_id'], 'order': -1}
				# players[str(j['object_id'])] = fragment
				players[j['mobile_name']] = fragment
				playersByID[str(j['object_id'])] = fragment
				playersByApiID[str(j['player_id'])] = fragment

		c = 0
		for i in respMatch['team']:
			if(c == 0):
				teamA = str(i['content_id']).upper()
			else:
				teamB = str(i['content_id']).upper()
			c += 1
			order = 0
			for j in i['player']:

				fragment = {'init': j['card_long'], 'short': j['mobile_name'], 'display': j['known_as'], 
							'bowlStyle': "" if j['bowling_style_long'] == None else j['bowling_style_long'].strip(), 'batStyle': j['batting_style_long'], 'team': teams[str(i['content_id'])],
							'keeper': j['keeper'], 'captain': j['captain'], '_id': j['object_id'], 'order': order}
				# players[str(j['object_id'])] = fragment
				players[j['mobile_name']] = fragment
				playersByID[str(j['object_id'])] = fragment
				playersByApiID[str(j['player_id'])] = fragment
				order += 1

				#captain
				if(j['captain'] == 1 and teamACaptain == ""):
					teamACaptain = j['card_long']
				elif(j['captain'] == 1 and teamBCaptain == ""):
					teamBCaptain = j['card_long']

				#keeper
				if(j['keeper'] == 1 and teamAKeeper == ""):
					teamAKeeper = j['card_long']
				elif(j['keeper'] == 1 and teamBKeeper == ""):
					teamBKeeper = j['card_long']

		teamApts, teamBpts = 1,1
		if(winner == teams[teamA]):
			teamApts = 2
		elif(winner == teams[teamB]):
			teamBpts = 2
		else:
			teamApts, teamBpts = 1,1

		root = detailsPattern.match(m.details_url).group(1) + "/"

		meta = {"teamsAbb": teamsAbb, "teams": teams, "city": city, 'compt': competition, 'decision': tossDecision, 'matchType': matchType,
				"neutral": neutral_venue, "numberOfOvers": numberOfOvers, 'teamsString': teamsString, "umpiresString": umpiresString,
				"venue": venue, "winner": winner, "tossWinner": tossWinner, "date": date, "season": season, "teamA": teamA,"teamB":teamB,
				"teamAKeeper": teamAKeeper, "teamBKeeper": teamBKeeper, "teamACaptain": teamACaptain, "teamBCaptain": teamBCaptain, "teamApts": teamApts,
					"teamBpts": teamBpts, "winnerMsg": winnerMsg, "inningsMeta": inningsMeta, "numberOfInnings": numberOfInnings, "playersByApiID": playersByApiID}

		# print(players)
		balls_via_API.main(cilink,
					 match, players,playersByID, root, meta, matchTracker, infoRows, update)

	except Exception:
		traceback.print_exc()


# doMatch('1025665', 'https://stats.espncricinfo.com/ci/engine/match/1025665.html', 'matchTrackerCPLUpdate', 'infoRowsCPLUpdate', matchData = {'matchType': "T20", "overs": 20})




