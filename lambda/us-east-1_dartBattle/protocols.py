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
protocols.py - logic handling "protocols" or secret codes for Dart Battle.

Protocols unlock in-game content, and are awarded to users who help spread
awareness of the product, win a contest, or through some other means. Enabling
a protocol will either result in a boost towards rank advancement, the
application of new greetings, new player roles, or similar.

"""
# Std Lib imports:
import datetime
import logging

# Amazon imports
from ask_sdk_model.ui.image import Image

# DartBattle imports:
import database

__all__ = [
    "toggleProtocol",
    "DartBattleProtocol",
    "ProtocolAboutFace",
    "ProtocolCrowsNest",
    "ProtocolMadDog",
    "ProtocolSilverSparrow",
    "ProtocolStingray",
    "ProtocolTelemetry"
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
def toggleProtocol(userSession):
    """Enables or disables a protocol by the name provided by the user.

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
    # Should never happen, but error-check to make sure the required slot is
    #  not missing for some reason:
    if not "PROTOCOLNAME" in userSession.request.slots:
        msg = "Programming error: missing slots."
        LOGGER.info("{}\nSLOTS: {}".format(msg, userSession.request.slots))
        return msg, "", "", "", None

    # Protocols given by the user must match both those defined in the skill
    #  slot definitions (in AWS Developer Console, Alexa), but also those
    #  registered in the code.
    incomingProtocol = userSession.request.slots["PROTOCOLNAME"]
    protocolAction = userSession.request.slots["PROTOCOLACTION"]
    text = ""
    title = ""
    speech = ""

    registeredProtocols = [
        ProtocolAboutFace(userSession),
        ProtocolCrowsNest(userSession),
        ProtocolMadDog(userSession),
        ProtocolSilverSparrow(userSession),
        ProtocolStingray(userSession),
        ProtocolTelemetry(userSession)
    ]
    allNames = []
    for regProtocol in registeredProtocols:
        allNames.extend(regProtocol.getNames())

    # Handle protocols that don't match the skill definition
    if incomingProtocol['status'] == "StatusCode.ER_SUCCESS_NO_MATCH":
        speech += ("There is no protocol named {} registered in the system. "
                   "If you feel as if this is an error, please contact support"
                   " at dart battle dot fun. "
                  ).format(incomingProtocol['value'])
        text += ("See Special Objectives at http://dartbattle.fun. "
                 "support@dartbattle.fun with problems.")
        title += 'Unknown protocol: "{}". '.format(incomingProtocol['value'])
    # Handle successful protocols, registered both with the skill and in the
    #  code
    elif incomingProtocol['value'] in allNames:
        protocol = [x for x in registeredProtocols if incomingProtocol['value'] in x.getNames()][0]
        if "enable" in protocolAction['value']:
            protocol.enable()
        elif "disable" in protocolAction['value']:
            protocol.disable()
        else:
            # This should never come up, but if the protocolAction slot
            #  receives a value other than enable or disable, respond to that:
            LOGGER.debug(
                "{} vs. enable or disable".format(protocolAction['value'])
            )
            speech += ("I can not perform the action {} on this protocol. "
                      ).format(protocolAction['value'])
        speech += protocol.speech
        title += protocol.title
        text += protocol.text
    # Handle protocols that match the skill definition but don't line up with
    #  any registered protocols in the code. Hopefully this never comes up.
    else:
        speech += ("I feel like I recognize that protocol, but I can't seem "
                   "to find it. You might want to contact support at dart "
                   "battle dot com. ")
        text += ("See Special Objectives at http://dartbattle.fun. "
                 "support@dartbattle.fun with problems.")
        title += 'Unfound protocol: "{}". '.format(incomingProtocol["value"])

    # Successful or not, finish the response with a prompt, reprompt & image
    speech += "What next? Start a battle? More options? "
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."

    cardImage = Image(
        small_image_url=DBS3_URL + "dartBattle_MO_720x480.jpg",
        large_image_url=DBS3_URL + "dartBattle_MO_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


class DartBattleProtocol(object):
    """Base class for Dart Battle Protocols (secret codes that unlock content.

    When invoked, protocols should do something such as advancing a player
    towards rank advancement, unlocking player roles, greetings, or other
    content.

    Some protocols support being disabled (such as custom greetings), whereas
    some protocols, once enabled, cannot be undone (such as progress toward
    rank advancement), and in such cases can not be enabled more than once.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, userSession):
        self.speech = ""
        self.text = ""
        self.title = ""
        self.name = ""
        self._names = []
        self.session = userSession
        self.protocolCodes = self.session.protocolCodes

    def _run(self):
        """The actions to be taken when the protocol is enabled.

        The class that uses this as its base class must specify the actions to
        take when the protocol is enabled.

        Raises:
            NotImplementedError

        """
        raise NotImplementedError("Subclass failed to re-implement _run().")

    def _updateDatabase(self, value=None):
        """Updates DB with timestamp to Reflect Protocol Usage.

        This serves as a record that the protocol has been run in the past,
        and can be queried by the session to prove as much. Storing the date
        allows for information to be given such as "this protocol was already
        enabled, on July 19th" or similar.

        Args:
            value (str): The value to store in the database for this protocol
                code (optional). Some protocols with a state that can be
                toggled will pass `False` into this value as an indication that
                it has been toggled off.

        """
        value = value or datetime.datetime.strftime(
            datetime.datetime.now(), "%m/%d/%Y"
            )
        self.protocolCodes[self.name] = value
        self.session.protocolCodes = self.protocolCodes
        database.updateRecordAttr(
            self.session,
            "protocolCodes",
            self.session.protocolCodes)

    @property
    def isActive(self):
        """Whether or not this protocol is currently active.

        Checks the persistent data in the session information for a protocol
        code that matches this protocol's name. If the value for a matching
        protocol name is not `False`, this protocol is considered active.

        Returns:
            bool: True if active, False otherwise.

        """
        if self.name in self.protocolCodes and \
                self.protocolCodes[self.name] != "False":
            return True
        return False

    def checkForDuplicate(self):
        """Warns a user who is activating this protocol if it's already active.

        Protocols can only be activated once, or toggled to be active and
        disabled. If activated or active, the speech prompts for this protocol
        are updated to tell that to the user.

        Returns:
            bool: Whether or not the protocol is already active.

        """
        if self.isActive:
            self.speech = (
                "Protocol {} has already been enabled and cannot be "
                "enabled again. "
                ).format(self.name)
            self.title = "Enable protocol {}".format(self.name)
            self.text = "Protocol {} already enabled".format(self.name)
            return True
        return False

    def disable(self):
        """Disables this protocol, if supported.

        Some protocols may be disabled. Some do not support disabling (such as
        one time rank advancement awards, etc.). The class that uses this as
        its base class needs to specify the appropriate actions for a disable
        request.

        Raises:
            NotImplementedError

        """
        raise NotImplementedError("Subclass has not defined this method!")

    def enable(self):
        """Runs the actions to perform for enabling this protocol, updates DB.

        """
        if self.checkForDuplicate():
            return
        self._run()
        self._updateDatabase()

    def getNames(self):
        """Returns the names of this protocol.

        Voice-based queries are subject to being misunderstood. Therefore,
        multiple different spellings (for commonly-misunderstood names on the
        part of the voice interaction client) may be provided for a protocol.

        Returns:
            [str]: A list of applicable names for this protocol.

        """
        return self._names or [self.name]


class ProtocolAboutFace(DartBattleProtocol):
    """The "About Face" protocol.

    This protocol is a one-time grant of 10 battles on a user's record, thereby
    advancing them toward the next rank.  This can be given out as a reward for
    completing a feedback survey about Dart Battle.

    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, session):
        super(ProtocolAboutFace, self).__init__(session)
        self.name = "about face"

    def _run(self):
        """The actions to be taken when enabling this protocol.

        Here, the user's total number of battles played in Dart Battle is
        supplemented by an additional 10 battles in the database. Then, the
        speech prompt for this protocol is updated to inform the user.

        """
        # Do protocol-specific things here
        numBattles = int(self.session.numBattles)
        numBattles += 10
        self.session.numBattles = str(numBattles)
        database.updateRecordAttr(self.session, "numBattles", str(numBattles))

        # Report Success
        self.speech = ("Thank you for taking the time to provide us with "
                       "your valued feedback.  10 battles have been added to "
                       "your total, getting you closer to the next "
                       "rank promotion. ")
        self.title = "Protocol: enabled"
        self.text = "+10 battles toward rank advancement"

    def disable(self):
        """Informs the user: once enabled, this protocol can't be disabled.

        Sets the speech text for this protocol with the appropriate message.

        """
        # In case someone tries to disable a protocol that they never enabled
        #  or toggled off:
        if not self.name in self.protocolCodes:
            self.speech = ("There is no protocol with that name which "
                           "is currently enabled. ")
            self.title = "Protocols"
            self.text = ("Earn protocols by visiting http://dartbattle.fun "
                         "and completing Special Objectives.")
        # Inform the user that this was already enabled and can't be disabled:
        else:
            self.speech = ("Protocol {} is permanent and cannot be disabled. "
                          ).format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = ("This protocol was enabled on {} and cannot be "
                         "disabled.").format(self.protocolCodes[self.name])


class ProtocolCrowsNest(DartBattleProtocol):
    """The "Crow's Nest" protocol.

    This protocol can be enabled to introduce "COMSAT Tactical Greetings",
    speech to be read by Alexa simulating a battle computer responding to
    military operations and battlefield conditions.  It can be disabled to
    return Dart Battle to typical greetings.

    This is awarded as a gift for spreading the word to friends about Dart
    Battle through a web form.

    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, session):
        super(ProtocolCrowsNest, self).__init__(session)
        self.name = "crow's nest"
        self._names = ["close nest", "crows nest", "crow's nest", "crowsnest"]

    def _run(self):
        """The actions to be taken when enabling this protocol.

        Here, the speech prompt for this protocol is updated to inform the
        user. The actual enabling of the protocol happens elsewhere, in the
        database update call.

        """
        self.speech = ("Thank you for helping to spread the word about Dart "
                       "Battle.  COMSAT tactical greetings are now "
                       "being added to the rotation of randomly selected "
                       "greetings. ")
        self.title = "Protocol: enabled"
        self.text = "COMSAT Tactical greetings have been added to rotation."

    def disable(self):
        """Disables this protocol.

        Sets the speech text for this protocol with the appropriate message.

        """
        # In case someone tries to disable a protocol that they never enabled
        #  or toggled off:
        if not self.name in self.protocolCodes:
            self.speech = ("There is no protocol with that name which "
                           "is currently enabled. ")
            self.title = "Protocols"
            self.text = ("Earn protocols by visiting http://dartbattle.fun "
                         "and completing Special Objectives.")
        # Actually disable this protocol and set the speech:
        else:
            self.speech = "Protocol {} now disabled. ".format(self.name)
            self.title = "Protocol: disabled"
            self.text = "COMSAT tactical greetings are now removed from rotation."
            self._updateDatabase(value="False")


class ProtocolMadDog(DartBattleProtocol):
    """The "Mad Dog" protocol.

    This protocol can be enabled to introduce "Angry Drill Sergeant" greetings,
    audio files to be played by Alexa featuring an angry drill sergeant barking
    orders.  It can be disabled to return Dart Battle to typical greetings.

    This is awarded as a gift for spreading the word to friends about Dart
    Battle through a web form.

    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, session):
        super(ProtocolMadDog, self).__init__(session)
        self.name = "mad dog"
        self._names = ["mad dog", "mad dogs"]

    def _run(self):
        """The actions to be taken when enabling this protocol.

        Here, the speech prompt for this protocol is updated to inform the
        user. The actual enabling of the protocol happens elsewhere, in the
        database update call.

        """
        self.speech = ("Thank you for helping to spread the word about Dart "
                       "Battle.  Angry Drill Sergeant greetings are now "
                       "being added to the rotation of randomly selected "
                       "greetings. ")
        self.title = "Protocol: enabled"
        self.text = ("Angry Drill Sergeant greetings have been added "
                     "to rotation.")

    def disable(self):
        """Disables this protocol.

        Sets the speech text for this protocol with the appropriate message.

        """
        # In case someone tries to disable a protocol that they never enabled
        #  or toggled off:
        if not self.name in self.protocolCodes:
            self.speech = ("There is no protocol with that name which "
                           "is currently enabled. ")
            self.title = "Protocols"
            self.text = ("Earn protocols by visiting http://dartbattle.fun "
                         "and completing Special Objectives.")
        # Actually disable this protocol and set the speech:
        else:
            self.speech = "Protocol {} now disabled. ".format(self.name)
            self.title = "Protocol: disabled"
            self.text = ("Angry Drill Sergeant greetings are now removed "
                         "from rotation.")
            self._updateDatabase(value="False")


