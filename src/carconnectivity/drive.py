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
from carconnectivity.attributes import RangeAttribute, LevelAttribute, EnumAttribute
from carconnectivity.units import Length

if TYPE_CHECKING:
    from typing import Dict
    from carconnectivity.vehicle import GenericVehicle


class Drives(GenericObject):
    """
    Represents the drives of a vehicle.
    """
    def __init__(self, vehicle: GenericVehicle) -> None:
        super().__init__(object_id='drives', parent=vehicle)
        self.total_range: RangeAttribute = RangeAttribute(name="total_range", parent=self, value=None, unit=Length.UNKNOWN)
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

    def __str__(self) -> str:
        return_string: str = 'Drives:\n'
        if self.total_range.enabled:
            return_string += f'{self.total_range}\n'
        for drive in self.drives.values():
            return_string += f'\t{drive}\n'
        return return_string


class GenericDrive(GenericObject):
    """
    A class to represent a generic drive.
    """
    def __init__(self, drive_id: str, drives: Drives) -> None:
        super().__init__(object_id=drive_id, parent=drives)
        self.type: EnumAttribute = EnumAttribute(name="type", parent=self, value=None)
        self.range: RangeAttribute = RangeAttribute(name="range", parent=self, value=None, unit=Length.UNKNOWN)
        self.level: LevelAttribute = LevelAttribute(name="level", parent=self, value=None)
        self.enabled = True

    def __str__(self) -> str:
        return_string: str = f'Drive: {self.id}\n'
        if self.type.enabled:
            return_string += f'{self.type}\n'
        if self.range.enabled:
            return_string += f'{self.range}\n'
        return return_string

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


class CombustionDrive(GenericDrive):
    """
    Represents an combustion drive.
    """
    def __init__(self, drive_id: str, drives: Drives) -> None:
        super().__init__(drive_id=drive_id, drives=drives)
