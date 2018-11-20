"""
teams.py

Functions relating to teams and team setup.
"""
# Std lib imports:
import enum
import logging
import os
import random

from ask_sdk_model.ui.image import Image

# DartBattle imports:
import database
import protocols
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


class PlayerRolesStandard(enum.Enum):
    captain = 1
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


class PlayerRolesSpecial(enum.Enum):
    communications_specialist = 2


class PlayerRanks(enum.Enum):
    newbie = 0
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


def assignTeamsAndRoles(numTeams, availablePlayers, userSession):
    # TODO: Look at session attrs to determine if special roles are unlocked.
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
        roles = list(PlayerRolesStandard.__members__.keys())
        if protocols.ProtocolTelemetry(userSession).isActive:
            roles.extend(list(PlayerRolesSpecial.__members__.keys()))
        needAssignment = list(teams[teamNum].keys())
        for i, player in enumerate(needAssignment):
            if i == 0:
                role = 'captain'
            else:
                role = random.choice(roles)
            playerRoles[teamNum].append("{:02d}".format(PlayerRoles[role].value))
            roles.remove(role)
            teams[teamNum][player] = role

    return teams, playerRoles


def clearTeamsIntent(userSession):
    userSession.usingTeams = False
    database.updateRecordTeams(userSession)
    speech = "Ok. "
    speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "
    speech += "Team information has been cleared. What's next? Start a battle? More options? Exit? "

    title = "Clear Teams"
    text = "Teams have been cleared."
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_ST_720x480.jpg",
        large_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_SUT_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def reciteTeamsIntent(session):
    """
    What are the teams?
    What teams are there?
    What teams do we have?
    Tell me the teams.

    """
    sessionAttributes = session['attributes']

    if not session.usingTeams:
        logging.info("Recite teams invoked but teams are not enabled.")
        speech = "No teams are currently set up. "
    else:
        teams = sessionAttributes['teams']
        speech = reciteTeamRoles(teams)
        if not speech:
            logging.info("Recite teams invoked but no team members found.")
            speech = "No teams are currently set up. "
        else:
            logging.info("Recite teams invoked successfully.")
    text = speech
    speech += "What next? Start a battle? More options? Exit? "
    title = "Teams"
    return {
        "version": os.environ['VERSION'],
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


def reciteTeamRoles(teams):
    speech = ""
    for teamNum in teams.keys():
        speech += "Team {}. ".format(teamNum)
        for player in teams[teamNum]:
            role = teams[teamNum][player].replace("_", " ")
            speech += "{} is your {}. ".format(player.title(), role)
    return speech


def setupTeamsIntent(userSession):
    allPlayers = {}
    speech = ""

    numTeams = int(userSession.request.slots["TEAMNUM"]["value"])
    numPlayers = int(userSession.request.slots["PLAYERNUM"]["value"])

    if numTeams > numPlayers:
        speech += "There can not be more teams than there are players. I'll make one team for each of the {} players. ".format(
            numPlayers)
        numTeams = numPlayers
    userSession.usingTeams = "True"
    userSession.numTeams = numTeams
    userSession.numPlayers = numPlayers

    # RANK (if it becomes important)
    playerRank = userSession.playerRank
    if playerRank == '00':
        playerRankName = "soldier"
    else:
        playerRankName = PlayerRanks(int(playerRank)).name.replace("_", " ")

    # TEAMS
    if numPlayers > 12:
        speech += "{}, my current design allows for a maximum of 12 players. ".format(playerRankName)
        speech += "If you need more, please let us know at support@dartbattle.fun. "
        speech += "Continuing with 12 players across {} teams. ".format(numTeams)
        numPlayers = 12
    else:
        speech += "Ok {} teams across {} players. ".format(numTeams, numPlayers)

    # PLAYERS
    missingPlayers = False
    playerOne = userSession.request.slots["PLAYERONE"]["value"]
    allPlayers['one'] = {"name": playerOne}
    for num, keyname in enumerate(['PLAYERTWO', 'PLAYERTHREE', 'PLAYERFOUR', 'PLAYERFIVE',
                                   'PLAYERSIX', 'PLAYERSEVEN', 'PLAYEREIGHT', 'PLAYERNINE',
                                   'PLAYERTEN', 'PLAYERELEVEN', 'PLAYERTWELVE']):
        if num + 2 > numPlayers:
            break
        if userSession.request.slots["PLAYERONE"]["status"] == "Empty":
            allPlayers[num + 2] = {'name': "player {}".format(num + 2)}
            missingPlayers = True
        else:
            playerNum = keyname[6:].lower()
            playerName = userSession.request.slots[keyname]["value"]
            allPlayers[playerNum] = {"name": playerName}
    if missingPlayers:
        speech += "I think I missed a player name or two. No worries, I'll use " + \
                  "their player number. "

    # BUILD
    speech += "Now building teams. "
    speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "

    teams, playerRoles = assignTeamsAndRoles(numTeams, [allPlayers[x]['name'] for x in allPlayers.keys()],
                                             userSession)
    userSession.playerRoles = playerRoles
    userSession.teams = teams
    database.updateRecordTeams(userSession)

    roleSpeech = reciteTeamRoles(teams)
    speech += roleSpeech
    speech += "How shall I proceed? Start a battle? More options? "
    text = roleSpeech
    title = "Setup Teams"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_ST_720x480.jpg",
        large_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_SUT_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def shuffleTeamsIntent(userSession):
    if not userSession.usingTeams:
        speech = "I would shuffle the teams, but no teams have been recently set up. "
        text = "No current teams. "
    else:
        speech = "Shuffling teams and roles... "
        speech = "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" />" + speech
        teamNums = userSession.teams.keys()
        playerNames = []
        for num in teamNums:
            playerNames.extend(list(userSession.teams[num].keys()))
        numTeams = len(teamNums)
        teams, playerRoles = assignTeamsAndRoles(numTeams, playerNames, userSession)
        userSession.playerRoles = playerRoles
        userSession.teams = teams
        database.updateRecordTeams(userSession)

        roleSpeech = reciteTeamRoles(teams)
        speech += roleSpeech
        text = speech
    speech += "What next? Start a battle? More options? Exit? "
    title = "Shuffle Teams"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_ST_720x480.jpg",
        large_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_SUT_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage
