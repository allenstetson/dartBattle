# Std Lib imports:
import datetime
import os

from ask_sdk_model.ui.image import Image

# DartBattle imports:
import database
import responses


def toggleProtocol(userSession):
    if not "PROTOCOLNAME" in userSession.request.slots:
        print("SLOTS: {}".format(userSession.request.slots))
        return "Programming error: missing slots.", "", "", "", None

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

    if incomingProtocol['status'] == "StatusCode.ER_SUCCESS_NO_MATCH":
        speech += "There is no protocol named {} registered in the system. If you feel as if this is an error, please contact support at dart battle dot fun. ".format(incomingProtocol['value'])
        text += 'See Special Objectives at http://dartbattle.fun. support@dartbattle.fun with problems.'
        title += 'Unknown protocol: "{}". '.format(incomingProtocol['value'])
    elif incomingProtocol['value'] in allNames:
        protocol = [x for x in registeredProtocols if incomingProtocol['value'] in x.getNames()][0]
        if "enable" in protocolAction['value']:
            protocol.enable()
        elif "disable" in protocolAction['value']:
            protocol.disable()
        else:
            print("{} vs. enable or disable".format(protocolAction['value']))
            speech += "I can not perform the action {} on this protocol. ".format(protocolAction['value'])
        speech += protocol.speech
        title += protocol.title
        text += protocol.text
    else:
        speech += "I feel like I recognize that protocol, but I can't seem to find it. You might want to contact support at dart battle dot com. "
        text += 'See Special Objectives at http://dartbattle.fun. support@dartbattle.fun with problems.'
        title += 'Unfound protocol: "{}". '.format(incomingProtocol["value"])
    speech += "What next? Start a battle? More options? "
    reprompt = "Try saying: Start Battle, Setup Teams, or More Options."

    cardImage = Image(
        small_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_MO_720x480.jpg",
        large_image_url="https://s3.amazonaws.com/dart-battle-resources/dartBattle_MO_1200x800.jpg"
    )
    return speech, reprompt, title, text, cardImage


class DartBattleProtocol(object):
    def __init__(self, userSession):
        self.speech = ""
        self.text = ""
        self.title = ""
        self.name = ""
        self._names = []
        self.session = userSession
        self.protocolCodes = self.session.protocolCodes

    def _run(self):
        raise NotImplementedError("Subclass failed to re-implement _run().")

    def _updateDatabase(self, value=None):
        """Updates DB with timestamp to Reflect Protocol Usage:

        """
        value = value or datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y")
        self.protocolCodes[self.name] = value
        self.session.protocolCodes = self.protocolCodes
        database.updateRecordProtocol(self.session)

    @property
    def isActive(self):
        if self.name in self.protocolCodes and self.protocolCodes[self.name] != "False":
            return True
        return False

    def checkForDuplicate(self):
        if self.isActive:
            self.speech = "Protocol {} has already been enabled and cannot be enabled again. ".format(self.name)
            self.title = "Enable protocol {}".format(self.name)
            self.text = "Protocol {} already enabled".format(self.name)
            return True

    def disable(self):
        raise NotImplementedError("Subclass has not defined this method!")

    def enable(self):
        if self.checkForDuplicate():
            return
        self._run()
        self._updateDatabase()

    def getNames(self):
        return self._names or [self.name]


class ProtocolAboutFace(DartBattleProtocol):
    def __init__(self, session):
        super(ProtocolAboutFace, self).__init__(session)
        self.name = "about face"

    def _run(self):
        # Do protocol-specific things here
        numBattles = int(self.session.numBattles)
        numBattles += 10
        self.session.numBattles = str(numBattles)
        database.updateRecord(self.session)

        # Report Success
        self.speech += "Thank you for taking the time to provide us with your valued feedback. "
        self.speech += "10 battles have been added to your total, getting you closer to the next rank promotion. "
        self.title += "Protocol: enabled"
        self.text += "+10 battles toward rank advancement"

    def disable(self):
        if not self.name in self.protocolCodes:
            self.speech = "There is no protocol with that name which is enabled. "
            self.title = "Protocols"
            self.text = "Earn protocols by visiting http://dartbattle.fun and completing Special Objectives."
        else:
            self.speech = "Protocol {} is permanent and cannot be disabled. ".format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = "This protocol was enabled on {} and cannot be disabled.".format(self.protocolCodes[self.name])


class ProtocolCrowsNest(DartBattleProtocol):
    def __init__(self, session):
        super(ProtocolCrowsNest, self).__init__(session)
        self.name = "crow's nest"
        self._names = ["close nest", "crows nest", "crow's nest", "crowsnest"]

    def _run(self):
        self.speech += "Thank you for helping to spread the word about Dart Battle. "
        self.speech += "COMSAT tactical greetings are now being added to the rotation of randomly selected greetings. "
        self.title += "Protocol: enabled"
        self.text += "COMSAT Tactical greetings have been added to rotation."

    def disable(self):
        if not self.name in self.protocolCodes:
            self.speech = "There is no protocol with that name which is enabled. "
            self.title = "Protocols"
            self.text = "Earn protocols by visiting http://dartbattle.fun and completing Special Objectives."
        else:
            self.speech = "Protocol {} now disabled. ".format(self.name)
            self.title = "Protocol: disabled"
            self.text = "COMSAT tactical greetings are now removed from rotation."
            self._updateDatabase(value="False")


