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
responses.py
Contains the responses to intents that pertain to the main skill menu.

Responses include:
    getOptionsResponse - for the help response, detailing supported options
    getWelcomeResponse - generating greetings when the skill first starts
    howToPlayResponse - recites the rules of the game for the user
    toggleSettingsResponse - allows enable/disable of events

"""

# Std Lib imports:
import os
import logging
import random

# Amazon Imports:
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata)
from ask_sdk_model.interfaces import display
from ask_sdk_model.ui.image import Image

# DartBattle imports:
import playlists
import rank
import teams


__all__ = [
    "getTestResponse",
    "getOptionsResponse",
    "getWelcomeResponse",
    "howToPlayResponse",
    "toggleSettingsResponse",
    "turnOffSettingsResponse",
    "turnOnSettingsResponse"
]


# =============================================================================
# GLOBALS
# =============================================================================
DBS3_URL = 'https://s3.amazonaws.com/dart-battle-resources/'

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


# =============================================================================
# TEST RESPONSES
# =============================================================================
def getTestResponse(session):
    """Function generating a simple text response.

    Used for testing certain menu interactions.

    NOT USED IN PRODUCTION

    """
    speech = "Perimeter compromised. Defenses will be breached in 5, 4, 3, 2, 1. "
    speech = '<audio src="' + DBS3_URL + 'scenarios/prospector/events/ceaseFire/event_Prospectors_00_CeaseFire_Bats_Any_00.mp3" /> '

    return {
        "version": os.environ['VERSION'],
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>" + speech + "</speak>"
            },
            "shouldEndSession": True
        }
    }


# =============================================================================
# SPECIFIC USER RESPONSES
# =============================================================================
def getOptionsResponse(session):
    """Generates a response for the help message of the skill.

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
    playerRank = session.playerRank
    if playerRank == '00':
        playerRankName = "soldier"
    else:
        playerRankName = rank.PlayerRanks(int(playerRank)).name.replace("_", " ")

    speech = ("<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" /> "
              "<audio src=\"" + DBS3_URL + "comsatTellWhatYouCanDo_01.mp3\" /> "
              "Of course Commander. {}, this comsat unit supports the "
              "following commands: "
              "for teams, you can say setup teams, tell me the teams, shuffle "
              "teams, clear the teams. For battles, you can say start a battle,"
              " start a 7 minute battle, or other duration besides 7. For rank,"
              " say what is my rank. For victories, you can say record a "
              "victory, tell me the victories, clear all victories, clear "
              "victories for someone's name.  To understand the rules of the "
              "game, you can say how do I play. "
              "Finally, you can say more options to hear this again. "
              "What would you like me to do next? "
             ).format(playerRankName)

    text = ("__TEAMS:__\n"
            "Setup teams, Tell me the teams, Shuffle teams.\n"
            "__BATTLES:__\n"
            "Start a battle, Start a _ minute battle.\n"
            "__RANK:__\n"
            "What rank am I?\n"
            "__VICTORIES:__\n"
            "Record a victory, Tell me the victories,\n"
            "Clear all victories, Clear victories for _.\n"
            "__OTHER:__\n"
            "How do I play?, More Options."
           )

    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."

    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_MO_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_MO_1200x800.jpg"
    )
    title = "Options"
    return speech, reprompt, title, text, cardImage


