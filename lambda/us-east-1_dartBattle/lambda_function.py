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
from ask_sdk_model.interfaces import audioplayer
from ask_sdk_model.interfaces.audioplayer.audio_player_state import AudioPlayerState
from ask_sdk_model.ui import SimpleCard, StandardCard
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model.slu.entityresolution import StatusCode

from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState, InSkillProductsResponse)


from ask_sdk_model import (
    Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
from ask_sdk_model.dialog import (
    ElicitSlotDirective, DelegateDirective)

from ask_sdk_model.intent_request import IntentRequest


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


# =============================================================================
# MAIN HANDLER
# =============================================================================
#@sb.request_handler(can_handle_func=is_intent_name("TurnOffSettingIntent"))
def test_handler(handler_input):
    # type: (HandlerInput) -> Response
    speech_text = "Welcome to the Alexa Skills Kit, you can say hello!"
    print("dialog_state = {}".format(IntentRequest().dialog_state))

    handler_input.response_builder.speak(speech_text).set_card(
        SimpleCard("Hello World", speech_text)).set_should_end_session(
        False)
    return handler_input.response_builder.response


class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Raises:
            ValueError: If something other than the sanctioned app calls this intent.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        # Prevent someone else from configuring a skill that sends requests to this:
        if handler_input.request_envelope.session.application.application_id != \
                "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28":
            raise ValueError("Invalid Application ID")

        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = responses.getWelcomeResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


"""
        elif event['request']['type'] == "AudioPlayer.PlaybackNearlyFinished":
            return on_playback_nearly_finished(event)
"""


# =============================================================================
# HANDLERS
# =============================================================================
class BattleDurationStartHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("StartBattleDurationIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, cardTitle, cardText, cardImage, directive = battle.startBattleDurationIntent(userSession)
        card = StandardCard(title=cardTitle, text=cardText, image=cardImage)
        handler_input.response_builder.speak(speech).set_card(card).add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class BattleStandardStartHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("StartBattleStandardIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, cardTitle, cardText, cardImage, directive = battle.startBattleStandardIntent(userSession)
        card = StandardCard(title=cardTitle, text=cardText, image=cardImage)
        handler_input.response_builder.speak(speech).set_card(card).add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return not (not is_intent_name("AMAZON.CancelIntent")(handler_input) and not is_intent_name(
            "AMAZON.StopIntent")(handler_input) and not is_intent_name("AMAZON.PauseIntent")(handler_input))

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        response = playback_stop(handler_input)
        return response


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        response = playback_stop(handler_input)
        return response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("AMAZON.HelpIntent")(handler_input) or is_intent_name("MoreOptionsIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = responses.getOptionsResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class HowToPlayHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("HowToPlayIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        speech, reprompt, cardTitle, cardText, cardImage, directive = responses.howToPlayResponse()
        card = StandardCard(title=cardTitle, text=cardText, image=cardImage)
        handler_input.response_builder.speak(speech).set_card(card).add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class RankQueryHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("RankQueryIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = rank.getRankResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TeamClearHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("ClearTeamsIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = teams.clearTeamsIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TeamSetupInProgressHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("SetupTeamsIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        current_intent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=current_intent
            )).response


class TeamSetupHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("SetupTeamsIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = teams.setupTeamsIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TeamShuffleHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("ShuffleTeamsIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = teams.shuffleTeamsIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        # FIXME: Response is wrong after cleared teams
        return handler_input.response_builder.response


class ToggleProtocolInProgressHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("EnableProtocolIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        current_intent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=current_intent
            )).response


class ToggleProtocolHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("EnableProtocolIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = protocols.toggleProtocol(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TurnOffSettingHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("TurnOffSettingIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = responses.turnOffSettingsResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TurnOnSettingHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("TurnOnSettingIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = responses.turnOnSettingsResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class VictoriesClearInProgressHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("ClearVictoryIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        current_intent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=current_intent
            )).response


class VictoriesClearHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("ClearVictoryIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = victories.clearVictoryIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class VictoriesReciteHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("ReciteVictoriesIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = victories.reciteVictoriesIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class VictoriesRecordInProgressHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("RecordVictoryIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        current_intent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=current_intent
            )).response


class VictoriesRecordHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("RecordVictoryIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = victories.recordVictoryIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
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


# =============================================================================
# FUNCTIONS
# =============================================================================
def playback_stop(handler_input):
    print("Session Attrs: {}".format(handler_input.attributes_manager.session_attributes))
    print("Audio: {}".format(AudioPlayerState().to_dict()))
    userSession = session.DartBattleSession(handler_input)

    speeches = [
        "Standing down.",
        "Of course.",
        "Canceling."
    ]
    speech = random.choice(speeches)

    if AudioPlayerState().player_activity:
        userSession.setAudioState(AudioPlayerState().token, AudioPlayerState().offsetInMilliseconds)

    responseBuilder = handler_input.response_builder
    responseBuilder.speak(speech).ask(speech)
    directive = audioplayer.StopDirective()
    responseBuilder.add_directive(directive)
    responseBuilder.set_should_end_session(True)

    return handler_input.response_builder.response


sb.add_request_handler(BattleDurationStartHandler())
sb.add_request_handler(BattleStandardStartHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(HowToPlayHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(RankQueryHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(TeamClearHandler())
sb.add_request_handler(TeamSetupInProgressHandler())
sb.add_request_handler(TeamSetupHandler())
sb.add_request_handler(TeamShuffleHandler())
sb.add_request_handler(TurnOffSettingHandler())
sb.add_request_handler(TurnOnSettingHandler())
sb.add_request_handler(ToggleProtocolInProgressHandler())
sb.add_request_handler(ToggleProtocolHandler())
sb.add_request_handler(VictoriesClearInProgressHandler())
sb.add_request_handler(VictoriesClearHandler())
sb.add_request_handler(VictoriesReciteHandler())
sb.add_request_handler(VictoriesRecordInProgressHandler())
sb.add_request_handler(VictoriesRecordHandler())
handler = sb.lambda_handler()

# {'version': '1.0', 'session': {'new': True, 'session_id': 'amzn1.echo-api.session.103a01a9-09b2-4223-a97c-d54c298efc82', 'user': {'user_id': 'amzn1.ask.account.AHQ53A7TTH5ELGE4FJB6RLVARNQ6DCN6EMDSUXCL5VDY4SDYTJGIC2A5EGNQMZNGF2HCOQJ242OVAEEZFQOIE3I246UXWKZGEOTXAVZWNVPJOCOHKSGFOKYG2KYWZI7CIPIEK2IHSGMANP3HX36MPPZKIS4A7KVEFRXLZNFXXOAFARCXOL3IIFBRUT5C67KDO27HH7HCF24IG7I', 'access_token': None, 'permissions': None}, 'attributes': None, 'application': {'application_id': 'amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28'}}, 'context': {'system': {'application': {'application_id': 'amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28'}, 'user': {'user_id': 'amzn1.ask.account.AHQ53A7TTH5ELGE4FJB6RLVARNQ6DCN6EMDSUXCL5VDY4SDYTJGIC2A5EGNQMZNGF2HCOQJ242OVAEEZFQOIE3I246UXWKZGEOTXAVZWNVPJOCOHKSGFOKYG2KYWZI7CIPIEK2IHSGMANP3HX36MPPZKIS4A7KVEFRXLZNFXXOAFARCXOL3IIFBRUT5C67KDO27HH7HCF24IG7I', 'access_token': None, 'permissions': None}, 'device': {'device_id': 'amzn1.ask.device.AES4DYXDO3B5ZTCVMKGUESOVSANNWHO3V7N3DP2RWW4LXYSCB3DIY6HR524ZVFNOOKQJAKGCCSR5YURCYK4UCQVX6KVB6WMV4VYEE23ND3MFK7IQWOD724XDPA7I6PBUZCXTQ4GKV4FFUFQSD3G4VORXTHXQ', 'supported_interfaces': {'audio_player': {}, 'display': None, 'video_app': None}}, 'api_endpoint': 'https://api.amazonalexa.com', 'api_access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxMzExMTg0LTBmNTctNDZlOC1hYjU5LTg3OTAyNzEzMGEyOCIsImV4cCI6MTUzNzUwOTQ3OSwiaWF0IjoxNTM3NTA1ODc5LCJuYmYiOjE1Mzc1MDU4NzksInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUVTNERZWERPM0I1WlRDVk1LR1VFU09WU0FOTldITzNWN04zRFAyUldXNExYWVNDQjNESVk2SFI1MjRaVkZOT09LUUpBS0dDQ1NSNVlVUkNZSzRVQ1FWWDZLVkI2V01WNFZZRUUyM05EM01GSzdJUVdPRDcyNFhEUEE3STZQQlVaQ1hUUTRHS1Y0RkZVRlFTRDNHNFZPUlhUSFhRIiwidXNlcklkIjoiYW16bjEuYXNrLmFjY291bnQuQUhRNTNBN1RUSDVFTEdFNEZKQjZSTFZBUk5RNkRDTjZFTURTVVhDTDVWRFk0U0RZVEpHSUMyQTVFR05RTVpOR0YySENPUUoyNDJPVkFFRVpGUU9JRTNJMjQ2VVhXS1pHRU9UWEFWWldOVlBKT0NPSEtTR0ZPS1lHMktZV1pJN0NJUElFSzJJSFNHTUFOUDNIWDM2TVBQWktJUzRBN0tWRUZSWExaTkZYWE9BRkFSQ1hPTDNJSUZCUlVUNUM2N0tETzI3SEg3SENGMjRJRzdJIn19.G16Z8BEynj3TX9TEILQL-rGjCClSQZR2oW59iJB0ClR2d5fvrtHSWpjYny9xVdx36PvgQIoL_jlUgHlClNciKAwomsBg8YvH4yTBSTGfvxZohsr4Feui-oY7I79-vd3WT1H0tg-HOcmnXjv_k_PfGzdrYE49ZIhJqMRNy0epTKMo9edTmhWweMB2PldmNMC27BJg2jXaxsp2HxBVig3gY-SsYsUI7QqxfQsN9GhYxFxEu7Cvdv3r4685LPIpAsqDpuDRCi_TL47hA9HLjdjX5qpyN3lt2cfpj8D22wQXUlTt_9JCubDPGADdcB-ByvMzLgcLoDthKtNdvxoX4v5ddw'}, 'audio_player': {'offset_in_milliseconds': None, 'token': None, 'player_activity': 'IDLE'}, 'display': None}, 'request': {'object_type': 'LaunchRequest', 'request_id': 'amzn1.echo-api.request.c75e2ea9-a482-4bfa-9d62-14dad9ca87ef', 'timestamp': datetime.datetime(2018, 9, 21, 4, 57, 59, tzinfo=tzlocal()), 'locale': 'en-US'}}
