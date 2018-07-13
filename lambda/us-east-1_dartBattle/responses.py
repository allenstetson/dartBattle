"""
responses.py
Contains the responses to intents.

"""
# Std Lib imports:
import os
import logging
import random

# DartBattle imports:
import database
import playlists
import rank
import teams

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# =============================================================================
# GENERIC RESPONSES
# =============================================================================
def continueDialog(sessionAttributes):
    message = dict()
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate'}]
    return {
        'version': os.environ['VERSION'],
        'sessionAttributes': sessionAttributes,
        'response': message
    }


def getTestResponse(session):
    speech = "Perimeter compromised. Defenses will be breached in 5, 4, 3, 2, 1. "
    speech = '<audio src="https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/pairUp/event_Arctic_09_PairUp_Yeti_Any_00.mp3" /> '

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
    sessionAttributes = session['attributes']

    if 'playerRank' in sessionAttributes:
        playerRank = sessionAttributes['playerRank']
        if playerRank == '00':
            playerRankName = "soldier"
        else:
            playerRankName = teams.PlayerRanks(int(playerRank)).name.replace("_", " ")
    else:
        playerRankName = "soldier"

    speech = "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "
    speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/comsatTellWhatYouCanDo_01.mp3\" /> "
    speech += "Of course Commander. {}, this comsat unit supports the following commands: ".format(playerRankName)
    speech += "for teams, you can say setup teams, tell me the teams, shuffle teams, "
    speech += "clear the teams. For battles, you can say start a battle, start a 7 minute battle, "
    speech += "or other duration besides 7. For rank, say what is my rank. "
    speech += "For victories, you can say record a victory, "
    speech += "tell me the victories, clear all victories, clear victories for someone's name. "
    speech += "To understand the rules of the game, you can say how do I play. "
    speech += "Finally, you can say more options to hear this again. "
    speech += "What would you like me to do next? "

    text = "__TEAMS:__\n"
    text += "Setup teams, Tell me the teams, Shuffle teams.\n"
    text += "__BATTLES:__\n"
    text += "Start a battle, Start a _ minute battle.\n"
    text += "__RANK:__\n"
    text += "What is my rank?\n"
    text += "__VICTORIES:__\n"
    text += "Record a victory, Tell me the victories,\n"
    text += "Clear all victories, Clear victories for _.\n"
    text += "__OTHER:__\n"
    text += "How do I play?, More Options."

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
                "title": "Options",
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_MO_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_MO_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def getWelcomeResponse(session):
    sessionAttributes = session['attributes']

    # __FORMAT:__
    # Music
    # Welcome to/back
    # I see you've just joined...
    # You've been promoted to...
    # You can say / Would you like to

    (isNewRank, rankNum) = rank.checkForPromotion(sessionAttributes)

    # -------------------------------------------------------------------------
    # Determine welcome
    # -------------------------------------------------------------------------
    if sessionAttributes['recentSession'] == "True":
        title = "Welcome Back"
        # TODO: "I'm here for you, troops/soldier.", "Resuming Dart Battle, protocol Igloo/Tango", "Welcome back.", "On alert.", "Monitoring enemy activity."
        if sessionAttributes['usingTeams'] == "True":
            tracks = [
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickA_Team_00.mp3",
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickB_Team_00.mp3",
                "rank"
            ]
            welcomeTracks = [random.choice(tracks)]
        else:
            tracks = [
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickA_NoTeam_00.mp3",
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickB_NoTeam_00.mp3",
                "rank"
            ]
            welcomeTracks = [random.choice(tracks)]
    else:
        title = "Welcome, Soldier"
        # TODO: "Dart Battle mission instantiated.", "Attention! Codename Dart Battle ready for orders.", "Dart Battle Protocol ready for commands."
        if sessionAttributes['usingTeams'] == "True":
            tracks = [
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_StandardA_Team_00.mp3",
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_StandardB_Team_00.mp3",
                "rank"
            ]
            welcomeTracks = [random.choice(tracks)]
        else:
            tracks = [
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_StandardA_NoTeam_00.mp3",
                "rank"
            ]
            welcomeTracks = [random.choice(tracks)]
    if welcomeTracks[0] == "rank":
        officerIntro = random.randint(0, 2)
        welcomeTrack = "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_{:02d}_Greeting_WelcomeBackA_Any_00.mp3"
        if isNewRank:
            welcomeTracks = [welcomeTrack.format(int(rankNum)-1)]
        else:
            welcomeTracks = [welcomeTrack.format(int(rankNum))]
        if officerIntro == 2 and int(rankNum) > 5:
            attn = "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_AttnOfficerA_Any_00.mp3"
            welcomeTrack = welcomeTracks[0]
            atEase = "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_AtEaseA_Any_00.mp3"
            welcomeTracks = [attn, welcomeTrack, atEase]

    welcome = ""
    for track in welcomeTracks:
        track = '<audio src="{}" /> '.format(track)
        welcome += track
    print("WELCOME: {}".format(welcome))

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
        promotionFile = playlists.GetRankPromotionFile(rankNum)
        logger.info("Received a promotion track to play: {}".format(promotionFile))
        promotion += "<audio src=\"{}\" />".format(promotionFile)
        sessionAttributes['playerRank'] = rankNum
        title = "Congratulations!"
        playerRankName = teams.PlayerRanks(int(rankNum)).name.replace("_", " ")
        text = "You are hereby promoted to {}.".format(playerRankName.title())
        imgName = "victory"

    # -------------------------------------------------------------------------
    # Handle new recruit
    # -------------------------------------------------------------------------
    justJoined = ""
    if sessionAttributes['playerRank'] == "00" and sessionAttributes['recentSession'] == "False":
        justJoined = '<audio src="https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_JustJoinedA_Any_00.mp3" />'

    # -------------------------------------------------------------------------
    # Handle 'you can' intro, options
    # -------------------------------------------------------------------------
    if sessionAttributes['recentSession'] == "True":
        if sessionAttributes['usingTeams'] == "True":
            tracks = [
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_OptionsQuickA_Team_00.mp3"
            ]
        else:
            tracks = [
                "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_OptionsQuickA_NoTeam_00.mp3"
            ]
    else:
        tracks = []
    tracks.append("https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_OptionsA_Any_00.mp3")
    tracks.append("https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_OptionsB_Any_00.mp3")
    youCan = random.choice(tracks)
    youCan = "<audio src=\"{}\" />".format(youCan)

    # -------------------------------------------------------------------------

    speech = welcome + justJoined + promotion + youCan
    print("SPEECH: {}".format(speech))

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    repromptText = "Try saying: Start Battle, Setup Teams, or More Options."
    return {
        'version': os.environ['VERSION'],
        'sessionAttributes': sessionAttributes,
        'response': {
            "directive": {
                "header": {
                    "namespace": "AudioPlayer",
                    "name": "ClearQueue",
                    "messageId": "{{STRING}}",
                    "dialogRequestId": "{{STRING}}"
                },
                "payload": {
                    "clearBehavior": "{{STRING}}"
                }
            },
            "outputSpeech": {
                "type": "SSML",
                "ssml": "<speak>"
                        "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/introMusic.mp3\" />" +
                        speech +
                        "</speak>"
                    },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': repromptText
                }
            },
            "card": {
                "type": "Standard",
                "title": title,
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_{}_720x480.jpg".format(imgName),
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_{}_1200x800.jpg".format(imgName)
                }
            },
            'shouldEndSession': False
        }
    }


