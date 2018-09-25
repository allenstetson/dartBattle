# Std lib imports:
import logging
import os

from ask_sdk_model.ui.image import Image

# DartBattle imports:
import teams

logger = logging.getLogger()
logger.setLevel(logging.INFO)

rankRequirements = {
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


def getRankResponse(userSession):
    global rankRequirements
    playerRank = userSession.playerRank
    playerRankName = teams.PlayerRanks(int(playerRank)).name.replace("_", " ")
    nextRankName = teams.PlayerRanks(int(playerRank)+1).name.replace("_", " ")
    # TODO: Account for General, where there is no next rank!
    numBattles = userSession.numBattles
    speech = "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/introMusic.mp3\" />"
    text = "Rank: {}, {} battles.\n".format(playerRankName.title(), numBattles)
    if numBattles:
        battlesRemaining = rankRequirements[int(playerRank)+1] - int(numBattles)
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
        small_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_720x480.jpg",
        large_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def checkForPromotion(userSession):
    global rankRequirements
    logger.info("Checking for promotion.")
    # TODO: centralize this:
    currentRank = int(userSession.playerRank)
    if int(userSession.numBattles) > rankRequirements[currentRank] and \
            int(userSession.numBattles) >= rankRequirements[currentRank + 1]:
        userSession.playerRank = "{:02d}".format(currentRank + 1)

        logger.info("Promotion to rank {} is earned!".format(currentRank + 1))
        return True, currentRank + 1
    return False, currentRank
