#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

"""Angular units and the canonical SUM plotting convention.

SUM plotting uses the mathematical convention:
    zero angle -> positive x axis
    positive angles -> counterclockwise
    negative angles -> clockwise
"""

from sumutilsruntime import (
    AGRAD,
    ARAD,
    PI,
    TAU,
    deg2gon,
    deg2gra,
    deg2rad,
    gon2deg,
    gon2rad,
    gra2deg,
    gra2rad,
    rad2deg,
    rad2gon,
    rad2gra,
);

ANGLE_ZERO_AXIS = "+x";
POSITIVE_ANGLE_DIRECTION = "counterclockwise";


def angle2rad(value, unit="rad"):
    """Convert a supported angular unit to radians."""
    key = str(unit or "rad").strip().lower();
    if key in ("rad", "radian", "radians"):
        return float(value);
    if key in ("deg", "degree", "degrees"):
        return deg2rad(float(value));
    if key in ("gra", "grad", "gradian", "gradians", "gon"):
        return gra2rad(float(value));
    raise ValueError("Unsupported angular unit: {}".format(unit));


__all__ = [
    "AGRAD",
    "ANGLE_ZERO_AXIS",
    "ARAD",
    "PI",
    "POSITIVE_ANGLE_DIRECTION",
    "TAU",
    "angle2rad",
    "deg2gon",
    "deg2gra",
    "deg2rad",
    "gon2deg",
    "gon2rad",
    "gra2deg",
    "gra2rad",
    "rad2deg",
    "rad2gon",
    "rad2gra",
];
