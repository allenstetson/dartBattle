"""
Dart Battle

"""
# Std Lib imports:
import logging
import os
import random

# DartBattle imports:
import battle
import database
import rank
import responses
import session
import teams
import victories

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# =============================================================================
# MAIN HANDLER
# =============================================================================
def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    # Prevent someone else from configuring a skill that sends requests to this:
    if 'session' in event:
        if (event['session']['application']['applicationId'] !=
                 "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"):
            raise ValueError("Invalid Application ID")

        if event['session']['new']:
            on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if 'request' in event:
        if event['request']['type'] == "LaunchRequest":
            return on_launch(event)
        elif event['request']['type'] == "IntentRequest":
            if event['request']['intent']['name'] in ["AMAZON.PauseIntent", "AMAZON.StopIntent"]:
                return playback_stop(event)
            return on_intent(event)
        elif event['request']['type'] == "SessionEndedRequest":
            return on_session_ended(event)
        elif event['request']['type'] == "AudioPlayer.PlaybackNearlyFinished":
            return on_playback_nearly_finished(event)


# =============================================================================
# HANDLERS
# =============================================================================
def on_intent(event):
    """ Called when the user specifies an intent for this skill """

    intent_request = event["request"]
    sessionInfo = session.DartBattleSession(event["session"])
    event["session"] = sessionInfo
    print("on_intent requestId=" + intent_request["requestId"] +
          ", sessionId=" + sessionInfo["sessionId"])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    # BATTLE
    if intent_name == "StartBattleStandardIntent":
        return battle.startBattleStandardIntent(intent, sessionInfo)
    elif intent_name == "StartBattleDurationIntent":
        return battle.startBattleDurationIntent(intent, sessionInfo)

    # OPTIONS/HELP
    elif intent_name == "MoreOptionsIntent":
        return responses.getOptionsResponse(sessionInfo)
    elif intent_name == "TurnOffSettingIntent":
        return responses.turnOffSettingsResponse(event)
    elif intent_name == "TurnOnSettingIntent":
        return responses.turnOnSettingsResponse(event)

    # PROTOCOLS
    elif intent_name == "EnableProtocolIntent":
        return responses.enableProtocol(event)

    # RANKS
    elif intent_name == "RankQueryIntent":
        return rank.getRankResponse(sessionInfo)

    # RULES
    elif intent_name == "HowToPlayIntent":
        return responses.howToPlayResponse()

    # TEAMS
    elif intent_name == "SetupTeamsIntent":
        return teams.setupTeamsIntent(intent_request, sessionInfo)
    elif intent_name == "ReciteTeamsIntent":
        return teams.reciteTeamsIntent(sessionInfo)
    elif intent_name == "ClearTeamsIntent":
        return teams.clearTeamsIntent(sessionInfo)
    elif intent_name == "ShuffleTeamsIntent":
        return teams.shuffleTeamsIntent(sessionInfo)

    # VICTORIES
    elif intent_name == "ClearVictoryIntent":
        return victories.clearVictoryIntent(intent_request, sessionInfo)
    elif intent_name == "RecordVictoryIntent":
        return victories.recordVictoryIntent(intent_request, sessionInfo)
    elif intent_name == "ReciteVictoriesIntent":
        return victories.reciteVictoriesIntent(sessionInfo)

    # STANDARD
    elif intent_name == "AMAZON.HelpIntent":
        return responses.getOptionsResponse(sessionInfo)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return on_session_end_request(event)

    # AUDIO
    elif intent_name == "AMAZON.ResumeIntent":
        return on_playback_resume(sessionInfo)
    elif intent_name in [
        "AMAZON.LoopOffIntent",
        "AMAZON.LoopOnIntent",
        "AMAZON.RepeatIntent",
        "AMAZON.ShuffleOffIntent",
        "AMAZON.ShuffleOnIntent"
        ]:
        return {
            'version': '1.0',
            'response': {
                'directives': [
                ]
            }
        }
    elif intent_name == "AMAZON.NextIntent":
        logger.info("NextIntent received: {} -- session: {}".format(intent_request, sessionInfo))
        return battle.skipToNextAudioPlayback(sessionInfo)
    elif intent_name == "AMAZON.PreviousIntent":
        return battle.reverseAudioPlayback(sessionInfo)
    elif intent_name == "AMAZON.StartOverIntent":
        return battle.restartAudioPlayback(sessionInfo)
    # --
    else:
        raise ValueError("Invalid intent: {}".format(intent_name))


def on_launch(event):
    """ Called when the user launches the skill without specifying what they
    want
    """
    sessionInfo = session.DartBattleSession(event['session'])
    logger.info('received on_launch call')
    # return responses.getTestResponse(sessionInfo)
    return responses.getWelcomeResponse(sessionInfo)


def on_playback_nearly_finished(event):
    print("Playback Nearly Finished. Event: {}".format(event))
    prevToken = event['request']['token']
    return battle.continueAudioPlayback(event, prevToken)


def on_playback_resume(sessionInfo):
    sessionAttributes = database.getSessionFromDB(sessionInfo)
    token = sessionAttributes.get('currentToken')
    offsetInMilliseconds = sessionAttributes.get('offsetInMilliseconds', "0")
    playlist = battle.ScenePlaylist('arctic', sessionAttributes)
    track = playlist.getTrackFromToken(token)
    output = {
        "version": os.environ['VERSION'],
        "sessionAttributes": sessionAttributes,
        "response": {
            "directives": [
                {
                    "type": "AudioPlayer.Play",
                    "playBehavior": "REPLACE_ALL",
                    "audioItem": {
                        "stream": {
                            "token": token,
                            "url": track,
                            "offsetInMilliseconds": int(offsetInMilliseconds)
                        }
                    }
                }
            ],
            "shouldEndSession": True
        }
    }
    logger.info("startBattle intent finished. Returning: {}".format(output))
    return output


def on_session_ended(event):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    session_ended_request = event['request']
    sessionInfo = event['session']
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + sessionInfo['sessionId'])
    # add cleanup logic here


def on_session_started(session_started_request, sessionInfo):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + sessionInfo['sessionId'])


def on_session_end_request(event):
    return playback_stop(event)


# =============================================================================
# FUNCTIONS
# =============================================================================
def playback_stop(event):
    sessionAttributes = database.getSessionFromDB(event['session'])
    speeches = [
        "Standing down.",
        "Of course.",
        "Canceling."
    ]
    speech = random.choice(speeches)

    if not 'AudioPlayer' in event['context'] or not 'token' in event['context']['AudioPlayer']:
        # No audio currently playing.
        return {
            "version": os.environ['VERSION'],
            "response": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": "<speak>" + speech + "</speak>"
                },
            },
            "shouldEndSession": True
        }
    sessionAttributes['currentToken'] = event['context']['AudioPlayer']['token']
    sessionAttributes['offsetInMilliseconds'] = event['context']['AudioPlayer']['offsetInMilliseconds']
    database.updateRecordToken(sessionAttributes)
    return {
        'version': '1.0',
        'response': {
            'directives': [
                {
                    'type': 'AudioPlayer.Stop'
                }
            ]
        }
    }
