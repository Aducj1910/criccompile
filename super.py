import requests, accessDB, core, certifi
from bs4 import BeautifulSoup
from pymongo import MongoClient
from espncricinfo.match import Match

headers={"User-Agent":"Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/58.0.3029.110Safari/537.36"}

#307852 T20i
#307847 Test
#307851 ODI
connection = MongoClient('mongodb+srv://admin:21441@cluster0.7y5hx.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())
db = connection['cricmanagerrecent']

def main(link, matcht, infor, matchdata, update):
	leagueLink = link
	#change id for other tournaments
	matchTracker = matcht
	infoRows = infor

	res = requests.get(leagueLink, headers=headers).text
	soup = BeautifulSoup(res, 'lxml')
	years = soup.findAll("a", href=True)
	matchData = matchdata

	# connection = MongoClient('localhost', 27017)

	document = db[matchTracker]
	m, d = 0,0

	for y in years:
		if("ci/engine/records/team/match_results.html?class=;" in y['href']) and int(y.text.split("/")[0]) > 2010:
			# print(y.text)
			res2 = requests.get(f"https://stats.espncricinfo.com{y['href']}", headers=headers).text
			soup2 = BeautifulSoup(res2, 'lxml')

			linksExt = soup2.findAll('a', class_="data-link", href=True)
			for l in linksExt:
				if("/ci/engine/match" in l['href']):
					mid = l['href'].split("/")[-1].replace(".html", "")
					fetch = document.find_one({"_id": str(mid)})
					if(fetch == None):
						print(mid + " Missing")
						m += 1
						m_ = Match(mid)
						print(m_.description)
						try:
							core.doMatch(mid, f"https://stats.espncricinfo.com/{l['href']}", matchTracker, infoRows, matchData, update)
						except:
							print(mid, "Failed")

					else:
						print(mid + " Done")
						d += 1
				
	print(f"{str(m)} / {str(m + d)}")
	return convertoxl.main(infoRows, matchTracker, "League")		

	#45 tests
	#159 t20
	#271 odi