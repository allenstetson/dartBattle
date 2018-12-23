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
from ask_sdk_model.interfaces import audioplayer
from ask_sdk_model.interfaces.audioplayer.audio_player_state import AudioPlayerState
from ask_sdk_model.ui import SimpleCard, StandardCard
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective, PlaybackNearlyFinishedRequest)
from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState, InSkillProductsResponse)
from ask_sdk_model import (
    Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
from ask_sdk_model.dialog import (
    ElicitSlotDirective, DelegateDirective)
from ask_sdk_model.interfaces import display
from ask_sdk_model.interfaces.monetization.v1 import PurchaseResult
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_model.interfaces.connections import SendRequestDirective

#sb = SkillBuilder()
sb = StandardSkillBuilder()


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


# =============================================================================
# HANDLERS
# =============================================================================
class AudioNextIntentHandler(AbstractRequestHandler):
    # Handler for Stop
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("AMAZON.NextIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        directive = battle.skipToNextAudioPlayback(userSession)
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioPlaybackFinishedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_request_type("AudioPlayer.PlaybackFinished")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        return {}


class AudioPlaybackNearlyFinishedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_request_type("AudioPlayer.PlaybackNearlyFinished")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        directive = battle.continueAudioPlayback(userSession)
        handler_input.response_builder.add_directive(
            directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioPlaybackStartedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_request_type("AudioPlayer.PlaybackStarted")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        return {}


class AudioPlaybackStoppedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_request_type("AudioPlayer.PlaybackStopped")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        token = handler_input.request_envelope.request.token
        oim = handler_input.request_envelope.request.offset_in_milliseconds
        userSession = session.DartBattleSession(handler_input)
        userSession.setAudioState(token, oim)
        return {}


class AudioPreviousIntentHandler(AbstractRequestHandler):
    # Handler for Stop
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("AMAZON.PreviousIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        directive = battle.reverseAudioPlayback(userSession)
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioResumeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)

        token = userSession.currentToken
        offsetInMilliseconds = int(userSession.offsetInMilliseconds)
        sessionInfo = token.split("_")[1]
        (playerRank, scenarioEnum, teams, sfx, soundtrack) = sessionInfo.split(".")
        scenarioName = battle.Scenarios(int(scenarioEnum)).name

        playlist = battle.Scenario(userSession, name=scenarioName)
        track = playlist.getTrackFromToken(token)
        largeImg = "https://s3.amazonaws.com/dart-battle-resources/dartBattle_SB_1200x800.jpg"

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
    # Handler for Stop
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        userSession = session.DartBattleSession(handler_input)
        directive = battle.restartAudioPlayback(userSession)
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioStopIntentHandler(AbstractRequestHandler):
    # Handler for Stop
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input) or
                is_intent_name("AMAZON.PauseIntent")(handler_input)
                )

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        directive = StopDirective()
        handler_input.response_builder.add_directive(directive).set_should_end_session(True)
        return handler_input.response_builder.response


class AudioUnsupported(AbstractRequestHandler):
    # Handler for Stop
    def can_handle(self, handler_input):
        """Inform the request handler of what intents/requests can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return (is_intent_name("AMAZON.LoopOffIntent")(handler_input) or
                is_intent_name("AMAZON.LoopOnIntent")(handler_input) or
                is_intent_name("AMAZON.RepeatIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOffIntent")(handler_input) or
                is_intent_name("AMAZON.ShuffleOnIntent")(handler_input)
                )

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            None

        """
        print("Unsupported audio intent called.")
        return {}


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


class ProductShopHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        """Inform the request handler of what intents can be handled by this object.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            bool: Whether or not the current intent can be handled by this object.

        """
        return is_intent_name("ShopIntent")(handler_input)

    def handle(self, handler_input):
        """ Handle the launch request; fetch and serve the appropriate response.

        Args:
            handler_input (ask_sdk_core.handler_input.HandlerInput): The input from Alexa.

        Returns:
            ask_sdk_model.response.Response: Response for this intent and device.

        """
        logger.info("In ProductShopHandler")
        userSession = session.DartBattleSession(handler_input)
        productName = userSession.request.slots["ProductName"]["value"]
        if productName and userSession.request.slots["ProductName"]["status"] in [StatusCode.ER_SUCCESS_MATCH, "StatusCode.ER_SUCCESS_MATCH"]:
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
            speech = ("There is currently one premium content scenario available "
                      "for activation. Prospector's Predicament pits you against "
                      "the outlaw Bonnie Hawkins in a do or die battle set in the "
                      "days of the American Old West. To learn more, ask dart battle "
                      "to tell me more about Prospector's Predicament. ")
        else:
            owned = [x for x in inSkillResponse.in_skill_products
                     if x.entitled == EntitledState.ENTITLED]
            if len(owned) == len(list(inSkillResponse.in_skill_products)):
                speech = ("Impressive, soldier. It appears as if you already own all "
                          "of the Dart Battle premium content scenarios. What else "
                          "can I help you with?")
            else:
                speech = ("There are currently no more premium content scenarios "
                          "available. What can I help you with?")
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
            logger.info("Connections.Response indicated failure. "
                       "Error: {}".format(
                        handler_input.request_envelope.request.status.message))
            return handler_input.response_builder.speak(
                "There was an error handling your Upsell request. "
                "Please try again or contact us for help.").response


class ProductDetailHandler(AbstractRequestHandler):
    """Handler for providing product detail to the user before buying.
    Resolve the product category and provide the user with the
    corresponding product detail message.
    User says: Alexa, tell me more about <product>
    """
    def can_handle(self, handler_input):
        return is_intent_name("ProductDetailIntent")(handler_input)

    def handle(self, handler_input):
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
                advertisement = "https://s3.amazonaws.com/dart-battle-resources/ad_Prospectors_01.mp3"
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
    """Handler for letting users buy the product.
    User says: Alexa, buy <category>.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("BuyIntent")(handler_input)

    def handle(self, handler_input, userSession=None):
        # type: (HandlerInput) -> Response
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
            logger.info("Sending Buy directive for product id '{}'".format(productId))
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


class BuyResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after a buy occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Buy")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In BuyResponseHandler")
        userSession = session.DartBattleSession(handler_input)
        inSkillResponse = userSession.monetizationData
        print("PAYLOAD: {}".format(handler_input.request_envelope.request.payload))
        product_id = handler_input.request_envelope.request.payload.get(
            "productId")
        print("PRODUCT_ID: {}".format(product_id))

        if inSkillResponse:
            print("IN_SKILL_PRODUCTS: {}".format(inSkillResponse.in_skill_products))
            product = [l for l in inSkillResponse.in_skill_products
                       if l.product_id == product_id]
            logger.info("Product = {}".format(str(product)))
            if handler_input.request_envelope.request.status.code == "200":
                speech = None
                reprompt = None
                purchase_result = handler_input.request_envelope.request.payload.get(
                    "purchaseResult")
                if purchase_result == PurchaseResult.ACCEPTED.value:
                    speech = ("Congratulations. {} has been added "
                              "to the random rotation of scenarios from which to choose when you start a battle. "
                              "What next?  Start a battle? Exit? ").format(product[0].name)
                    reprompt = "What next?  Start a battle? Exit? "
                elif purchase_result in (
                        PurchaseResult.DECLINED.value,
                        PurchaseResult.ERROR.value,
                        PurchaseResult.NOT_ENTITLED.value):
                    speech = ("Thanks for your interest in {}.  "
                              "What next?  Start a battle? Exit? ".format(product[0].name))
                    reprompt = "What next?  Start a battle? Exit? "
                elif purchase_result == PurchaseResult.ALREADY_PURCHASED.value:
                    logger.info("Already purchased product")
                    speech = " What next?  Start a battle? Exit? "
                    reprompt = "What next?  Start a battle? Exit? "
                else:
                    # Invalid purchase result value
                    logger.info("Purchase result: {}".format(purchase_result))
                    return FallbackIntentHandler().handle(handler_input)

                return handler_input.response_builder.speak(speech).ask(
                    reprompt).response
            else:
                logger.info("Connections.Response (code {}) indicated failure. ".format(handler_input.request_envelope.request.status.code) +
                            "Error: {}".format(handler_input.request_envelope.request.status.message))

                return handler_input.response_builder.speak(
                    "There was an error handling your purchase request. "
                    "Please try again or contact us for help by emailing support at dart battle dot fun. ").response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for fallback intent.
    2018-July-12: AMAZON.FallbackIntent is currently available in all
    English locales. This handler will not be triggered except in that
    locale, so it can be safely deployed for any locale. More info
    on the fallback intent can be found here: https://developer.amazon.com/docs/custom-skills/standard-built-in-intents.html#fallback
    """
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = (
                "Sorry. I cannot help with that. I can help you with "
                "some facts. "
                "To hear a random fact you can say "
                "'Tell me a fact', or to hear about the premium categories "
                "for purchase, say 'What can I buy'. For help, say , "
                "'Help me'... So, what can I help you with?"
            )
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(
            reprompt).response


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


class ProtocolToggleInProgressHandler(AbstractRequestHandler):
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


class ProtocolToggleHandler(AbstractRequestHandler):
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
# Request and Response Loggers
# =============================================================================
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
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

# {'version': '1.0', 'session': {'new': True, 'session_id': 'amzn1.echo-api.session.103a01a9-09b2-4223-a97c-d54c298efc82', 'user': {'user_id': 'amzn1.ask.account.AHQ53A7TTH5ELGE4FJB6RLVARNQ6DCN6EMDSUXCL5VDY4SDYTJGIC2A5EGNQMZNGF2HCOQJ242OVAEEZFQOIE3I246UXWKZGEOTXAVZWNVPJOCOHKSGFOKYG2KYWZI7CIPIEK2IHSGMANP3HX36MPPZKIS4A7KVEFRXLZNFXXOAFARCXOL3IIFBRUT5C67KDO27HH7HCF24IG7I', 'access_token': None, 'permissions': None}, 'attributes': None, 'application': {'application_id': 'amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28'}}, 'context': {'system': {'application': {'application_id': 'amzn1.ask.skill.d1311184-0f57-46e8-ab59-879027130a28'}, 'user': {'user_id': 'amzn1.ask.account.AHQ53A7TTH5ELGE4FJB6RLVARNQ6DCN6EMDSUXCL5VDY4SDYTJGIC2A5EGNQMZNGF2HCOQJ242OVAEEZFQOIE3I246UXWKZGEOTXAVZWNVPJOCOHKSGFOKYG2KYWZI7CIPIEK2IHSGMANP3HX36MPPZKIS4A7KVEFRXLZNFXXOAFARCXOL3IIFBRUT5C67KDO27HH7HCF24IG7I', 'access_token': None, 'permissions': None}, 'device': {'device_id': 'amzn1.ask.device.AES4DYXDO3B5ZTCVMKGUESOVSANNWHO3V7N3DP2RWW4LXYSCB3DIY6HR524ZVFNOOKQJAKGCCSR5YURCYK4UCQVX6KVB6WMV4VYEE23ND3MFK7IQWOD724XDPA7I6PBUZCXTQ4GKV4FFUFQSD3G4VORXTHXQ', 'supported_interfaces': {'audio_player': {}, 'display': None, 'video_app': None}}, 'api_endpoint': 'https://api.amazonalexa.com', 'api_access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJhdWQiOiJodHRwczovL2FwaS5hbWF6b25hbGV4YS5jb20iLCJpc3MiOiJBbGV4YVNraWxsS2l0Iiwic3ViIjoiYW16bjEuYXNrLnNraWxsLmQxMzExMTg0LTBmNTctNDZlOC1hYjU5LTg3OTAyNzEzMGEyOCIsImV4cCI6MTUzNzUwOTQ3OSwiaWF0IjoxNTM3NTA1ODc5LCJuYmYiOjE1Mzc1MDU4NzksInByaXZhdGVDbGFpbXMiOnsiY29uc2VudFRva2VuIjpudWxsLCJkZXZpY2VJZCI6ImFtem4xLmFzay5kZXZpY2UuQUVTNERZWERPM0I1WlRDVk1LR1VFU09WU0FOTldITzNWN04zRFAyUldXNExYWVNDQjNESVk2SFI1MjRaVkZOT09LUUpBS0dDQ1NSNVlVUkNZSzRVQ1FWWDZLVkI2V01WNFZZRUUyM05EM01GSzdJUVdPRDcyNFhEUEE3STZQQlVaQ1hUUTRHS1Y0RkZVRlFTRDNHNFZPUlhUSFhRIiwidXNlcklkIjoiYW16bjEuYXNrLmFjY291bnQuQUhRNTNBN1RUSDVFTEdFNEZKQjZSTFZBUk5RNkRDTjZFTURTVVhDTDVWRFk0U0RZVEpHSUMyQTVFR05RTVpOR0YySENPUUoyNDJPVkFFRVpGUU9JRTNJMjQ2VVhXS1pHRU9UWEFWWldOVlBKT0NPSEtTR0ZPS1lHMktZV1pJN0NJUElFSzJJSFNHTUFOUDNIWDM2TVBQWktJUzRBN0tWRUZSWExaTkZYWE9BRkFSQ1hPTDNJSUZCUlVUNUM2N0tETzI3SEg3SENGMjRJRzdJIn19.G16Z8BEynj3TX9TEILQL-rGjCClSQZR2oW59iJB0ClR2d5fvrtHSWpjYny9xVdx36PvgQIoL_jlUgHlClNciKAwomsBg8YvH4yTBSTGfvxZohsr4Feui-oY7I79-vd3WT1H0tg-HOcmnXjv_k_PfGzdrYE49ZIhJqMRNy0epTKMo9edTmhWweMB2PldmNMC27BJg2jXaxsp2HxBVig3gY-SsYsUI7QqxfQsN9GhYxFxEu7Cvdv3r4685LPIpAsqDpuDRCi_TL47hA9HLjdjX5qpyN3lt2cfpj8D22wQXUlTt_9JCubDPGADdcB-ByvMzLgcLoDthKtNdvxoX4v5ddw'}, 'audio_player': {'offset_in_milliseconds': None, 'token': None, 'player_activity': 'IDLE'}, 'display': None}, 'request': {'object_type': 'LaunchRequest', 'request_id': 'amzn1.echo-api.request.c75e2ea9-a482-4bfa-9d62-14dad9ca87ef', 'timestamp': datetime.datetime(2018, 9, 21, 4, 57, 59, tzinfo=tzlocal()), 'locale': 'en-US'}}
