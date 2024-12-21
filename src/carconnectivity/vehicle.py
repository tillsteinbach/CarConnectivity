"""Module for vehicle classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, RangeAttribute

if TYPE_CHECKING:
    from carconnectivity.garage import Garage
    from carconnectivity.drive import GenericDrive


class GenericVehicle(GenericObject):  # pylint: disable=too-many-instance-attributes
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
        self.vin = StringAttribute("vin", self, vin)
        self.name = StringAttribute("name", self)
        self.model = StringAttribute("model", self)
        self.license_plate = StringAttribute("license_plate", self)
        self.odometer: RangeAttribute = RangeAttribute(name="odometer", parent=self, value=None, unit=None)
        self.total_range: RangeAttribute = RangeAttribute(name="total_range", parent=self, value=None, unit=None)
        self.drives: dict[GenericDrive] = {}
        self.enabled = True

    def __str__(self) -> str:
        return_string: str = 'Vehicle:\n'
        return_string += f'{self.vin}\n'
        if self.name.enabled:
            return_string += f'{self.name}\n'
        if self.model.enabled:
            return_string += f'{self.model}\n'
        if self.license_plate.enabled:
            return_string += f'{self.license_plate}\n'
        if self.odometer.enabled:
            return_string += f'{self.odometer}\n'
        if self.total_range.enabled:
            return_string += f'{self.total_range}\n'
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
