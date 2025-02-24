"""
Module for information about the vehicle maintenance
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import DateAttribute, RangeAttribute
from carconnectivity.units import Length


if TYPE_CHECKING:
    from carconnectivity.vehicle import GenericVehicle


class Maintenance(GenericObject):
    """
    Represents the maintenance of a vehicle.
    """
    def __init__(self, vehicle: GenericVehicle) -> None:
        super().__init__(object_id='maintenance', parent=vehicle)
        self.inspection_due_at = DateAttribute('inspection_due_at', parent=self, tags={'carconnectivity'})
        self.inspection_due_after = RangeAttribute('inspection_due_after', parent=self, tags={'carconnectivity'}, unit=Length.KM)
        self.oil_service_due_at = DateAttribute('oil_service_due_at', parent=self, tags={'carconnectivity'})
        self.oil_service_due_after = RangeAttribute('oil_service_due_after', parent=self, tags={'carconnectivity'}, unit=Length.KM)
