"""
This module defines classes related to fuel tanks.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import VolumeAttribute
from carconnectivity.units import Volume

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.drive import CombustionDrive


class FuelTank(GenericObject):
    """
    Represents the fuel tank of a vehicle.
    """
    def __init__(self, drive: CombustionDrive, initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id='fuel_tank', parent=drive, initialization=initialization)
        self.available_capacity: VolumeAttribute = VolumeAttribute(name='available_capacity', parent=self, value=None, unit=Volume.L,
                                                                   minimum=0, precision=0.1, tags={'carconnectivity'},
                                                                   initialization=self.get_initialization('available_capacity'))
