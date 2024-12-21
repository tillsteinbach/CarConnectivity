"""
This module defines enumerations for various units of measurement, including temperature and length.

Classes:
    Temperature (Enum): An enumeration representing different temperature units.

    Length (Enum): Enum representing different units of length.
"""
from enum import Enum


class GenericUnit(Enum,):
    """
    GenericUnit is an enumeration class that represents various units of measurement
    used in the car connectivity context. This class is intended to be extended
    with specific units as needed.
    """


class Temperature(GenericUnit,):
    """
    An enumeration representing different temperature units.

    Attributes:
        C (str): Celsius temperature unit represented by '°C'.
        F (str): Fahrenheit temperature unit represented by '°F'.
        K (str): Kelvin temperature unit represented by '°K'.
        INVALID (str): Represents an invalid temperature unit.
        UNKNOWN (str): Represents an unknown temperature unit.
    """
    C = '°C'
    F = '°F'
    K = '°K'
    INVALID = 'invalid'
    UNKNOWN = 'unknown temperature unit'


class Length(GenericUnit,):
    """
    Enum representing different units of length.

    Attributes:
        KM (str): Kilometers.
        MI (str): Miles.
        INVALID (str): Invalid length unit.
        UNKNOWN (str): Unknown length unit.
    """
    KM = 'km'
    MI = 'mi'
    INVALID = 'invalid'
    UNKNOWN = 'unknown length unit'


class Level(GenericUnit,):
    """
    A class representing a unit of measurement for levels.

    Attributes:
        PERCENTAGE (str): A string representing the percentage unit ('%').
        INVALID (str): A string representing an invalid unit.
        UNKNOWN (str): A string representing an unknown level unit.
    """
    PERCENTAGE = '%'
    INVALID = 'invalid'
    UNKNOWN = 'unknown level unit'