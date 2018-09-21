"""
Dart Battle

"""
# Std Lib imports:
import logging
import os
import random

# Amazon imports
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState, InSkillProductsResponse)

sb = SkillBuilder()

# DartBattle imports:
import battle
import database
import protocols
import rank
import responses
import session
import teams
import victories

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class AlexaDataIntermediate(dict):
    """Makes new data look like old data for now, so that I don't have to rewrite everything."""
    def __init__(self, handler_input):
        super(AlexaDataIntermediate, self).__init__()
        handlerDict = handler_input.request_envelope.to_dict()
        for keyname in handlerDict.keys():
            self[keyname] = handlerDict[keyname]
        self['session']['sessionId'] = self['session']['session_id']
        self['session']['context'] = handlerDict['context']
        self['session']['context']['System'] = self['session']['context']['system']
        self['session']['context']['System']['user']['userId'] = self['session']['context']['system']['user']['user_id']
        self['session']['user']['userId'] = self['session']['context']['system']['user']['user_id']
        self['session']['attributes'] = {}

# =============================================================================
# MAIN HANDLER
# =============================================================================
@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    # Prevent someone else from configuring a skill that sends requests to this:
    if handler_input.request_envelope.session.application.application_id != \
                 "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28":
            raise ValueError("Invalid Application ID")

    alexaDataIntermediate = AlexaDataIntermediate(handler_input)
    event = handler_input.request_envelope
    if event.session.new:
        on_session_started({'requestId': event.request.request_id},
                           alexaDataIntermediate['session'])

    speech = on_launch(alexaDataIntermediate)
    handler_input.response_builder.speak(speech).set_card(
         SimpleCard("Hello World", "round butt")).set_should_end_session(
         False)
    return handler_input.response_builder.response

"""
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
"""

# =============================================================================
# HANDLERS
# =============================================================================
"""
@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech = "<audio src=\"https://s3.amazonaws.com/dart-battle-resources/choiceMusic.mp3\" /> "
    speech += "Welcome to the Alexa Skills Kit, you can say hello!"
    #print(handler_input.attributes_manager.session_attributes)
    #print(handler_input.attributes_manager.request_attributes)
    #print(handler_input.context)
    #print(handler_input.request_envelope)
    #print(handler_input.request_envelope.session)
    #print(handler_input.request_envelope.to_dict())
    print(handler_input.request_envelope.session.application..application_id)

    handler_input.response_builder.speak(speech).set_card(
         SimpleCard("Hello World", "round butt")).set_should_end_session(
         False)
    return handler_input.response_builder.response
"""

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "You can say hello to me!"

    handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
        SimpleCard("Hello World", speech_text))
    return handler_input.response_builder.response

@sb.request_handler(
    can_handle_func=lambda handler_input :
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Goodbye!"

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text))
    return handler_input.response_builder.response

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
        return battle.startBattleStandardIntent(sessionInfo)
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
        return protocols.enableProtocol(event)

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
#    elif intent_name == "AMAZON.HelpIntent":
#        return responses.getOptionsResponse(sessionInfo)
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
    session = database.getSessionFromDB(sessionInfo)
    sessionAttributes = session["attributes"]

    token = sessionAttributes.get('currentToken')
    offsetInMilliseconds = sessionAttributes.get('offsetInMilliseconds', "0")
    sessionInfo = token.split("_")[1]
    (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
    scenarioName = battle.Scenarios(int(scenarioEnum)).name

    playlist = battle.Scenario(sessionAttributes, name=scenarioName)
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
          + ", sessionId=" + sessionInfo['session_id'])


def on_session_end_request(event):
    return playback_stop(event)


# =============================================================================
# FUNCTIONS
# =============================================================================
def playback_stop(event):
    session = database.getSessionFromDB(event['session'])
    sessionAttributes = session["attributes"]

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


handler = sb.lambda_handler()

