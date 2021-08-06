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
events.py - Random Events for use during battles

"""


# =============================================================================
# Imports
# =============================================================================
# Std Lib imports
import enum


__all__ = [
    "EventCategories"
]

# =============================================================================
# Classes
# =============================================================================
class EventCategories(enum.Enum):
    """The category types for soundtrack events, used for tokens."""
    Intro = 0
    InCount = 1
    Soundtrack = 2
    CeaseFire = 3
    ExclusiveShot = 4
    HoldOn = 5
    LayDown = 6
    PairUp = 7
    Protect = 8
    Reset = 9
    Resupply = 10
    Retreat = 11
    SpecificTarget = 12
    Shelter = 13
    SplitUp = 14
    TagFeature = 15
    TagInOrder = 16
    TagManyToOne = 17
    TagOneToOne = 18
    TagOneToMany = 19
    ZeroEliminations = 20
    OutCount = 21
    Outtro = 22
    Tail = 23
    Promo = 24
    DropAndRoll = 25
    Duel = 26


