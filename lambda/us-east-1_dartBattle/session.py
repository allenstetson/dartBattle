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
session.py - containing convenience objects for pulling data from session, DB

Amazon Alexa passes an event handler with a request envelope containing a
session object. Within that object can be found application information, user
information, information about slots and their values, audio player state and
tokens for current and next tracks, etc.

Accessing this information can often be frustrating, particularly in the case
of slots that do not have a concept of existing with a NoneType value; unset
slots simply do not exist and will throw an AttributeError if one tries to
access it.

The objects below help to make the experience easier by providing a session
object containing properties for commonly-accessed information, normally
found in disparate locations and structures, all accessed through a simple
mechanism.  Slots are populated as properties on the DartBattleRequest object
and exist even if unset, allowing NoneType tests, etc.

"""
# Std Lib imports
import datetime
import logging

# Amazon imports
from ask_sdk_model.services.service_exception import ServiceException

# DartBattle imports:
import database


__all__ = [
    "DartBattleRequest",
    "DartBattleSession"
]


# =============================================================================
# GLOBALS
# =============================================================================
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


# =============================================================================
# CLASSES
# =============================================================================
class DartBattleRequest(object):
    """A convenience object for accessing things within the request envelope.

    Slots are like variables expected by a specific intent by the recipe
    defined for that intent at the AWS Developer Console. Accessing those
    values requires nuance and can be confusing. This object makes accessing
    those easier.

    Slots are populated when the object is first created, and can be updated
    upon request.

    Args:
        requestEnvelope (ask_sdk_core.handler_input.request_envelope): The
            request envelope as provided by Amazon Alexa.

    """
    def __init__(self, requestEnvelope):
        self._requestEnvelope = requestEnvelope
        self.slots = {}
        self.populateSlots()

    @property
    def isNew(self):
        """Whether or not this session is considered a new session.

        This property is read-only.

        Returns:
            bool: True if this is a new session, False otherwise.

        """
        return self._requestEnvelope.session.new

    @property
    def requestId(self):
        """The ID of the incoming request, assigned by Amazon Alexa.

        Each incoming request has an ID. This is a convenience object for
        accessing that ID, should it become important.

        Returns:
            str: the ID of the request represented by this object.

        """
        return self._requestEnvelope.request_id

    def populateSlots(self):
        """Populates the slots of the request assigning logical values.

        Slots can be difficult to access, and do not support the concept of
        being empty, unassigned, NoneType, etc. which makes it hard to
        test slots. This convenience method not only puts the slots in an
        easy to reach spot for the user, but also populates a status for each
        slot indicating whether it is filled or empty.

        Returns:
            dict: The dictionary of slots with their value and status.

        """
        filledSlots = self._requestEnvelope.request.intent.slots
        slots = {}

        for slotName in filledSlots:
            slots[slotName] = filledSlots[slotName].to_dict()
            try:
                slots[slotName]['status'] = \
                    str(filledSlots[slotName].resolutions.resolutions_per_authority[0].status.code)
            except (TypeError, AttributeError):
                slots[slotName]['status'] = "Empty"
            try:
                slots[slotName]['id'] = \
                    str(filledSlots[slotName].resolutions.resolutions_per_authority[0].values[0].value.id)
            except (TypeError, AttributeError):
                slots[slotName]['id'] = "None"
            # dict_keys(['confirmation_status', 'name', 'resolutions', 'value', 'status'])
        self.slots = slots


class DartBattleSession(object):
    """The Amazon Alexa session convenience object.

    This object contains a variety of useful information from the Amazon Alexa
    skill session, usually found in different locations on the request_handler,
    accessed through different means, now all collated in one easy to work with
    object.

    Args:
        handler_input (ask_sdk_core.handler_input): The input provided by
            Amazon Alexa to handlers. This contains the request_envelope,
            attributes_manager, context from the Lambda service,
            service_client_factory, and template_factory. We use this to
            extract relevant data.

    """
    def __init__(self, handler_input):
        self._handlerInput = handler_input
        self._sessionAttributes = self.populateAttrs()
        self._monetizationData = None
        self.populateMonetizationData()

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def attributes(self):
        """All known attributes and values from the session and database.

        This hugely useful property is a dict of attribute names found within
        the input_handler's attributes_manager, as well as (importantly), the
        Dart Battle DynamoDB database. It reflects the state of all persistent
        data, as well as transient data from the session such as slots and
        values from voice interaction as well as audio tokens and offset.

        Returns:
            dict: The dict of all known attributes with their values.

        """
        if self._sessionAttributes:
            return self._sessionAttributes
        self._sessionAttributes = self.populateAttrs()
        return self._sessionAttributes

    @property
    def battleDuration(self):
        """The desired duration of a battle, in seconds.

        The user may specify the number of minutes that they wish to have a
        battle last. This number is translated into seconds and divided between
        available audio track durations as well as event durations. This
        property holds the desired battle length in seconds.

        Setting this property will result in the database being updated with
        the new value.

        Returns:
            str: The number of seconds desired for battle.  (Why a string and
                not an int? Because of the way that our DynamoDB was built...
                that's why - to be honest, this property is always turned into
                an int once queried in the code, so this could return an int,
                and recast it for storage... TODO).

        """
        if not self.attributes.get("battleDuration"):
            self._sessionAttributes["battleDuration"] = "240"
        return self._sessionAttributes["battleDuration"]

    @battleDuration.setter
    def battleDuration(self, value):
        self._sessionAttributes["battleDuration"] = value
        database.updateRecordAttr(self.session, "battleDuration", value)

    @property
    def dateCreated(self):
        """The date that the user first started Dart Battle.

        This allows us to track how long the user has been engaged with Dart
        Battle, should that ever be useful.

        Setting this property does not automatically update the DB. Updates
        will be up to the user. Typically this is only set once in a lifetime.

        Returns:
            str: The datetime that the user first started Dart Battle.

        """
        if not self.attributes.get("dateCreated"):
            lastRun = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            self._sessionAttributes["dateCreated"] = lastRun
        return self._sessionAttributes["dateCreated"]

    @dateCreated.setter
    def dateCreated(self, value):
        self._sessionAttributes["dateCreated"] = value

    @property
    def currentToken(self):
        """The current Audio Player token.

        Amazon's Audio Player is used by Dart Battle for playing audio tracks
        that exceed 240 seconds or of higher streaming quality. The audio
        player uses tokens to identify the tracks being played, and assembling
        playlists to track previous and next tracks. The currently-playing
        track token can be accessed through this property.

        NOTE!: Amazon Audio Player SDK 1.0, when playing a playlist, the
        currentToken always reports the next-up token, not the current token,
        so BE CAREFUL when interacting with playlists (logic in the
        battle.Scenario accounts for this behavior, so queries through that obj
        will result in the correct values and actions).

        Setting this property does not automatically update the DB. Updates
        will be up to the user. Typically this property changes frequently
        during playback and is only stored upon skill exit.

        Returns:
            str: The token of the current (or next, see warning above) audio
                file. A sample Dart Battle audio token might resemble:
                "session_02.01.1.1_track_01_playlist_01.00_02.02.90_03.14_04.02.30_05.22"
                Which would indicate the following information about the track:
                rank02, arctic01, sfx1, sndtrk1, current track01, 1:intro,
                2:sndtrk90s, 3:event14, 4:sndtrk30s, 5:outtro

        """
        if not self.attributes.get("currentToken"):
            self._sessionAttributes["currentToken"] = \
                    self._handlerInput.request_envelope.request.token
        return self._sessionAttributes["currentToken"]

    @currentToken.setter
    def currentToken(self, value):
        self._sessionAttributes["currentToken"] = value

    @property
    def lastRun(self):
        """The datetime that the user last started Dart Battle.

        Setting this property will not result in the database being updated.
        Updates to the database are up to the user.

        Returns:
            str: The datetime that the session was last run.

        """
        if not self.attributes.get("lastRun"):
            lastRun = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            self._sessionAttributes["lastRun"] = lastRun
        return self._sessionAttributes["lastRun"]

    @lastRun.setter
    def lastRun(self, value):
        self._sessionAttributes["lastRun"] = value

    @property
    def monetizationData(self):
        """A list of in skill-products associated with Dart Battle.

        The response is of type ask_sdk_model.services.monetization.
            in_skill_products_response.InSkillProductsResponse
        which can be a bit of a beast (TODO: make this response more user-
        friendly). Through this, we can check to see which products the
        user has or has not purchased.

        This property is read-only.

        Returns:
            ask_sdk_model.services.monetization.in_skill_products_response.
                InSkillProductsResponse: The Amazon object containing
                monetization data.

        """
        if self._monetizationData:
            return self._monetizationData
        return self.populateMonetizationData()

    @property
    def numBattles(self):
        """The number of battles invoked by the user throughout history.

        Setting this property will not result in an update to the database.
        Updates to the database are left up to the user. Typically this is
        updated once the user starts a new battle or after a protocol is
        enabled.

        Returns:
            str: The number of battles invoked by the user since the beginning
                of time. (Why a string? Because of the way that our DynamoDB
                is set up. TODO: this could/should be changed some day)

        """
        if not self.attributes.get("numBattles"):
            self._sessionAttributes["numBattles"] = "0"
        return self._sessionAttributes["numBattles"]

    @numBattles.setter
    def numBattles(self, value):
        self._sessionAttributes["numBattles"] = value

    @property
    def offsetInMilliseconds(self):
        """The audio offset of the current track in milliseconds.

        In order to resume playback of an audio track from where it left off,
        one must know the audio offset of that track relative to the start of
        the track (0 milliseconds). This information is provided by the Audio
        Player, and this property makes it easy to query.

        Setting this property will not result in an update to the database.
        Updates to the database are left up to the user. Typically this is
        updated when the playback of a track is stopped or paused or the skill
        is exited.

        Returns:
            str: The audio offset in milliseconds (why a str? Because of the
                way that our DynamoDB is set up. TODO: alter the DB some day
                to store int for this value).

        """
        if not self.attributes.get("offsetInMilliseconds"):
            self._sessionAttributes["offsetInMilliseconds"] = "0"
        return self._sessionAttributes["offsetInMilliseconds"]

    @offsetInMilliseconds.setter
    def offsetInMilliseconds(self, value):
        self._sessionAttributes["offsetInMilliseconds"] = value

    @property
    def playerRank(self):
        """Enum representing the user's current rank.

        See rank.py for more information on ranks.

        Setting this property does result in the updating of the database with
        the new value, but only if the value differs from what is currently
        stored.

        Returns:
            str: The enum representing the user's current rank. (Why a string?
                because of the way that our DynamoDB is constructed. Also
                because it allows for padding, if we care about that)

        """
        if not self.attributes.get("playerRank"):
            self._sessionAttributes["playerRank"] = "00"
        return self._sessionAttributes["playerRank"]

    @playerRank.setter
    def playerRank(self, value):
        if "playerRank" in self.attributes:
            if self._sessionAttributes.get("playerRank") == value:
                return
            self._sessionAttributes["playerRank"] = value
            database.updateRecordAttr(self.session, "playerRank", value)
            return
        self._sessionAttributes["playerRank"] = value

    @property
    def playerRoles(self):
        """The roles in use by each team.

        When teams are formed, player roles are distributed to all players, and
        the resulting assignments are stored. This property allows access to
        those assignments so that we can tell what roles are in use (thereby
        invoking appropriate events for the team).

        The roles should be formatted in a dict with the key being the team
        number (starting from 1 and up) and the values being lists of strings
        representing the enums of the roles in use. An example:
        {1: ["01", "05"], 2: ["01", "03"]}

        Setting this property does not currently perform any checks on the
        incoming data structure, and does not result in the database being
        updated. Database updates are up to the user. Typically, this property
        changes when new teams are formed, or teams are shuffled.

        Returns:
            {int: [str]}: A dict of team numbers and corresponding role enums.

        """
        if not self.attributes.get("playerRoles"):
            self._sessionAttributes["playerRoles"] = {}
        return self._sessionAttributes["playerRoles"]

    @playerRoles.setter
    def playerRoles(self, value):
        self._sessionAttributes["playerRoles"] = value

    @property
    def protocolCodes(self):
        """The protocol codes, if any, that have been enabled, with values.

        Protocols (secret codes that unlock in-game content) have titles, and
        when enabled, typically write a datetime of when it was enabled. If
        that protocol is ever disabled, it usually receives a string value of
        "False". And example record might look like:
        {"telemetry": "11/29/2018"}

        Setting this property does not result in a database update. Database
        updates are up to the user. This typically gets set when a protocol is
        enabled or disabled.

        Returns:
            {str: str}: The protocol codes, along with their values.

        """
        if not self.attributes.get("protocolCodes"):
            self._sessionAttributes["protocolCodes"] = {}
        return self._sessionAttributes["protocolCodes"]

    @protocolCodes.setter
    def protocolCodes(self, value):
        self._sessionAttributes["protocolCodes"] = value

    @property
    def recentSession(self):
        """Whether or not the user has recently invoked a Dart Battle session.

        "Recent" in this case is currently set to any time in the last 24 hours
        (although this may be prone to being changed in database.py).  If the
        user has invoked a session any time within the window, this returns
        "True", otherwise it returns "False" (why strings and not bool? Because
        of how the DynamoDB is structured).  This allows us to make decisions
        about greetings and promotions, to ensure that content is customized
        for the user.

        Setting this property does not result in a database update. Database
        updates are up to the user. This typically changes as soon as a user
        invokes the skill and the database is queried.

        Returns:
            str: "True" if a session had been invoked in the last 24 hours,
                "False" otherwise.

        """
        if not self.attributes.get("recentSession"):
            self._sessionAttributes["recentSession"] = "False"
        return self._sessionAttributes["recentSession"]

    @recentSession.setter
    def recentSession(self, value):
        self._sessionAttributes["recentSession"] = value

    @property
    def request(self):
        """Convenience object for accessing the request envelope.

        This property cannot be set.

        Returns:
            ask_sdk_core.handler_input.request_envelope: The request envelope
                as provided by Amazon Alexa.

        """
        return DartBattleRequest(self._handlerInput.request_envelope)

    @property
    def sfx(self):
        """Whether or not sound effects are enabled for the session.

        This property stores and returns strings, due to the way that our
        DynamoDB table was set up.

        Setting this property does not result in a database update. Database
        updates are up to the user to perform. This typically changes if the
        user asks to enable or disable sound effects. (That ability may or may
        not be currently supported; audio tracks with music but without sfx
        would need to be created)

        Returns:
            str: "True" if sound effects are enabled, "False" otherwise.

        """
        if not self.attributes.get("sfx"):
            self._sessionAttributes["sfx"] = "True"
        return self._sessionAttributes["sfx"]

    @sfx.setter
    def sfx(self, value):
        self._sessionAttributes["sfx"] = value

    @property
    def soundtrack(self):
        """Whether or not soundtracks are enabled for the session.

        This property stores and returns strings, due to the way that our
        DynamoDB table was set up.

        Setting this property does not result in a database update. Database
        updates are up to the user to perform. This typically changes if the
        user asks to enable or disable soundtracks. (That ability may or may
        not be currently supported; audio tracks with sfx but without music
        would need to be created)

        Returns:
            str: "True" if soundtracks are enabled, "False" otherwise.

        """
        if not self.attributes.get("soundtrack"):
            self._sessionAttributes["soundtrack"] = "True"
        return self._sessionAttributes["soundtrack"]

    @soundtrack.setter
    def soundtrack(self, value):
        self._sessionAttributes["soundtrack"] = value

    @property
    def teams(self):
        """The teams, their players, and the roles assigned to the players.

        The data is structured as a dict with a team number key, a value of
        another dict with the player number, and the value of the role assigned
        to that player. An example resembles:
        {1: {"player 1": "explosives_expert", "player 4": "captain"}, 2:...}

        Setting this property does not result in a database update. Database
        updates would be up to the user. This value usually changes when teams
        are created or shuffled.

        Returns:
            {dict}: A nested dictionary with keys representing team numbers and
                value representing the chosen players and assigned roles.

        """
        if not self.attributes.get("teams"):
            self._sessionAttributes["teams"] = {}
        return self._sessionAttributes["teams"]

    @teams.setter
    def teams(self, value):
        self._sessionAttributes["teams"] = value

    @property
    def userId(self):
        """The unique ID issued to the user by Amazon.

        This ID is persistent over the lifetime of the skill. If the skill is
        ever disabled by the user and re-enabled, the user's ID will change.
        This unique value is used by the DynamoDB as the key for the database
        item containing all values pertinent to the user.

        Setting this property does not result in a database update. Database
        updates are up to the user. This property is typically only set once
        in a lifetime, when a new user starts up the skill for the first time.

        Returns:
            str: A very long string beginning with "amzn1.ask.account." unique
                per user.

        """
        if not self.attributes.get("userId"):
            self._sessionAttributes["userId"] = \
                self._sessionAttributes['context']['System']['user']['userId']
        return self._sessionAttributes["userId"]

    @userId.setter
    d
    "DartBattleRequest",ef userId(self, value):
        self._sessionAttributes["userId"] = value

    @property
    def usingEvents(self):
        """Whether or not events are enabled for the session.

        This property stores and returns strings, due to the way that our
        DynamoDB table was set up.

        Setting this property does result in a database update. This typically
        changes if the user asks to enable or disable events.

        Returns:
            str: "True" if events are enabled, "False" otherwise.

        """
        if not self.attributes.get("usingEvents"):
            self._sessionAttributes["usingEvents"] = "True"
        return self._sessionAttributes["usingEvents"]

    @usingEvents.setter
    def usingEvents(self, value):
        self._sessionAttributes["usingEvents"] = value
        database.updateToggleEvents(self)

    @property
    def usingTeams(self):
        """Whether or not teams are enabled for the session.

        This property stores and returns strings, due to the way that our
        DynamoDB table was set up.

        Setting this property does not result in a database update. Database
        updates are up to the user to perform. This typically changes if the
        user asks to enable or disable teams.

        Returns:
            str: "True" if teams are enabled, "False" otherwise.

        """
        if not self.attributes.get("usingTeams"):
            self._sessionAttributes["usingTeams"] = "False"
        return self._sessionAttributes["usingTeams"]

    @usingTeams.setter
    def usingTeams(self, value):
        self._sessionAttributes["usingTeams"] = value

    @property
    def victories(self):
        """The victories per player with their dates and times.

        This is a potentially giant list of all players who has ever had a
        victory associated with them. Victories have a datetime associated with
        them so that we can identify daily totals, etc.  An example resembes:
        {"Jonah": {0: "2019.01.11 15:30:36", 1: "2018.11.19 12:30:27"}, "Owen"...}

        Setting this property does not update the database. Database updates
        are up to the user to perform. This property typically changes when the
        user asks to record or delete a victory.

        Returns:
            {dict}: A nested dict with player names as keys, values being an
                ascending integer as a key with a value of the datetime for the
                victory.

        """
        if not self.attributes.get("victories"):
            self._sessionAttributes["victories"] = {}
        return self._sessionAttributes["victories"]

    @victories.setter
    def victories(self, value):
        self._sessionAttributes["victories"] = value

    def populateAttrs(self):
        """Populates all properties and attributes of this object.

        This leverages the current session information available to us through
        the handler_input passed in from Amazon Alexa, and also through the
        persistent data stored in the database.  Sometimes this is called via
        an audio event (such as next or previous track), in which case the
        handler_input lacks a lot of information. In that case, we only
        update the audio token from the handler_input information.

        Returns:
            dict: The entire dictionary of known attributes, upon which the
                properties of the object are based.

        """
        self._sessionAttributes = \
            self._handlerInput.attributes_manager.request_attributes
        self._sessionAttributes["userId"] = \
            self._handlerInput.request_envelope.context.system.user.user_id
        dbAttrs = database.getSessionFromDB(self)
        for attrName in dbAttrs:
            if not self._sessionAttributes.get(attrName):
                self._sessionAttributes[attrName] = dbAttrs[attrName]
        if self._handlerInput.request_envelope.session:
            self._handlerInput.attributes_manager.session_attributes = \
                self._sessionAttributes
        else:
            # This is a non-session request; almost certainly triggered by an
            #  audio event. Update token to current:
            self.currentToken = self._handlerInput.request_envelope.request.token
        return self._sessionAttributes

    def populateMonetizationData(self):
        """Does the work to retrieve monetization data for Dart Battle.

        Monetization data includes available premium content and information on
        whether or not the user has purchased them.

        In the alpha for monetization, with which this was first authored,
        there were enormous problems with Amazon's monetization service,
        frequently resulting in a ServiceException, and therefore, a try/except
        exists to catch and report those instances. A forum conversation for
        this problem was opened at:

        https://amazon.developer.forums.answerhub.com/questions/
            185823/serviceexception-in-get-in-skill-products-error-40.html

        Returns:
            ask_sdk_model.services.monetization.in_skill_products_response.
                InSkillProductsResponse

        """
        try:
            locale = self._handlerInput.request_envelope.request.locale
            monServ = \
                self._handlerInput.service_client_factory.get_monetization_service()
            self._monetizationData = monServ.get_in_skill_products(locale)
            LOGGER.info("Monetization service success!")
            return self._monetizationData
        except ServiceException as e:
            msg = "(!!!): ServiceException received from Monetization Service: {}"
            msg = msg.format(e.message)
            LOGGER.warning(msg)

    def setAudioState(self, currentToken, offsetInMilliseconds):
        """Updates the audio state with the current token and offset.

        Calling this results in a database update.

        Args:
            currentToken (str): The currently playing audio track's token.

            offsetInMilliseconds (int): The current offset of the current audio
                track in milliseconds from the start of the track (0).

        """
        if currentToken:
            self.currentToken = currentToken
        if offsetInMilliseconds:
            self.offsetInMilliseconds = offsetInMilliseconds
        database.updateRecordToken(self)
