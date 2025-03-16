"""Module for window heating classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute
from carconnectivity.commands import Commands

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import GenericVehicle


class WindowHeatings(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent all window heaters in the vehicle.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create window heatings without vehicle')
        super().__init__(object_id='window_heating', parent=vehicle)
        self.commands: Commands = Commands(parent=self)
        self.heating_state = EnumAttribute("heating_state", self, value_type=WindowHeatings.HeatingState, tags={'carconnectivity'})
        self.windows: Dict[str, WindowHeatings.WindowHeating] = {}

    class HeatingState(Enum):
        """
        Enum for heating state.
        """
        ON = 'on'
        OFF = 'off'
        UNSUPPORTED = 'unsupported'
        INVALID = 'invalid'
        UNKNOWN = 'unknown heating state'

    class WindowHeating(GenericObject):
        """
        A class to represent a window heating in the vehicle.
        """
        def __init__(self, window_id: str, window_heatings: WindowHeatings) -> None:
            super().__init__(object_id=window_id, parent=window_heatings)
            self.window_id: str = window_id
            self.heating_state = EnumAttribute("heating_state", self, value_type=WindowHeatings.HeatingState, tags={'carconnectivity'})
