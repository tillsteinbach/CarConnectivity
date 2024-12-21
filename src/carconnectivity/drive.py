"""Module for vehicle classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import RangeAttribute, LevelAttribute
from carconnectivity.units import Length

if TYPE_CHECKING:
    from carconnectivity.vehicle import GenericVehicle, ElectricVehicle, CombustionVehicle


class GenericDrive(GenericObject):
    """
    A class to represent a generic vehicle.

    Attributes:
    -----------
    vin : StringAttribute
        The vehicle identification number (VIN) of the vehicle.
    license_plate : StringAttribute
        The license plate of the vehicle.
    """
    def __init__(self, drive_id: str, vehicle: GenericVehicle) -> None:
        super().__init__(object_id=drive_id, parent=vehicle)
        self.range: RangeAttribute = RangeAttribute(name="range", parent=self, value=None, unit=Length.UNKNOWN)
        self.level: LevelAttribute = LevelAttribute(name="level", parent=self, value=None)
        self.enabled = True

    def __str__(self) -> str:
        return_string: str = f'Drive: {self.id}\n'
        if self.range.enabled:
            return_string += f'{self.range}\n'
        return return_string


class ElectricDrive(GenericDrive):
    """
    Represents an electric vehicle.
    """
    def __init__(self, drive_id: str, vehicle: ElectricVehicle) -> None:
        super().__init__(drive_id=drive_id, vehicle=vehicle)


class CombustionDrive(GenericDrive):
    """
    Represents an combustion vehicle.
    """
    def __init__(self, drive_id: str, vehicle: CombustionVehicle) -> None:
        super().__init__(drive_id=drive_id, vehicle=vehicle)
