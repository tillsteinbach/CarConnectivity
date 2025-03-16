"""
Module for charging.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import DateAttribute, EnumAttribute, SpeedAttribute, PowerAttribute, LevelAttribute, CurrentAttribute, BooleanAttribute
from carconnectivity.charging_connector import ChargingConnector
from carconnectivity.commands import Commands

if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity.vehicle import ElectricVehicle


class Charging(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent the charging of a vehicle.
    """
    # pylint: disable=duplicate-code
    def __init__(self, vehicle: Optional[ElectricVehicle] = None,  origin: Optional[Charging] = None) -> None:
        if origin is not None:
            super().__init__(parent=vehicle, origin=origin)
            self.delay_notifications = True
            self.commands: Commands = origin.commands
            self.commands.parent = self
            self.connector: ChargingConnector = origin.connector
            self.connector.parent = self
            self.state: EnumAttribute[Charging.ChargingState] = origin.state
            self.state.parent = self
            self.type: EnumAttribute[Charging.ChargingType] = origin.type
            self.type.parent = self
            self.rate: SpeedAttribute = origin.rate
            self.rate.parent = self
            self.power: PowerAttribute = origin.power
            self.power.parent = self
            self.estimated_date_reached: DateAttribute = origin.estimated_date_reached
            self.settings: Charging.Settings = origin.settings
            self.settings.parent = self
            self.estimated_date_reached.parent = self
        else:
            if vehicle is None:
                raise ValueError('Cannot create charging without vehicle')
            super().__init__(object_id='charging', parent=vehicle)
            self.delay_notifications = True
            self.commands: Commands = Commands(parent=self)
            self.connector: ChargingConnector = ChargingConnector(charging=self)
            self.state: EnumAttribute[Charging.ChargingState] = EnumAttribute("state", parent=self, value_type=Charging.ChargingState,
                                                                              tags={'carconnectivity'})
            self.type: EnumAttribute[Charging.ChargingType] = EnumAttribute("type", parent=self, value_type=Charging.ChargingType,
                                                                            tags={'carconnectivity'})
            self.rate: SpeedAttribute = SpeedAttribute("rate", parent=self, tags={'carconnectivity'})
            self.power: PowerAttribute = PowerAttribute("power", parent=self, tags={'carconnectivity'})
            self.estimated_date_reached: DateAttribute = DateAttribute("estimated_date_reached", parent=self, tags={'carconnectivity'})
            self.settings: Charging.Settings = Charging.Settings(parent=self)
        self.delay_notifications = False

    # pylint: enable=duplicate-code

    class ChargingState(Enum,):
        """
        Enum representing the various states of charging.

        Attributes:
            OFF (str): The charging state is off.
            READY_FOR_CHARGING (str): The vehicle is ready for charging.
            CHARGING (str): The vehicle is currently charging.
            CONSERVATION (str): The vehicle is in conservation mode.
            ERROR (str): There is an error in the charging system.
            UNSUPPORTED (str): The charging state is unsupported.
            DISCHARGING (str): The vehicle is discharging.
            UNKNOWN (str): The charging state is unknown.
        """
        OFF = 'off'
        READY_FOR_CHARGING = 'ready_for_charging'
        CHARGING = 'charging'
        CONSERVATION = 'conservation'
        ERROR = 'error'
        UNSUPPORTED = 'unsupported'
        DISCHARGING = 'discharging'
        UNKNOWN = 'unknown charging state'

    class ChargingType(Enum,):
        """
        Enum representing different types of car charging.

        Attributes:
            INVALID (str): Represents an invalid charging type.
            OFF (str): Represents the state when charging is off.
            AC (str): Represents AC (Alternating Current) charging.
            DC (str): Represents DC (Direct Current) charging.
            UNSUPPORTED (str): Represents an unsupported charging type.
            UNKNOWN (str): Represents an unknown charging type.
        """
        INVALID = 'invalid'
        OFF = 'off'
        AC = 'ac'
        DC = 'dc'
        UNSUPPORTED = 'unsupported'
        UNKNOWN = 'unknown charge type'

    class Settings(GenericObject):
        """
        This class represents the settings for car  charging.
        """
        def __init__(self, parent: Optional[GenericObject] = None, origin: Optional[Charging.Settings] = None) -> None:
            if origin is not None:
                super().__init__(parent=parent, origin=origin)
                self.target_level: LevelAttribute = origin.target_level
                self.target_level.parent = self
                self.maximum_current: CurrentAttribute = origin.maximum_current
                self.maximum_current.parent = self
                self.auto_unlock: BooleanAttribute = origin.auto_unlock
                self.auto_unlock.parent = self
            else:
                super().__init__(object_id="settings", parent=parent)
                self.target_level: LevelAttribute = LevelAttribute("target_level", parent=self, tags={'carconnectivity'})
                self.maximum_current: CurrentAttribute = CurrentAttribute("maximum_current", parent=self, tags={'carconnectivity'})
                self.auto_unlock: BooleanAttribute = BooleanAttribute("auto_unlock", parent=self, tags={'carconnectivity'})
