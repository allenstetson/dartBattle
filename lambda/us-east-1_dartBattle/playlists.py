# std lib imports:
import datetime
import random

# Dart Battle imports:
import rank

def GetRankPromotionFile(rank):
    rankFile = 'https://s3.amazonaws.com/dart-battle-resources/common/common_Any_{}_RankPromotion_Any_00.mp3'
    rankFile = rankFile.format(rank)
    return rankFile


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
    def intro(self):
        intros = [
            ""
        ]
        return random.choice(intros)

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

            teamTokenEvents = self._getEventsWithTeamToken(teamToken, tracks=eventTracks)
            if not teamTokenEvents:
                teamTokenEvents = self._getEventsWithTeamToken("Any", eventTracks)
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
    @property
    def intro(self):
        intros = [
            "https://s3.amazonaws.com/dart-battle-resources/arcticIntro.mp3"
        ]
        return random.choice(intros)

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

    @property
    def intro(self):
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
            'https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/OldWest_Intro_test.mp3',
        ]
        self.soundtrack = "https://s3.amazonaws.com/dart-battle-resources/sndtrk/oldWest/sndtrk_OldWest_Music_Sfx_{}s.mp3"
        self.outCount = "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/outCounts/outCount_Arctic_00_YourBattleEnds_Any_00.mp3"
        self.outtro = "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/outtros/outtro_Arctic_00_CeaseFire_NoTeam_00.mp3"
        self.outtroTeams = "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/outtros/outtro_Arctic_00_CeaseFire_Team_00.mp3"
        self.prettyName = "Prospector's Predicament"

    @property
    def intro(self):
        intros = [
            "https://s3.amazonaws.com/dart-battle-resources/scenarios/prospector/OldWest_Intro_test.mp3"
        ]
        return random.choice(intros)

    def getIntro(self, rank=None, variant=None):
        return self.intro

# TODO: Handle SFX, Music preferences, rank
