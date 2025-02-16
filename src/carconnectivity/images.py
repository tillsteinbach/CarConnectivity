"""Module for car images."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import ImageAttribute

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import GenericVehicle


class Images(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent all vehicle images.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create images without vehicle')
        super().__init__(object_id='images', parent=vehicle)
        self.images: Dict[str, ImageAttribute] = {}
