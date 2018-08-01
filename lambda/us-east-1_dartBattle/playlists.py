# std lib imports:
import datetime
import random

# Dart Battle imports:
import protocols
import rank

def GetRankPromotionFile(rank):
    rank = int(rank)
    rankFile = 'https://s3.amazonaws.com/dart-battle-resources/common/common_Any_{:02d}_RankPromotion_Any_00.mp3'
    rankFile = rankFile.format(rank)
    return rankFile


class Greeting(object):
    def __init__(self, sessionAttributes):
        self.sessionAttributes = sessionAttributes
        self.crowsNestGreetings = [
            "Scanning biometric data for field soldiers. Increased pulse detected. Initiating battle sequence. Awaiting orders. ",
            "Initiating secure uplink to satellite. Uplink acquired, handshake initiated. Combat interface ready for instruction. ",
            "Stitching battlefield photogrammetry. Closing edge loops and interpolating surface points. " +
            "Battlefield metrics have been distributed to combat vehicles and qualifying infantry. Standing by.",
            "Reboot complete. Repairing damage to central targeting systems. Unit tests passed. Awaiting instruction.",
            "Damage sustained. Artillery servos 8 and 12 are offline. Electromagnetic shield operating at reduced levels. Ready for input.",
            "Enemy activity detected. Raising defensive perimeter. Sealing entrances on levels Charlie through Foxtrot. Further instruction required from authorized personnel."
        ]
        self.madDogGreetings = [
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/protocols/madDog/protocol_MadDog_00_Greeting_Dance_Any_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/protocols/madDog/protocol_MadDog_00_Greeting_Diaper_Any_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/protocols/madDog/protocol_MadDog_00_Greeting_Disappointment_Any_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/protocols/madDog/protocol_MadDog_00_Greeting_DontCry_Any_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/protocols/madDog/protocol_MadDog_00_Greeting_Malfunction_Any_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/protocols/madDog/protocol_MadDog_00_Greeting_Smell_Any_00.mp3' /> "
        ]
        self.noTeamGreetingsStandard = [
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_StandardA_NoTeam_00.mp3' /> ",
        ]
        self.noTeamGreetingsQuick = [
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickA_NoTeam_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickB_NoTeam_00.mp3' /> ",
        ]
        self.officerGreetings = [
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_{:02d}_Greeting_WelcomeBackA_Any_00.mp3' /> "
        ]
        self.officerGreetingHead = "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_AttnOfficerA_Any_00.mp3' /> "
        self.officerGreetingTail = "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_AtEaseA_Any_00.mp3' /> "
        self.teamGreetingsStandard = [
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_StandardA_Team_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_StandardB_Team_00.mp3' /> ",
        ]
        self.teamGreetingsQuick = [
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickA_Team_00.mp3' /> ",
            "<audio src='https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Greeting_QuickB_Team_00.mp3' /> ",
        ]

    def getGreeting(self):
        greetings = []
        if self.sessionAttributes.get("recentSession", "False") == "True":
            if self.sessionAttributes.get("usingTeams", "False") == "True":
                # Recent Teams
                greetings.extend(self.teamGreetingsQuick)
            else:
                # Recent Individual
                greetings.extend(self.noTeamGreetingsQuick)
        else:
            if self.sessionAttributes.get("usingTeams", "False") == "True":
                # Not recent Teams
                greetings.extend(self.teamGreetingsStandard)
            else:
                # Not recent Individual
                greetings.extend(self.noTeamGreetingsStandard)

        # Officer greetings
        if int(self.sessionAttributes.get("playerRank", "00")) > 0:
            officerGreetings = []
            for track in self.officerGreetings:
                track = track.format(int(self.sessionAttributes["playerRank"]))
                officerIntro = random.randint(0, 2)
                if officerIntro == 2 and int(self.sessionAttributes["playerRank"]) > 5:
                    track = "{}{}{}".format(self.officerGreetingHead, track, self.officerGreetingTail)
                officerGreetings.append(track)
            greetings.extend(officerGreetings)

        # Protocol greetings
        session = {"attributes": self.sessionAttributes}
        if protocols.ProtocolCrowsNest(session).isActive:
            greetings.extend(self.crowsNestGreetings)
        if protocols.ProtocolMadDog(session).isActive:
            greetings.extend(self.madDogGreetings)

        # Final selection
        selection = random.choice(greetings)
        return selection


