import random


def GetRankPromotionFile(rank):
    rankFile = 'https://s3.amazonaws.com/dart-battle-resources/common/common_Any_{}_RankPromotion_Any_00.mp3'
    rankFile = rankFile.format(rank)
    return rankFile


class Arctic(object):
    def __init__(self):
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

        self.soundtrack = "https://s3.amazonaws.com/dart-battle-resources/sndtrk_Arctic_Music_Sfx_{}s"
        self.outtro = "https://s3.amazonaws.com/dart-battle-resources/tail_NoTeam.mp3"
        self.outtroTeams = "https://s3.amazonaws.com/dart-battle-resources/tail_Team.mp3"

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------
    @property
    def events(self):
        allEvents = []
        for event in self._events:
            for i in range(12):
                allEvents.append(event.format(i))
        return allEvents

    @property
    def intro(self):
        intros = [
            "https://s3.amazonaws.com/dart-battle-resources/arcticIntro.mp3"
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

    def getIntro(self, rank=None, variant=None):
        intros = {
            "A": "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/intros/intro_arctic_A_{:02d}_Any.mp3",
            "B": "https://s3.amazonaws.com/dart-battle-resources/scenarios/arctic/intros/intro_arctic_B_{:02d}_Any.mp3"
        }
        if not variant:
            randKey = random.choice(list(intros.keys()))
            randTrack = intros[randKey].format(int(rank))
            return (randKey, randTrack)
        return variant, intros[variant].format(int(rank))


class NoEvents01(object):
    def __init__(self):
        self._events = None
        self.soundtrack = "https://s3.amazonaws.com/dart-battle-resources/sndtrk_Arctic_Music_Sfx_{}s"
        self.outtro = "https://s3.amazonaws.com/dart-battle-resources/tail_NoTeam.mp3"
        self.outtroTeams = "https://s3.amazonaws.com/dart-battle-resources/tail_Team.mp3"

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

    def getIntro(self, rank=None, variant=None):
        return (None, None)

"""
        # TODO: Handle SFX, Music preferences, rank
        self.allEvents = [
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_Shelter_AirStrike_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_Shelter_Avalanche_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_Shelter_Blizzard_Any_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_SplitUp_HeatSignature_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_SplitUp_IceBreak_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagFeature_AirStrikeCancel_Team_03.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagFeature_BombDefuse_Team_05.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagFeature_ComputerHack_Team_02.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagFeature_WeatherDoorSecure_Team_08.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagInOrder_StrategyWeaponSize_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagManyToOne_TechnologyEnergy_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagManyToOne_TechnologyShield_Team_00.mp3',
            'https://s3.amazonaws.com/dart-battle-resources/event_Arctic_10_TagOneToOne_Intel_Team_07.mp3',
        ]
"""