class ProtocolSilverSparrow(DartBattleProtocol):
    """The "Silver Sparrow" protocol.

    This protocol is a one-time grant of 5 battles on a user's record, thereby
    advancing them toward the next rank.

    This is awarded as a gift for spreading the word to friends about Dart
    Battle through a web form.
    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, session):
        super(ProtocolSilverSparrow, self).__init__(session)
        self.name = "silver sparrow"

    def _run(self):
        """The actions to be taken when enabling this protocol.

        Here, the user's total number of battles played in Dart Battle is
        supplemented by an additional 5 battles in the database. Then, the
        speech prompt for this protocol is updated to inform the user.

        """
        # Do protocol-specific things here
        numBattles = int(self.session.numBattles)
        numBattles += 5
        self.session.numBattles = str(numBattles)
        database.updateRecordAttr(self.session, "numBattles", str(numBattles))

        # Report Success
        self.speech = ("Thank you for helping to spread the word about Dart "
                       "Battle.  5 battles have been added to your total, "
                       "getting you closer to the next rank promotion. ")
        self.title = "Protocol: enabled"
        self.text = "+5 battles toward rank advancement"

    def disable(self):
        """Informs the user: once enabled, this protocol can't be disabled.

        Sets the speech text for this protocol with the appropriate message.

        """
        # In case someone tries to disable a protocol that they never enabled
        #  or toggled off:
        if not self.name in self.protocolCodes:
            self.speech = ("There is no protocol with that name which "
                           "is currently enabled. ")
            self.title = "Protocols"
            self.text = ("Earn protocols by visiting http://dartbattle.fun "
                         "and completing Special Objectives.")
        # Inform the user that this was already enabled and can't be disabled:
        else:
            self.speech = ("Protocol {} is permanent and cannot be disabled. "
                          ).format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = ("This protocol was enabled on {} and cannot be "
                         "disabled.").format(self.protocolCodes[self.name])


class ProtocolStingray(DartBattleProtocol):
    """The "About Face" protocol.

    This protocol is a one-time grant of 10 battles on a user's record, thereby
    advancing them toward the next rank.

    This is awarded as a gift for spreading the word to friends about Dart
    Battle through a web form.

    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, session):
        super(ProtocolStingray, self).__init__(session)
        self.name = "stingray"
        self._names = ["stingray", "sting ray"]

    def _run(self):
        """The actions to be taken when enabling this protocol.

        Here, the user's total number of battles played in Dart Battle is
        supplemented by an additional 10 battles in the database. Then, the
        speech prompt for this protocol is updated to inform the user.

        """
        # Do protocol-specific things here
        numBattles = int(self.session.numBattles)
        numBattles += 10
        self.session.numBattles = str(numBattles)
        database.updateRecordAttr(self.session, "numBattles", str(numBattles))

        # Report Success
        self.speech = ("Thank you for helping to spread the word about Dart "
                       "Battle.  10 battles have been added to your total, "
                       "getting you closer to the next rank promotion. ")
        self.title = "Protocol: enabled"
        self.text = "+10 battles toward rank advancement"

    def disable(self):
        """Informs the user: once enabled, this protocol can't be disabled.

        Sets the speech text for this protocol with the appropriate message.

        """
        # In case someone tries to disable a protocol that they never enabled
        #  or toggled off:
        if not self.name in self.protocolCodes:
            self.speech = ("There is no protocol with that name which "
                           "is currently enabled. ")
            self.title = "Protocols"
            self.text = ("Earn protocols by visiting http://dartbattle.fun "
                         "and completing Special Objectives.")
        # Inform the user that this was already enabled and can't be disabled:
        else:
            self.speech = ("Protocol {} is permanent and cannot be disabled. "
                          ).format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = ("This protocol was enabled on {} and cannot be "
                         "disabled.").format(self.protocolCodes[self.name])

