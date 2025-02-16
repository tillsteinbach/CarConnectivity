"""Module for lights classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute

if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity.vehicle import GenericVehicle


class Lights(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent all lights in the vehicle.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create lights without vehicle')
        super().__init__(object_id='lights', parent=vehicle)
        self.light_state = EnumAttribute("light_state", self, tags={'carconnectivity'})
        self.lights: dict[str, Lights.Light] = {}

    class LightState(Enum):
        """
        Enum for light state.
        """
        ON = 'on'
        OFF = 'off'
        INVALID = 'invalid'
        UNKNOWN = 'unknown light state'

    class Light(GenericObject):
        """
        A class to represent a light in the vehicle.
        """
        def __init__(self, light_id: str, lights: Lights) -> None:
            super().__init__(object_id=light_id, parent=lights)
            self.light_id: str = light_id
            self.light_state = EnumAttribute("light_state", self, tags={'carconnectivity'})
