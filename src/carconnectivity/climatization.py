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
            self.state: EnumAttribute = EnumAttribute("state", self, value_type=Climatization.ClimatizationState, tags={'carconnectivity'})
            self.estimated_date_reached: DateAttribute = DateAttribute("estimated_date_reached", self, tags={'carconnectivity'})
            self.settings: Climatization.Settings = Climatization.Settings(parent=self)

    class Settings(GenericObject):
        """
        This class represents the settings for car  charging.
        """
        def __init__(self, parent: Optional[GenericObject] = None, origin: Optional[Climatization.Settings] = None) -> None:
            if origin is not None:
                super().__init__(parent=parent, origin=origin)
                self.commands: Commands = origin.commands
                self.commands.parent = self
                self.target_temperature: TemperatureAttribute = origin.target_temperature
                self.target_temperature.parent = self
                self.window_heating: BooleanAttribute = origin.window_heating
                self.window_heating.parent = self
                self.seat_heating: BooleanAttribute = origin.seat_heating
                self.seat_heating.parent = self
                self.climatization_at_unlock: BooleanAttribute = origin.climatization_at_unlock
                self.climatization_at_unlock.parent = self
                self.climatization_without_external_power: BooleanAttribute = origin.climatization_without_external_power
                self.climatization_without_external_power.parent = self
                self.heater_source: EnumAttribute = origin.heater_source
                self.heater_source.parent = self
            else:
                super().__init__(object_id="settings", parent=parent)
                self.commands: Commands = Commands(parent=self)
                self.target_temperature: TemperatureAttribute = TemperatureAttribute("target_temperature", parent=self, tags={'carconnectivity'})
                self.window_heating: BooleanAttribute = BooleanAttribute("window_heating", parent=self, tags={'carconnectivity'})
                self.seat_heating: BooleanAttribute = BooleanAttribute("seat_heating", parent=self, tags={'carconnectivity'})
                self.climatization_at_unlock: BooleanAttribute = BooleanAttribute("climatization_at_unlock", parent=self, tags={'carconnectivity'})
                self.climatization_without_external_power: BooleanAttribute = BooleanAttribute("climatization_without_external_power", parent=self,
                                                                                               tags={'carconnectivity'})
                self.heater_source: EnumAttribute = EnumAttribute("heater_source", parent=self, value_type=Climatization.Settings.HeaterSource,
                                                                  tags={'carconnectivity'})

        class HeaterSource(Enum,):
            """
            Enum representing different sources of a heater.

            Attributes:
                ELECTRIC (str): Represents an electric heater source.
                UNKNOWN (str): Represents an unknown heater source.
            """
            ELECTRIC = 'electric'
            UNKNOWN = 'unknown heater source'

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
