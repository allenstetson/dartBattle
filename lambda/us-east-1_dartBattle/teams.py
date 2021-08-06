###############################################################################
# Copyright (c) 2019 Allen Stetson, allen.stetson@gmail.com
# All rights reserved. No duplication allowed.
#
# This file is part of DartBattle.
#
# DartBattle may not be copied and/or distributed without the express
# permission of Allen Stetson.
###############################################################################
"""
teams.py

Functions relating to teams and team setup.

"""
# Std lib imports:
import logging
import random

# Amazon imports:
from ask_sdk_model.ui.image import Image

# DartBattle imports:
import database
import protocols
import rank
import roles


# =============================================================================
# GLOBALS
# =============================================================================
DBS3_URL = "https://s3.amazonaws.com/dart-battle-resources/"

HAS_TEAMS = False

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


# =============================================================================
# FUNCTIONS
# =============================================================================
def assignTeamsAndRoles(numTeams, availablePlayers, userSession):
    """Splits available players up into teams and assigns roles.

    A user can form any number of teams (up to the number of players), and
    provide a list of players. Those players are randomly split up into teams
    and randomly assigned a role. The Captain is a required role, and each team
    will have one by default. Beyond that, roles are randomly chosen. Roles
    add to imaginative gameplace, and also may be featured in events, giving
    players more engagement.

    Args:
        numTeams (int): The number of teams desired.

        availablePlayers ([str]): The list of player names.

        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        {dict}, {dict}: Two nested dictionaries. The first represents the teams
            with primary keys of the team numbers (1, 2, etc.) with values of
            the player string names. Those names are keys with values of the
            role assignments ("captain"). An example resembles:
            {1: {"Asher": "Heavy Weapons Expert", "Owen": "Captain"}, 2:...}
            The second dict is a player dict which contains the same data but
            organized by player instead of by team, and using an enum to
            express roles. An example is:
            {"Asher": {1: "06"}, "Owen": {1: "00"}, ...}

    """
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
        rolesList = list(roles.PlayerRolesStandard.__members__.keys())
        if protocols.ProtocolTelemetry(userSession).isActive:
            rolesList.extend(list(roles.PlayerRolesSpecial.__members__.keys()))
        needAssignment = list(teams[teamNum].keys())
        for i, player in enumerate(needAssignment):
            if i == 0:
                role = 'captain'
            else:
                role = random.choice(rolesList)
            playerRoles[teamNum].append("{:02d}".format(roles.PlayerRoles[role].value))
            rolesList.remove(role)
            teams[teamNum][player] = role

    return teams, playerRoles


def clearTeamsIntent(userSession):
    """Clears existing teams and returns Dart Battle into individual mode.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        str: the speech to speak to the user
        str: reprompt speech if the user fails to reply
        str: the title to display on the response card
        str: text to display on the response card
        ask_sdk_model.ui.image.Image: image to display on the response card

    """
    userSession.usingTeams = False
    database.updateRecordTeams(userSession)
    speech = "Ok. "
    speech += "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" /> "
    speech += ("Team information has been cleared. What's next? "
               "Start a battle? More options? Exit? ")

    title = "Clear Teams"
    text = "Teams have been cleared."
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_ST_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_SUT_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def reciteTeamsIntent(session):
    """Recites existing teams, players, and player roles..

    After some error checking to ensure that teams are enabled and that valid
    teams have been formed, this simply calls reciteTeamRoles to generate
    speech that lists the team roles. This is invoked when the user utters a
    phrase such as:
        What are the teams?
        What teams are there?
        What teams do we have?
        Tell me the teams.

    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        str: the speech to speak to the user
        str: reprompt speech if the user fails to reply
        str: the title to display on the response card
        str: text to display on the response card
        ask_sdk_model.ui.image.Image: image to display on the response card

    """
    sessionAttributes = session['attributes']

    if not session.usingTeams:
        LOGGER.info("Recite teams invoked but teams are not enabled.")
        speech = "No teams are currently set up. "
    else:
        teams = sessionAttributes['teams']
        speech = reciteTeamRoles(teams)
        if not speech:
            LOGGER.info("Recite teams invoked but no team members found.")
            speech = "No teams are currently set up. "
        else:
            LOGGER.info("Recite teams invoked successfully.")
    text = speech
    speech += "What next? Start a battle? More options? Exit? "
    title = "Teams"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_ST_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_SUT_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def reciteTeamRoles(teams):
    """Iterates the teams and builds speech to list players and roles.

    Args:
        teams (dict): Team dict from session with keys as the team numbers,
            values as the players, and values of the players being their roles.

    Returns:
        str: The speech to read which lists teams, players, and their roles.

    """
    LOGGER.debug("in reciteTeamRoles")
    speech = ""
    for teamNum in teams.keys():
        speech += "Team {}. ".format(teamNum)
        for player in teams[teamNum]:
            role = teams[teamNum][player].replace("_", " ")
            speech += "{} is your {}. ".format(player.title(), role)
    return speech


