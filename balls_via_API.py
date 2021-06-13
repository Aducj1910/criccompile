import requests, re, xl
from fuzzywuzzy import process
from bs4 import BeautifulSoup

catcherPattern = re.compile(r"c\s(.+?(?=b\s))b\s(.+)")
playerOutPattern = re.compile(r"(.+?(?=\s(\w|run out|obstructing the field|retired hurt)\s))")

def main(link_, matchID, players,playersByID, root, meta, matchTracker, infoRows, update):
    root_call = f"https://hs-consumer-api.espncricinfo.com/v1/pages/match/comments?lang=en&seriesId=1251947&matchId={matchID}"
    #&inningNumber=1&commentType=ALL&fromInningOver=02
    p_api = meta['playersByApiID']
    log = []

    playersProcessingList = []
    for i in players:
        playersProcessingList.append(i)

    def getInit(qry):
            try:
                return [players[qry], qry]
            except:
                toRet = players[process.extract(qry, playersProcessingList, limit=2)[0][0]]
                reassign = ""
                for abc in players:
                    if(players[abc]['init'] == qry or players[abc]['short']== qry or players[abc]['display']== qry):
                        reassign = players[abc]['short']


                return [toRet, reassign]

    res = requests.get(link_).text
    soup = BeautifulSoup(res, 'lxml')
    resultLinks = soup.find('div', class_="best-player-name")
    bestplayer = ""
    if(resultLinks != None):
        bestplayer= resultLinks.text

    inn = 0
    for inning in range(meta['numberOfInnings']):
        inn += 1
        batTeam = meta['teams'][str(meta['inningsMeta'][inn - 1]['batting_team_id'])]
        print("Batting team:", batTeam)

        

        currentBatting = {}
        wickets = 0


        isInningsEnd = False
        doubleCounter = 2
        while not isInningsEnd:
            custom_call = root_call + f"&inningNumber={str(inn)}&commentType=ALL&fromInningOver={str(doubleCounter)}"
            data = requests.get(custom_call).json()
            if(len(data['comments']) != 0):
                commentsList = data['comments']
                commentsList.reverse()
                for comm in commentsList:
                    localLog = []
                    bowlerInfo = p_api[str(comm['bowlerPlayerId'])]
                    batsmanInfo = p_api[str(comm['batsmanPlayerId'])]

                    if(f"inn{str(inn)}" not in p_api[str(comm['batsmanPlayerId'])]):
                        p_api[str(comm['batsmanPlayerId'])][f"inn{str(inn)}"] = 0

                    if("runs" not in p_api[str(comm['batsmanPlayerId'])]):
                        p_api[str(comm['batsmanPlayerId'])]["runs"] = 0

                    if(str(wickets) not in currentBatting):
                        currentBatting[str(wickets)] = {batsmanInfo['init']: None}
                    else:
                        if(batsmanInfo['init'] not in currentBatting[str(wickets)]):
                            currentBatting[str(wickets)][batsmanInfo['init']] = None

                    dis = comm['dismissalText']

                    #dismissal info
                    fielders, outKind, playerOut = "", "", ""
                    if(comm['isWicket']):
                        wickets += 1

                    if(dis != None):
                        outKind = dis['short'].title()
                        print(dis['commentary'])
                        playerOut = getInit(playerOutPattern.match(dis['commentary']).group(1))[0]['init']

                        if(outKind.lower() == "caught"):
                            comment = dis['long'].replace("†", "")
                            catcher = catcherPattern.match(comment).group(1)
                            catcher = getInit(catcher)[0]
                            fielders = catcher['init']



                    localLog += [batsmanInfo['init'], comm['batsmanRuns'], batTeam, bowlerInfo['init'], comm['byes'],
                                comm['byes'] + comm['legbyes'] + comm['wides'] + comm['noballs'], fielders, outKind, comm['legbyes'], inn, 
                                comm['oversActual'], matchID, "" if comm['noballs'] == 0 else comm['noballs'], "",
                                playerOut, comm['totalRuns'], "" if comm['wides'] == 0 else comm['wides'], 1 if comm['isSix'] or comm['isFour'] else 0,
                                0, meta['city'], meta['compt'], meta['decision'], meta['matchType'], 0, meta['neutral'], meta['numberOfOvers'], 
                                getInit(bestplayer)[0]['init'], meta['teamsString'], meta['umpiresString'], meta['venue'],  meta['winner'], meta['tossWinner'], 
                                meta['date'],  meta['season'], comm['overNumber']]

                    bowlTeam = ""
                    for tm in meta['teams']:
                        if(batTeam != meta['teams'][tm]):
                            bowlTeam = meta['teams'][tm]

                    batStyle = p_api[str(comm['batsmanPlayerId'])]['batStyle']
                    bowlStyle = p_api[str(comm['bowlerPlayerId'])]['bowlStyle']
                    condensedBowl = bowlStyle
                    condensedBat = batStyle

                    bowlHand_r = ""
                    bowlType_r = ""

                    end = ''
                    if(comm['overNumber'] % 2 == 1):
                        end = "Near End"
                    else:
                        end = "Far End"

                    if(bowlStyle == "right-arm fast"):
                        condensedBowl = "RAF"
                        bowlHand_r = "Right Arm"
                        bowlType_r = "Fast"


                    if(bowlStyle == "right-arm medium-fast" or "right-arm fast-medium"  in bowlStyle or bowlStyle == "right-arm medium"):
                        condensedBowl = "RAFM "
                        bowlHand_r = "Right Arm"
                        bowlType_r = "Fast"


                    if(bowlStyle == "left-arm fast"):
                        condensedBowl = "LAF"
                        bowlHand_r = "Left Arm"
                        bowlType_r = "Fast"


                    if(bowlStyle == "left-arm medium-fast" or bowlStyle == "left-arm fast-medium" or bowlStyle == "left-arm medium"):
                        condensedBowl = "LAFM"
                        bowlHand_r = "Left Arm"
                        bowlType_r = "Fast"


                    if(bowlStyle == "right-arm offbreak"):
                        condensedBowl = "RAOS"
                        bowlHand_r = "Right Arm"
                        bowlType_r = "Spin"


                    if(bowlStyle == "slow left-arm orthodox"):
                        condensedBowl = "LAOS"
                        bowlHand_r = "Left Arm"
                        bowlType_r = "Spin"


                    if("legbreak" in bowlStyle):
                        condensedBowl = "RALS"
                        bowlHand_r = "Right Arm"
                        bowlType_r = "Spin"


                    if(bowlStyle == "left arm wrist spin" or bowlStyle == "left-arm wrist-spin"):
                        condensedBowl = "LAWS" #not sure
                        bowlHand_r = "Left Arm"
                        bowlType_r = "Spin"

                    if("right" in batStyle):
                        condensedBat = "RHB"
                    elif("left" in batStyle):
                        condensedBat = "LHB"

                    # phase = ""
                    # if(comm['overNumber'] < 11):
                    #     phase = "phase 1"
                    # elif(comm['overNumber'] < 41):
                    #     phase = "phase 2"
                    # else:
                    #     phase = "phase 3"

                    phase = ""
                    if(meta['numberOfOvers'] == 20):
                        if(comm['overNumber'] < 7):
                            phase = "powerplay"
                        elif(comm['overNumber'] < 16):
                            phase = "middle overs"
                        else:
                            phase = "death overs"
                    elif(meta['numberOfOvers'] == 50):
                        if(comm['overNumber'] < 11):
                            phase = "phase one"
                        elif(comm['overNumber'] < 31):
                            phase = "phase two"
                        else:
                            phase = "phase three"


                    lkeeper = ""
                    if(meta['teams'][meta['teamA']] == bowlTeam):
                        lkeeper = meta['teamAKeeper']
                    else:
                        lkeeper = meta['teamBKeeper']

                    # print(comm['oversActual'], outKind, fielders, playerOut)
                    p_api[str(comm['batsmanPlayerId'])][f"inn{str(inn)}"] += 1 if comm['noballs'] == 0 and comm['wides'] == 0 else 0
                    p_api[str(comm['batsmanPlayerId'])]["runs"] += comm['batsmanRuns']


                    localLog += [condensedBowl, condensedBat, bowlTeam, comm['totalRuns'] - comm['byes'] - comm['legbyes'],
                                0, phase, "", bowlHand_r, bowlType_r, end, "", "", "", "", "", "", "", lkeeper, "", 
                                 p_api[str(comm['batsmanPlayerId'])][f"inn{str(inn)}"], meta['teamACaptain'], meta['teamAKeeper'], meta['teamBCaptain'],
                                 meta['teamBKeeper'], meta['teamApts'], meta['teamBpts'], meta['winnerMsg'],"runs",str(comm['batsmanPlayerId']), 
                                 wickets]

                    log.append(localLog)
                    print(comm['oversActual'])



                doubleCounter += 2



            else:
                isInningsEnd = True



        for lg in log:
            if(lg[2] == batTeam):
                wkts = lg[-1]
                del lg[-1]
                if(str(wkts) in currentBatting):  
                    for btnb in currentBatting[str(wkts)]:
                        if(btnb != lg[0]):
                             lg[13] = btnb
                else:
                    lg[13] = ""

        # n = []
        # for lg in log:
            # k = lg[-1]
            # ob = p_api[k]['runs']
            # print(ob)
            # n.append(ob)
            # lg.append(ob)

        # for i in range(len(n)):
            # log[i][-2] = n[i]



    print(log[9], len(log[9]))
    xl.viaDB(log, matchID, matchTracker, infoRows, update)
