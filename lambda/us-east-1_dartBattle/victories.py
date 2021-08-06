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
victories.py - Module with logic for interacting with victories.

This includes recording, clearing, and reciting.

"""
# Std Lib imports:
import datetime
import logging

# Amazon Imports:
from ask_sdk_model.ui.image import Image

# DartBattle imports:
import database


__all__ = [
    "clearVictoryIntent",
    "countVictories",
    "reciteVictoriesIntent",
    "recordVictoryIntent"
]


# =============================================================================
# Globals
# =============================================================================
DBS3_URL = "https://s3.amazonaws.com/dart-battle-resources/"

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


# =============================================================================
# Functions
# =============================================================================
def clearVictoryIntent(userSession):
    """Clears victories for a team or user, or all victories from all time.

    TODO: Support clearing victories just from today.

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
    speech = "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" />"
    # Check to see if a particular name was given:
    playerName = userSession.request.slots["PLAYER"]["value"]
    # If the "name" provided was a cancel operation:
    if playerName.lower() in ["no", "stop", "cancel", "nope"]:
        speech += "Ok, canceling the request to clear all victories. "
    # If the "name" provided was confirmation, that means clear all:
    elif playerName.lower() in ["yes", "please", "continue", "proceed"]:
        database.clearRecordVictory(userSession)
        speech += "All victories have been cleared for all players. "
    # Otherwise, that means the name provided was an actual player or team:
    else:
        database.clearRecordVictory(userSession, victor=playerName)
        speech += "Victories for player {} have been cleared. ".format(playerName)

    # Issue appropriate response:
    text = speech
    speech += "How else may I assist? Start a battle? More options? Exit? "
    title = "Clear Victories"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_victory_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_victory_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def countVictories(victories):
    """Totals up the victories per player over their lifetime and from today.

    Args:
        victories (dict): A dictionary of player names and a value which is a
            list of their victories with datetime stamps.

    Returns:
        dict, dict: The dict of today's victories and the dict of lifetime
            victories. These have number-of-victories as their keys, and
            a list of player/team names that achieved that number as their
            value.

    """
    now = datetime.datetime.now()
    lifeVix = {}
    todayVix = {}
    # Iterate all victors (player names or team names):
    for victor in victories:
        # Total all lifetime vitories:
        lifeTime = len(victories[victor])
        if lifeTime == 0:
            # bail if they have no victories. This can happen if their
            #  victories were cleared, but their record persisted in the DB:
            continue

        # Check the dates to see if any of them occurred in the last 24 hours:
        today = ([x for x in victories[victor] if \
                (now - datetime.datetime.strptime(x, "%Y.%m.%d %H:%M:%S")).days < 1])

        # Store the result - not by player! - but by total victories. This
        #  makes it much easier to sort in order to find the top victors.
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


def reciteVictoriesIntent(userSession):
    """Reports victories for top 3 players of today & all time.

    TODO: Support the query for a single player name, reciting that player's
    overall placement ("4th") and number of victories.

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
    victories = database.getVictoriesFromDB(userSession)
    (today, lifetime) = countVictories(victories)
    speech = "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" />"
    text = ""

    # Today's victories:
    if not today:
        speech += "No victories are recorded for today. "
        text = "Today: No Victories"
    else:
        numToday = sum(map(len, today.values()))
        # we only want the top 3 players, no more
        if numToday > 3:
            numToday = 3
        # if there was only one victory, the speech is slightly different:
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
                # account for plural vs. singular:
                wordElim = "elimination"
                if numVix > 1:
                    wordElim += "s"
                speech += "{} with {} {}. ".format(victor, numVix, wordElim)
                text += "{} ({})\n".format(victor.title(), numVix)
                numReported += 1

    # Lifetime victories:
    if not lifetime:
        speech += "There are no victories recorded at all. "
        text += 'No Victories!\nTry: "Record a victory"'
    else:
        numLifetime = sum(map(len, lifetime.values()))
        # Again, we only want 3 players, no more:
        if numLifetime > 3:
            numLifetime = 3
        # If there's only one player, the speech changes a little:
        if numLifetime == 1:
            speech += "The top player of all time is "
        else:
            speech += "The top {} players of all time are ".format(numLifetime)
        text += "All Time: *"

        # Since we key off of number of victories, sorting the dict in reverse
        #  will give us the victories from highest to lowest:
        numReported = 0
        for numVix in sorted(lifetime, reverse=True):
            # bail if we've already reported the top 3:
            if numReported == numLifetime:
                break
            for victor in lifetime[numVix]:
                # report the victory, accounting for plural vs singular:
                wordElim = "elimination"
                if numVix > 1:
                    wordElim += "s"
                speech += "{} with {} {}. ".format(victor, numVix, wordElim)
                text += "{} ({})\n".format(victor, numVix)
                numReported += 1
                if numReported == numLifetime:
                    break

    # Issue appropriate response:
    speech += "What next? Start a battle? More options? Exit? "
    title = "Victories"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_victory_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_victory_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def recordVictoryIntent(userSession):
    """Records a victory in the database for the given name.

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
    speech = "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" />"
    # Catch sneaky users who try recording victories without ever battling:
    if userSession.numBattles == "0":
        speech += ("You must first complete a battle in order to record a "
                   "victory. ")
        text = "Victories come after hard-fought battles."
    else:
        victorName = userSession.request.slots["VICTOR"]["value"]
        _, vicToday, vicTotal = \
                database.updateRecordVictory(userSession, victorName)
        speech += "Okay. Recorded a victory for {}. ".format(victorName)
        # Report the new number of victories for that name:
        if vicToday == 1:
            vicToday = "1 victory"
        else:
            vicToday = "{} victories".format(vicToday)
        if vicTotal == 1:
            vicTotal = "1 lifetime victory"
        else:
            vicTotal = "{} lifetime victories".format(vicTotal)
        speech += "{} has {} today, and {}. ".format(
            victorName,
            vicToday,
            vicTotal)
        text = "Victory recorded for {}.\n".format(victorName.title())
        text += "{} has {} today, and {}. ".format(
            victorName.title(),
            vicToday,
            vicTotal)
    speech += "What next? Start a battle? More options? "
    title = "Record a Victory"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_victory_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_victory_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage
