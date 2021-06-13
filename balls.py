from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support import select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import re, requests, xl, copy, traceback
from fuzzywuzzy import process
from espncricinfo.match import Match

toPattern = re.compile(r"(.+?(?=\sto\s))\sto\s(.+?(?=,))")
athletePattern = re.compile(r"http:\/\/core\..+?(?=\/\d)\/.+?(?=\/)\/athletes\/(\d.+)")

def main(link_, matchID, players,playersByID, root, meta, matchTracker, infoRows, update):
    r1 = requests.get(link_)
    print(playersByID)
    linkred = r1.url
    # print(playersByID)

    # print(playersByID)
    log = []
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    options = webdriver.ChromeOptions()
    options.headless = True
    # options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1400,710")
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument('log-level=3')
    # options.add_argument("--proxy-server='direct://'")
    # options.add_argument("--proxy-bypass-list=*")
    # options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=options)
    # driver.get(matchLink + "full-scorecard") 
    driver.get(linkred.replace("full-scorecard", "ball-by-ball-commentary"))    
    driver.execute_script("window.scrollTo(0, 500)")

    try:  
        # innBtn = driver.find_element_by_class_name('dropdown-container comment-inning-dropdown')
        innBtn = driver.find_element_by_xpath('//*[@id="main-container"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/button')
        innBtn.click()
        # driver.execute_script("arguments[0].click();", innBtn)

        inningsDiv = driver.find_element_by_class_name('ci-dd__menu')
        inningsUl = inningsDiv.find_elements_by_xpath("//ul")[1]
        inningsLi = inningsUl.find_elements_by_tag_name("li")

        numberOfInnings = len(inningsLi)
        print(numberOfInnings)  

        bestPlayerList = driver.find_elements_by_class_name("best-player-name")
        bestPlayer = ""

        for i in bestPlayerList:
            bestPlayer = i.text


        playersProcessingList = []
        for i in players:
            playersProcessingList.append(i)
            if(players[i]['display'] == bestPlayer):
                bestPlayer = players[i]['init']



        inn = 0
        for inning in range(meta['numberOfInnings']):
                inn += 1
                driver.refresh()
                # loopInningsChangeButton = driver.find_element_by_class_name("dropdown-container")
                loopInningsChangeButton = driver.find_element_by_xpath('//*[@id="main-container"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/button')
                driver.execute_script("arguments[0].click();", loopInningsChangeButton)
                # loopInningsChangeButton.click()

                wait = WebDriverWait(driver, 1)

                loopInningsDiv = wait.until(EC.visibility_of_element_located((By. CLASS_NAME, 'ci-dd__menu')))
                #//*[@id="main-container"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div/div/ul/li[1]
                #//*[@id="main-container"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div/div/ul/li[2]


                # loopInningsDiv = driver.find_element_by_class_name("ci-dd__menu")
                inningsToClick = driver.find_element_by_xpath(f'//*[@id="main-container"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div/div/ul/li[{str(inn)}]')
                driver.execute_script("arguments[0].click();", inningsToClick)
                # loopInningsUl = loopInningsDiv.find_elements_by_xpath("//ul")[1]
                # loopInningsLi = loopInningsUl.find_elements_by_tag_name("li")
                # loopInningsLi[-numberOfInnings + inning].click()
                batTeam = driver.find_element_by_xpath('//*[@id="main-container"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/button')
                # print(meta['teamsAbb'])
                batTeamTxt = batTeam.text if batTeam.text != "TKR" else "RedSt"
                batTeam = meta['teams'][str(meta['inningsMeta'][inn - 1]['batting_team_id'])]
                print("Batting team:", batTeam)
                # if(batTeamTxt not in meta['teamsAbb']):
                    # pass
                # else:
                    # batTeam = meta['teamsAbb'][batTeamTxt]



                last_height = driver.execute_script("return document.body.scrollHeight")

                while True:

                        # Scroll down to the bottom.
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                        # Wait to load the page.
                        sleep(0.5)

                        # Calculate new scroll height and compare with last scroll height.
                        new_height = driver.execute_script("return document.body.scrollHeight")

                        if new_height == last_height:

                            break

                        last_height = new_height

                # runComments = driver.find_elements_by_class_name('match-comment-run-container')
                # overComments = driver.find_elements_by_class_name('match-comment-over')
                # desc = driver.find_elements_by_class_name('match-comment-short-text')
                wrap = driver.find_elements_by_class_name('match-comment')
                wrap.reverse()

                currentBatting = {}
                wickets = 0
                latestOver = 0

                overBalls = 0

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




                for w in wrap:
                    overBalls += 1
                    localLog = []

                    over = w.find_element_by_class_name('match-comment-over')
                    run = w.find_element_by_class_name('match-comment-run-container')
                    desc = w.find_element_by_class_name('match-comment-short-text')


                    print(over.text, run.text, desc.text, inn)
                    bowler = toPattern.match(desc.text).group(1)
                    batter = toPattern.match(desc.text).group(2)

                    overDiff = int(over.text.split(".")[0]) - latestOver
                    if(overDiff != 0):
                        overBalls = 1
                        latestOver = int(over.text.split(".")[0])

                    fetchOver = f"{str(over.text.split('.')[0])}.{str(overBalls)}"

                    fnlBowler = getInit(bowler)[0]
                    fnlBatter = getInit(batter)[0]

                    bowler = getInit(bowler)[1]
                    batter = getInit(batter)[1]

                    if(f"inn{str(inn)}" not in players[batter]):
                        players[batter][f"inn{str(inn)}"] = 0

                    if(str(wickets) not in currentBatting):
                        currentBatting[str(wickets)] = {fnlBatter['init']: None}
                    else:
                        if(fnlBatter['init'] not in currentBatting[str(wickets)]):
                            currentBatting[str(wickets)][fnlBatter['init']] = None

           

                    print(fnlBowler['init'], fnlBatter['init'])

                    outs = w.find_elements_by_class_name('match-comment-wicket')
                    if(len(outs) != 0):
                        wickets += 1

                    runc = run.text.replace("•", "0")

                    wides = ""
                    noBalls = ""
                    byes = 0
                    legByes = 0
                    total = 0
                    fielder = ""
                    playerOut = ""
                    kind = ""
                    extras = 0

                    ball = 1

                    if(runc.isnumeric()):
                        total = int(runc)
                    elif(runc != "W"):
                        split = list(runc)
                        scr = ""
                        extras = ""
                        for ii in split:
                            if(ii.isnumeric()):
                                extras = int(ii)
                            else:
                                scr += ii

                        total += extras
                        if(scr == "w"):
                            ball = 0
                            wides = extras
                        if(scr == "nb"):
                            ball = 0
                            noBalls = 1
                            extras = 1
                        if(scr == "b"):
                            byes += extras
                        if(scr == "lb"):
                            byes += extras

                    elif(runc == "W"):
                        addum = f"{str(inn)}{str(fetchOver.split('.')[0])}0{str(fetchOver.split('.')[1])}0" if len(str(fetchOver.split('.')[1])) == 1 else f"{str(inn)}{str(fetchOver.split('.')[0])}{str(fetchOver.split('.')[1])}0"
                        more = root + addum
                        print(more)
                        dim = requests.get(more).json()['dismissal']

                        kind = dim['type'].capitalize()
                        playerOut = playersByID[athletePattern.match(dim['batsman']['athlete']['$ref']).group(1)]['init']

                        if('fielder' in dim):
                            if(not dim['fielder']['athlete']['$ref'].endswith('athletes/0')):
                                fielder = playersByID[athletePattern.match(dim['fielder']['athlete']['$ref']).group(1)]['init']




                    players[batter][f"inn{str(inn)}"] += ball

                    bowlTeam = ""
                    for tm in meta['teams']:
                        if(batTeam != meta['teams'][tm]):
                            bowlTeam = meta['teams'][tm]



                    localLog += [fnlBatter['init'], total - extras, batTeam, fnlBowler['init'], byes, extras, fielder, kind, legByes, inn, over.text,
                                    matchID, noBalls, "", playerOut, total, wides, 1 if (total - extras) == 4 or (total - extras) == 6 else 0, 
                                    0, meta['city'], meta['compt'], meta['decision'], meta['matchType'], 0, meta['neutral'], meta['numberOfOvers'],
                                    bestPlayer, meta['teamsString'], meta['umpiresString'], meta['venue'],  meta['winner'], meta['tossWinner'],
                                    meta['date'], meta['season'],]

                    overNumber = int(over.text.split(".")[0]) + 1

                    batStyle = players[batter]['batStyle']
                    bowlStyle = players[bowler]['bowlStyle']
                    condensedBowl = bowlStyle
                    condensedBat = batStyle

                    bowlHand_r = ""
                    bowlType_r = ""

                    end = ''
                    if(overNumber % 2 == 1):
                        end = "Near End"
                    else:
                        end = "Far End"

                    if(bowlStyle == "right-arm fast"):
                        condensedBowl = "RAF"
                        bowlHand_r = "Right Arm"
                        bowlType_r = "Fast"


                    if(bowlStyle == "right-arm medium-fast" or bowlStyle == "right-arm fast-medium" or bowlStyle == "right-arm medium"):
                        condensedBowl = "RAFM"
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


                    if(bowlStyle == "left arm wrist spin"):
                        condensedBowl = "LAWS" #not sure
                        bowlHand_r = "Left Arm"
                        bowlType_r = "Spin"

                    if("right" in batStyle):
                        condensedBat = "RHB"
                    elif("left" in batStyle):
                        condensedBat = "LHB"

                    # phase = ""
                    # if(overNumber < 11):
                    #     phase = "phase 1"
                    # elif(overNumber < 41):
                    #     phase = "phase 2"
                    # else:
                    #     phase = "phase 3"

                    phase = ""
                    if(meta['numberOfOvers'] == 20):
                        if(overNumber < 7):
                            phase = "powerplay"
                        elif(overNumber < 16):
                            phase = "middle overs"
                        else:
                            phase = "death overs"
                    elif(meta['numberOfOvers'] == 50):
                        if(overNumber < 11):
                            phase = "phase one"
                        elif(overNumber < 31):
                            phase = "phase two"
                        else:
                            phase = "phase three"


                    lkeeper = ""
                    if(meta['teams'][meta['teamA']] == bowlTeam):
                        lkeeper = meta['teamAKeeper']
                    else:
                        lkeeper = meta['teamBKeeper']

                    localLog += [overNumber, condensedBowl, condensedBat, bowlTeam, total - byes - legByes, 0,
                                 phase, "", bowlHand_r, bowlType_r, end, "", "", "", "", "", "", "", lkeeper, "", 
                                 players[batter][f"inn{str(inn)}"], meta['teamACaptain'], meta['teamAKeeper'], meta['teamBCaptain'],
                                 meta['teamBKeeper'], meta['teamApts'], meta['teamBpts'], meta['winnerMsg'], wickets]

                    log.append(localLog)
                    # print(localLog)

                    #NON STRIKER VIA WICKETS NUMBER
                    #ALSO SHORT FORM FROM API TO GET THE DROPDOWN REFERENCE
                    #USE DROPDOWN TO SEE BATTING ORDER AND DECIDE KEEPER
                    #USE FOW FROM API TO DECIDE NON-STRIKER

                    #SCHEDULE
                    #1. CONNECT TO CORE.py AND SELECT SHORT FOR PLAYERS VARIABLE INSTEAD OF FUZZYWUZZY
                    #2. ADD ALL API INFO
                    #3. REGEX TO DECIDE OUT TYPE AND CATCHER
                    #4. EXTRAS, BYES, ETC. HANDLE
                    #5. ANY OTHER EXCEL INFO
                    #6. ADD BALLS FACED BY INNINGS SPECIFIC OBJECT IN players VARIABLE
                    #7. USE FOW FROM API TO DECIDE NON-STRIKER


                    
                    # c += 1
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



        # for logg in log:
            # print(logg[13], len(logg))
        xl.viaDB(log, matchID, matchTracker, infoRows, update)
        driver.quit()
        print(log)

    except Exception:
        driver.quit()
        traceback.print_exc()