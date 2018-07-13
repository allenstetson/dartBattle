# Std Lib imports:
import datetime
import os

# DartBattle imports:
import database
import responses


def clearVictoryIntent(request, session):
    speech = ""
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
        database.clearRecordVictory(sessionAttributes)
        speech += "All victories have been cleared for all players. "
    else:
        database.clearRecordVictory(sessionAttributes, victor=playerName)
        speech += "Victories for player {} have been cleared. ".format(playerName)
    text = speech
    speech += "How else may I assist? Start a battle? More options? Exit? "
    title = "Clear Victories"
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


def reciteVictoriesIntent(session):  # TODO: Support single player request (place, numVix)
    sessionAttributes = session['attributes']
    victories = database.getVictoriesFromDB(sessionAttributes)
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
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def recordVictoryIntent(request, session):
    speech = ""
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
        (success, vicToday, vicTotal) = database.updateRecordVictory(sessionAttributes, victorName)
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
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_victory_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }
