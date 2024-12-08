"""Module for vehicle classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute

if TYPE_CHECKING:
    from carconnectivity.garage import Garage


class GenericVehicle(GenericObject):
    """
    A class to represent a generic vehicle.

    Attributes:
    -----------
    vin : StringAttribute
        The vehicle identification number (VIN) of the vehicle.
    license_plate : StringAttribute
        The license plate of the vehicle.
    """
    def __init__(self, vin: str, garage: Garage) -> None:
        super().__init__(object_id=vin, parent=garage)
        self.vin = StringAttribute("VIN", self, vin)
        self.license_plate = StringAttribute("licensePlate", self)
        self.enabled = True

    def __str__(self) -> str:
        return_string: str = 'Vehicle:\n'
        return_string += f'{self.vin}\n'
        if self.license_plate.enabled:
            return_string += f'{self.license_plate}\n'
        return return_string


class ElectricVehicle(GenericVehicle):
    """
    Represents an electric vehicle.
    """
    def __init__(self, vin: str, garage: Garage) -> None:
        super().__init__(vin=vin, garage=garage)


class CombustionVehicle(GenericVehicle):
    """
    Represents an combustion vehicle.
    """
    def __init__(self, vin: str, garage: Garage) -> None:
        super().__init__(vin=vin, garage=garage)


class HybridVehicle(ElectricVehicle, CombustionVehicle):
    """
    Represents a hybrid vehicle.
    """
    def __init__(self, vin: str, garage: Garage) -> None:
        super().__init__(vin=vin, garage=garage)