class Playlist(object):
    def __init__(self):
        self._events = []
        self.inCount = "https://s3.amazonaws.com/dart-battle-resources/common/inCount_Any_00_YourBattleBegins_Any_00.mp3"
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
        allEvents = []
        for event in self._events:
            for i in range(len(rank.rankRequirements)):
                allEvents.append(event.format(i))
        return allEvents

    @property
    def promo(self):
        promos = [
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_AudioDirectives_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_ClearTeams_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_DisableEvents_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_Facebook_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_HowDoIPlay_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_HowMoreScenarios_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_HowMoreScenarios_B.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_QuickTeamSetup_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_RankPromotion_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_RememberRoles_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_SafetyReminder_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_SafetyReminder_B.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_ShuffleTeams_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_TeamMode_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_VisualOutput_A.mp3",
            # Duplicates for weighting
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_Facebook_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_HowMoreScenarios_A.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/promos/promo_Any_00_HowMoreScenarios_B.mp3",
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
        tails = [
            "https://s3.amazonaws.com/dart-battle-resources/common/common_Any_00_Tail_RateUsA_Any_00.mp3",
            # NoneTypes for the chance that no Tail takes place.
            None,
            None,
            None
        ]
        return random.choice(tails)

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------
    def getEventsForRank(self, rank):
        allEvents = []
        for event in self._events:
            allEvents.append(event.format(int(rank)))
        return allEvents

    @staticmethod
    def getIntro(rank=None, variant=None):
        intros = {
            "A": "",
        }
        if not variant:
            randKey = random.choice(list(intros.keys()))
            randTrack = intros[randKey].format(int(rank))
            return randKey, randTrack
        return variant, intros[variant].format(int(rank))

    def _getEventsWithCategory(self, eventCategory, tracks=None):
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if eventCategory in x]
        return matches

    def _getEventsWithRoles(self, roles, tracks=None):
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if roles in x]
        return matches

    def _getEventsWithTeamToken(self, teamToken, tracks=None):
        teamToken = "_{}_".format(teamToken)
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if teamToken in x]
        return matches

    def _getEventsWithTitle(self, eventTitle, tracks=None):
        tracks = tracks or self.getEventsForRank('00')
        matches = [x for x in tracks if eventTitle in x]
        return matches

    def getEventWithProperties(self, rank=None, eventCategory=None, eventTitle=None, teamToken=None, roles=None):
        rank = rank or '00'
        def filterTracksWithRank(rank):
            rankTracks = self.getEventsForRank(rank)

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
        selections = filterTracksWithRank(rank)
        if not selections:
            selections = filterTracksWithRank('00')
        if not selections:
            return None
        if len(selections) > 1:
            print("WARNING! More than one track matched getEventWithProperties:")
            print("Properties: rank, {}; eventCategory, {}; eventTitle, {}; teamToken, {}; roles, {}".format(rank, eventCategory, eventTitle, teamToken, roles))
            print("Tracks: {}".format(selections))
            print("Using first one found.")
        selection = selections[0]
        return selection

    @staticmethod
    def isActive(sessionAttributes):
        usingEvents = sessionAttributes.get("usingEvents", "True")
        if usingEvents:
            return True
        return False


