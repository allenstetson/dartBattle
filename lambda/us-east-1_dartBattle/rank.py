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
rank.py
Contains logic for dealing with ranks, including checking for a promotion, and
reporting the status of the user's current rank.

"""
# Std lib imports:
import logging

from ask_sdk_model.ui.image import Image

# DartBattle imports:
import teams


__all__ = [
    "checkForPromotion",
    "getRankResponse"
]


# =============================================================================
# GLOBALS
# =============================================================================
DBS3_URL = "https://s3.amazonaws.com/dart-battle-resources/"

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

RANK_REQUIREMENTS = {  #pylint: disable=invalid-name
    0: 0,
    1: 1,
    2: 5,
    3: 15,
    4: 30,
    5: 60,
    6: 100,
    7: 140,
    8: 175,
    9: 200,
    10: 250,
    11: 300,
}


# =============================================================================
# FUNCTIONS
# =============================================================================
def checkForPromotion(userSession):
    """Determines whether or not the user is due for a rank promotion.

    Checks the total number of battles that the user has participated in over
    their history of using Dart Battle. Compares that total against their
    current rank to see if the number of battles warrants a rank promotion.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    Returns:
        bool, int: True if a promotion is warranted, False otherwise. The
            integer representing the warranted rank of the user at this time.

    """
    LOGGER.info("Checking for promotion.")
    # TODO: centralize this:
    currentRank = int(userSession.playerRank)
    if int(userSession.numBattles) > RANK_REQUIREMENTS[currentRank] and \
            int(userSession.numBattles) >= RANK_REQUIREMENTS[currentRank + 1]:
        userSession.playerRank = "{:02d}".format(currentRank + 1)

        LOGGER.info("Promotion to rank {} is earned!".format(currentRank + 1))
        return True, currentRank + 1
    return False, currentRank


def getRankResponse(userSession):
    """Reports the current rank of the user and requirements for promotion.

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
    playerRank = userSession.playerRank
    playerRankName = teams.PlayerRanks(int(playerRank)).name.replace("_", " ")
    nextRankName = teams.PlayerRanks(int(playerRank)+1).name.replace("_", " ")
    # TODO: Account for General, where there is no next rank!
    numBattles = userSession.numBattles
    speech = "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" />"
    text = "Rank: {}, {} battles.\n".format(playerRankName.title(), numBattles)
    if numBattles:
        battlesRemaining = RANK_REQUIREMENTS[int(playerRank)+1] - int(numBattles)
        speech += "You have battled {} times, ".format(numBattles)
        speech += "and your current rank is {}. ".format(playerRankName)
        speech += "You have {} battles remaining ".format(battlesRemaining)
        speech += "until you reach the rank of {}. ".format(nextRankName)
        text += "{} battles until {}.".format(battlesRemaining, nextRankName)
    else:
        speech += "You are currently a {}. ".format(playerRankName)

    speech += "What would you like next? Start a battle? Exit?"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    title = "What is my rank?"
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_HTP_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_HTP_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage
