"""
Module for information about the vehicle software
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import GenericVehicle


class Software(GenericObject):
    """
    Represents the software of a vehicle.
    """
    def __init__(self, vehicle: GenericVehicle, initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id='software', parent=vehicle, initialization=initialization)
        self.version = StringAttribute('version', parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('version'))