class Arctic(Playlist):
    def __init__(self):
        super(Arctic, self).__init__()
        self._events = [
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/ceaseFire/event_Arctic_{:02d}_CeaseFire_HeatSignature_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/ceaseFire/event_Arctic_{:02d}_CeaseFire_IceBreak_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/ceaseFire/event_Arctic_{:02d}_CeaseFire_Yeti_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_06.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_13.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/dugIn/event_Arctic_{:02d}_ExclusiveShot_DugIn_Team_14.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/holdOn/event_Arctic_{:02d}_HoldOn_Avalanche_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/holdOn/event_Arctic_{:02d}_HoldOn_Blizzard_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/holdOn/event_Arctic_{:02d}_HoldOn_IceBreak_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/layDown/event_Arctic_{:02d}_LayDown_Avalanche_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/layDown/event_Arctic_{:02d}_LayDown_Blizzard_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/layDown/event_Arctic_{:02d}_LayDown_HeatSignature_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/layDown/event_Arctic_{:02d}_LayDown_Yeti_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/pairUp/event_Arctic_{:02d}_PairUp_Avalanche_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/pairUp/event_Arctic_{:02d}_PairUp_Blizzard_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/pairUp/event_Arctic_{:02d}_PairUp_Fog_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/pairUp/event_Arctic_{:02d}_PairUp_Yeti_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_{:02d}_Protect_Airlift_Team_10.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_01.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_03.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_04.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_06.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_07.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_08.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_09.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_10.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_11.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_12.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_13.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/protect/event_Arctic_00_Protect_KeyTeamMember_Team_14.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/reset/event_Arctic_00_Reset_TechnologyTimeTravel_NoTeam_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/reset/event_Arctic_00_Reset_TechnologyTimeTravel_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/resupply/event_Arctic_{:02d}_Resupply_Reinforcements_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/resupply/event_Arctic_{:02d}_Resupply_Yeti_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/retreat/event_Arctic_{:02d}_Retreat_Avalanche_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/retreat/event_Arctic_{:02d}_Retreat_Blizzard_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/retreat/event_Arctic_{:02d}_Retreat_Fog_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/retreat/event_Arctic_{:02d}_Retreat_IceBreak_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/retreat/event_Arctic_{:02d}_Retreat_Yeti_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_01.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_03.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_04.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_06.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_07.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_08.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_09.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_10.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_11.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_12.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_13.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/specificTarget/event_Arctic_00_SpecificTarget_KeyTeamMember_Team_14.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/shelter/event_Arctic_{:02d}_Shelter_Airstrike_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/shelter/event_Arctic_{:02d}_Shelter_Avalanche_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/splitUp/event_Arctic_{:02d}_SplitUp_IceBreak_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/splitUp/event_Arctic_{:02d}_SplitUp_HeatSignature_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagFeature/event_Arctic_00_TagFeature_AirstrikeCancel_Team_02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagFeature/event_Arctic_{:02d}_TagFeature_BombDefuse_Team_04.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagFeature/event_Arctic_{:02d}_TagFeature_BombDefuse_Team_05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagFeature/event_Arctic_{:02d}_TagFeature_ComputerHack_Team_02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagFeature/event_Arctic_{:02d}_TagFeature_WeatherDoor_Team_08.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_00_TagManyToOne_NewOrders_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_01.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_03.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_04.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_06.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_07.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_08.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_09.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_10.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_11.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_12.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_13.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyEnergy_Team_14.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_01.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_03.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_04.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_06.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_07.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_08.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_09.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_10.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_11.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_12.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_13.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagManyToOne/event_Arctic_{:02d}_TagManyToOne_TechnologyShield_Team_14.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.01.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.03.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.04.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.06.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.07.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.08.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.10.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.11.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.12.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.13.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_MedicalAttention_Team_09.14.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/tagOneToOne/event_Arctic_00_TagOneToOne_NewIntel_Team_07.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/events/zeroEliminations/event_Arctic_{:02d}_ZeroEliminations_HalfDamage_Team_00.mp3',
        ]

        self.soundtrack = "https://s3.amazonaws.com/dart-battle-resources/sndtrk/sndtrk_Arctic_Music_Sfx_{}s.mp3"
        self.soundtrackOnly = ""
        self.soundtrackSfx = ""
        self.outCount = "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/outCounts/outCount_Arctic_00_YourBattleEnds_Any_00.mp3"
        self.outtro = "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/outtros/outtro_Arctic_00_CeaseFire_NoTeam_00.mp3"
        self.outtroTeams = "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/outtros/outtro_Arctic_00_CeaseFire_Team_00.mp3"
        self.prettyName = "Arctic Defense"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------
    @staticmethod
    def getIntro(rank=None, variant=None):
        intros = {
            "A": "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/intros/intro_arctic_A_{:02d}_Any.mp3",
            "B": "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/intros/intro_arctic_B_{:02d}_Any.mp3"
        }
        if not variant:
            randKey = random.choice(list(intros.keys()))
            randTrack = intros[randKey].format(int(rank))
            return randKey, randTrack
        return variant, intros[variant].format(int(rank))