def howToPlayResponse():
    text = "- Use foam-based weaponry, score eliminations.\n"
    text += "- No head shots or point blank shots.\n"
    text += "- Listen for special events!\n"
    text += "- When eliminated, wait 5 seconds to rejoin.\n"
    text += "- Be honest!\n"
    text += "- Wear eye protection.\n"
    text += "- Settle disputes in a friendly manner.\n"
    text += " - HAVE FUN"
    response = {
        "version": os.environ['VERSION'],
        "response": {
            "card": {
                "type": "Standard",
                "title": "How to Play",
                "text": text,
                "image": {
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_1200x800.jpg"
                }
            },
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "REPLACE_ALL",
                    "audioItem": {
                        "stream": {
                            "token": "howToPlay_track01",
                            "url": "https://s3.amazonaws.com/dart-battle-resources/howDoIPlay.mp3",
                            "offsetInMilliseconds": 0
                        }
                    }
                }
            ]
        }
    }
    return response


def toggleSettingsResponse(event, enabled):
    request = event["request"]
    session = event["session"]
    sessionAttributes = session["attributes"]

    dialogState = request['dialogState']
    if dialogState in ["STARTED", "IN_PROGRESS"]:
        return continueDialog(sessionAttributes)
    elif dialogState == 'COMPLETED':
        # sessionAttributes = session.get('attributes', database.getDefaultSessionAttrs(session['user']['userId']))
        pass
    attrName = request['intent']['slots']['ATTRNAME']['value']

    speech = ""
    if attrName.lower() == "events":
        speech += "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "
        if enabled:
            speech += "Events enabled. "
        else:
            speech += "Events disabled. Your battles will have no events until re-enabled. "
        success = database.updateToggleEvents(sessionAttributes, enabled)
        if success:
            if enabled:
                sessionAttributes['usingEvents'] = "True"
            else:
                sessionAttributes['usingEvents'] = "False"
        title = "Disable Events."
        text = "Events are disabled."
    else:
        speech += "I'd like to comply, but I don't recognize {}. ".format(attrName)
        title = "Did you say {}?".format(attrName)
        text = "Did Not Compute"
    speech += "What next? "

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
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_HTP_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


def turnOffSettingsResponse(event):
    enabled = False
    return toggleSettingsResponse(event, enabled)


def turnOnSettingsResponse(event):
    enabled = True
    return toggleSettingsResponse(event, enabled)
