"""
This module defines classes related to vehicle drives.

It includes the Drives class to manage multiple drives of a vehicle,
and the GenericDrive class along with its subclasses ElectricDrive
and CombustionDrive to represent different types of vehicle drives.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import RangeAttribute, LevelAttribute, EnumAttribute, EnergyAttribute, SpeedAttribute, MinutesAttribute
from carconnectivity.units import Length, Speed, FuelConsumption, ElectricConsumption, Minutes
from carconnectivity.battery import Battery

if TYPE_CHECKING:
    from typing import Dict
    from carconnectivity.vehicle import GenericVehicle


class Drives(GenericObject):
    """
    Represents the drives of a vehicle.
    """
    def __init__(self, vehicle: GenericVehicle) -> None:
        super().__init__(object_id='drives', parent=vehicle)
        self.total_range: RangeAttribute = RangeAttribute(name="total_range", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                          tags={'carconnectivity'})
        self.last_trip_distance: RangeAttribute = RangeAttribute(name="last_trip_distance", parent=self, value=None, unit=Length.KM, minimum=0, tags={'carconnectivity'}) 
        self.last_trip_average_speed: SpeedAttribute = SpeedAttribute(name="last_trip_averageSpeed", parent=self, value=None, unit=Speed.KMH, minimum=0, tags={'carconnectivity'}) 
        self.last_trip_duration: MinutesAttribute = MinutesAttribute(name="last_trip_duration", parent=self, value=None, unit=Minutes.MIN, minimum=0, tags={'carconnectivity'}) 
        self.drives: Dict[str, GenericDrive] = {}

    def add_drive(self, drive: GenericDrive) -> None:
        """
        Adds a drive to the drives of the vehicle.

        Parameters:
        -----------
        drive : GenericDrive
            The drive to add.
        """
        self.drives[drive.id] = drive


class GenericDrive(GenericObject):
    """
    A class to represent a generic drive.
    """
    def __init__(self, drive_id: str, drives: Drives) -> None:
        super().__init__(object_id=drive_id, parent=drives)
        self.type: EnumAttribute = EnumAttribute(name="type", parent=self, value=None, tags={'carconnectivity'})
        self.range: RangeAttribute = RangeAttribute(name="range", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                    tags={'carconnectivity'})
        self.level: LevelAttribute = LevelAttribute(name="level", parent=self, value=None, minimum=0, precision=0.1, tags={'carconnectivity'})
        self.enabled = True

    # pylint: disable=duplicate-code
    class Type(Enum):
        """
        Enum representing different types of drives.
        """
        ELECTRIC = 'electric'
        FUEL = 'fuel'
        GASOLINE = 'gasoline'
        PETROL = 'petrol'
        DIESEL = 'diesel'
        CNG = 'cng'
        LPG = 'lpg'
        INVALID = 'invalid'
        UNKNOWN = 'unknown drive type'
    # pylint: enable=duplicate-code


class ElectricDrive(GenericDrive):
    """
    Represents an electric drive.
    """
    def __init__(self, drive_id: str, drives: Drives) -> None:
        super().__init__(drive_id=drive_id, drives=drives)
        self.battery: Battery = Battery(drive=self)
        self.last_trip_electric_consumption: EnergyAttribute = EnergyAttribute(name="last_trip_electricConsumption", parent=self, value=None, unit=ElectricConsumption.KWH, tags={'carconnectivity'}) 


class CombustionDrive(GenericDrive):
    """
    Represents an combustion drive.
    """
    def __init__(self, drive_id: str, drives: Drives) -> None:
        super().__init__(drive_id=drive_id, drives=drives)
        self.last_trip_fuel_consumption: EnergyAttribute = EnergyAttribute(name="last_trip_fuelConsumption", parent=self, value=None, unit=FuelConsumption.L, minimum=0, tags={'carconnectivity'}) 


class DieselDrive(CombustionDrive):
    """
    Represents a diesel combustion drive.
    """
    def __init__(self, drive_id: str, drives: Drives) -> None:
        super().__init__(drive_id=drive_id, drives=drives)
        self.adblue_range: RangeAttribute = RangeAttribute(name="adblue_range", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                           tags={'carconnectivity'})
        self.adblue_level: LevelAttribute = LevelAttribute(name="adblue_level", parent=self, value=None, minimum=0, precision=0.1,
                                                           tags={'carconnectivity'})