class NoEvents01(Playlist):
    def __init__(self):
        super(NoEvents01, self).__init__()
        self.soundtrack = "https://s3.amazonaws.com/dart-battle-resources/sndtrk/sndtrk_Arctic_Music_Sfx_{}s.mp3"
        self.outtro = "https://s3.amazonaws.com/dart-battle-resources/tail_NoTeam.mp3"
        self.outtroTeams = "https://s3.amazonaws.com/dart-battle-resources/tail_Team.mp3"
        self.prettyName = "NoEvents01"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def events(self):
        return None

    # -------------------------------------------------------------------------
    # PUBLIC METHODS
    # -------------------------------------------------------------------------
    def getEventsForRank(self, rank):
        return None

    @staticmethod
    def getIntro(rank=None, variant=None):
        return None, None

    @staticmethod
    def isActive(sessionAttributes):
        usingEvents = sessionAttributes.get("usingEvents", "True")
        if usingEvents:
            return False
        return True


class Prospector(Playlist):
    def __init__(self):
        super(Prospector, self).__init__()
        self._events = [
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/ceaseFire/event_Prospectors_00_CeaseFire_Bats_Any_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/ceaseFire/event_Prospectors_00_CeaseFire_CaveIn_Any_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_AlternatePath_Team_12.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_01.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_02.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_03.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_04.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_05.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_06.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_07.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_08.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_09.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_10.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_11.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_12.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_13.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_CoverFire_Team_14.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_01.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_02.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_03.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_04.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_05.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_06.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_07.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_08.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_09.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_10.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_11.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_12.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_13.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/exclusiveShot/event_Prospectors_00_ExclusiveShot_Outgunned_Team_14.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/holdOn/event_Prospectors_00_HoldOn_CaveIn_Any_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/holdOn/event_Prospectors_00_HoldOn_Earthquake_Any_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/layDown/event_Prospectors_00_LayDown_Bats_Any_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/protect/event_Prospectors_00_Protect_AlternatePath_Team_12.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/reset/event_Prospectors_00_Reset_HallOfGems_Any_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/resupply/event_Prospectors_00_Resupply_OutOfAmmo_Any_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/retreat/event_Prospectors_00_Retreat_CaveIn_NoTeam_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/retreat/event_Prospectors_00_Retreat_CaveIn_Team_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/retreat/event_Prospectors_00_Retreat_FlashFlood_NoTeam_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/retreat/event_Prospectors_00_Retreat_FlashFlood_Team_00.mp3",
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/events/specificTarget/event_Prospectors_00_SpecificTarget_BackRoute_Team_12.mp3",



        ]
        self.soundtrack = "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/sndtrk/sndtrk_OldWest_Music_Sfx_{}s.mp3"
        self.outCount = "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/outCounts/outCount_Prospectors_00_YourBattleEnds_Any_00.mp3"
        self.outtro = "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/outtros/outtro_Prospectors_00_CeaseFire_NoTeam_00.mp3"
        self.outtroTeams = "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/outtros/outtro_Prospectors_00_CeaseFire_Team_00.mp3"
        self.prettyName = "Prospector's Predicament"

    @staticmethod
    def getIntro(rank=None, variant=None):
        rank = rank or '00'
        intros = {
            "A": "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/OldWest_Intro_test.mp3"
        }
        if not variant:
            randKey = random.choice(list(intros.keys()))
            randTrack = intros[randKey].format(int(rank))
            return randKey, randTrack
        return variant, intros[variant].format(int(rank))

# TODO: Handle SFX, Music preferences, rank
