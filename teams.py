"""
teams.py

Functions relating to teams and team setup.
"""
import datetime
import enum
import logging
import random

import database
import responses

logger = logging.getLogger()
logger.setLevel(logging.INFO)
HAS_TEAMS = False


class PlayerRoles(enum.Enum):
    none = 0
    captain = 1
    communications_specialist = 2
    computer_specialist = 3
    electrician = 4
    explosives_expert = 5
    heavy_weapons_expert = 6
    intelligence_officer = 7
    mechanic = 8
    medic = 9
    pilot = 10
    science_officer = 11
    scout = 12
    sniper = 13
    special_forces_operative = 14
    any = 99


class PlayerRanks(enum.Enum):
    private = 1
    corporal = 2
    sergeant = 3
    lieutenant = 4
    captain = 5
    lieutenant_colonel = 6
    colonel = 7
    brigadier_general = 8
    major_general = 9
    lieutenant_general = 10
    general = 11


def assignTeamsandRoles(numTeams, availablePlayers):
    numPlayers = len(availablePlayers)
    playersPerTeam = int(numPlayers / numTeams)
    teams = {}
    for team in range(numTeams):
        teams[str(team + 1)] = {}  # str req'd for dynaodb
        for i in range(playersPerTeam):
            pick = random.choice(availablePlayers)
            teams[str(team + 1)][pick] = None
            availablePlayers.remove(pick)
    leftoverIdx = 0
    while availablePlayers:
        leftoverIdx += 1
        leftover = availablePlayers[0]
        teams[str(leftoverIdx)][leftover] = None
        availablePlayers.remove(leftover)

    # ROLES
    playerRoles = {}
    for teamNum in teams:
        playerRoles[teamNum] = []
        roles = list(PlayerRoles.__members__.keys())
        needAssignment = list(teams[teamNum].keys())
        for i, player in enumerate(needAssignment):
            if i == 0:
                role = 'captain'
            else:
                role = random.choice(roles)
                while role in ['any', 'none']:
                    role = random.choice(roles)
            playerRoles[teamNum].append("{:02d}".format(PlayerRoles[role].value))
            roles.remove(role)
            teams[teamNum][player] = role

    return teams, playerRoles