def getWelcomeResponse(session):
    """Generates the greeting to be played when the skill first starts up.

    This logic is highly complicated, and the greetings can take a huge variety
    of forms depending on various protocols, player rank, promotion conditions,
    and number of invocations for the day.

    The general format for the greeting is as follows:
    1. Music
      The standard Dart Battle music.
    2. Welcome To/Back
      A greeting that changes based on the user's usage history and taking into
      account whether or not we are in team mode.
    3. New User Greeting
      If the user is brand new to the skill, a special welcome message is
      played. ("I see that you've just joined...")
    4. You can say / Would you like to
      This is a prompt to get the user started, randomly selected from a
      variety of choices.

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
    (isNewRank, rankNum) = rank.checkForPromotion(session)

    # -------------------------------------------------------------------------
    # Determine welcome
    # -------------------------------------------------------------------------
    if session.recentSession == "True":
        title = "Welcome Back"
        # TODO: additional titles:
        #  "I'm here for you, troops/soldier.", "Resuming Dart Battle,
        #  protocol Igloo/Tango", "Welcome back.", "On alert.", "Monitoring
        #  enemy activity."
    else:
        title = "Welcome, Soldier"
        # TODO: additional titles:
        #  "Dart Battle mission instantiated.", "Attention! Codename Dart
        #  Battle ready for orders.", "Dart Battle Protocol ready for
        #  commands."

    welcome = playlists.Greeting(session).getGreeting()

    # -------------------------------------------------------------------------

    text = "Try saying:\n"
    text += "- Setup Teams,\n"
    text += "- Start a Battle,\n"
    text += "- More Options"
    imgName = "SB"

    # -------------------------------------------------------------------------
    # Handle rank increase
    # -------------------------------------------------------------------------
    promotion = ""
    if isNewRank:
        promotionFile = playlists.getRankPromotionFile(rankNum)
        msg = "Received a promotion track to play: {}".format(promotionFile)
        LOGGER.info(msg)
        promotion += "<audio src=\"{}\" />".format(promotionFile)
        session.playerRank = rankNum
        title = "Congratulations!"
        playerRankName = rank.PlayerRanks(int(rankNum)).name.replace("_", " ")
        text = "You are hereby promoted to {}.".format(playerRankName.title())
        imgName = "victory"

    # -------------------------------------------------------------------------
    # Handle new recruit
    # -------------------------------------------------------------------------
    justJoined = ""
    if session.playerRank == "00" and session.recentSession == "False":
        justJoined = '<audio src="' + DBS3_URL + 'common/common_Any_00_Greeting_JustJoinedA_Any_00.mp3" />'

    # -------------------------------------------------------------------------
    # Handle 'you can' intro, options
    # -------------------------------------------------------------------------
    if session.recentSession == "True":
        if session.usingTeams == "True":
            tracks = [
                DBS3_URL + "common/common_Any_00_Greeting_OptionsQuickA_Team_00.mp3"
            ]
        else:
            tracks = [
                DBS3_URL + "common/common_Any_00_Greeting_OptionsQuickA_NoTeam_00.mp3"
            ]
    else:
        tracks = []
    tracks.append(DBS3_URL + "common/common_Any_00_Greeting_OptionsA_Any_00.mp3")
    tracks.append(DBS3_URL + "common/common_Any_00_Greeting_OptionsB_Any_00.mp3")
    youCan = random.choice(tracks)
    youCan = "<audio src=\"{}\" />".format(youCan)

    # -------------------------------------------------------------------------

    speech = welcome + justJoined + promotion + youCan
    print("SPEECH: {}".format(speech))

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."

    speech = "<audio src=\"" + DBS3_URL + "introMusic.mp3\" />" + speech
    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_{}_720x480.jpg".format(imgName),
        large_image_url=DBS3_URL + "dartBattle_{}_1200x800.jpg".format(imgName)
    )
    return speech, reprompt, title, text, cardImage


def howToPlayResponse():
    """Generates the rules on how to play.

    Returns:
        str: the speech to speak to the user
        str: reprompt speech if the user fails to reply
        str: the title to display on the response card
        str: text to display on the response card
        ask_sdk_model.ui.image.Image: image to display on the response card
        ask_sdk_model.interfaces.audioplayer.PlayDirective: an audio play
            directive defining an audio track to play back in the audio player.
            (This audio track is over a minute long, necessitating the use of
            the audio player instead of a track embedded in the speech.)

    """
    speech = "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" />"
    text = "- Use foam-based weaponry, score eliminations.\n"
    text += "- No head shots or point blank shots.\n"
    text += "- Listen for special events!\n"
    text += "- When eliminated, wait 5 seconds to rejoin.\n"
    text += "- Be honest!\n"
    text += "- Wear eye protection.\n"
    text += "- Settle disputes in a friendly manner.\n"
    text += " - HAVE FUN"
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."

    smallImg = DBS3_URL + "dartBattle_HTP_720x480.jpg"
    largeImg = DBS3_URL + "dartBattle_HTP_1200x800.jpg"
    cardImage = Image(
        small_image_url=smallImg,
        large_image_url=largeImg
    )
    title = "How to Play"
    directive = PlayDirective(
        play_behavior=PlayBehavior.REPLACE_ALL,
        audio_item=AudioItem(
            stream=Stream(
                expected_previous_token=None,
                token="howToPlay_track01",
                url=DBS3_URL + "howDoIPlay.mp3",
                offset_in_milliseconds=0
            ),
            metadata=AudioItemMetadata(
                title=title,
                subtitle=text,
                art=display.Image(
                    content_description=title,
                    sources=[
                        display.ImageInstance(
                            url=largeImg
                        )
                    ]
                ),
                background_image=display.Image(
                    content_description=title,
                    sources=[
                        display.ImageInstance(
                            url=largeImg
                        )
                    ]
                )
            )
        )
    )
    return speech, reprompt, title, text, cardImage, directive


def toggleSettingsResponse(userSession, enabled):
    """Method used to enable/disable events & potentially other settings.

    Currently, events are the only thing under the user's control to enable or
    disable.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

        enabled (bool): The desired state of the setting, True for on, False
            for off.

    Returns:
        str: the speech to speak to the user
        str: reprompt speech if the user fails to reply
        str: the title to display on the response card
        str: text to display on the response card
        ask_sdk_model.ui.image.Image: image to display on the response card

    """
    if not "ATTRNAME" in userSession.request.slots:
        print("SLOTS: {}".format(userSession.request.slots))
        return "Programming error: missing slots.", "", "", "", None

    attr = userSession.request.slots["ATTRNAME"]
    text = ""
    title = ""

    speech = ""
    if attr['status'] == "StatusCode.ER_SUCCESS_NO_MATCH":
        msg = "I'd like to comply, but I don't recognize {}. "
        msg = msg.format(attr['value'])
        speech += msg
        title = "Did you say {}?".format(attr['value'])
        text = "Did Not Compute"
    elif attr['value'].lower() == "events":
        speech += "<audio src=\"" + DBS3_URL + "choiceMusic.mp3\" /> "
        if enabled:
            speech += "Events enabled. "
            text = "Events enabled."
            userSession.usingEvents = "True"
            title = "Enable Events."
        else:
            speech += "Events disabled. Your battles will have no events "
            speech += "until re-enabled. "
            text = "Events disabled."
            userSession.usingEvents = "False"
            title = "Disable Events."
    else:
        # Quite unexpected, but this will catch anything other than
        #  sanctioned input
        speech = ("I'm not sure what to do with the slot {} "
                  "that has a status of {}. ")
        speech = speech.format(attr['value'], attr['status'])
        print(speech)
    speech += "What next? "
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."

    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_HTP_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_HTP_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


def turnOffSettingsResponse(userSession):
    """Function resulting in the disabling of a setting such as Events."""
    enabled = False
    return toggleSettingsResponse(userSession, enabled)


def turnOnSettingsResponse(userSession):
    """Function resulting in the enabling of a setting such as Events."""
    enabled = True
    return toggleSettingsResponse(userSession, enabled)
