"""Module for position classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute, FloatAttribute

if TYPE_CHECKING:
    from typing import Optional


class Position(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a position.
    """
    def __init__(self, parent: Optional[GenericObject] = None) -> None:
        super().__init__(object_id='position', parent=parent)
        self.position_type: EnumAttribute = EnumAttribute("position_type", self)
        self.latitude: FloatAttribute = FloatAttribute("latitude", self)
        self.longitude: FloatAttribute = FloatAttribute("longitude", self)

    def __str__(self) -> str:
        return_string: str = 'Position:'
        if self.latitude.enabled and self.latitude.value is not None:
            return_string += f' {self.latitude.value}'
        if self.longitude.enabled and self.longitude.value is not None:
            return_string += f' {self.longitude.value}'
        return_string += '\n'
        return return_string

    class PositionType(Enum):
        """
        Enum for position type.
        """
        PARKING = 'parking'
        DRIVING = 'driving'
        INVALID = 'invalid'
        UNKNOWN = 'unknown'
