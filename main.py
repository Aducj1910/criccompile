import requests, re, accessDB, unicodedata, core, balls
from bs4 import BeautifulSoup

headers={"User-Agent":"Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/58.0.3029.110Safari/537.36"}
playerLinkPattern = re.compile(r"\/player\/.+(?=-)-(\d+)")
enginePlayerPattern = re.compile(r"\/ci\/engine\/player\/(\d+)\.html.+")
topInfoPattern = re.compile(r"Statistics \/ Statsguru \/ (.+(?= \/))")
stylePattern = re.compile(r".+?(?=-)- (.+?(-hand bat)); (.+?(?=(;| -)))")
secondaryStylePattern = re.compile(r".+?(?= -) - (.+?(?= -))")

testPattern = re.compile(r"Statistics")
def addPlayers(link):
	scorelink = link
	res = requests.get(scorelink, headers=headers).text
	soup = BeautifulSoup(res, 'lxml')
	resultLinks = soup.findAll('a', class_="small", href=True)
	playerIDs = []
	localPlayerObject = {}
	onceC = False
	onceW = False

	def confirmBowlStyle(style):
		if("," in style):
			styleArr = style.split(", ")
			return styleArr[0]
		else:
			return style

	for i in resultLinks:
		if('/player/' in i['href']):
			linkmatch = playerLinkPattern.match(i['href'])
			_id = linkmatch.group(1)
			isWK = False
			isCaptain = False
			playerNameList = i.text.replace(",", "").split(" ")
			indexcounter = 0
			for j in playerNameList:
				playerNameList[indexcounter] = unicodedata.normalize("NFKD", j)
				indexcounter += 1

			name = " ".join(playerNameList)
			if(name.endswith(" ")):
				name = name[:-1]

			if ("(c)" in name):
				if("†" in name):
					name = name.replace(" (c)†", "")
					isCaptain = True
					isWK = True
				else:
					name = name.replace(" (c)", "")
					isCaptain = True

			elif ("†" in name):
				name = name.replace(" †", "")
				isWK = True

			captainTeam = "none"
			keeperTeam = "none"
			if(onceC and isCaptain):
				captainTeam = "bowling"
			elif(isCaptain):
				captainTeam = "batting"
				onceC = True

			if(onceW and isWK):
				keeperTeam = "bowling"
			elif(isWK):
				keeperTeam = "batting"
				onceW = True

			rep = False
			for jj in playerIDs:
				if(jj['displayName'] == name and isCaptain == False and isWK == False):
					rep = True

			if(not rep):
				playerIDs.append({"displayName" : name, "isCaptain" : isCaptain, "isWK" : isWK, "_id": _id, 
					"captainTeam": captainTeam, "keeperTeam": keeperTeam})




	for i in playerIDs:
		isCapt, isW, cpt, kpt = i['isCaptain'], i['isWK'], i['captainTeam'], i['keeperTeam']
		if(accessDB.checkPlayer(i['_id'])):
			fetch = accessDB.receivePlayer(i['_id'])
			i = fetch
			i['isCaptain'] = isCapt
			i['isWK'] = isW
			i['captainTeam'] = cpt
			i['keeperTeam'] = kpt
			localPlayerObject[fetch['playerInitials']] = i
			# localPlayerObject[fetch['playerInitials']]['isCaptain'] = isCapt
			# localPlayerObject[fetch['playerInitials']]['isWK'] = isW

		else:
			infoLink = f"https://stats.espncricinfo.com/ci/engine/player/{str(i['_id'])}.html?class=1;type=allround" 
			res = requests.get(infoLink, headers=headers).text
			soup = BeautifulSoup(res, 'lxml')
			topInfo = soup.find('div', class_="icc-home")
			initText = topInfo.text.replace('\n', '').replace('\r', '')
			mainInfo = soup.find('p', style="padding-bottom:10px")
			mainText = mainInfo.text.replace('\n', '').replace('\r', '')
			styleMatch = stylePattern.match(mainText)
			if(styleMatch == None):
				secondaryStyleMatch = secondaryStylePattern.match(mainText)
				if(secondaryStyleMatch == None):
					batStyle, bowlStyle = "not found", "not found"
				else:
					batStyle, bowlStyle = secondaryStyleMatch.group(1), "not found"


			else:
				if("wicketkeep" not in styleMatch.group(3)):
					batStyle, bowlStyle = styleMatch.group(1), confirmBowlStyle(styleMatch.group(3))
				else:
					batStyle, bowlStyle = styleMatch.group(1), "not found"


			# topInfoMatch = topInfoPattern.match(initText)


			i['playerInitials'] = topInfoMatch.group(1)
			i['batStyle'] = batStyle
			i['bowlStyle'] = bowlStyle

			localPlayerObject[i['playerInitials']] = i
			accessDB.addPlayerInit(i)


	if(True):
		print("Going to core.py")
		balls.main(link, '226374', localPlayerObject)
		#matchID - 100
		# print(playerIDs)
addPlayers(r"https://www.espncricinfo.com/series/south-africa-tour-of-australia-2005-06-209671/australia-vs-south-africa-only-t20i-226374/full-scorecard")