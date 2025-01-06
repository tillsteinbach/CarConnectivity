"""
Module for charging.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import DurationAttribute, EnumAttribute, FloatAttribute

if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity.vehicle import ElectricVehicle


class Charging(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent the charging of a vehicle.
    """
    def __init__(self, vehicle: Optional[ElectricVehicle] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create charging without vehicle')
        super().__init__(object_id='charging', parent=vehicle)
        self.delay_notifications = True
        self.state: EnumAttribute = EnumAttribute("state", parent=self)
        self.type: EnumAttribute = EnumAttribute("type", parent=self)
        self.rate: FloatAttribute = FloatAttribute("rate", parent=self)
        self.power: FloatAttribute = FloatAttribute("power", parent=self)
        self.remaining_duration: DurationAttribute = DurationAttribute("remaining_duration", parent=self)
        self.delay_notifications = False

    def __str__(self) -> str:
        return_string: str = 'Charging:\n'
        if self.state.enabled and self.state.value is not None:
            return_string += f'State: {self.state.value.value}\n'
        if self.type.enabled and self.type.value is not None:
            return_string += f'Type: {self.type.value.value}\n'
        if self.remaining_duration.enabled:
            return_string += f'Remaining duration: {self.remaining_duration.value}\n'
        return return_string

    class ChargingState(Enum,):
        OFF = 'off'
        READY_FOR_CHARGING = 'ready_for_charging'
        CHARGING = 'charging'
        CONSERVATION = 'conservation'
        ERROR = 'error'
        UNSUPPORTED = 'unsupported'
        DISCHARGING = 'discharging'
        UNKNOWN = 'unknown charging state'

    class ChargingType(Enum,):
        INVALID = 'invalid'
        OFF = 'off'
        AC = 'ac'
        DC = 'dc'
        UNSUPPORTED = 'unsupported'
        UNKNOWN = 'unknown charge type'
