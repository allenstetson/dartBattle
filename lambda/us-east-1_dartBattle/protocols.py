# Std Lib imports:
import datetime
import os

# DartBattle imports:
import database


def enableProtocol(event):
    request = event['request']
    session = event['session']
    sessionAttributes = session["attributes"]
    speech = ""
    text = ""
    title = ""
    if 'slots' in request['intent'] and 'PROTOCOLNAME' in request['intent']['slots']:
        protocolName = request['intent']['slots']['PROTOCOLNAME']['value']
    else:
        protocolName = None
    registeredProtocols = [
        ProtocolSilverSparrow(session)
    ]

    if protocolName in [x.name for x in registeredProtocols]:
        protocol = [x for x in registeredProtocols if x.name == protocolName][0]
        protocol.enable()
        speech = protocol.speech
        title = protocol.title
        text = protocol.text
    speech += "What next? Start a battle? More options? "
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
                    "smallImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_MO_720x480.jpg",
                    "largeImageUrl": "https://s3.amazonaws.com/dart-battle-resources/dartBattle_MO_1200x800.jpg"
                }
            },
            "shouldEndSession": False
        }
    }


class DartBattleProtocol(object):
    def __init__(self, session):
        self.speech = ""
        self.text = ""
        self.title = ""
        self.name = ""
        self.session = session
        self.sessionAttributes = self.session["attributes"]
        self.protocolCodes = self.sessionAttributes.get("protocolCodes", {})

    def _run(self):
        raise NotImplementedError("Subclass failed to re-implement _run().")

    def _updateDatabase(self):
        """Updates DB with timestamp to Reflect Protocol Usage:

        """
        value = datetime.datetime.strftime(datetime.datetime.now(), "%m/%d/%Y")
        self.protocolCodes[self.name] = value
        self.sessionAttributes["protocolCodes"] = self.protocolCodes
        database.updateRecordProtocol(self.sessionAttributes)

    def checkForDuplicate(self):
        if self.name in self.protocolCodes and self.protocolCodes[self.name] != "False":
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


class ProtocolSilverSparrow(DartBattleProtocol):
    def __init__(self, session):
        super(ProtocolSilverSparrow, self).__init__(session)
        self.name = "silver sparrow"

    def _run(self):
        # Do protocol-specific things here
        numBattles = int(self.sessionAttributes['numBattles'])
        numBattles += 5
        self.sessionAttributes['numBattles'] = str(numBattles)
        database.updateRecord(self.sessionAttributes)

        # Report Success
        self.speech += "5 battles have been added to your total, getting you closer to the next rank promotion. "
        self.title += "Protocol Silver Sparrow: enabled"
        self.text += "+5 battles toward rank advancement"

    def disable(self):
        if not self.name in self.protocolCodes:
            self.speech = "There is no protocol with that name which is enabled. "
            self.title = "Protocols"
            self.text = "Earn protocols by visiting http://dartbattle.fun and completing Special Objectives."
        else:
            self.speech = "Protocol {} is permanent and cannot be disabled. ".format(self.name)
            self.title = "Protocol Silver Sparrow: enabled (permanent)"
            self.text = "This protocol was enabled on {} and cannot be disabled.".format(self.protocolCodes[self.name])