def setupTeamsIntent(userSession):
    """Sets up desired number of teams with random player/role assignment.

    After checking that the user provided legal values, Dart Battle is put
    into "team mode", player names are validated, and teams are built.
    The database is then updated with persistent attributes to reflect the
    new teams, and the appropriate response is issued.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        str: the speech to speak to the user
        str: reprompt speech if the user fails to reply
        str: the title to display on the response card
        str: text to display on the response card
        ask_sdk_model.ui.image.Image: image to display on the response card

    """
    allPlayers = {}
    speech = ""

    numTeams = int(userSession.request.slots["TEAMNUM"]["value"])
    numPlayers = int(userSession.request.slots["PLAYERNUM"]["value"])

    # Check for a legal number of teams:
    if numTeams > numPlayers:
        speech += ("There can not be more teams than there are players. "
                   "I'll make one team for each of the {} players. ")
        speech = speech.format(numPlayers)
        numTeams = numPlayers
    userSession.usingTeams = "True"
    userSession.numTeams = numTeams
    userSession.numPlayers = numPlayers

    # RANK (if it becomes important)
    playerRank = userSession.playerRank
    if playerRank == '00':
        playerRankName = "soldier"
    else:
        playerRankName = rank.PlayerRanks(int(playerRank)).name.replace("_", " ")

    # TEAMS
    if numPlayers > 12:
        speech += ("{}, my current design allows for a maximum of 12 players. "
                   "If you need more, please let us know at "
                   "support@dartbattle.fun. Continuing with 12 players "
                   "across {} teams. ")
        speech = speech.format(playerRankName, numTeams)
        numPlayers = 12
    else:
        speech += "Ok {} teams across {} players. ".format(numTeams, numPlayers)

    # PLAYERS
    missingPlayers = 0
    playerOne = userSession.request.slots["PLAYERONE"]["value"]
    allPlayers['one'] = {"name": playerOne}
    for num, keyname in enumerate(['PLAYERTWO', 'PLAYERTHREE', 'PLAYERFOUR',
                                   'PLAYERFIVE', 'PLAYERSIX', 'PLAYERSEVEN',
                                   'PLAYEREIGHT', 'PLAYERNINE', 'PLAYERTEN',
                                   'PLAYERELEVEN', 'PLAYERTWELVE']):
        # bail if we have gone past the number of available players:
        if num + 2 > numPlayers:
            break
        # if user did not provide names for the players, just use "player #":
        if userSession.request.slots[keyname]["status"] == "Empty":
            allPlayers[num + 2] = {'name': "player {}".format(num + 2)}
            missingPlayers += 1
        # otherwise, use provided names:
        else:
            playerNum = keyname[6:].lower()
            playerName = userSession.request.slots[keyname]["value"]
            allPlayers[playerNum] = {"name": playerName}
    # Sometimes, Alexa fails to associate spoken names with player name slots.
    #  If the number of requested players and the number of filled slots do not
    #  match, we know that we have some missing players. Just use "player #"
    #  for the missing players.
    if missingPlayers:
        # The user might intentionally shortcut to using player numbers by just
        #  saying "one" in response to the names prompt. Detect this and go
        #  straight to using player numbers.
        if missingPlayers == (numPlayers - 1) and \
                allPlayers["one"]["name"] in ["one", "1", 1]:
            allPlayers["one"]["name"] = "player 1"
            speech += "Using player numbers."
        # otherwise, warn the user that some names were missed, and that we'll
        #  be using player numbers.
        else:
            if missingPlayers == 1:
                first = ["I missed a player name. ", "I missed one name. "]
            else:
                first = ["I think I missed some player names. ",
                         "I missed some player names. "]
            last = ["No worries, I'll use their player number. ",
                    "I'll use their player numbers instead. "]
            speech += random.choice(first) + random.choice(last)
    LOGGER.info(allPlayers)

    # BUILD
    speech += "Now building teams. "
    speech += "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" /> "

    teams, playerRoles = assignTeamsAndRoles(
        numTeams,
        [allPlayers[x]['name'] for x in allPlayers],
        userSession
        )
    # Update persistent session information to reflect the new teams:
    userSession.playerRoles = playerRoles
    userSession.teams = teams
    database.updateRecordTeams(userSession)

    # Return appropriate response:
    roleSpeech = reciteTeamRoles(teams)
    speech += roleSpeech
    speech += "How shall I proceed? Start a battle? More options? "
    text = roleSpeech
    title = "Setup Teams"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_ST_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_SUT_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def shuffleTeamsIntent(userSession):
    """Shuffles existing players across new teams, assigns new roles.

    This uses the same number of teams as previously specified, the same
    players specified, but redistributes them to teams, and assigns them
    new player roles.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        str: the speech to speak to the user
        str: reprompt speech if the user fails to reply
        str: the title to display on the response card
        str: text to display on the response card
        ask_sdk_model.ui.image.Image: image to display on the response card

    """
    if not userSession.usingTeams:
        speech = ("I would shuffle the teams, but no teams have been "
                  "recently set up. ")
        text = "No current teams. "
    else:
        speech = ("<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" />"
                  "Shuffling teams and roles... ")
        teamNums = userSession.teams.keys()
        playerNames = []
        for num in teamNums:
            playerNames.extend(list(userSession.teams[num].keys()))
        numTeams = len(teamNums)
        teams, playerRoles = assignTeamsAndRoles(
            numTeams,
            playerNames,
            userSession)
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
        small_image_url=DBS3_URL + "dartBattle_ST_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_SUT_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage
