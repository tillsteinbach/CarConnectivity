"""Module for position classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute, FloatAttribute, TemperatureAttribute, DateAttribute

if TYPE_CHECKING:
    from typing import Optional


class Climatization(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a climatization.
    """
    def __init__(self, parent: Optional[GenericObject] = None) -> None:
        super().__init__(object_id='climatization', parent=parent)
        self.state: EnumAttribute = EnumAttribute("state", self)
        self.target_temperature: TemperatureAttribute = FloatAttribute("target_temperature", self)
        self.estimated_date_reached: DateAttribute = DateAttribute("estimated_date_reached", self)

    def __str__(self) -> str:
        return_string: str = 'Position:'
        if self.state.enabled and self.state.value is not None:
            return_string += f'State: {self.state.value.value}'
        if self.target_temperature.enabled and self.target_temperature.value is not None:
            return_string += f'Target Temperature: {self.target_temperature.value}'
        if self.estimated_date_reached.enabled and self.estimated_date_reached.value is not None:
            return_string += f'Estimated Date Temperature Reached: {self.estimated_date_reached.value}'
        return_string += '\n'
        return return_string

    class ClimatizationState(Enum,):
        """
        Enum representing the state of the climatization system.

        Attributes:
            OFF (str): Climatization is turned off.
            HEATING (str): Climatization is in heating mode.
            COOLING (str): Climatization is in cooling mode.
            VENTILATION (str): Climatization is in ventilation mode.
            INVALID (str): Climatization state is invalid.
            UNKNOWN (str): Climatization state is unknown.
        """
        OFF = 'off'
        HEATING = 'heating'
        COOLING = 'cooling'
        VENTILATION = 'ventilation'
        INVALID = 'invalid'
        UNKNOWN = 'unknown climatization state'
