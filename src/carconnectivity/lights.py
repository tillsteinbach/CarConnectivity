"""Module for lights classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import GenericVehicle


class Lights(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent all lights in the vehicle.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None, initialization: Optional[Dict] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create lights without vehicle')
        super().__init__(object_id='lights', parent=vehicle, initialization=initialization)
        self.light_state: EnumAttribute[Lights.LightState] = EnumAttribute("light_state", self, tags={'carconnectivity'},
                                                                           value_type=Lights.LightState,
                                                                           initialization=self.get_initialization('light_state'))
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
        def __init__(self, light_id: str, lights: Lights, initialization: Optional[Dict] = None) -> None:
            super().__init__(object_id=light_id, parent=lights, initialization=initialization)
            self.light_id: str = light_id
            self.light_state: EnumAttribute[Lights.LightState] = EnumAttribute("light_state", self, tags={'carconnectivity'},
                                                                               value_type=Lights.LightState,
                                                                               initialization=self.get_initialization('light_state'))
