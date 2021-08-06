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
roles.py

Functions relating to player roles. Players receive roles when playing on
teams. Every team has one Captain, and then other members are randomly assigned
a different role. Roles help boost imaginative play, but may also be called out
during events to perform special actions.

Some roles are only accessible through the purchase of premium content or by
earning them through the completion of tasks.

"""
import enum


__all__ = [
    "PlayerRoles",
    "PlayerRolesSpecial",
    "PlayerRolesStandard"
]

# =============================================================================
# CLASSES
# =============================================================================
class PlayerRoles(enum.Enum):
    """The entire list of possible roles, including premium content."""
    none = 0
    captain = 1
    communications_specialist = 2
    computer_specialist = 3
    electrician = 4
    explosives_expert = 5
    heavy_weapons_expert = 6
    intelligence_officer = 7
    mechanic = 8
    medic = 9
    pilot = 10
    science_officer = 11
    scout = 12
    sniper = 13
    special_forces_operative = 14
    any = 99


class PlayerRolesSpecial(enum.Enum):
    """The list of premium content roles that a user may unlock."""
    communications_specialist = 2


class PlayerRolesStandard(enum.Enum):
    """The starting list of player roles, excluding premium content."""
    captain = 1
    computer_specialist = 3
    electrician = 4
    explosives_expert = 5
    heavy_weapons_expert = 6
    intelligence_officer = 7
    mechanic = 8
    medic = 9
    pilot = 10
    science_officer = 11
    scout = 12
    sniper = 13
    special_forces_operative = 14
