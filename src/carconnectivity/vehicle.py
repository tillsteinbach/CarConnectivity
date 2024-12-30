"""Module for vehicle classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, EnumAttribute, RangeAttribute
from carconnectivity.doors import Doors

if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity.garage import Garage
    from carconnectivity.drive import GenericDrive
    from carconnectivity_connectors.base.connector import BaseConnector


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
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(origin=origin)
            self.vin: StringAttribute = origin.vin
            self.name: StringAttribute = origin.name
            self.model: StringAttribute = origin.model
            self.type: EnumAttribute = origin.type
            self.license_plate: StringAttribute = origin.license_plate
            self.odometer: RangeAttribute = origin.odometer
            self.total_range: RangeAttribute = origin.total_range
            self.drives: dict[str, GenericDrive] = origin.drives
            self.doors: Doors = origin.doors
            self.enabled = origin.enabled
            self.managing_connectors = origin.managing_connectors
        else:
            if garage is None:
                raise ValueError('Cannot create vehicle without garage')
            super().__init__(object_id=vin, parent=garage)
            if vin is None:
                raise ValueError('VIN cannot be None')
            self.vin = StringAttribute("vin", self, vin)
            self.name = StringAttribute("name", self)
            self.model = StringAttribute("model", self)
            self.type = EnumAttribute("type", self, GenericVehicle.Type.UNKNOWN)
            self.license_plate = StringAttribute("license_plate", self)
            self.odometer: RangeAttribute = RangeAttribute(name="odometer", parent=self, value=None, unit=None)
            self.total_range: RangeAttribute = RangeAttribute(name="total_range", parent=self, value=None, unit=None)
            self.drives: dict[str, GenericDrive] = {}
            self.doors: Doors = Doors(vehicle=self)

            self.managing_connectors: list[Optional[BaseConnector]] = []
            if managing_connector is not None:
                self.managing_connectors.append(managing_connector)

            self.enabled = True

    def is_managed_by_connector(self, connector: Optional[BaseConnector]) -> bool:
        """
        Checks if the vehicle is managed by the given connector.

        Args:
            connector (Optional[BaseConnector]): The connector to check.

        Returns:
            bool: True if the vehicle is managed by the given connector, False otherwise.
        """
        return connector in self.managing_connectors

    def __str__(self) -> str:
        return_string: str = 'Vehicle:\n'
        return_string += f'{self.vin}\n'
        if self.name.enabled:
            return_string += f'{self.name}\n'
        if self.model.enabled:
            return_string += f'{self.model}\n'
        if self.license_plate.enabled:
            return_string += f'{self.license_plate}\n'
        if self.type.enabled:
            return_string += f'{self.type}\n'
        if self.odometer.enabled:
            return_string += f'{self.odometer}\n'
        if self.total_range.enabled:
            return_string += f'{self.total_range}\n'
        if self.doors.enabled:
            return_string += f'{self.doors}\n'
        return return_string

    class Type(Enum,):
        """
        Enum representing different types of cars.
        """
        ELECTRIC = 'electric'
        FUEL = 'fuel'
        HYBRID = 'hybrid'
        GASOLINE = 'gasoline'
        PETROL = 'petrol'
        DIESEL = 'diesel'
        CNG = 'cng'
        LPG = 'lpg'
        INVALID = 'invalid'
        UNKNOWN = 'unknown car type'


class ElectricVehicle(GenericVehicle):
    """
    Represents an electric vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(origin=origin)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)


class CombustionVehicle(GenericVehicle):
    """
    Represents an combustion vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(origin=origin)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)


class HybridVehicle(ElectricVehicle, CombustionVehicle):
    """
    Represents a hybrid vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(origin=origin)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
