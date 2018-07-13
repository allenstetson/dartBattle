# Std lib imports:
import logging
import os

# DartBattle imports:
import database
import responses
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


def getRankResponse(session):
    global rankRequirements
    sessionAttributes = session['attributes']
    playerRank = sessionAttributes.get('playerRank', '00')
    playerRankName = teams.PlayerRanks(int(playerRank)).name.replace("_", " ")
    nextRankName = teams.PlayerRanks(int(playerRank)+1).name.replace("_", " ")
    # TODO: Account for General, where there is no next rank!
    numBattles = sessionAttributes.get('numBattles', 0)
    speech = "You are currently a {}.".format(playerRankName)
    text = "Rank: {}, {} battles.\n".format(playerRankName.title(), numBattles)
    if numBattles:
        battlesRemaining = rankRequirements[int(playerRank)+1] - int(numBattles)
        speech = "You have battled {} times, ".format(numBattles)
        speech += "and your current rank is {}. ".format(playerRankName)
        speech += "You have {} battles remaining ".format(battlesRemaining)
        speech += "until you reach the rank of {}. ".format(nextRankName)
        text += "{} battles until {}.".format(battlesRemaining, nextRankName)
    speech += "What would you like next? Start a battle? Exit?"

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
                "title": "What is my rank?",
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def checkForPromotion(sessionAttributes):
    global rankRequirements
    logger.info("Checking for promotion.")
    # TODO: centralize this:
    currentRank = int(sessionAttributes['playerRank'])
    numBattles = sessionAttributes['numBattles']
    if int(numBattles) > rankRequirements[currentRank] and \
            int(numBattles) >= rankRequirements[currentRank + 1]:
        sessionAttributes['playerRank'] = "{:02d}".format(currentRank + 1)
        database.updateRecord(sessionAttributes)
        logger.info("Promotion to rank {} is earned!".format(currentRank + 1))
        return True, currentRank + 1
    return False, currentRank
