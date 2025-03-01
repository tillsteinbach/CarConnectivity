"""Module for position classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute, FloatAttribute
from carconnectivity.units import LatitudeLongitude

if TYPE_CHECKING:
    from typing import Optional


class Position(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a position.
    """
    def __init__(self, parent: Optional[GenericObject] = None) -> None:
        super().__init__(object_id='position', parent=parent)
        self.position_type: EnumAttribute = EnumAttribute("position_type", parent=self, value_type=Position.PositionType,
                                                          tags={'carconnectivity'})
        self.latitude: FloatAttribute = FloatAttribute("latitude", parent=self, minimum=-90, maximum=90, unit=LatitudeLongitude.DEGREE,
                                                       tags={'carconnectivity'})
        self.longitude: FloatAttribute = FloatAttribute("longitude", parent=self, minimum=-180, maximum=180, unit=LatitudeLongitude.DEGREE,
                                                        tags={'carconnectivity'})

    class PositionType(Enum):
        """
        Enum for position type.
        """
        PARKING = 'parking'
        DRIVING = 'driving'
        INVALID = 'invalid'
        UNKNOWN = 'unknown'
