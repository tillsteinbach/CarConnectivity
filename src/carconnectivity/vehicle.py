"""
Module for vehicle classes.

This module defines various classes representing different types of vehicles,
including generic vehicles, electric vehicles, combustion vehicles, and hybrid vehicles.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.interfaces import IGenericVehicle
from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, EnumAttribute, RangeAttribute, TemperatureAttribute, IntegerAttribute
from carconnectivity.doors import Doors
from carconnectivity.windows import Windows
from carconnectivity.lights import Lights
from carconnectivity.software import Software
from carconnectivity.drive import Drives
from carconnectivity.charging import Charging
from carconnectivity.drive import ElectricDrive, CombustionDrive
from carconnectivity.units import Length
from carconnectivity.position import Position
from carconnectivity.climatization import Climatization
from carconnectivity.commands import Commands
from carconnectivity.maintenance import Maintenance
from carconnectivity.window_heating import WindowHeatings

# pylint: disable=duplicate-code
SUPPORT_IMAGES = False  # pylint: disable=invalid-name
try:
    from PIL import Image  # pylint: disable=unused-import # noqa: F401
    from carconnectivity.images import Images  # pylint: disable=ungrouped-imports
    SUPPORT_IMAGES = True  # pylint: disable=invalid-name
except ImportError:
    pass
# pylint: enable=duplicate-code

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.garage import Garage

    from carconnectivity_connectors.base.connector import BaseConnector


class GenericVehicle(GenericObject, IGenericVehicle):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a generic vehicle.

    Attributes:
    -----------
    vin : StringAttribute
        The vehicle identification number (VIN) of the vehicle.
    license_plate : StringAttribute
        The license plate of the vehicle.
    """
    # pylint: disable-next=too-many-statements,duplicate-code,too-many-arguments,too-many-positional-arguments
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None, initialization: Optional[Dict] = None) -> None:
        if origin is not None:
            super().__init__(parent=garage, origin=origin, initialization=initialization)
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
            self.type: EnumAttribute[GenericVehicle.Type] = origin.type
            self.type.parent = self
            self.license_plate: StringAttribute = origin.license_plate
            self.license_plate.parent = self
            self.odometer: RangeAttribute = origin.odometer
            self.odometer.parent = self
            self.state: EnumAttribute[GenericVehicle.State] = origin.state
            self.state.parent = self
            self.connection_state: EnumAttribute[GenericVehicle.ConnectionState] = origin.connection_state
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
                self.images.parent = self
            self.managing_connectors = origin.managing_connectors
        else:
            if vin is None:
                raise ValueError('Cannot create vehicle without VIN')
            if garage is None:
                raise ValueError('Cannot create vehicle without garage')
            super().__init__(object_id=vin.upper(), parent=garage, initialization=initialization)
            self.delay_notifications = True
            if vin is None:
                raise ValueError('VIN cannot be None')
            self.commands: Commands = Commands(parent=self)
            self.vin: StringAttribute = StringAttribute("vin", self, vin.upper(), tags={'carconnectivity'}, initialization=self.get_initialization('vin'))
            self.name: StringAttribute = StringAttribute("name", self, tags={'carconnectivity'}, initialization=self.get_initialization('name'))
            self.manufacturer: StringAttribute = StringAttribute("manufacturer", self, tags={'carconnectivity'},
                                                                 initialization=self.get_initialization('manufacturer'))
            self.model: StringAttribute = StringAttribute("model", self, tags={'carconnectivity'}, initialization=self.get_initialization('model'))
            self.model_year: IntegerAttribute = IntegerAttribute("model_year", self, tags={'carconnectivity'},
                                                                 initialization=self.get_initialization('model_year'))
            self.type: EnumAttribute[GenericVehicle.Type] = EnumAttribute("type", parent=self, tags={'carconnectivity'}, value_type=GenericVehicle.Type,
                                                                          initialization=self.get_initialization('type'))
            self.license_plate: StringAttribute = StringAttribute("license_plate", self, tags={'carconnectivity'},
                                                                  initialization=self.get_initialization('license_plate'))
            self.odometer: RangeAttribute = RangeAttribute(name="odometer", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                           tags={'carconnectivity'}, initialization=self.get_initialization('odometer'))
            self.state: EnumAttribute[GenericVehicle.State] = EnumAttribute("state", parent=self, tags={'carconnectivity'}, value_type=GenericVehicle.State,
                                                                            initialization=self.get_initialization('state'))
            self.connection_state: EnumAttribute[GenericVehicle.ConnectionState] = EnumAttribute("connection_state", parent=self, tags={'carconnectivity'},
                                                                                                 value_type=GenericVehicle.ConnectionState,
                                                                                                 initialization=self.get_initialization('connection_state'))
            self.drives: Drives = Drives(vehicle=self, initialization=self.get_initialization('drives'))
            self.doors: Doors = Doors(vehicle=self, initialization=self.get_initialization('doors'))
            self.windows: Windows = Windows(vehicle=self, initialization=self.get_initialization('windows'))
            self.lights: Lights = Lights(vehicle=self, initialization=self.get_initialization('lights'))
            self.software: Software = Software(vehicle=self, initialization=self.get_initialization('software'))
            self.position: Position = Position(parent=self, initialization=self.get_initialization('position'))
            self.climatization: Climatization = Climatization(vehicle=self, initialization=self.get_initialization('climatization'))
            self.window_heatings: WindowHeatings = WindowHeatings(vehicle=self, initialization=self.get_initialization('window_heating'))
            self.outside_temperature: TemperatureAttribute = TemperatureAttribute("outside_temperature", parent=self, minimum=-40, maximum=85, precision=0.1,
                                                                                  tags={'carconnectivity'},
                                                                                  initialization=self.get_initialization('outside_temperature'))
            self.specification: GenericVehicle.VehicleSpecification = \
                GenericVehicle.VehicleSpecification(vehicle=self, initialization=self.get_initialization('specification'))
            self.maintenance: Maintenance = Maintenance(vehicle=self, initialization=self.get_initialization('maintenance'))
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
        def __init__(self, vehicle: Optional[GenericVehicle] = None, origin: Optional[GenericVehicle.VehicleSpecification] = None,
                     initialization: Optional[Dict] = None) -> None:
            if origin is not None:
                super().__init__(origin=origin, initialization=initialization)
                self.steering_wheel_position: EnumAttribute = origin.steering_wheel_position
                self.steering_wheel_position.parent = self
            else:
                if vehicle is None:
                    raise ValueError('Cannot create specification without vehicle')
                super().__init__(object_id='specification', parent=vehicle, initialization=initialization)
                self.delay_notifications = True
                self.steering_wheel_position: EnumAttribute[GenericVehicle.VehicleSpecification.SteeringPosition] = \
                    EnumAttribute("steering_wheel_position", parent=self,
                                  value_type=GenericVehicle.VehicleSpecification.SteeringPosition,
                                  tags={'carconnectivity'},
                                  initialization=self.get_initialization('steering_wheel_position'))
                self.gearbox: EnumAttribute[GenericVehicle.VehicleSpecification.GearboxType] = \
                    EnumAttribute("gearbox", parent=self, value_type=GenericVehicle.VehicleSpecification.GearboxType, tags={'carconnectivity'},
                                  initialization=self.get_initialization('gearbox'))
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
    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None, initialization: Optional[Dict] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin, initialization=initialization)
            if isinstance(origin, ElectricVehicle):
                self.charging: Charging = origin.charging
                self.charging.parent = self
            else:
                self.charging: Charging = Charging(vehicle=self)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector, initialization=initialization)
            self.charging: Charging = Charging(vehicle=self, initialization=self.get_initialization('charging'))

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
    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None, initialization: Optional[Dict] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin, initialization=initialization)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector, initialization=initialization)

    def get_combustion_drive(self) -> Optional[CombustionDrive]:
        """
        Returns the combustion drive of the vehicle.

        Returns:
            Drives.CombustionDrive: The electric drive of the vehicle.
        """
        if self.drives is not None and self.drives.drives is not None and len(self.drives.drives) > 0:
            for drive in self.drives.drives.values():
                if isinstance(drive, CombustionDrive) and drive.enabled:
                    return drive
        return None


class HybridVehicle(ElectricVehicle, CombustionVehicle):
    """
    Represents a hybrid vehicle.
    """
    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[GenericVehicle] = None, initialization: Optional[Dict] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin, initialization=initialization)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector, initialization=initialization)