#{'version': '1.0', 'session': {'new': True, 'session_id': 'amzn1.echo-api.session.103a01a9-09b2-4223-a97c-d54c298efc82', 'user': {'user_id': 'amzn1.ask.account.AHQ53A7TTH5ELGE4FJB6RLVARNQ6DCN6EMDSUXCL5VDY4SDYTJGIC2A5EGNQMZNGF2HCOQJ242OVAEEZFQOIE3I246UXWKZGEOTXAVZWNVPJOCOHKSGFOKYG2KYWZI7CIPIEK2IHSGMANP3HX36MPPZKIS4A7KVEFRXLZNFXXOAFARCXOL3IIFBRUT5C67KDO27HH7HCF24IG7I', 'access_token': None, 'permissions': None}, 'attributes': None, 'application': {'application_id': 'amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28'}}, 'context': {'system': {'application': {'application_id': 'amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28'}, 'user': {'user_id': 'amzn1.ask.account.AHQ53A7TTH5ELGE4FJB6RLVARNQ6DCN6EMDSUXCL5VDY4SDYTJGIC2A5EGNQMZNGF2HCOQJ242OVAEEZFQOIE3I246UXWKZGEOTXAVZWNVPJOCOHKSGFOKYG2KYWZI7CIPIEK2IHSGMANP3HX36MPPZKIS4A7KVEFRXLZNFXXOAFARCXOL3IIFBRUT5C67KDO27HH7HCF24IG7I', 'access_token': None, 'permissions': None}, 'device': {'device_id': 'amzn1.ask.device.AES4DYXDO3B5ZTCVMKGUESOVSANNWHO3V7N3DP2RWW4LXYSCB3DIY6HR524ZVFNOOKQJAKGCCSR5YURCYK4UCQVX6KVB6WMV4VYEE23ND3MFK7IQWOD724XDPA7I6PBUZCXTQ4GKV4FFUFQSD3G4VORXTHXQ', 'supported_interfaces': {'audio_player': {}, 'display': None, 'video_app': None}}, 'api_endpoint': 'https://api.amazonalexa.com', 'api_access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxMzExMTg0LTBmNTctNDZlOC1hYjU5LTg3OTAyNzEzMGEyOCIsImV4cCI6MTUzNzUwOTQ3OSwiaWF0IjoxNTM3NTA1ODc5LCJuYmYiOjE1Mzc1MDU4NzksInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUVTNERZWERPM0I1WlRDVk1LR1VFU09WU0FOTldITzNWN04zRFAyUldXNExYWVNDQjNESVk2SFI1MjRaVkZOT09LUUpBS0dDQ1NSNVlVUkNZSzRVQ1FWWDZLVkI2V01WNFZZRUUyM05EM01GSzdJUVdPRDcyNFhEUEE3STZQQlVaQ1hUUTRHS1Y0RkZVRlFTRDNHNFZPUlhUSFhRIiwidXNlcklkIjoiYW16bjEuYXNrLmFjY291bnQuQUhRNTNBN1RUSDVFTEdFNEZKQjZSTFZBUk5RNkRDTjZFTURTVVhDTDVWRFk0U0RZVEpHSUMyQTVFR05RTVpOR0YySENPUUoyNDJPVkFFRVpGUU9JRTNJMjQ2VVhXS1pHRU9UWEFWWldOVlBKT0NPSEtTR0ZPS1lHMktZV1pJN0NJUElFSzJJSFNHTUFOUDNIWDM2TVBQWktJUzRBN0tWRUZSWExaTkZYWE9BRkFSQ1hPTDNJSUZCUlVUNUM2N0tETzI3SEg3SENGMjRJRzdJIn19.G16Z8BEynj3TX9TEILQL-rGjCClSQZR2oW59iJB0ClR2d5fvrtHSWpjYny9xVdx36PvgQIoL_jlUgHlClNciKAwomsBg8YvH4yTBSTGfvxZohsr4Feui-oY7I79-vd3WT1H0tg-HOcmnXjv_k_PfGzdrYE49ZIhJqMRNy0epTKMo9edTmhWweMB2PldmNMC27BJg2jXaxsp2HxBVig3gY-SsYsUI7QqxfQsN9GhYxFxEu7Cvdv3r4685LPIpAsqDpuDRCi_TL47hA9HLjdjX5qpyN3lt2cfpj8D22wQXUlTt_9JCubDPGADdcB-ByvMzLgcLoDthKtNdvxoX4v5ddw'}, 'audio_player': {'offset_in_milliseconds': None, 'token': None, 'player_activity': 'IDLE'}, 'display': None}, 'request': {'object_type': 'LaunchRequest', 'request_id': 'amzn1.echo-api.request.c75e2ea9-a482-4bfa-9d62-14dad9ca87ef', 'timestamp': datetime.datetime(2018, 9, 21, 4, 57, 59, tzinfo=tzlocal()), 'locale': 'en-US'}}