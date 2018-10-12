# DartBattle imports:
import database
import datetime
# from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model.services.service_exception import ServiceException
# import six


class DartBattleSession(object):
    def __init__(self, handler_input):
        print('-> ANAND: Initializing custom session object DartBattleSession...')
        self._handler_input = handler_input
        self._sessionAttributes = self.populateAttrs()
        self._monetizationData = None
        self.populateMonetizationData()

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def attributes(self):
        if self._sessionAttributes:
            return self._sessionAttributes
        self._sessionAttributes = self.populateAttrs()
        return self._sessionAttributes

    @attributes.setter
    def attributes(self, value):
        for keyName in self.attributes.keys():
            if keyName in value:
                self._sessionAttributes[keyName] = value[keyName]

    @property
    def battleDuration(self):
        if not self.attributes.get("battleDuration"):
            self._sessionAttributes["battleDuration"] = "240"
        return self._sessionAttributes["battleDuration"]

    @battleDuration.setter
    def battleDuration(self, value):
        self._sessionAttributes["battleDuration"] = value
        database.updateRecordDuration(self)

    @property
    def dateCreated(self):
        if not self.attributes.get("dateCreated"):
            lastRun = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            self._sessionAttributes["dateCreated"] = lastRun
        return self._sessionAttributes["dateCreated"]

    @dateCreated.setter
    def dateCreated(self, value):
        self._sessionAttributes["dateCreated"] = value

    @property
    def currentToken(self):
        if not self.attributes.get("currentToken"):
            self._sessionAttributes["currentToken"] = self._handler_input.request_envelope.request.token
        return self._sessionAttributes["currentToken"]

    @currentToken.setter
    def currentToken(self, value):
        self._sessionAttributes["currentToken"] = value

    @property
    def lastRun(self):
        if not self.attributes.get("lastRun"):
            lastRun = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            self._sessionAttributes["lastRun"] = lastRun
        return self._sessionAttributes["lastRun"]

    @lastRun.setter
    def lastRun(self, value):
        self._sessionAttributes["lastRun"] = value

    @property
    def monetizationData(self):
        print('-> ANAND: DartBattleSession object returning property self.monetizationData')
        if self._monetizationData:
            return self._monetizationData
        print('-> ANAND (!!!): DartBattleSession object recognizing that self.monetizationData is'
              ' empty! Calling self.populateMonetizationData one more time in case we can achieve '
              'success; returning the result either way.')
        return self.populateMonetizationData()

    @property
    def numBattles(self):
        if not self.attributes.get("numBattles"):
            self._sessionAttributes["numBattles"] = "0"
        return self._sessionAttributes["numBattles"]

    @numBattles.setter
    def numBattles(self, value):
        self._sessionAttributes["numBattles"] = value

    @property
    def offsetInMilliseconds(self):
        if not self.attributes.get("offsetInMilliseconds"):
            self._sessionAttributes["offsetInMilliseconds"] = "0"
        return self._sessionAttributes["offsetInMilliseconds"]

    @offsetInMilliseconds.setter
    def offsetInMilliseconds(self, value):
        self._sessionAttributes["offsetInMilliseconds"] = value

    @property
    def playerRank(self):
        if not self.attributes.get("playerRank"):
            self._sessionAttributes["playerRank"] = "00"
        return self._sessionAttributes["playerRank"]

    @playerRank.setter
    def playerRank(self, value):
        if "playerRank" in self.attributes:
            if self._sessionAttributes.get("playerRank") == value:
                return
            self._sessionAttributes["playerRank"] = value
            database.updateRecord(self)
            return
        self._sessionAttributes["playerRank"] = value

    @property
    def playerRoles(self):
        if not self.attributes.get("playerRoles"):
            self._sessionAttributes["playerRoles"] = []
        return self._sessionAttributes["playerRoles"]

    @playerRoles.setter
    def playerRoles(self, value):
        self._sessionAttributes["playerRoles"] = value

    @property
    def protocolCodes(self):
        if not self.attributes.get("protocolCodes"):
            self._sessionAttributes["protocolCodes"] = {}
        return self._sessionAttributes["protocolCodes"]

    @protocolCodes.setter
    def protocolCodes(self, value):
        self._sessionAttributes["protocolCodes"] = value

    @property
    def recentSession(self):
        if not self.attributes.get("recentSession"):
            self._sessionAttributes["recentSession"] = "False"
        return self._sessionAttributes["recentSession"]

    @recentSession.setter
    def recentSession(self, value):
        self._sessionAttributes["recentSession"] = value

    @property
    def request(self):
        return DartBattleRequest(self._handler_input.request_envelope)

    @property
    def sfx(self):
        if not self.attributes.get("sfx"):
            self._sessionAttributes["sfx"] = "True"
        return self._sessionAttributes["sfx"]

    @sfx.setter
    def sfx(self, value):
        self._sessionAttributes["sfx"] = value

    @property
    def soundtrack(self):
        if not self.attributes.get("soundtrack"):
            self._sessionAttributes["soundtrack"] = "True"
        return self._sessionAttributes["soundtrack"]

    @soundtrack.setter
    def soundtrack(self, value):
        self._sessionAttributes["soundtrack"] = value

    @property
    def teams(self):
        if not self.attributes.get("teams"):
            self._sessionAttributes["teams"] = {}
        return self._sessionAttributes["teams"]

    @teams.setter
    def teams(self, value):
        self._sessionAttributes["teams"] = value

    @property
    def userId(self):
        if not self.attributes.get("userId"):
            self._sessionAttributes["userId"] = ['context']['System']['user']['userId']
        return self._sessionAttributes["userId"]

    @userId.setter
    def userId(self, value):
        self._sessionAttributes["userId"] = value

    @property
    def usingEvents(self):
        if not self.attributes.get("usingEvents"):
            self._sessionAttributes["usingEvents"] = "True"
        return self._sessionAttributes["usingEvents"]

    @usingEvents.setter
    def usingEvents(self, value):
        self._sessionAttributes["usingEvents"] = value
        database.updateToggleEvents(self)

    @property
    def usingTeams(self):
        if not self.attributes.get("usingTeams"):
            self._sessionAttributes["usingTeams"] = "False"
        return self._sessionAttributes["usingTeams"]

    @usingTeams.setter
    def usingTeams(self, value):
        self._sessionAttributes["usingTeams"] = value

    @property
    def victories(self):
        if not self.attributes.get("victories"):
            self._sessionAttributes["victories"] = {}
        return self._sessionAttributes["victories"]

    @victories.setter
    def victories(self, value):
        self._sessionAttributes["victories"] = value

    def populateAttrs(self):
        print('-> ANAND: Populating custom session attributes from entry in DynamoDB matching user_id of user...')
        print('-> ANAND: (NOTE: This method can be bypassed, and the problem still exists, so this method should'
              'not be interfering with monetization call. Still, including it for the sake of being thorough.')
        self._sessionAttributes = self._handler_input.attributes_manager.request_attributes
        self._sessionAttributes["userId"] = self._handler_input.request_envelope.context.system.user.user_id
        dbAttrs = database.getSessionFromDB(self)
        for attrName in dbAttrs:
            if not self._sessionAttributes.get(attrName):
                print("--> Setting attribute {}...".format(attrName))
                self._sessionAttributes[attrName] = dbAttrs[attrName]
        if self._handler_input.request_envelope.session:
            print('-> ANAND (Important!): replacing handler_input.attributes_manager.session_attributes '
                  'with attributes dictionary created by adding any attrs found in DynamoDB...')
            self._handler_input.attributes_manager.session_attributes = self._sessionAttributes
        else:
            # This is a non-session request; almost certainly triggered by an audio event. Update token to current:
            print("-> ANAND: handler_input.request_envelope had no valid session data. This request must have"
                  " originated outside of a session...")
            self.currentToken = self._handler_input.request_envelope.request.token
            print("@@@ {}".format(self._handler_input.request_envelope.to_dict()))
        print("-> ANAND: session attributes have been set.")
        return self._sessionAttributes

    def populateMonetizationData(self):
        print('-> ANAND: populating monetization data for the user...')
        try:
            print('-> ANAND: Attempting to reach the monetization service...')
            locale = self._handler_input.request_envelope.request.locale
            print('--> ANAND: locale is {}'.format(locale))
            ms = self._handler_input.service_client_factory.get_monetization_service()
            print('--> ANAND: monetization service client retrieved from client factory: {}'.format(ms))
            print('-> ANAND: attempting to ms.get_in_skill_products(locale)')
            self._monetizationData = ms.get_in_skill_products(locale)
            print("- Monetization service success!")
            return self._monetizationData
        except ServiceException as e:
            print("-> ANAND (!!!): ServiceException received from Monetization Service: {}".format(e))

    def setAudioState(self, currentToken, offsetInMilliseconds):
        if currentToken:
            self.currentToken = currentToken
        if offsetInMilliseconds:
            self.offsetInMilliseconds = offsetInMilliseconds
        database.updateRecordToken(self)


class DartBattleRequest(object):
    def __init__(self, request_envelope):
        self._request_envelope = request_envelope
        self.slots = {}
        self.populateSlots()

    @property
    def isNew(self):
        return self._request_envelope.session.new

    @property
    def requestId(self):
        return self._request_envelope.request_id

    def populateSlots(self):
        filledSlots = self._request_envelope.request.intent.slots
        slots = {}

        for slotName in filledSlots:
            slots[slotName] = filledSlots[slotName].to_dict()
            try:
                slots[slotName]['status'] = str(filledSlots[slotName].resolutions.resolutions_per_authority[0].status.code)
            except (TypeError, AttributeError) as e:
                slots[slotName]['status'] = "Empty"
            # dict_keys(['confirmation_status', 'name', 'resolutions', 'value', 'status'])
        self.slots = slots