class ProtocolMadDog(DartBattleProtocol):
    def __init__(self, session):
        super(ProtocolMadDog, self).__init__(session)
        self.name = "mad dog"
        self._names = ["mad dog", "mad dogs"]

    def _run(self):
        self.speech += "Thank you for helping to spread the word about Dart Battle. "
        self.speech += "Angry Drill Sergeant greetings are now being added to the rotation of randomly selected greetings. "
        self.title += "Protocol: enabled"
        self.text += "Angry Drill Sergeant greetings have been added to rotation."

    def disable(self):
        if not self.name in self.protocolCodes:
            self.speech = "There is no protocol with that name which is enabled. "
            self.title = "Protocols"
            self.text = "Earn protocols by visiting http://dartbattle.fun and completing Special Objectives."
        else:
            self.speech = "Protocol {} now disabled. ".format(self.name)
            self.title = "Protocol: disabled"
            self.text = "Angry Drill Sergeant greetings are now removed from rotation."
            self._updateDatabase(value="False")


class ProtocolSilverSparrow(DartBattleProtocol):
    def __init__(self, session):
        super(ProtocolSilverSparrow, self).__init__(session)
        self.name = "silver sparrow"

    def _run(self):
        # Do protocol-specific things here
        numBattles = int(self.session.numBattles)
        numBattles += 5
        self.session.numBattles = str(numBattles)
        database.updateRecord(self.session)

        # Report Success
        self.speech += "Thank you for helping to spread the word about Dart Battle. "
        self.speech += "5 battles have been added to your total, getting you closer to the next rank promotion. "
        self.title += "Protocol: enabled"
        self.text += "+5 battles toward rank advancement"

    def disable(self):
        if not self.name in self.protocolCodes:
            self.speech = "There is no protocol with that name which is enabled. "
            self.title = "Protocols"
            self.text = "Earn protocols by visiting http://dartbattle.fun and completing Special Objectives."
        else:
            self.speech = "Protocol {} is permanent and cannot be disabled. ".format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = "This protocol was enabled on {} and cannot be disabled.".format(self.protocolCodes[self.name])


class ProtocolStingray(DartBattleProtocol):
    def __init__(self, session):
        super(ProtocolStingray, self).__init__(session)
        self.name = "stingray"
        self._names = ["stingray", "sting ray"]

    def _run(self):
        # Do protocol-specific things here
        numBattles = int(self.session.numBattles)
        numBattles += 10
        self.session.numBattles = str(numBattles)
        database.updateRecord(self.session)

        # Report Success
        self.speech += "Thank you for helping to spread the word about Dart Battle. "
        self.speech += "10 battles have been added to your total, getting you closer to the next rank promotion. "
        self.title += "Protocol: enabled"
        self.text += "+10 battles toward rank advancement"

    def disable(self):
        if not self.name in self.protocolCodes:
            self.speech = "There is no protocol with that name which is enabled. "
            self.title = "Protocols"
            self.text = "Earn protocols by visiting http://dartbattle.fun and completing Special Objectives."
        else:
            self.speech = "Protocol {} is permanent and cannot be disabled. ".format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = "This protocol was enabled on {} and cannot be disabled.".format(self.protocolCodes[self.name])


class ProtocolTelemetry(DartBattleProtocol):
    def __init__(self, session):
        super(ProtocolTelemetry, self).__init__(session)
        self.name = "telemetry"
        self._names = ["telemetry"]

    def _run(self):
        # Do protocol-specific things here
        numBattles = int(self.session.numBattles)
        numBattles += 10
        self.session.numBattles = str(numBattles)
        database.updateRecord(self.session)

        # Report Success
        self.speech += '<audio src="https://s3.amazonaws.com/dart-battle-resources/protocols/telemetry/protocol_Telemetry_00_Enable.mp3" /> '
        self.title += "Protocol Telemetry: enabled"
        self.text += "New team role!: Communications Specialist"

    def disable(self):
        if not self.name in self.protocolCodes:
            self.speech = "There is no protocol with that name which is enabled. "
            self.title = "Protocols"
            self.text = "Earn protocols by visiting http://dartbattle.fun and completing Special Objectives."
        else:
            self.speech = "Protocol {} is permanent and cannot be disabled. ".format(self.name)
            self.title = "Protocol: enabled (permanent)"
            self.text = "This protocol was enabled on {} and cannot be disabled.".format(self.protocolCodes[self.name])

