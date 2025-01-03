"""
Module for vehicle classes.

This module defines various classes representing different types of vehicles,
including generic vehicles, electric vehicles, combustion vehicles, and hybrid vehicles.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, EnumAttribute, RangeAttribute
from carconnectivity.doors import Doors
from carconnectivity.windows import Windows
from carconnectivity.lights import Lights
from carconnectivity.software import Software
from carconnectivity.drive import Drives
from carconnectivity.units import Length

if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity.garage import Garage

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
            self.delay_notifications = True
            self.vin: StringAttribute = origin.vin
            self.vin.parent = self
            self.name: StringAttribute = origin.name
            self.name.parent = self
            self.model: StringAttribute = origin.model
            self.model.parent = self
            self.type: EnumAttribute = origin.type
            self.type.parent = self
            self.license_plate: StringAttribute = origin.license_plate
            self.license_plate.parent = self
            self.odometer: RangeAttribute = origin.odometer
            self.odometer.parent = self
            self.state: EnumAttribute = origin.state
            self.state.parent = self
            self.drives: Drives = origin.drives
            self.drives.parent = self
            self.doors: Doors = origin.doors
            self.doors.parent = self
            self.windows: Windows = origin.windows
            self.windows.parent = self
            self.lights: Lights = origin.lights
            self.lights.parent = self
            self.software: Software = origin.software
            self.software.parent = self
            self.enabled = origin.enabled
            self.managing_connectors = origin.managing_connectors
        else:
            if garage is None:
                raise ValueError('Cannot create vehicle without garage')
            super().__init__(object_id=vin.upper(), parent=garage)
            self.delay_notifications = True
            if vin is None:
                raise ValueError('VIN cannot be None')
            self.vin = StringAttribute("vin", self, vin.upper())
            self.name = StringAttribute("name", self)
            self.model = StringAttribute("model", self)
            self.type = EnumAttribute("type", parent=self)
            self.license_plate = StringAttribute("license_plate", self)
            self.odometer: RangeAttribute = RangeAttribute(name="odometer", parent=self, value=None, unit=Length.UNKNOWN)
            self.state = EnumAttribute("state", parent=self)
            self.drives: Drives = Drives(vehicle=self)
            self.doors: Doors = Doors(vehicle=self)
            self.windows: Windows = Windows(vehicle=self)
            self.lights: Lights = Lights(vehicle=self)
            self.software: Software = Software(vehicle=self)

            self.managing_connectors: list[BaseConnector] = []
            if managing_connector is not None:
                self.managing_connectors.append(managing_connector)

            self.enabled = True
        self.delay_notifications = False

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
        if self.state.enabled:
            return_string += f'{self.state}\n'
        if self.drives.enabled:
            return_string += f'{self.drives}\n'
        if self.doors.enabled:
            return_string += f'{self.doors}\n'
        if self.windows.enabled:
            return_string += f'{self.windows}\n'
        if self.lights.enabled:
            return_string += f'{self.lights}\n'
        return return_string

    class Type(Enum):
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

    class State(Enum):
        """
        Enum representing different states of a vehicle.
        """
        OFFLINE = 'offline'
        PARKED = 'parked'
        IGNITION_ON = 'ignition_on'
        DRIVING = 'driving'
        INVALID = 'invalid'
        UNKNOWN = 'unknown vehicle state'


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