class ProtocolTelemetry(DartBattleProtocol):
    """The "Telemetry" protocol.

    This protocol can be enabled to introduce the "Communication Specialist"
    player role. Upon enabling, the new role and associated events become
    available to the player across multiple scenarios.

    This is awarded as a gift for completing special objectives on the Dart
    Battle web site. Once enabled, this protocol cannot be disabled.

    Args:
        session (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, session):
        super(ProtocolTelemetry, self).__init__(session)
        self.name = "telemetry"
        self._names = ["telemetry"]

    def _run(self):
        """The actions to be taken when enabling this protocol.

        Here, the speech prompt for this protocol is updated to inform the
        user. The actual enabling of the protocol happens elsewhere, in the
        database update call.

        """
        # Report Success
        self.speech += '<audio src="' + DBS3_URL + \
                'protocols/telemetry/protocol_Telemetry_00_Enable.mp3" /> '
        self.title += "Protocol Telemetry: enabled"
        self.text += "New team role!: Communications Specialist"

    def disable(self):
        """Informs the user: once enabled, this protocol can't be disabled.

        Sets the speech text for this protocol with the appropriate message.

        """
        # In case someone tries to disable a protocol that they never enabled
        #  or toggled off:
        if not self.name in self.protocolCodes:
            self.speech = ("There is no protocol with that name which "
                           "is currently enabled. ")
            self.title = "Protocols"
            self.text = ("Earn protocols by visiting http://dartbattle.fun "
                         "and completing Special Objectives.")
        # Inform the user that this was already enabled and can't be disabled:
        else:
            self.speech = ("Protocol {} is permanent and cannot be disabled. "
                          ).format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = ("This protocol was enabled on {} and cannot be "
                         "disabled.".format(self.protocolCodes[self.name]))
