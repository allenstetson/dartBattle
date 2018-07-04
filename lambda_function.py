"""
Dart Battle

"""
import random

import responses
import battle
import database
import teams
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# =============================================================================
# MAIN HANDLER
# =============================================================================

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    #Prevent someone else from configuring a skill that sends requests to this:
    if 'session' in event:
        if (event['session']['application']['applicationId'] !=
                 "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28"):
             raise ValueError("Invalid Application ID")

        if event['session']['new']:
            on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if 'request' in event:
        if event['request']['type'] == "LaunchRequest":
            return on_launch(event['request'], event['session'])
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

    intent_request = event['request']
    session = event['session']
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    # BATTLE
    if intent_name == "StartBattleStandardIntent":
        return battle.startBattleStandardIntent(intent, session)
    elif intent_name == "StartBattleDurationIntent":
        return battle.startBattleDurationIntent(intent, session)

    # OPTIONS/HELP
    elif intent_name == "MoreOptionsIntent":
        return responses.getOptionsResponse(session)
    elif intent_name == "TurnOffSettingIntent":
        return responses.turnOffSettingsResponse(event)
    elif intent_name == "TurnOnSettingIntent":
        return responses.turnOnSettingsResponse(event)

    # PROTOCOLS
    elif intent_name == "EnableProtocolIntent":
        return responses.enableProtocol(event)

    # RANKS
    elif intent_name == "RankQueryIntent":
        return responses.getRankResponse(session)

    # RULES
    elif intent_name == "HowToPlayIntent":
        return responses.howToPlayResponse(session)

    # TEAMS
    elif intent_name == "SetupTeamsIntent":
        return teams.setupTeamsIntent(intent_request, session)
    elif intent_name == "ReciteTeamsIntent":
        return teams.reciteTeamsIntent(intent_request, session)
    elif intent_name == "ClearTeamsIntent":
        return teams.clearTeamsIntent(intent_request, session)
    elif intent_name == "ShuffleTeamsIntent":
        return teams.shuffleTeamsIntent(intent, session)

    # VICTORIES
    elif intent_name == "ClearVictoryIntent":
        return teams.clearVictoryIntent(intent_request, session)
    elif intent_name == "RecordVictoryIntent":
        return teams.recordVictoryIntent(intent_request, session)
    elif intent_name == "ReciteVictoriesIntent":
        return teams.reciteVictoriesIntent(intent_request, session)

    # STANDARD
    elif intent_name == "AMAZON.HelpIntent":
        return responses.getOptionsResponse(session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return on_session_end_request(event)

    # AUDIO
    elif intent_name == "AMAZON.ResumeIntent":
        return on_playback_resume(session)
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
        logger.info("NextIntent received: {} -- session: {}".format(intent_request, session))
        return battle.skipToNextAudioPlayback(session)
    elif intent_name == "AMAZON.PreviousIntent":
        return battle.reverseAudioPlayback(session)
    elif intent_name == "AMAZON.StartOverIntent":
        return battle.restartAudioPlayback(session)
    # --
    else:
        raise ValueError("Invalid intent: {}".format(intent_name))


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    logger.info('received on_launch call')
    #return responses.getTestResponse(session)
    return responses.getWelcomeResponse(session)


def on_playback_nearly_finished(event):
    print("Playback Nearly Finished. Event: {}".format(event))
    prevToken = event['request']['token']
    return battle.continueAudioPlayback(event, prevToken)


def on_playback_resume(session):
    sessionAttributes = database.GetSessionFromDB(session)
    token = sessionAttributes.get('currentToken')
    offsetInMilliseconds = sessionAttributes.get('offsetInMilliseconds', "0")
    playlist = battle.ScenePlaylist('arctic', sessionAttributes)
    track = playlist.getTrackFromToken(token)
    output =  {
        "version": responses.VERSION,
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
    session = event['session']
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


def on_session_started(session_started_request, session):
    """ Called when the session starts """
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_session_end_request(event):
    return playback_stop(event)


# =============================================================================
# FUNCTIONS
# =============================================================================
def playback_stop(event):
    sessionAttributes = database.GetSessionFromDB(event['session'])
    speeches = [
        "Standing down.",
        "Of course.",
        "Canceling."
    ]
    speech = random.choice(speeches)

    if not 'AudioPlayer' in event['context'] or not 'token' in event['context']['AudioPlayer']:
        # No audio currently playing.
        return {
            "version": responses.VERSION,
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
    database.UpdateRecordToken(sessionAttributes)
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
