"""Module for position classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute, TemperatureAttribute, DateAttribute, BooleanAttribute
from carconnectivity.commands import Commands

if TYPE_CHECKING:
    from typing import Optional

    from carconnectivity.vehicle import GenericVehicle


class Climatization(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a climatization.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None, origin: Optional[Climatization] = None) -> None:
        if origin is not None:
            super().__init__(origin=origin)
            self.commands: Commands = origin.commands
            self.commands.parent = self
            self.state: EnumAttribute = origin.state
            self.state.parent = self
            self.estimated_date_reached: DateAttribute = origin.estimated_date_reached
            self.estimated_date_reached.parent = self
            self.settings: Climatization.Settings = Climatization.Settings(origin=origin.settings)
        else:
            super().__init__(object_id='climatization', parent=vehicle)
            self.commands: Commands = Commands(parent=self)
            self.state: EnumAttribute = EnumAttribute("state", self)
            self.estimated_date_reached: DateAttribute = DateAttribute("estimated_date_reached", self)
            self.settings: Climatization.Settings = Climatization.Settings(parent=self)

    def __str__(self) -> str:
        return_string: str = 'Climatization:'
        if self.state.enabled and self.state.value is not None:
            return_string += f'State: {self.state.value.value}'
        if self.estimated_date_reached.enabled and self.estimated_date_reached.value is not None:
            return_string += f'Estimated Date Temperature Reached: {self.estimated_date_reached.value}'
        if self.settings is not None and self.settings.enabled:
            return_string += f'Settings: {self.settings}'
        return_string += '\n'
        return return_string

    class Settings(GenericObject):
        """
        This class represents the settings for car  charging.
        """
        def __init__(self, parent: Optional[GenericObject] = None, origin: Optional[Climatization.Settings] = None) -> None:
            if origin is not None:
                super().__init__(origin=origin)
                self.commands: Commands = Commands(parent=self)
                self.target_temperature: TemperatureAttribute = origin.target_temperature
                self.target_temperature.parent = self
                self.window_heating: BooleanAttribute = origin.window_heating
                self.window_heating.parent = self
                self.seat_heating: BooleanAttribute = origin.seat_heating
                self.seat_heating.parent = self
                self.climatization_at_unlock: BooleanAttribute = origin.climatization_at_unlock
                self.climatization_at_unlock.parent = self
            else:
                super().__init__(object_id="settings", parent=parent)
                self.target_temperature: TemperatureAttribute = TemperatureAttribute("target_temperature", parent=self)
                self.window_heating: BooleanAttribute = BooleanAttribute("window_heating", parent=self)
                self.seat_heating: BooleanAttribute = BooleanAttribute("seat_heating", parent=self)
                self.climatization_at_unlock: BooleanAttribute = BooleanAttribute("climatization_at_unlock", parent=self)

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
