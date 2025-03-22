"""
Module for vehicle classes.

This module defines various classes representing different types of vehicles,
including generic vehicles, electric vehicles, combustion vehicles, and hybrid vehicles.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, EnumAttribute, RangeAttribute, TemperatureAttribute, IntegerAttribute
from carconnectivity.doors import Doors
from carconnectivity.windows import Windows
from carconnectivity.lights import Lights
from carconnectivity.software import Software
from carconnectivity.drive import Drives
from carconnectivity.charging import Charging
from carconnectivity.drive import ElectricDrive
from carconnectivity.units import Length
from carconnectivity.position import Position
from carconnectivity.climatization import Climatization
from carconnectivity.commands import Commands
from carconnectivity.maintenance import Maintenance
from carconnectivity.window_heating import WindowHeatings

# pylint: disable=duplicate-code
SUPPORT_IMAGES = False
try:
    from PIL import Image  # pylint: disable=unused-import # noqa: F401
    from carconnectivity.images import Images  # pylint: disable=ungrouped-imports
    SUPPORT_IMAGES = True
except ImportError:
    pass
# pylint: enable=duplicate-code

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
    # pylint: disable-next=too-many-statements,duplicate-code
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(parent=garage, origin=origin)
            self.delay_notifications = True
            self.commands: Commands = origin.commands
            self.commands.parent = self
            self.vin: StringAttribute = origin.vin
            self.vin.parent = self
            self.name: StringAttribute = origin.name
            self.name.parent = self
            self.manufacturer: StringAttribute = origin.manufacturer
            self.manufacturer.parent = self
            self.model: StringAttribute = origin.model
            self.model.parent = self
            self.model_year: IntegerAttribute = origin.model_year
            self.model_year.parent = self
            self.type: EnumAttribute = origin.type
            self.type.parent = self
            self.license_plate: StringAttribute = origin.license_plate
            self.license_plate.parent = self
            self.odometer: RangeAttribute = origin.odometer
            self.odometer.parent = self
            self.state: EnumAttribute = origin.state
            self.state.parent = self
            self.connection_state: EnumAttribute = origin.connection_state
            self.connection_state.parent = self
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
            self.position: Position = origin.position
            self.position.parent = self
            self.enabled = origin.enabled
            self.climatization: Climatization = origin.climatization
            self.climatization.parent = self
            self.window_heatings: WindowHeatings = origin.window_heatings
            self.window_heatings.parent = self
            self.outside_temperature: TemperatureAttribute = origin.outside_temperature
            self.outside_temperature.parent = self
            self.specification: GenericVehicle.VehicleSpecification = origin.specification
            self.specification.parent = self
            self.maintenance: Maintenance = origin.maintenance
            self.maintenance.parent = self
            if SUPPORT_IMAGES:
                self.images: Images = origin.images
            self.managing_connectors = origin.managing_connectors
        else:
            if vin is None:
                raise ValueError('Cannot create vehicle without VIN')
            if garage is None:
                raise ValueError('Cannot create vehicle without garage')
            super().__init__(object_id=vin.upper(), parent=garage)
            self.delay_notifications = True
            if vin is None:
                raise ValueError('VIN cannot be None')
            self.commands: Commands = Commands(parent=self)
            self.vin = StringAttribute("vin", self, vin.upper(), tags={'carconnectivity'})
            self.name = StringAttribute("name", self, tags={'carconnectivity'})
            self.manufacturer = StringAttribute("manufacturer", self, tags={'carconnectivity'})
            self.model = StringAttribute("model", self, tags={'carconnectivity'})
            self.model_year = IntegerAttribute("model_year", self, tags={'carconnectivity'})
            self.type = EnumAttribute("type", parent=self, tags={'carconnectivity'}, value_type=GenericVehicle.Type)
            self.license_plate = StringAttribute("license_plate", self, tags={'carconnectivity'})
            self.odometer: RangeAttribute = RangeAttribute(name="odometer", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, tags={'carconnectivity'})
            self.state = EnumAttribute("state", parent=self, tags={'carconnectivity'}, value_type=GenericVehicle.State)
            self.connection_state = EnumAttribute("connection_state", parent=self, tags={'carconnectivity'}, value_type=GenericVehicle.ConnectionState)
            self.drives: Drives = Drives(vehicle=self)
            self.doors: Doors = Doors(vehicle=self)
            self.windows: Windows = Windows(vehicle=self)
            self.lights: Lights = Lights(vehicle=self)
            self.software: Software = Software(vehicle=self)
            self.position: Position = Position(parent=self)
            self.climatization: Climatization = Climatization(vehicle=self)
            self.window_heatings: WindowHeatings = WindowHeatings(vehicle=self)
            self.outside_temperature: TemperatureAttribute = TemperatureAttribute("outside_temperature", parent=self, minimum=-40, maximum=85,
                                                                                  tags={'carconnectivity'})
            self.specification: GenericVehicle.VehicleSpecification = GenericVehicle.VehicleSpecification(vehicle=self)
            self.maintenance: Maintenance = Maintenance(vehicle=self)
            if SUPPORT_IMAGES:
                self.images: Images = Images(vehicle=self)

            self.managing_connectors: list[BaseConnector] = []
            if managing_connector is not None:
                self.managing_connectors.append(managing_connector)

            self.enabled = True
        self.delay_notifications = False
    # pylint: enable=duplicate-code

    def is_managed_by_connector(self, connector: Optional[BaseConnector]) -> bool:
        """
        Checks if the vehicle is managed by the given connector.

        Args:
            connector (Optional[BaseConnector]): The connector to check.

        Returns:
            bool: True if the vehicle is managed by the given connector, False otherwise.
        """
        return connector in self.managing_connectors

    class VehicleSpecification(GenericObject):
        """
        A class to represent the specification of a vehicle.
        """
        def __init__(self, vehicle: Optional[GenericVehicle] = None, origin: Optional[GenericVehicle.VehicleSpecification] = None) -> None:
            if origin is not None:
                super().__init__(origin=origin)
                self.steering_wheel_position: EnumAttribute = origin.steering_wheel_position
                self.steering_wheel_position.parent = self
            else:
                if vehicle is None:
                    raise ValueError('Cannot create specification without vehicle')
                super().__init__(object_id='specification', parent=vehicle)
                self.delay_notifications = True
                self.steering_wheel_position: EnumAttribute = EnumAttribute("steering_wheel_position", parent=self,
                                                                            value_type=GenericVehicle.VehicleSpecification.SteeringPosition,
                                                                            tags={'carconnectivity'})
                self.gearbox: EnumAttribute = EnumAttribute("gearbox", parent=self, value_type=GenericVehicle.VehicleSpecification.GearboxType,
                                                            tags={'carconnectivity'})
                self.delay_notifications = False

        class SteeringPosition(Enum):
            """
            Enum representing the position of the steering wheel.
            """
            LEFT = 'left'
            RIGHT = 'right'
            INVALID = 'invalid'
            UNKNOWN = 'unknown steering position'

        class GearboxType(Enum):
            """
            Enum representing the type of the gearbox.
            """
            MANUAL = 'manual'
            AUTOMATIC = 'automatic'
            INVALID = 'invalid'
            UNKNOWN = 'unknown gearbox type'

    # pylint: disable=duplicate-code
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
    # pylint: enable=duplicate-code

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

    class ConnectionState(Enum):
        """
        Enum representing different states of a vehicle connection.

        Attributes:
        -----------
        ONLINE : str
            The vehicle is online.
        REACHABLE : str
            The vehicle is reachable but may be sleeping.
        OFFLINE : str
            The vehicle is offline.
        INVALID : str
            The vehicle connection state is invalid.
        UNKNOWN : str
            The vehicle connection state is unknown.
        """
        ONLINE = 'online'
        REACHABLE = 'reachable'
        OFFLINE = 'offline'
        INVALID = 'invalid'
        UNKNOWN = 'unknown vehicle state'


class ElectricVehicle(GenericVehicle):
    """
    Represents an electric vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
            if isinstance(origin, ElectricVehicle):
                self.charging: Charging = origin.charging
                self.charging.parent = self
            else:
                self.charging: Charging = Charging(vehicle=self)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
            self.charging: Charging = Charging(vehicle=self)

    def get_electric_drive(self) -> Optional[ElectricDrive]:
        """
        Returns the electric drive of the vehicle.

        Returns:
            Drives.ElectricDrive: The electric drive of the vehicle.
        """
        if self.drives is not None and self.drives.drives is not None and len(self.drives.drives) > 0:
            for drive in self.drives.drives.values():
                if isinstance(drive, ElectricDrive) and drive.enabled:
                    return drive
        return None


class CombustionVehicle(GenericVehicle):
    """
    Represents an combustion vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)


class HybridVehicle(ElectricVehicle, CombustionVehicle):
    """
    Represents a hybrid vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