def clearTeamsIntent(request, session):
    if not "attributes" in session:
        sessionAttributes = database.GetSessionFromDB(session)
    else:
        sessionAttributes = session['attributes']

    sessionAttributes['usingTeams'] = False
    database.UpdateRecordTeams(sessionAttributes)
    speech = "Ok. "
    speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "
    speech += "Team information has been cleared. What's next? Start a battle? More options? Exit? "

    title = "Clear Teams"
    text = "Teams have been cleared."

    return {
        "version": responses.VERSION,
        "sessionAttributes": sessionAttributes,
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_ST_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SUT_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def clearVictoryIntent(request, session):
    speech = ""
    if not "attributes" in session:
        sessionAttributes = database.GetSessionFromDB(session)
    else:
        sessionAttributes = session['attributes']

    dialogState = request['dialogState']
    if dialogState in ["STARTED", "IN_PROGRESS"]:
        return responses.continueDialog(sessionAttributes)
    elif dialogState == 'COMPLETED':
        sessionAttributes = session['attributes']
    playerName = request['intent']['slots']['PLAYER']['value']
    if playerName.lower() in ["no", "stop", "cancel", "nope"]:
        speech += "Ok, canceling the request to clear all victories. "
    elif playerName.lower() in ["yes", "please", "continue", "proceed"]:
        database.ClearRecordVictory(sessionAttributes)
        speech += "All victories have been cleared for all players. "
    else:
        database.ClearRecordVictory(sessionAttributes, victor=playerName)
        speech += "Victories for player {} have been cleared. ".format(playerName)
    text = speech
    speech += "How else may I assist? Start a battle? More options? Exit? "
    title = "Clear Victories"
    return {
        "version": responses.VERSION,
        "sessionAttributes": sessionAttributes,
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def countVictories(victories):
    now = datetime.datetime.now()
    lifeVix = {}
    todayVix = {}
    for victor in victories:
        lifeTime = len(victories[victor])
        if lifeTime == 0:
            continue
        today = ([x for x in victories[victor] if (now - datetime.datetime.strptime(x, "%Y.%m.%d %H:%M:%S")).days < 1])
        if not lifeTime in lifeVix:
            lifeVix[lifeTime] = []
        lifeVix[lifeTime].append(victor)
        numToday = len(today)
        if not numToday:
            continue
        if not numToday in todayVix:
            todayVix[numToday] = []
        todayVix[numToday].append(victor)
    return todayVix, lifeVix


def shuffleTeamsIntent(request, session):
    """
                "teams": {
                "1": {
                    "George": "captain",
                    "player 4": "special_forces_operative",
                    "player 3": "pilot"
                },
                "2": {
                    "player 2": "heavy_weapons",
                    "player 5": "captain"
                }
            },

    :param request:
    :param session:
    :return:
    """
    if not "attributes" in session:
        sessionAttributes = database.GetSessionFromDB(session)
    else:
        sessionAttributes = session['attributes']

    if not "teams" in sessionAttributes:
        speech = "I would shuffle the teams, but no teams have been recently set up."
        text = "No current teams."
    else:
        speech = "Shuffling teams and roles... "
        teamNums = sessionAttributes['teams'].keys()
        playerNames = []
        for num in teamNums:
            playerNames.extend(list(sessionAttributes['teams'][num].keys()))
        numTeams = len(teamNums)
        teams, playerRoles = assignTeamsandRoles(numTeams, playerNames)
        sessionAttributes['playerRoles'] = playerRoles
        sessionAttributes['teams'] = teams
        success = database.UpdateRecordTeams(sessionAttributes)

        roleSpeech = ReciteTeamRoles(teams)
        speech += roleSpeech
    text = speech
    speech += "What next? Start a battle? More options? Exit? "
    title = "Shuffle Teams"
    return {
        "version": responses.VERSION,
        "sessionAttributes": sessionAttributes,
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_ST_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SUT_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def reciteTeamsIntent(request, session):
    """
    What are the teams?
    What teams are there?
    What teams do we have?
    Tell me the teams.

    :param request:
    :param session:
    :return:
    """
    if not "attributes" in session:
        sessionAttributes = database.GetSessionFromDB(session)
    else:
        sessionAttributes = session['attributes']

    if not sessionAttributes['usingTeams']:
        logging.info("Recite teams invoked but teams are not enabled.")
        speech = "No teams are currently set up. "
    else:
        teams = sessionAttributes['teams']
        speech = ReciteTeamRoles(teams)
        if not speech:
            logging.info("Recite teams invoked but no team members found.")
            speech = "No teams are currently set up. "
        else:
            logging.info("Recite teams invoked successfully.")
    text = speech
    speech += "What next? Start a battle? More options? Exit? "
    title = "Teams"
    return {
        "version": responses.VERSION,
        "sessionAttributes": sessionAttributes,
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_ST_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SUT_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def ReciteTeamRoles(teams):
    speech = ""
    for teamNum in teams.keys():
        speech += "Team {}. ".format(teamNum)
        for player in teams[teamNum]:
            role = teams[teamNum][player].replace("_", " ")
            speech += "{} is your {}. ".format(player.title(), role)
    return speech


def reciteVictoriesIntent(request, session):  #TODO: Support single player request (place, numVix)
    if not "attributes" in session:
        sessionAttributes = database.GetSessionFromDB(session)
    else:
        sessionAttributes = session['attributes']

    victories = database.GetVictoriesFromDB(sessionAttributes)
    (today, lifetime) = countVictories(victories)
    speech = ""
    text = ""
    if not today:
        speech += "No victories are recorded for today. "
        text = "Today: No Victories"
    else:
        numToday = sum(map(len, today.values()))
        if numToday > 3:
            numToday = 3
        if numToday == 1:
            speech += "The top player of today is "
        else:
            speech += "The top {} players of today are ".format(numToday)
        text += "Today: *"
        numReported = 0
        for numVix in sorted(today, reverse=True):
            if numReported == numToday:
                break
            for victor in today[numVix]:
                wordElim = "elimination"
                if numVix > 1:
                    wordElim += "s"
                speech += "{} with {} {}. ".format(victor, numVix, wordElim)
                text += "{} ({})\n".format(victor.title(), numVix)
                numReported += 1
    if not lifetime:
        speech += "There are no victories recorded at all. "
        text += 'No Victories!\nTry: "Record a victory"'
    else:
        numLifetime = sum(map(len, lifetime.values()))
        if numLifetime > 3:
            numLifetime = 3
        if numLifetime == 1:
            speech += "The top player of all time is "
        else:
            speech += "The top {} players of all time are ".format(numLifetime)
        text += "All Time: *"
        numReported = 0
        for numVix in sorted(lifetime, reverse=True):
            if numReported == numLifetime:
                break
            for victor in lifetime[numVix]:
                wordElim = "elimination"
                if numVix > 1:
                    wordElim += "s"
                speech += "{} with {} {}. ".format(victor, numVix, wordElim)
                text += "{} ({})\n".format(victor, numVix)
                numReported += 1
                if numReported == numLifetime:
                    break

    speech += "What next? Start a battle? More options? Exit? "
    title = "Victories"

    return {
        "version": responses.VERSION,
        "sessionAttributes": sessionAttributes,
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def recordVictoryIntent(request, session):
    speech = ""
    if not "attributes" in session:
        sessionAttributes = database.GetSessionFromDB(session)
    else:
        sessionAttributes = session['attributes']

    dialogState = request['dialogState']
    if dialogState in ["STARTED", "IN_PROGRESS"]:
        return responses.continueDialog(sessionAttributes)
    elif dialogState == 'COMPLETED':
        sessionAttributes = session['attributes']
    if sessionAttributes['numBattles'] == "0":
        speech += "You must first complete a battle in order to record a victory. "
        text = "Victories come after hard-fought battles."
    else:
        victorName = request['intent']['slots']['VICTOR']['value']
        (success, vicToday, vicTotal) = database.UpdateRecordVictory(sessionAttributes, victorName)
        speech += "Okay. Recorded a victory for {}. ".format(victorName)
        if vicToday == 1:
            vicToday = "1 victory"
        else:
            vicToday = "{} victories".format(vicToday)
        if vicTotal == 1:
            vicTotal = "1 lifetime victory"
        else:
            vicTotal = "{} lifetime victories".format(vicTotal)
        speech += "{} has {} today, and {}. ".format(victorName, vicToday, vicTotal)
        text = "Victory recorded for {}.\n".format(victorName.title())
        text += "{} has {} today, and {}. ".format(victorName.title(), vicToday, vicTotal)
    speech += "What next? Start a battle? More options? "

    title = "Record a Victory"

    return {
        "version": responses.VERSION,
        "sessionAttributes": sessionAttributes,
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def setupTeamsIntent(request, session):
    if not "attributes" in session:
        sessionAttributes = database.GetSessionFromDB(session)
    else:
        sessionAttributes = session['attributes']

    dialogState = request['dialogState']
    if dialogState in ["STARTED", "IN_PROGRESS"]:
        return responses.continueDialog(sessionAttributes)
    elif dialogState == 'COMPLETED':
        sessionAttributes = session['attributes']

    allPlayers = {}
    numTeams = int(request['intent']['slots']['TEAMNUM']['value'])
    numPlayers = int(request['intent']['slots']['PLAYERNUM']['value'])
    sessionAttributes['usingTeams'] = "True"
    sessionAttributes['numTeams'] = numTeams
    sessionAttributes['numPlayers'] = numPlayers

    # RANK (if it becomes important)
    if 'playerRank' in sessionAttributes:
        playerRank = sessionAttributes['playerRank']
        if playerRank == '00':
            playerRankName = "soldier"
        else:
            playerRankName = PlayerRanks(int(playerRank)).name.replace("_", " ")
    else:
        playerRankName = "soldier"

    #TEAMS
    if numPlayers > 12:
        speech = "{}, my current design allows for a maximum of 12 players. ".format(playerRankName)
        speech += "If you need more, please let us know at support@dartbattle.fun. "
        speech += "Continuing with 12 players across {} teams. ".format(numTeams)
        numPlayers = 12
    else:
        speech = "Ok {} teams across {} players. ".format(numTeams, numPlayers)

    #PLAYERS
    missingPlayers = False
    playerOne = request['intent']['slots']['PLAYERONE']['value']
    allPlayers['one'] = {"name": playerOne}
    for num, keyname in enumerate(['PLAYERTWO', 'PLAYERTHREE', 'PLAYERFOUR', 'PLAYERFIVE',
            'PLAYERSIX', 'PLAYERSEVEN', 'PLAYEREIGHT', 'PLAYERNINE',
            'PLAYERTEN', 'PLAYERELEVEN', 'PLAYERTWELVE']):
        if num + 2 > numPlayers:
            break
        if 'value' in request['intent']['slots'][keyname]:
            playerNum = keyname[6:].lower()
            playerName = request['intent']['slots'][keyname]['value']
            allPlayers[playerNum] = {"name": playerName}
        else:
            allPlayers[num + 2] = {'name': "player {}".format(num + 2)}
            missingPlayers = True
    if missingPlayers:
        speech += "I think I missed a player name or two. No worries, I'll use "+\
            "their player number. "

    # BUILD
    speech += "Now building teams. "
    speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "

    teams, playerRoles = assignTeamsandRoles(numTeams, [allPlayers[x]['name'] for x in allPlayers.keys()])
    sessionAttributes['playerRoles'] = playerRoles
    sessionAttributes['teams'] = teams
    database.UpdateRecordTeams(sessionAttributes)

    roleSpeech = ReciteTeamRoles(teams)
    speech += roleSpeech
    speech += "How shall I proceed? Start a battle? More options? "

    text = roleSpeech
    title = "Setup Teams"
    return {
        "version": responses.VERSION,
        "sessionAttributes": sessionAttributes,
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_ST_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SUT_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }
