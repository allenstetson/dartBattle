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
Dart Battle

This is the main entry point for Dart Battle, configured as such in `AWS
Lambda`.  At its core is Amazon Alexa's `StandardSkillBuilder` which
empowers Alexa to interact with the code through request handlers,
defined throughout the module, and registered at the bottom of the
module. Handlers include all required standard handlers as well as all
custom handlers, and Audio Directive handlers, as defined by Amazon.

Handlers are called by Alexa through various intents which are defined in the
interaction model for the skill found at the Amazon Alexa Developer Console:
https://developer.amazon.com/alexa/console/ask
Each intent defines utterances which are used by the Machine Learning
algorithms to determine the best intent to invoke based on words spoken.
Intents may require certain "slots" to be filled before invoking the handler.
Slots are essentially variables which receive values based on the spoken words.
All of this information is passed to the handler in the `handler_input` by
Amazon Alexa.

Logging is enabled for this module, which will result in logs created in
`Amazon CloudWatch`.

Due to how Lambda builds the application area, local imports (`from . import
module`) do not properly function, but local modules are available directly
from the python import path, and are therefore imported directly.

"""

# Std Lib imports:
import logging
import random

# Amazon imports
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model import DialogState
from ask_sdk_model.dialog import DelegateDirective
from ask_sdk_model.interfaces import audioplayer
from ask_sdk_model.interfaces.audioplayer.audio_player_state import AudioPlayerState
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective)
from ask_sdk_model.interfaces import display
from ask_sdk_model.interfaces.connections import SendRequestDirective
from ask_sdk_model.interfaces.monetization.v1 import PurchaseResult
from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState)
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model.ui import StandardCard
from ask_sdk.standard import StandardSkillBuilder

# DartBattle imports:
import battle
import protocols
import rank
import responses
import session
import teams
import victories

sb = StandardSkillBuilder()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# =============================================================================
# GLOBALS
# =============================================================================
DBS3_URL = "https://s3.amazonaws.com/dart-battle-resources/"

# =============================================================================
# MAIN HANDLER
# =============================================================================
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler called when the skill is first initiated."""
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Raises:
            ValueError: If something other than the sanctioned app calls this
                intent.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and
                device.

        """
        # Prevent someone else from configuring a skill that sends requests
        #  to this:
        if handler_input.request_envelope.session.application.application_id != \
                "amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28":
            raise ValueError("Invalid Application ID")

        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = \
                responses.getWelcomeResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


# =============================================================================
# HANDLERS
# =============================================================================
class AudioNextIntentHandler(AbstractRequestHandler):
    """Handler for skipping audio track and playing the next in the queue."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("AMAZON.NextIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and
                device.

        """
        userSession = session.DartBattleSession(handler_input)
        directive = battle.skipToNextAudioPlayback(userSession)
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioPlaybackFinishedHandler(AbstractRequestHandler):
    """Handler called by Alexa when an audio track finishes playing."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        return {}


class AudioPlaybackNearlyFinishedHandler(AbstractRequestHandler):
    """Handler called by Alexa seconds before audio track finishes playing."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch and serve the appropriate response.

        In this case, the next audio track is queued up for playback. In the
        event that this is the last track, null information is passed back,
        indicating to Alexa that playback can stop after this track.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        directive = battle.continueAudioPlayback(userSession)
        handler_input.response_builder.add_directive(
            directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioPlaybackStartedHandler(AbstractRequestHandler):
    """Handler called by Alexa as an audio track starts playing."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        return {}


class AudioPlaybackStoppedHandler(AbstractRequestHandler):
    """Handler called by Alexa as an audio track stops playing."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        In this case, when a user stops the audio track, statistics such as the
        current track and its playback timecode are stored in the persistent
        data so that the track can be resumed by the user later.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        token = handler_input.request_envelope.request.token
        oim = handler_input.request_envelope.request.offset_in_milliseconds
        userSession = session.DartBattleSession(handler_input)
        userSession.setAudioState(token, oim)
        return {}


class AudioPreviousIntentHandler(AbstractRequestHandler):
    """Handler called when the user requests to skip to the previous track."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("AMAZON.PreviousIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        directive = battle.reverseAudioPlayback(userSession)
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioResumeHandler(AbstractRequestHandler):
    """Handler for when the user asks to resume playback of a stopped track."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        token = userSession.currentToken
        offsetInMilliseconds = int(userSession.offsetInMilliseconds)
        sessionInfo = token.split("_")[1]
        scenarioEnum = sessionInfo.split(".")[1]
        scenarioName = battle.Scenarios(int(scenarioEnum)).name

        playlist = battle.Scenario(userSession, name=scenarioName)
        track = playlist.getTrackFromToken(token)
        largeImg = DBS3_URL + "dartBattle_SB_1200x800.jpg"

        directive = PlayDirective(
            play_behavior=PlayBehavior.REPLACE_ALL,
            audio_item=AudioItem(
                stream=Stream(
                    expected_previous_token=None,
                    token=token,
                    url=track,
                    offset_in_milliseconds=offsetInMilliseconds
                ),
                metadata=AudioItemMetadata(
                    title=scenarioName,
                    subtitle="",
                    art=display.Image(
                        content_description=scenarioName,
                        sources=[
                            display.ImageInstance(
                                url=largeImg
                            )
                        ]
                    ),
                    background_image=display.Image(
                        content_description=scenarioName,
                        sources=[
                            display.ImageInstance(
                                url=largeImg
                            )
                        ]
                    )
                )
            )
        )
        print("Resuming track {} at {} ms".format(track, offsetInMilliseconds))
        handler_input.response_builder.add_directive(
            directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioStartOverIntentHandler(AbstractRequestHandler):
    """Handler for starting audio over from the beginning of the track."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        directive = battle.restartAudioPlayback(userSession)
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioStopIntentHandler(AbstractRequestHandler):
    """Handler for stopping audio playback of a currently playing track."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input)
               )

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        directive = StopDirective()
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioUnsupported(AbstractRequestHandler):
    """Catch-all handler for any unsupported audio directives."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("AMAZON.LoopOffIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOnIntent")(handler_input) or
                is_intent_name("AMAZON.RepeatIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOffIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOnIntent")(handler_input)
               )

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            None

        """
        print("Unsupported audio intent called.")
        return {}


class BattleDurationStartHandler(AbstractRequestHandler):
    """Handler for starting a battle of a specified duration of minutes."""
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("StartBattleDurationIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, cardTitle, cardText, cardImage, directive = \
                battle.startBattleDurationIntent(userSession)
        card = StandardCard(title=cardTitle, text=cardText, image=cardImage)
        responseBuilder = handler_input.response_builder
        responseBuilder.speak(speech).set_card(card)
        responseBuilder.add_directive(directive).set_should_end_session(True)
        return responseBuilder.response


class BattleStandardStartHandler(AbstractRequestHandler):
    """Handler to start a battle when the user did not specify a duration."""
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("StartBattleStandardIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, cardTitle, cardText, cardImage, directive = \
                battle.startBattleStandardIntent(userSession)
        card = StandardCard(title=cardTitle, text=cardText, image=cardImage)
        responseBuilder = handler_input.response_builder
        responseBuilder.speak(speech).set_card(card)
        responseBuilder.add_directive(directive).set_should_end_session(True)
        return responseBuilder.response


class ProductShopHandler(AbstractRequestHandler):
    """Hander invoked when a user asks to "buy"/"shop" for premium content."""
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("ShopIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        logger.info("In ProductShopHandler")
        userSession = session.DartBattleSession(handler_input)
        productName = userSession.request.slots["ProductName"]["value"]
        if productName and userSession.request.slots["ProductName"]["status"] \
                in [StatusCode.ER_SUCCESS_MATCH, "StatusCode.ER_SUCCESS_MATCH"]:
            print("BUY MATCH: {}".format(userSession.request.slots))
            return BuyHandler().handle(handler_input, userSession=userSession)
        else:
            print("BUY NO MATCH: {}".format(userSession.request.slots))

        inSkillResponse = userSession.monetizationData

        if not inSkillResponse:
            speech = ("I am having trouble reaching Amazon's monetization "
                      "service. What else can I do for you?")
            reprompt = "I didn't catch that. Can you try again?"
            return handler_input.response_builder.speak(speech).ask(
                reprompt).response

        # Inform the user about what products are available for purchase
        purchasable = [l for l in inSkillResponse.in_skill_products
                       if l.entitled == EntitledState.NOT_ENTITLED and
                       l.purchasable == PurchasableState.PURCHASABLE]

        if purchasable:
            speech = ("There is currently one premium content scenario "
                      "available for activation. Prospector's Predicament "
                      "pits you against the outlaw Bonnie Hawkins in a do or "
                      "die battle set in the days of the American Old West. "
                      "To learn more, ask dart battle to tell me more about "
                      "Prospector's Predicament. ")
        else:
            owned = [x for x in inSkillResponse.in_skill_products
                     if x.entitled == EntitledState.ENTITLED]
            if len(owned) == len(list(inSkillResponse.in_skill_products)):
                speech = ("Impressive, soldier. It appears as if you already "
                          "own all of the Dart Battle premium content "
                          "scenarios. What else can I help you with?")
            else:
                speech = ("There are currently no more premium content "
                          "scenarios available. What can I help you with?")
        reprompt = "Try saying start a battle, set up teams, or more options. "
        return handler_input.response_builder.speak(speech).ask(
            reprompt).response


class UpsellResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after an upsell occurs."""
    def can_handle(self, handler_input):
        return (is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Upsell")

    def handle(self, handler_input):
        logger.info("In UpsellResponseHandler")

        if handler_input.request_envelope.request.status.code == "200":
            if handler_input.request_envelope.request.payload.get(
                    "purchaseResult") == PurchaseResult.DECLINED.value:
                speech = "Ok. Hope you change your mind. "
                reprompt = "You can say, start a battle and stuff. "
                return handler_input.response_builder.speak(speech).ask(
                    reprompt).response
        else:
            msg = "Connections.Response indicated failure. Error: {}"
            msg = msg.format(handler_input.request_envelope.request.status.message)
            logger.info(msg)
            return handler_input.response_builder.speak(
                "There was an error handling your Upsell request. "
                "Please try again or contact us for help.").response
        return None


class ProductDetailHandler(AbstractRequestHandler):
    """Handler for providing product detail to the user before buying.

    Resolve the product category and provide the user with the
    corresponding product detail message.
    User says: Alexa, tell me more about <product>

    """
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("ProductDetailIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        logger.info("In ProductDetailHandler")
        userSession = session.DartBattleSession(handler_input)
        inSkillResponse = userSession.monetizationData

        if not inSkillResponse:
            speech = ("I am having trouble reaching Amazon's monetization "
                      "service. What else can I do for you?")
            reprompt = "I didn't catch that. Can you try again?"
            return handler_input.response_builder.speak(speech).ask(
                reprompt).response

        logger.info("inSkillResponse: {}".format(inSkillResponse))
        productName = userSession.request.slots["ProductName"]["value"]
        productName = productName.replace(" ", "_").replace("'", "")
        logger.info("Product Name passed in: {}".format(productName))

        # No entity resolution match
        if productName is None:
            speech = ("I don't think we have a product by that name.  "
                      "Can you try again?")
            reprompt = "I didn't catch that. Can you try again?"
            return handler_input.response_builder.speak(speech).ask(
                reprompt).response
        else:
            for item in inSkillResponse.in_skill_products:
                print("  -> PRODUCT: {}".format(item.reference_name))
            product = [l for l in inSkillResponse.in_skill_products
                       if l.reference_name.lower() == productName.lower()]
            if product:
                advertisement = DBS3_URL + "ad_Prospectors_01.mp3"
                speech = ("<audio src=\"{}\" />  To buy it, say Buy {}".format(
                    advertisement,
                    product[0].name)
                         )
                reprompt = (
                    "I didn't catch that. To buy {}, say Buy {}".format(
                        product[0].name, product[0].name))
            else:
                speech = ("I don't think we have a product by that name.  "
                          "Can you try again?")
                reprompt = "I didn't catch that. Can you try again?"

            return handler_input.response_builder.speak(speech).ask(
                reprompt).response


class BuyHandler(AbstractRequestHandler):
    """Handler for letting users buy premium content products.

    User says: Alexa, buy <category>.

    """
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("BuyIntent")(handler_input)

    def handle(self, handler_input, userSession=None):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        logger.info("In BuyHandler")
        if not userSession:
            userSession = session.DartBattleSession(handler_input)

        # Inform the user about what products are available for purchase
        inSkillResponse = userSession.monetizationData
        if inSkillResponse:
            product = [l for l in inSkillResponse.in_skill_products
                       if l.reference_name]
            print("PRODUCT: {}".format(product))
            productId = product[0].product_id

            #productId = userSession.request.slots["ProductName"]["id"]
            msg = "Sending Buy directive for product id '{}'"
            logger.info(msg, productId)
            return handler_input.response_builder.add_directive(
                SendRequestDirective(
                    name="Buy",
                    payload={
                        "InSkillProduct": {
                            "productId": productId
                        }
                    },
                    token="correlationToken")
            ).response
        return None


class BuyResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after a buy occurs."""
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Buy")

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        logger.info("In BuyResponseHandler")
        userSession = session.DartBattleSession(handler_input)
        inSkillResponse = userSession.monetizationData
        print("PAYLOAD: {}".format(handler_input.request_envelope.request.payload))
        productId = handler_input.request_envelope.request.payload.get(
            "productId")
        print("PRODUCT_ID: {}".format(productId))

        if inSkillResponse:
            print("IN_SKILL_PRODUCTS: {}".format(inSkillResponse.in_skill_products))
            product = [l for l in inSkillResponse.in_skill_products
                       if l.product_id == productId]
            logger.info("Product = {}".format(str(product)))
            if handler_input.request_envelope.request.status.code == "200":
                speech = None
                reprompt = None
                purchaseResult = handler_input.request_envelope.request.payload.get(
                    "purchaseResult")
                if purchaseResult == PurchaseResult.ACCEPTED.value:
                    speech = ("Congratulations. {} has been added to the "
                              "random rotation of scenarios from which to "
                              "choose when you start a battle. What next?  "
                              "Start a battle? Exit? ").format(product[0].name)
                    reprompt = "What next?  Start a battle? Exit? "
                elif purchaseResult in (
                        PurchaseResult.DECLINED.value,
                        PurchaseResult.ERROR.value,
                        PurchaseResult.NOT_ENTITLED.value):
                    speech = ("Thanks for your interest in {}.  What next?  "
                              "Start a battle? Exit? ".format(product[0].name))
                    reprompt = "What next?  Start a battle? Exit? "
                elif purchaseResult == PurchaseResult.ALREADY_PURCHASED.value:
                    logger.info("Already purchased product")
                    speech = " What next?  Start a battle? Exit? "
                    reprompt = "What next?  Start a battle? Exit? "
                else:
                    # Invalid purchase result value
                    logger.info("Purchase result: {}".format(purchaseResult))
                    return FallbackIntentHandler().handle(handler_input)

                return handler_input.response_builder.speak(speech).ask(
                    reprompt).response
            else:
                msg = "Connections.Response (code {}) indicated failure. "
                logger.info(
                    msg.format(
                        handler_input.request_envelope.request.status.code
                    ) + "Error: {}".format(
                        handler_input.request_envelope.request.status.message
                    )
                )

                return handler_input.response_builder.speak(
                    "There was an error handling your purchase request. "
                    "Please try again or contact us for help by emailing "
                    "support at dart battle dot fun. ").response
        return None


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for fallback intent, a catch-all required by Amazon."""
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        logger.info("In FallbackIntentHandler")
        speech = (
            "Sorry. I cannot help with that. "
            "For help, say , 'Help me'... Now, what can I do for you?"
            )
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(
            reprompt).response


class CancelAndStopIntentHandler(AbstractRequestHandler):
    """Handler for when a user tells Alexa to 'stop' or 'cancel' the skill."""
    def can_handle(self, handler_input):
        """Inform the handler of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return not (
            not is_intent_name("AMAZON.CancelIntent")(handler_input)
            and not is_intent_name("AMAZON.StopIntent")(handler_input)
            and not is_intent_name("AMAZON.PauseIntent")(handler_input)
            )

    def handle(self, handler_input):
        """ Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speeches = [
            "Standing down.",
            "Of course.",
            "Canceling."
        ]
        speech = random.choice(speeches)

        if AudioPlayerState().player_activity:
            userSession.setAudioState(
                AudioPlayerState().token,
                AudioPlayerState().offsetInMilliseconds
            )

        responseBuilder = handler_input.response_builder
        responseBuilder.speak(speech).ask(speech)
        directive = audioplayer.StopDirective()
        responseBuilder.add_directive(directive)
        responseBuilder.set_should_end_session(True)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("AMAZON.HelpIntent")(handler_input) or \
                is_intent_name("MoreOptionsIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = \
                responses.getOptionsResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class HowToPlayHandler(AbstractRequestHandler):
    """Handler for when the user asks "how do I play" which recites rules."""
    def can_handle(self, handler_input):
        """Inform the request handler of what intents are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("HowToPlayIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        speech, reprompt, cardTitle, cardText, cardImage, directive = \
                responses.howToPlayResponse()
        card = StandardCard(title=cardTitle, text=cardText, image=cardImage)
        responseBuilder = handler_input.response_builder
        responseBuilder.speak(speech).set_card(card)
        responseBuilder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class ProtocolToggleInProgressHandler(AbstractRequestHandler):
    """Handler: user asks 'enable'/'disable' a protocol, without specifying.

    This uses a DelegateDirective to continue the prompt to the user for more
    information about which specific protocol to enable/disable.  Protocols are
    what Dart Battle calls secret codes to unlock special in-game content.

    """
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("EnableProtocolIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        currentIntent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=currentIntent
            )).response


class ProtocolToggleHandler(AbstractRequestHandler):
    """Handler that enables/disables specific protocols.

    Protocols are what Dart Battle calls secret codes to unlock special in-game
    content.

    """
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("EnableProtocolIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = protocols.toggleProtocol(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class RankQueryHandler(AbstractRequestHandler):
    """Handler for "Tell me my rank" which reports rank & advancement goal."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("RankQueryIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = rank.getRankResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler called by Alexa when the skill's session concludes.

    Speech may or may not be spoken depending on the trigger that ends the
    session. Either way, the userSession is updated with all permanent
    attributes including Audio Player State.

    """
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speeches = [
            "Standing down.",
            "Of course.",
            "Canceling."
        ]
        speech = random.choice(speeches)

        if AudioPlayerState().player_activity:
            userSession.setAudioState(
                AudioPlayerState().token,
                AudioPlayerState().offsetInMilliseconds
            )

        responseBuilder = handler_input.response_builder
        responseBuilder.speak(speech).ask(speech)
        directive = audioplayer.StopDirective()
        responseBuilder.add_directive(directive)
        responseBuilder.set_should_end_session(True)
        return handler_input.response_builder.response


class TeamClearHandler(AbstractRequestHandler):
    """Handler called when the user requests to "clear the teams"."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("ClearTeamsIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = \
                teams.clearTeamsIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TeamSetupInProgressHandler(AbstractRequestHandler):
    """Handler called when user wants to form teams; prompts for more info.

    Uses the DelegateDirective to prompt the user for number of players,
    number of teams, and player names.

    """
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("SetupTeamsIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        currentIntent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=currentIntent
            )).response


class TeamSetupHandler(AbstractRequestHandler):
    """Handler called when team setup slots are filled, really makes teams."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("SetupTeamsIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = \
                teams.setupTeamsIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TeamShuffleHandler(AbstractRequestHandler):
    """Handler called when user requests to "shuffle the teams"."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("ShuffleTeamsIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = \
                teams.shuffleTeamsIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        # FIXME: Response is wrong after cleared teams
        return handler_input.response_builder.response


class TurnOffSettingHandler(AbstractRequestHandler):
    """Handler for disabling events and maybe other settings."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("TurnOffSettingIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = \
                responses.turnOffSettingsResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class TurnOnSettingHandler(AbstractRequestHandler):
    """Handler for enabling events and maybe other settings."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("TurnOnSettingIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = \
                responses.turnOnSettingsResponse(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class VictoriesClearInProgressHandler(AbstractRequestHandler):
    """Handler that collects more info for clearing victories.

    Uses a DelegateDirective to prompt the user for the name of an individual
    or team for which to clear the victories, or prompt for confirmation.

    """
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("ClearVictoryIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state != DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        currentIntent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=currentIntent
            )).response


class VictoriesClearHandler(AbstractRequestHandler):
    """Handler for clearing victories once all information is gathered."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("ClearVictoryIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = victories.clearVictoryIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class VictoriesReciteHandler(AbstractRequestHandler):
    """Handler: recites victories when user asks "tell me the victories"."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return is_intent_name("ReciteVictoriesIntent")(handler_input)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)
        speech, reprompt, cardTitle, cardText, cardImage = \
                victories.reciteVictoriesIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


class VictoriesRecordInProgressHandler(AbstractRequestHandler):
    """Handler that collects more info for recording victories.

    Uses a DelegateDirective to prompt the user for the name of an individual
    or team for which to record the victory.

    """
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
        currentIntent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(
            DelegateDirective(
                updated_intent=currentIntent
            )).response


class VictoriesRecordHandler(AbstractRequestHandler):
    """Handler for actually recording a victory for a player or team."""
    def can_handle(self, handler_input):
        """Inform the request of what intents/requests are handled by this obj.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this obj.

        """
        return (is_intent_name("RecordVictoryIntent")(handler_input)
                and handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        """Handle the launch request; fetch & serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent & device.

        """
        userSession = session.DartBattleSession(handler_input)

        speech, reprompt, cardTitle, cardText, cardImage = \
                victories.recordVictoryIntent(userSession)
        handler_input.response_builder.speak(speech).ask(reprompt).set_card(
            StandardCard(title=cardTitle, text=cardText, image=cardImage)
        ).set_should_end_session(False)
        return handler_input.response_builder.response


# =============================================================================
# Request and Response Loggers
# =============================================================================
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope.

    The request envelope contains all information from the session including
    user ID, slots and values, etc.

    This is a request interceptor, allowing the interception of logging data
    which can be scraped and sent to CloudWatch through `logger`.

    """
    def process(self, handler_input):
        """Pull the request envelope from the handler and log it to CloudWatch.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

        Returns:
            None

        """
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope.

    Handlers return responses which are interpreted by the Amazon device. This
    object intercepts the passing of that response, allowing us to log the
    response to CloudWatch.

    Returns:
        None

    """
    def process(self, handler_input, response):
        """Pass the response on to the logger.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input
                from Alexa.

            response (ask_sdk_model.Response): The response to Alexa.

        """
        logger.info("Response: {}".format(response))


# =============================================================================
# SKILL BUILDER
# =============================================================================
sb.add_request_handler(AudioNextIntentHandler())
sb.add_request_handler(AudioPlaybackFinishedHandler())
sb.add_request_handler(AudioPlaybackNearlyFinishedHandler())
sb.add_request_handler(AudioPlaybackStartedHandler())
sb.add_request_handler(AudioPlaybackStoppedHandler())
sb.add_request_handler(AudioPreviousIntentHandler())
sb.add_request_handler(AudioResumeHandler())
sb.add_request_handler(AudioStartOverIntentHandler())
sb.add_request_handler(AudioStopIntentHandler())
sb.add_request_handler(AudioUnsupported())
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
sb.add_request_handler(ProtocolToggleInProgressHandler())
sb.add_request_handler(ProtocolToggleHandler())
sb.add_request_handler(VictoriesClearInProgressHandler())
sb.add_request_handler(VictoriesClearHandler())
sb.add_request_handler(VictoriesReciteHandler())
sb.add_request_handler(VictoriesRecordInProgressHandler())
sb.add_request_handler(VictoriesRecordHandler())

sb.add_request_handler(ProductShopHandler())
sb.add_request_handler(UpsellResponseHandler())
sb.add_request_handler(ProductDetailHandler())
sb.add_request_handler(BuyHandler())
sb.add_request_handler(BuyResponseHandler())

sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())
handler = sb.lambda_handler()
