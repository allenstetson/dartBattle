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
playlists.py - Audio track and speech playlists for use throughout the skill.

"""
# std lib imports:
import logging
import random

# Amazon imports:
from ask_sdk_model.services.monetization import EntitledState

# Dart Battle imports:
import protocols
import rank


__all__ = [
    'getRankPromotionFile',
    'Greeting',
    'Playlist',
    'Arctic',
    'NoEvents01',
    'Prospector'
]

# The whole point of this module is to issue URLs which are mostly quite long,
#  and as a result, the line-length rule is oft-violated in this module.
#  Therefore, disabling this check so that other errors are noticed:
# pylint: disable=line-too-long

# =============================================================================
# Globals
# =============================================================================
DBS3_URL = "https://s3.amazonaws.com/dart-battle-resources/"

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)


# =============================================================================
# Functions
# =============================================================================
def getRankPromotionFile(userRank):
    """Gets the promotion audio for the appropriate rank when a user advances.

    Args:
        userRank (int): The rank enum for which to fetch the promotion audio.

    Returns:
        str: The url to the correct promotion audio file.

    """
    userRank = int(userRank)
    rankFile = DBS3_URL + 'common/common_Any_{:02d}_RankPromotion_Any_00.mp3'
    rankFile = rankFile.format(userRank)
    return rankFile


# =============================================================================
# Classes
# =============================================================================
class Greeting(object):
    """
    Object containing all options for a greeting and logic for choosing them.

    This object contains greetings for special protocols (secret codes that
    unlock in-game content such as greetings), for team mode, individual mode,
    and for officers.

    Logic will determine which greetings fit best based on the user session
    data, and a random choice from those greetings will be returned.

    This ensures that a variety of greetings, seemingly tailored for the user,
    are available to enrich the user's experience.

    Args:
        userSession (session.DartBattleSession): an object with properties
            representing all slots, values, and information from the user's
            session, including user ID, Audio Directive state, etc.

    """
    def __init__(self, userSession):
        self.session = userSession
        self.crowsNestGreetings = [
            "Scanning biometric data for field soldiers. Increased pulse " +\
                    "detected. Initiating battle sequence. Awaiting orders. ",
            "Initiating secure uplink to satellite. Uplink acquired, " +\
                    "handshake initiated. Combat interface ready for instruction. ",
            "Stitching battlefield photogrammetry. Closing edge loops and " +\
                    "interpolating surface points. Battlefield metrics have " +\
                    "been distributed to combat vehicles and qualifying " +\
                    "infantry. Standing by.",
            "Reboot complete. Repairing damage to central targeting " +\
                    "systems. Unit tests passed. Awaiting instruction.",
            "Damage sustained. Artillery servos 8 and 12 are offline. " +\
                    "Electromagnetic shield operating at reduced levels. " +\
                    "Ready for input.",
            "Enemy activity detected. Raising defensive perimeter. Sealing " +\
                    "entrances on levels Charlie through Foxtrot. Further " +\
                    "instruction required from authorized personnel."
        ]
        self.madDogGreetings = [
            "<audio src='" + DBS3_URL + "protocols/madDog/protocol_MadDog_00_Greeting_Dance_Any_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "protocols/madDog/protocol_MadDog_00_Greeting_Diaper_Any_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "protocols/madDog/protocol_MadDog_00_Greeting_Disappointment_Any_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "protocols/madDog/protocol_MadDog_00_Greeting_DontCry_Any_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "protocols/madDog/protocol_MadDog_00_Greeting_Malfunction_Any_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "protocols/madDog/protocol_MadDog_00_Greeting_Smell_Any_00.mp3' /> "
        ]
        self.noTeamGreetingsStandard = [
            "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_StandardA_NoTeam_00.mp3' /> ",
        ]
        self.noTeamGreetingsQuick = [
            "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_QuickA_NoTeam_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_QuickB_NoTeam_00.mp3' /> ",
        ]
        self.officerGreetings = [
            "<audio src='" + DBS3_URL + "common/common_Any_{:02d}_Greeting_WelcomeBackA_Any_00.mp3' /> "
        ]
        self.officerGreetingHead = "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_AttnOfficerA_Any_00.mp3' /> "
        self.officerGreetingTail = "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_AtEaseA_Any_00.mp3' /> "
        self.teamGreetingsStandard = [
            "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_StandardA_Team_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_StandardB_Team_00.mp3' /> ",
        ]
        self.teamGreetingsQuick = [
            "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_QuickA_Team_00.mp3' /> ",
            "<audio src='" + DBS3_URL + "common/common_Any_00_Greeting_QuickB_Team_00.mp3' /> ",
        ]

    def getGreeting(self):
        """Determines the best greeting to play based on user session data.

        This method keeps a list of applicable greetings based on whether the
        skill is running in team mode or not, whether various protocols are
        enabled, and whether or not the user is high enough rank to be
        considered an officer.

        It then makes a random choice from the list and returns that as the
        greeting to be played.

        Returns:
            str: The speech, sometimes with audio URL, to play as a greeting.

        """
        greetings = []
        if self.session.recentSession == "True":
            if self.session.usingTeams == "True":
                # Recent Teams
                greetings.extend(self.teamGreetingsQuick)
            else:
                # Recent Individual
                greetings.extend(self.noTeamGreetingsQuick)
        else:
            if self.session.usingTeams == "True":
                # Not recent Teams
                greetings.extend(self.teamGreetingsStandard)
            else:
                # Not recent Individual
                greetings.extend(self.noTeamGreetingsStandard)

        # Officer greetings
        if int(self.session.playerRank) > 0:
            officerGreetings = []
            for track in self.officerGreetings:
                track = track.format(int(self.session.playerRank))
                officerIntro = random.randint(0, 2)
                if officerIntro == 2 and int(self.session.playerRank) > 5:
                    track = "{}{}{}".format(
                        self.officerGreetingHead,
                        track,
                        self.officerGreetingTail
                        )
                officerGreetings.append(track)
            greetings.extend(officerGreetings)

        # Protocol greetings
        if protocols.ProtocolCrowsNest(self.session).isActive:
            greetings.extend(self.crowsNestGreetings)
        if protocols.ProtocolMadDog(self.session).isActive:
            greetings.extend(self.madDogGreetings)

        # Final selection
        selection = random.choice(greetings)
        return selection


class Playlist(object):
    """The base object for all playlists that serve audio for scenarios.

    Playlists consist of the following properties:
      * events: A list of all possible tracks that could be played as events
            during a scenario.
      * inCount: A track to be played immediately before the battle begins,
            counting down the number of seconds until the start.
      * outCount: A track to be played which counts down until the end of the
            scenario, letting players know that their game is ending.
      * outtro: A track to play after the conclusion of the game, reminding
            players to cease fire, count up the eliminations, and record
            victories.
      * outtroTeams: A track to play after the conclusion of the game if we
            are in team mode, reminding teams to cease fire, count up the
            eliminations, and record team victories.
      * prettyName: The pretty, public name of the scenario (used for
            display cards).
      * promo: A random, weighted promotional track to be played as the very
            first track while the scenario "loads". This track reminds users of
            some potentially overlooked features, informs them of charitable
            donations, points them to the Dart Battle social media outlets,
            reminds them of safety practices, and more.
      * soundtrack: A URL to music that can be used during the scenario. This
            URL most likely has a placeholder for formatting the duration of
            the desired track in seconds (30, 60, 90, etc).
      * tail: The absolutely final track to play before the skill exits due to
            the Audio Player rules set forth by Amazon which prevent a skill
            from starting/resuming after finishing a playlist until explicitly
            invoked by the user. This track reminds users to rate the Dart
            Battle skill in the skill store.

    """
    def __init__(self):
        self._events = []
        self.inCount = DBS3_URL + "common/inCount_Any_00_YourBattleBegins_Any_00.mp3"
        self.soundtrack = ""
        self.outCount = ""
        self.outtro = ""
        self.outtroTeams = ""
        self.prettyName = "Default Playlist"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def events(self):
        """A list of all tracks appropriate for playing as an event.

        A scenario playlist that subclasses this object will maintain a list
        in the private variable self._events which this property method will
        use to seed the events list. Events often have a format placeholder
        for an integer representing the rank enum. This property method formats
        each track for each valid enum and appends them to the list.

        returns:
            [str]: a list of URL strings representing all appropriate tracks
                from which to choose for an event.

        """
        allEvents = []
        for event in self._events:
            for i in range(len(rank.rankRequirements)):
                allEvents.append(event.format(i))
        return allEvents

    @property
    def promo(self):
        """A track to play as a promotion before the battle scenario loads.

        This property method will construct a weighted list of promotions,
        applicable to all scenarios, and then return a random choice from that
        list. It is possible to return no promotion, which keeps users from
        expecting and therefore ignoring promotions every time.

        """
        promos = [
            DBS3_URL + "scenarios/promos/promo_Any_00_AudioDirectives_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_ClearTeams_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_DisableEvents_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_Facebook_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_HowDoIPlay_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_HowMoreScenarios_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_HowMoreScenarios_B.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_QuickTeamSetup_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_RankPromotion_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_RememberRoles_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_SafetyReminder_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_SafetyReminder_B.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_ShuffleTeams_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_TeamMode_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_VisualOutput_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_Charity_A.mp3",
            # Duplicates for weighting
            DBS3_URL + "scenarios/promos/promo_Any_00_Facebook_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_HowMoreScenarios_A.mp3",
            DBS3_URL + "scenarios/promos/promo_Any_00_HowMoreScenarios_B.mp3",
            # NoneTypes for the chance that no Promotion takes place.
            None,
            None,
            None,
            None,
            None,
        ]
        return random.choice(promos)

    @property
    def tail(self):
        """The absolutely final track to be played at the end of a scenario.

        Amazon prevents a skill from restarting or resuming after a playlist
        is finished playing in the Audio Player. The skill will end once a
        playlist concludes. Immediately prior to ending, this track is played.
        It is either a NoneType which indicates that there is no track to be
        played, or it is a reminder to rate Dart Battle in the Amazon Skill
        Store.

        returns:
            str: The URL to the track (if any) to be played as a tail. NoneType
                if no tail is to be played.

        """
        tails = [
            DBS3_URL + "common/common_Any_00_Tail_RateUsA_Any_00.mp3",
            # NoneTypes for the chance that no Tail takes place.
            None,
            None,
            None
        ]
        return random.choice(tails)

    # -------------------------------------------------------------------------
    # PRIVATE METHODS
    # -------------------------------------------------------------------------
    def _getEventsWithCategory(self, eventCategory, tracks=None):
        """Chooses events based on categories.

        Events can have a specified category such as "TagManyToOne", "retreat",
        "pairUp", etc. This method allows for the selection of events based on
        that category.

        Args:
            eventCategory (str): The string name of the category desired.

            tracks ([str]): A list of tracks from which to choose (optional).

        Returns:
            [str]: a list of URLs to tracks that match the desired category.

        """
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if eventCategory in x]
        return matches

    def _getEventsWithRoles(self, roles, tracks=None):
        """Chooses events based on roles.

        Events can have a specified role enum such as 9 for Medic, 13 for
        Sniper, or 6 for Heavy Weapons Expert.This method allows for the
        selection of events based on given role enums.

        Args:
            roles ([str]): One or more role enums that must be present in a
                track URL for that track to be valid.

            tracks ([str]): A list of tracks from which to choose (optional).

        Returns:
            [str]: a list of URLs to tracks that match the desired roles.

        """
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if roles in x]
        return matches

    def _getEventsWithTeamToken(self, teamToken, tracks=None):
        """Chooses events based on team token ("Team", "NoTeam" or "Any").

        Events can be made with teams in mind and some can only be relevant
        when played during individual play. Some work for both modes. The URL
        for the event will specify their relevance with a token, and this
        method allows for the selection of events based on the desired token.

        Args:
            teamToken (str): The desired team mode ("Team", "NoTeam", or "Any")

            tracks ([str]): A list of tracks from which to choose (optional).

        Returns:
            [str]: a list of URLs to tracks that match the desired token.

        """
        teamToken = "_{}_".format(teamToken)
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if teamToken in x]
        return matches

    def _getEventsWithTitle(self, eventTitle, tracks=None):
        """Chooses events based on event title.

        Every event has a title which describes it. This can be
        "LayDown_Avalanche", or "Duel_EqualMatch", "ExclusiveShot_CoverFire",
        etc. This  method allows for the selection of events based on the
        desired title.

        Args:
            eventTitle (str): The desired event title.

            tracks ([str]): A list of tracks from which to choose (optional).

        Returns:
            [str]: a list of URLs to tracks that match the desired title.

        """
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if eventTitle in x]
        return matches

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------
    def getEventsForRank(self, userRank):
        """Gets a list of all event tracks appropriate for a given player rank.

        Events are almost always customized for a particular player rank,
        ensuring that the player is addressed by the appropriate rank title
        during play. This lends an impression of a gameplay specifically
        tailored to the player, as well as provides value to a player advancing
        in rank.

        This method will cull the list of available event tracks, removing
        tracks that call the player by an inaccurate title.

        Args:
            userRank (int): The enum representing the user's current rank.

        Returns:
            [str]: a list of URLs for tracks appropriate to play as events
                for the user of this rank.

        """
        allEvents = []
        for event in self._events:
            allEvents.append(event.format(int(userRank)))
        return allEvents

    def getEventWithProperties(self, userRank=None, eventCategory=None,
                               eventTitle=None, teamToken=None, roles=None):
        """Gets events that match incoming properties and returns one.

        Generally, this method is called with all properties specified, and
        only one track should match all incoming properties. However, should
        more than one match be found, a warning is logged and the first one
        found is returned.

        Args:
            userRank (int): The enum representing the user's current rank.

            eventCategory (str): The desired category of event ("duel", etc.).

            eventTitle (str): The title of the event ("Duel_EqualMatch", etc.).

            teamToken (str): The current team mode that the event needs to
                fulfill ("Team", "NoTeam", "Any").

            roles ([int]): The enums for one or more roles that the event needs
                to apply to (6 for "Heavy Weapons Expert", etc.).

        Returns:
            str: The URL to the event track to be played which matches the
                incoming criteria.

        """
        userRank = userRank or '00'

        def filterTracksWithRank(uRank):
            """Reduces full list of tracks to only tracks with specified rank.

            Args:
                uRank (int): The user rank; the enum representing the user's
                    current rank.

            Returns:
                [str]: A list of qualified tracks, corresponding to the given
                    rank.

            """
            rankTracks = self.getEventsForRank(uRank)

            eventTracks = self._getEventsWithCategory(eventCategory, tracks=rankTracks)
            if not eventTracks:
                eventTracks = self._getEventsWithCategory(eventCategory)
            if not eventTracks:
                return None

            titleTracks = self._getEventsWithTitle(eventTitle, tracks=eventTracks)
            if not titleTracks:
                return None

            teamTokenEvents = self._getEventsWithTeamToken(teamToken, tracks=titleTracks)
            if not teamTokenEvents:
                teamTokenEvents = self._getEventsWithTeamToken("Any", titleTracks)
            if not teamTokenEvents:
                return None

            finalSelections = self._getEventsWithRoles(roles, tracks=teamTokenEvents)
            if not finalSelections:
                return None

            return finalSelections
        selections = filterTracksWithRank(userRank)
        if not selections:
            selections = filterTracksWithRank('00')
        if not selections:
            return None
        if len(selections) > 1:
            msg = ("WARNING! More than one track matched "
                   "getEventWithProperties:\nProperties: userRank, {}; "
                   "eventCategory, {}; eventTitle, {}; teamToken, {}; "
                   "roles, {}\nTracks: {}\nUsing first one found.")
            msg = msg.format(
                userRank,
                eventCategory,
                eventTitle,
                teamToken,
                roles,
                selections
                )
            LOGGER.warning(msg)
        selection = selections[0]
        return selection

    @staticmethod
    def getIntro(userRank=None, variant=None):
        """Selects an introductory track to be played for a scenario.

        A scenario can have multiple variants which contribute to the variety
        of available games and increases replay value. This method not only
        selects an introductory track, but also returns a designation of the
        chosen variant (A, B, C) which can be used in Audio Player track tokens
        and leveraged to keep a consistency between tracks. For instance, a
        scenario with a variant of B for the intro may also have a B variant
        for the outCount or outtro which may accompany the intro.

        TODO: Move the definition of the intros to the __init__ method,
        allowing objects that subclass this to leverage this logic without
        reimplementing this method.

        Args:
            userRank (int): The enum representing the user's current rank.

            variant (str): The variant chosen for this scenario (A, B, C), if
                known.

        Returns:
            str, str: The variant chosen for this scenario (A, B, C), and the
                URL to the track to play as the introduction for this scenario.

        """
        intros = {
            "A": "",
        }
        if not variant:
            randKey = random.choice(list(intros.keys()))
            randTrack = intros[randKey].format(int(userRank))
            return randKey, randTrack
        return variant, intros[variant].format(int(userRank))

    @staticmethod
    def isActive(userSession):
        """Whether or not the current scenario is available to the user.

        A variety of conditions could mean that the current scenario is or is
        not available to a user. It might be premium content which the user has
        not yet paid for. It could be a scenario containing events when the
        user has disabled events, etc.

        Args:
            userSession (session.DartBattleSession): an object with properties
                representing all slots, values, and information from the user's
                session, including user ID, Audio Directive state, etc.

        Returns:
            bool: whether or not this scenario is available to the user.

        """
        usingEvents = userSession.usingEvents
        if usingEvents == "True":
            return True
        return False


class Arctic(Playlist):
    """Playlist for the Arctic Defense scenario.

    Arctic Defense is the first scenario available to players for free when the
    skill is activated.

    Several tracks such as promos come from the base class, but all event,
    outtro and outCount tracks are specified by this class. This scenario
    supports two variants, A and B.

    """
    def __init__(self):
        super(Arctic, self).__init__()
        arcEventsURL = DBS3_URL + 'scenarios/arctic/events/'

        self._events = [
            arcEventsURL + 'ceaseFire/event_Arctic_{:02d}_CeaseFire_HeatSignature_Any_00.mp3',
            arcEventsURL + 'ceaseFire/event_Arctic_{:02d}_CeaseFire_IceBreak_Any_00.mp3',
            arcEventsURL + 'ceaseFire/event_Arctic_{:02d}_CeaseFire_Yeti_Any_00.mp3',
            arcEventsURL + 'dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_05.mp3',
            arcEventsURL + 'dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_06.mp3',
            arcEventsURL + 'dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_13.mp3',
            arcEventsURL + 'dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_14.mp3',
            arcEventsURL + 'holdOn/event_Arctic_{:02d}_HoldOn_Avalanche_Any_00.mp3',
            arcEventsURL + 'holdOn/event_Arctic_{:02d}_HoldOn_Blizzard_Any_00.mp3',
            arcEventsURL + 'holdOn/event_Arctic_{:02d}_HoldOn_IceBreak_Any_00.mp3',
            arcEventsURL + 'layDown/event_Arctic_{:02d}_LayDown_Avalanche_Any_00.mp3',
            arcEventsURL + 'layDown/event_Arctic_{:02d}_LayDown_Blizzard_Any_00.mp3',
            arcEventsURL + 'layDown/event_Arctic_{:02d}_LayDown_HeatSignature_Any_00.mp3',
            arcEventsURL + 'layDown/event_Arctic_{:02d}_LayDown_Yeti_Any_00.mp3',
            arcEventsURL + 'pairUp/event_Arctic_{:02d}_PairUp_Avalanche_Team_00.mp3',
            arcEventsURL + 'pairUp/event_Arctic_{:02d}_PairUp_Blizzard_Team_00.mp3',
            arcEventsURL + 'pairUp/event_Arctic_{:02d}_PairUp_Fog_Team_00.mp3',
            arcEventsURL + 'pairUp/event_Arctic_{:02d}_PairUp_Yeti_Team_00.mp3',
            arcEventsURL + 'protect/event_Arctic_{:02d}_Protect_Airlift_Team_10.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_01.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_02.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_03.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_04.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_05.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_06.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_07.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_08.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_09.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_10.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_11.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_12.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_13.mp3',
            arcEventsURL + 'protect/event_Arctic_00_Protect_KeyTeamMember_Team_14.mp3',
            arcEventsURL + 'reset/event_Arctic_00_Reset_TechnologyTimeTravel_NoTeam_00.mp3',
            arcEventsURL + 'reset/event_Arctic_00_Reset_TechnologyTimeTravel_Team_00.mp3',
            arcEventsURL + 'resupply/event_Arctic_{:02d}_Resupply_Reinforcements_Any_00.mp3',
            arcEventsURL + 'resupply/event_Arctic_{:02d}_Resupply_Yeti_Any_00.mp3',
            arcEventsURL + 'retreat/event_Arctic_{:02d}_Retreat_Avalanche_Any_00.mp3',
            arcEventsURL + 'retreat/event_Arctic_{:02d}_Retreat_Blizzard_Any_00.mp3',
            arcEventsURL + 'retreat/event_Arctic_{:02d}_Retreat_Fog_Any_00.mp3',
            arcEventsURL + 'retreat/event_Arctic_{:02d}_Retreat_IceBreak_Any_00.mp3',
            arcEventsURL + 'retreat/event_Arctic_{:02d}_Retreat_Yeti_Any_00.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_01.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_02.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_03.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_04.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_05.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_06.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_07.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_08.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_09.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_10.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_11.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_12.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_13.mp3',
            arcEventsURL + 'specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_14.mp3',
            arcEventsURL + 'shelter/event_Arctic_{:02d}_Shelter_Airstrike_Any_00.mp3',
            arcEventsURL + 'shelter/event_Arctic_{:02d}_Shelter_Avalanche_Any_00.mp3',
            arcEventsURL + 'splitUp/event_Arctic_{:02d}_SplitUp_IceBreak_Team_00.mp3',
            arcEventsURL + 'splitUp/event_Arctic_{:02d}_SplitUp_HeatSignature_Team_00.mp3',
            arcEventsURL + 'tagFeature/event_Arctic_00_TagFeature_AirstrikeCancel_Team_02.mp3',
            arcEventsURL + 'tagFeature/event_Arctic_{:02d}_TagFeature_BombDefuse_Team_04.mp3',
            arcEventsURL + 'tagFeature/event_Arctic_{:02d}_TagFeature_BombDefuse_Team_05.mp3',
            arcEventsURL + 'tagFeature/event_Arctic_{:02d}_TagFeature_ComputerHack_Team_02.mp3',
            arcEventsURL + 'tagFeature/event_Arctic_{:02d}_TagFeature_WeatherDoor_Team_08.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_00_TagManyToOne_NewOrders_Team_00.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_01.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_02.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_03.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_04.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_05.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_06.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_07.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_08.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_09.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_10.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_11.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_12.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_13.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_14.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_01.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_02.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_03.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_04.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_05.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_06.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_07.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_08.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_09.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_10.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_11.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_12.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_13.mp3',
            arcEventsURL + 'tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_14.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.01.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.02.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.03.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.04.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.05.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.06.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.07.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.08.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.10.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.11.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.12.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.13.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.14.mp3',
            arcEventsURL + 'tagOneToOne/event_Arctic_00_TagOneToOne_NewIntel_Team_07.mp3',
            arcEventsURL + 'zeroEliminations/event_Arctic_{:02d}_ZeroEliminations_HalfDamage_Team_00.mp3',
        ]

        self.soundtrack = DBS3_URL + "sndtrk/sndtrk_Arctic_Music_Sfx_{}s.mp3"
        self.outCount = DBS3_URL + "scenarios/arctic/outCounts/outCount_Arctic_00_YourBattleEnds_Any_00.mp3"
        self.outtro = DBS3_URL + "scenarios/arctic/outtros/outtro_Arctic_00_CeaseFire_NoTeam_00.mp3"
        self.outtroTeams = DBS3_URL + "scenarios/arctic/outtros/outtro_Arctic_00_CeaseFire_Team_00.mp3"
        self.prettyName = "Arctic Defense"

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------
    @staticmethod
    def getIntro(userRank=None, variant=None):
        """Selects an introductory track to be played for a scenario.

        This scenario supports two variants, A and B.

        Args:
            userRank (int): The enum representing the user's current rank.

            variant (str): The variant chosen for this scenario (A, B, C), if
                known.

        Returns:
            str, str: The variant chosen for this scenario (A, B, C), and the
                URL to the track to play as the introduction for this scenario.

        """
        intros = {
            "A": DBS3_URL + "scenarios/arctic/intros/intro_arctic_A_{:02d}_Any.mp3",
            "B": DBS3_URL + "scenarios/arctic/intros/intro_arctic_B_{:02d}_Any.mp3"
        }
        if not variant:
            randKey = random.choice(list(intros.keys()))
            randTrack = intros[randKey].format(int(userRank))
            return randKey, randTrack
        return variant, intros[variant].format(int(userRank))


class NoEvents01(Playlist):
    """Playlist for a scenario without any events.

    When a user disables events in Dart Battle, this is the scenario that is
    issued. It is based on Arctic Defense, playing the same soundtrack, but
    without any events.

    """
    def __init__(self):
        super(NoEvents01, self).__init__()
        self.soundtrack = DBS3_URL + "sndtrk/sndtrk_Arctic_Music_Sfx_{}s.mp3"
        self.outtro = DBS3_URL + "tail_NoTeam.mp3"
        self.outtroTeams = DBS3_URL + "tail_Team.mp3"
        self.prettyName = "NoEvents01"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def events(self):
        """Overrides any logic to choose events, just returns None."""
        return None

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------
    def getEventsForRank(self, userRank):
        """Overrides any logic to choose events for rank, just returns None."""
        return None

    @staticmethod
    def getIntro(userRank=None, variant=None):
        """Overrides any logic to choose an intro, just returns None."""
        return None, None

    @staticmethod
    def isActive(userSession):
        """Whether or not the current scenario is available to the user.

        This scenario is active only if events are disabled.

        Args:
            userSession (session.DartBattleSession): an object with properties
                representing all slots, values, and information from the user's
                session, including user ID, Audio Directive state, etc.

        Returns:
            bool: whether or not this scenario is available to the user.

        """
        usingEvents = userSession.usingEvents
        if usingEvents == "True":
            return False
        return True


class Prospector(Playlist):
    """Playlist for the Prospector's Predicament scenario.

    Prospector's Predicament is the first Premium Content scenario, available
    to users only if they have paid for the content.

    Several tracks such as promos come from the base class, but all event,
    outtro and outCount tracks are specified by this class. This scenario
    supports only one variant, A.

    """
    def __init__(self):
        super(Prospector, self).__init__()
        prosEventsURL = DBS3_URL + "scenario/prospector/events/"

        self._events = [
            prosEventsURL + "ceaseFire/event_Prospectors_00_CeaseFire_Bats_Any_00.mp3",
            prosEventsURL + "ceaseFire/event_Prospectors_00_CeaseFire_CaveIn_Any_00.mp3",
            prosEventsURL + "ceaseFire/event_Prospectors_00_CeaseFire_DynamiteCrate_Any_00.mp3",
            prosEventsURL + "ceaseFire/event_Prospectors_00_CeaseFire_LightsOut_Any_00.mp3",
            prosEventsURL + "ceaseFire/event_Prospectors_00_CeaseFire_ProtectGems_Any_00.mp3",
            prosEventsURL + "dropAndRoll/event_Prospectors_00_DropAndRoll_Dynamite_Any_00.mp3",
            prosEventsURL + "dropAndRoll/event_Prospectors_00_DropAndRoll_Lanterns_Any_00.mp3",
            prosEventsURL + "dropAndRoll/event_Prospectors_00_DropAndRoll_MolotovCocktail_Any_00.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.02.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.03.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.04.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.05.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.06.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.07.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.08.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.09.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.10.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.11.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.12.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.13.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_01.14.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_02.05.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_02.06.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_02.11.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_06.12.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_06.13.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_Dispute_Team_08.10.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.02.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.03.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.04.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.05.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.06.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.07.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.08.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.09.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.10.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.11.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.12.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.13.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_01.14.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_02.05.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_02.06.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_02.11.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_04.09.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_05.08.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_06.12.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_06.13.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_07.09.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_07.12.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_07.13.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_08.10.mp3",
            prosEventsURL + "duel/event_Prospectors_00_Duel_EqualMatch_Team_13.14.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_AlternatePath_Team_12.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_01.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_02.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_03.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_04.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_05.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_06.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_07.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_08.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_09.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_10.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_11.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_12.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_13.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_14.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_01.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_02.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_03.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_04.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_05.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_06.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_07.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_08.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_09.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_10.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_11.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_12.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_13.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_GatlingGun_Team_14.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_01.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_02.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_03.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_04.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_05.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_06.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_07.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_08.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_09.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_10.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_11.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_12.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_13.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_14.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_01.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_02.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_03.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_04.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_05.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_06.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_07.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_08.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_09.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_10.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_11.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_12.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_13.mp3",
            prosEventsURL + "exclusiveShot/event_Prospectors_00_ExclusiveShot_PrecisionGems_Team_14.mp3",
            prosEventsURL + "holdOn/event_Prospectors_00_HoldOn_CaveIn_Any_00.mp3",
            prosEventsURL + "holdOn/event_Prospectors_00_HoldOn_Earthquake_Any_00.mp3",
            prosEventsURL + "holdOn/event_Prospectors_00_HoldOn_FlashFlood_Any_00.mp3",
            prosEventsURL + "layDown/event_Prospectors_00_LayDown_Bats_Any_00.mp3",
            prosEventsURL + "layDown/event_Prospectors_00_LayDown_GatlingGun_Any_00.mp3",
            prosEventsURL + "layDown/event_Prospectors_00_LayDown_SmokeOut_Any_00.mp3",
            prosEventsURL + "pairUp/event_Prospectors_00_PairUp_LightsOut_Team_00.mp3",
            prosEventsURL + "pairUp/event_Prospectors_00_PairUp_SmokeOut_Team_00.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_AlternatePath_Team_12.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_01.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_02.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_03.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_04.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_05.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_06.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_07.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_08.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_09.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_10.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_11.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_12.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_13.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_Defuse_Team_14.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_01.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_02.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_03.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_04.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_05.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_06.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_07.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_08.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_09.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_10.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_11.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_12.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_13.mp3",
            prosEventsURL + "protect/event_Prospectors_00_Protect_WeakenTheStructure_Team_14.mp3",
            prosEventsURL + "reset/event_Prospectors_00_Reset_HallOfGems_Any_00.mp3",
            prosEventsURL + "resupply/event_Prospectors_00_Resupply_OutOfAmmo_Any_00.mp3",
            prosEventsURL + "retreat/event_Prospectors_00_Retreat_CaveIn_NoTeam_00.mp3",
            prosEventsURL + "retreat/event_Prospectors_00_Retreat_CaveIn_Team_00.mp3",
            prosEventsURL + "retreat/event_Prospectors_00_Retreat_FlashFlood_NoTeam_00.mp3",
            prosEventsURL + "retreat/event_Prospectors_00_Retreat_FlashFlood_Team_00.mp3",
            prosEventsURL + "retreat/event_Prospectors_00_Retreat_GatlingGun_Any_00.mp3",
            prosEventsURL + "shelter/event_Prospectors_00_Shelter_Bats_Any_00.mp3",
            prosEventsURL + "shelter/event_Prospectors_00_Shelter_CaveIn_Any_00.mp3",
            prosEventsURL + "shelter/event_Prospectors_00_Shelter_Earthquake_Any_00.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_BackRoute_Team_12.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_DynamiteDanger_Team_05.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_01.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_02.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_03.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_04.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_05.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_06.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_07.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_08.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_09.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_10.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_11.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_12.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_13.mp3",
            prosEventsURL + "specificTarget/event_Prospectors_00_SpecificTarget_WeakSupports_Team_14.mp3",
            prosEventsURL + "splitUp/event_Prospectors_00_SplitUp_AlternatePath_Any_00.mp3",
            prosEventsURL + "splitUp/event_Prospectors_00_SplitUp_Bats_Any_00.mp3",
            prosEventsURL + "splitUp/event_Prospectors_00_SplitUp_GatlingGun_Any_00.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_01.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_02.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_03.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_04.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_05.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_06.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_07.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_08.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_09.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_10.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_11.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_12.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_13.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_CoverOfDarkness_Team_14.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_01.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_02.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_03.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_04.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_05.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_06.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_07.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_08.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_09.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_10.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_11.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_12.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_13.mp3",
            prosEventsURL + "tagFeature/event_Prospectors_00_TagFeature_FloodDoor_Team_14.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_01.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_02.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_03.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_04.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_05.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_06.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_07.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_08.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_09.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_10.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_11.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_12.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_13.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DistributeDynamite_Team_14.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DugIn_Team_06.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DugIn_Team_07.mp3",
            prosEventsURL + "tagManyToOne/event_Prospectors_00_TagManyToOne_DugIn_Team_14.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.01.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.02.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.03.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.04.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.05.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.06.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.07.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.08.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.10.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.11.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.12.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.13.mp3",
            prosEventsURL + "tagOneToOne/event_Prospectors_00_TagOneToOne_FetchTheDoc_Team_09.14.mp3",

        ]
        self.soundtrack = DBS3_URL + "scenarios/prospector/sndtrk/sndtrk_OldWest_Music_Sfx_{}s.mp3"
        self.outCount = DBS3_URL + "scenarios/prospector/outCounts/outCount_Prospectors_00_YourBattleEnds_Any_00.mp3"
        self.outtro = DBS3_URL + "scenarios/prospector/outtros/outtro_Prospectors_00_CeaseFire_NoTeam_00.mp3"
        self.outtroTeams = DBS3_URL + "scenarios/prospector/outtros/outtro_Prospectors_00_CeaseFire_Team_00.mp3"
        self.prettyName = "Prospector's Predicament"

    @staticmethod
    def getIntro(userRank=None, variant=None):
        """Selects an introductory track to be played for a scenario.

        This scenario supports a single variant, A.

        Args:
            userRank (int): The enum representing the user's current rank.

            variant (str): The variant chosen for this scenario (A, B, C), if
                known.

        Returns:
            str, str: The variant chosen for this scenario (A, B, C), and the
                URL to the track to play as the introduction for this scenario.

        """
        userRank = userRank or '00'
        intros = {
            "A": DBS3_URL + "scenarios/prospector/intros/intro_Prospectors_00_IntroA_Any_00.mp3"
        }
        if not variant:
            randKey = random.choice(list(intros.keys()))
            randTrack = intros[randKey].format(int(userRank))
            return randKey, randTrack
        return variant, intros[variant].format(int(userRank))

    def isActive(self, userSession):
        """Whether or not the current scenario is available to the user.

        This scenario is only active tor the user if events are enabled AND the
        user has purchased the premium content for this scenario.

        Args:
            userSession (session.DartBattleSession): an object with properties
                representing all slots, values, and information from the user's
                session, including user ID, Audio Directive state, etc.

        Returns:
            bool: whether or not this scenario is available to the user.

        """
        usingEvents = userSession.usingEvents
        if not usingEvents == "True":
            return False
        entitlement = [x for x in userSession.monetizationData.in_skill_products if x.name == self.prettyName]
        if entitlement:
            if entitlement[0].entitled == EntitledState.ENTITLED:
                print("$$ Looks like Prospector's Predicament HAS been purchased by this user!")
                return True
            print("Looks like Prospector's Predicament has not been purchased by this user.")
        return False

# TODO: Handle SFX, Music preferences, rank
