"""
Module for information about the vehicle software
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute

if TYPE_CHECKING:
    from carconnectivity.vehicle import GenericVehicle


class Software(GenericObject):
    """
    Represents the software of a vehicle.
    """
    def __init__(self, vehicle: GenericVehicle) -> None:
        super().__init__(object_id='software', parent=vehicle)
        self.version = StringAttribute('version', parent=self, tags={'carconnectivity'})
