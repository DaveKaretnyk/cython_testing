# Copyright (c) 2012-2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import logging

from enum import IntEnum, unique


@unique
class Normalization(IntEnum):
    """ Simple enum class to communicate the possible normalizations to
    clients.

    Normalizations: Spotsize, Intensity, Objective, Projector, BeamBlanker,
    ImageCorrector, ProbeCorrector.

    The precise enumeration type coming from the server (e.g. via IOM) is
    intentionally not exposed to clients.
    """

    # Values chosen to match what gets generated from IOM type library by comtraits - gives some
    # degree of compatibility for prototyping.
    Spotsize = 0
    Intensity = 1
    Objective = 2
    Projector = 3
    BeamBlanker = 4
    ImageCorrector = 5
    ProbeCorrector = 6

    # Define the iteration order (only needed for Python 2.X).
    __order__ = 'Spotsize, Intensity, Objective, Projector, BeamBlanker,' \
                'ImageCorrector, ProbeCorrector'
