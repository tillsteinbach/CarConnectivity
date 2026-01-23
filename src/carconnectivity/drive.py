"""
This module defines classes related to vehicle drives.

It includes the Drives class to manage multiple drives of a vehicle,
and the GenericDrive class along with its subclasses ElectricDrive
and CombustionDrive to represent different types of vehicle drives.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum
from datetime import datetime, timezone

from carconnectivity.observable import Observable
from carconnectivity.objects import GenericObject
from carconnectivity.attributes import RangeAttribute, LevelAttribute, EnumAttribute, EnergyConsumptionAttribute, FuelConsumptionAttribute
from carconnectivity.units import Length, EnergyConsumption, FuelConsumption
from carconnectivity.battery import Battery
from carconnectivity.fuel_tank import FuelTank

if TYPE_CHECKING:
    from typing import Dict, Optional
    from carconnectivity.vehicle import GenericVehicle


class Drives(GenericObject):
    """
    Represents the drives of a vehicle.
    """
    def __init__(self, vehicle: GenericVehicle, initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id='drives', parent=vehicle, initialization=initialization)
        self.total_range: RangeAttribute = RangeAttribute(name="total_range", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                          tags={'carconnectivity'}, initialization=self.get_initialization('total_range'))
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
    def __init__(self, drive_id: str, drives: Drives, initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id=drive_id, parent=drives, initialization=initialization)
        self.type: EnumAttribute[GenericDrive.Type] = EnumAttribute(name="type", parent=self, value=None, tags={'carconnectivity'},
                                                                    value_type=GenericDrive.Type, initialization=self.get_initialization('type'))
        self.range: RangeAttribute = RangeAttribute(name="range", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                    tags={'carconnectivity'}, initialization=self.get_initialization('range'))
        self.range_estimated_full: RangeAttribute = RangeAttribute(name="range_estimated_full", parent=self, value=None, unit=Length.UNKNOWN, minimum=0,
                                                                   precision=0.1, tags={'carconnectivity'},
                                                                   initialization=self.get_initialization('range_estimated_full'))
        self.range_wltp: RangeAttribute = RangeAttribute(name="range_wltp", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                         tags={'carconnectivity'}, initialization=self.get_initialization('range_wltp'))
        self.level: LevelAttribute = LevelAttribute(name="level", parent=self, value=None, minimum=0, precision=0.1, tags={'carconnectivity'},
                                                    initialization=self.get_initialization('level'))
        self.enabled = True

        self.range.add_observer(self.__on_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)
        self.level.add_observer(self.__on_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)

    def __on_range_or_level_change(self, element: EnumAttribute, flags: Observable.ObserverEvent) -> None:
        del element
        del flags
        if self.range.enabled and self.level.enabled and self.range.value is not None and self.level.value is not None and self.level.value > 0:
            new_range_estimated_full: float = self.range.value / self.level.value * 100
            if self.range_estimated_full.value != new_range_estimated_full:
                measurement_time: Optional[datetime] = self.range.last_updated
                if measurement_time is None and self.level.last_updated is not None:
                    measurement_time = self.level.last_updated
                if measurement_time is None:
                    measurement_time = datetime.now(tz=timezone.utc)
                self.range_estimated_full._set_value(value=new_range_estimated_full, measured=measurement_time,  # pylint: disable=protected-access
                                                     unit=self.range.unit)
                self.range_estimated_full.precision = self.range.precision

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
    def __init__(self, drive_id: str, drives: Drives, initialization: Optional[Dict] = None) -> None:
        super().__init__(drive_id=drive_id, drives=drives, initialization=initialization)
        self.battery: Battery = Battery(drive=self, initialization=self.get_initialization('battery'))
        self.consumption: EnergyConsumptionAttribute = EnergyConsumptionAttribute(name="consumption", parent=self, value=None,
                                                                                  unit=EnergyConsumption.UNKNOWN,
                                                                                  minimum=0, precision=0.01, tags={'carconnectivity'},
                                                                                  initialization=self.get_initialization('consumption'))

        self.range.add_observer(self.__on_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)
        self.level.add_observer(self.__on_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)

    def __on_range_or_level_change(self, element: EnumAttribute, flags: Observable.ObserverEvent) -> None:
        del element
        del flags
        # pylint: disable=too-many-boolean-expressions
        if self.range.enabled and self.level.enabled and self.range.value is not None and self.level.value is not None and self.level.value > 0 \
                and self.battery.enabled and self.battery is not None and self.battery.available_capacity.enabled \
                and self.battery.available_capacity.value is not None and self.battery.available_capacity.value > 0:
            new_estimated_consuption: float = self.battery.available_capacity.value / (self.range.value / self.level.value * 100) * 100
            if self.consumption.value != new_estimated_consuption:
                measurement_time: Optional[datetime] = self.range.last_updated
                if measurement_time is None and self.level.last_updated is not None:
                    measurement_time = self.level.last_updated
                if measurement_time is None:
                    measurement_time = datetime.now(tz=timezone.utc)
                if self.range.unit == Length.KM:
                    unit: EnergyConsumption = EnergyConsumption.KWH100KM
                else:
                    unit = EnergyConsumption.KWH100MI
                self.consumption._set_value(value=new_estimated_consuption, measured=measurement_time, unit=unit)  # pylint: disable=protected-access


class CombustionDrive(GenericDrive):
    """
    Represents an combustion drive.
    """
    def __init__(self, drive_id: str, drives: Drives, initialization: Optional[Dict] = None) -> None:
        super().__init__(drive_id=drive_id, drives=drives, initialization=initialization)
        self.fuel_tank: FuelTank = FuelTank(drive=self, initialization=self.get_initialization('fuel_tank'))
        self.consumption: FuelConsumptionAttribute = FuelConsumptionAttribute(name="consumption", parent=self, value=None,
                                                                              unit=FuelConsumption.UNKNOWN,
                                                                              minimum=0, precision=0.1, tags={'carconnectivity'},
                                                                              initialization=self.get_initialization('consumption'))

        self.range.add_observer(self.__on_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)
        self.level.add_observer(self.__on_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)

    def __on_range_or_level_change(self, element: EnumAttribute, flags: Observable.ObserverEvent) -> None:
        del element
        del flags
        # pylint: disable-next=too-many-boolean-expressions
        if self.range.enabled and self.level.enabled and self.range.value is not None and self.level.value is not None and self.level.value > 0 \
                and self.fuel_tank.enabled and self.fuel_tank is not None and self.fuel_tank.available_capacity.enabled \
                and self.fuel_tank.available_capacity.value is not None and self.fuel_tank.available_capacity.value > 0:
            new_estimated_consuption: float = self.fuel_tank.available_capacity.value / (self.range.value / self.level.value * 100) * 100
            if self.consumption.value != new_estimated_consuption:
                measurement_time: Optional[datetime] = self.range.last_updated
                if measurement_time is None and self.level.last_updated is not None:
                    measurement_time = self.level.last_updated
                if measurement_time is None:
                    measurement_time = datetime.now(tz=timezone.utc)
                if self.range.unit == Length.KM:
                    unit: FuelConsumption = FuelConsumption.L100KM
                else:
                    unit = FuelConsumption.MPG
                self.consumption._set_value(value=new_estimated_consuption, measured=measurement_time, unit=unit)  # pylint: disable=protected-access


class DieselDrive(CombustionDrive):
    """
    Represents a diesel combustion drive.
    """
    def __init__(self, drive_id: str, drives: Drives, initialization: Optional[Dict] = None) -> None:
        super().__init__(drive_id=drive_id, drives=drives, initialization=initialization)
        self.adblue_tank: FuelTank = FuelTank(drive=self, initialization=self.get_initialization('adblue_tank'))
        self.adblue_range: RangeAttribute = RangeAttribute(name="adblue_range", parent=self, value=None, unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                           tags={'carconnectivity'}, initialization=self.get_initialization('adblue_range'))
        self.adblue_level: LevelAttribute = LevelAttribute(name="adblue_level", parent=self, value=None, minimum=0, precision=0.1,
                                                           tags={'carconnectivity'}, initialization=self.get_initialization('adblue_level'))
        self.adblue_range_estimated_full: RangeAttribute = RangeAttribute(name="adblue_range_estimated_full", parent=self, value=None,
                                                                          unit=Length.UNKNOWN, minimum=0, precision=0.1,
                                                                          tags={'carconnectivity'},
                                                                          initialization=self.get_initialization('adblue_range_estimated_full'))
        self.adblue_consumption: FuelConsumptionAttribute = FuelConsumptionAttribute(name="adblue_consumption", parent=self, value=None,
                                                                                     unit=FuelConsumption.UNKNOWN,
                                                                                     minimum=0, precision=0.01, tags={'carconnectivity'},
                                                                                     initialization=self.get_initialization('adblue_consumption'))

        self.adblue_range.add_observer(self.__on_adblue_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                       priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)
        self.adblue_level.add_observer(self.__on_adblue_range_or_level_change, Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT,
                                       priority=Observable.ObserverPriority.INTERNAL_HIGH, on_transaction_end=True)

    def __on_adblue_range_or_level_change(self, element: EnumAttribute, flags: Observable.ObserverEvent) -> None:
        del element
        del flags
        if self.adblue_range.enabled and self.adblue_level.enabled and self.adblue_range.value is not None and self.adblue_level.value is not None \
                and self.adblue_level.value > 0:
            new_range_estimated_full: float = self.adblue_range.value / self.adblue_level.value * 100
            if self.adblue_range_estimated_full.value != new_range_estimated_full:
                measurement_time: Optional[datetime] = self.adblue_range.last_updated
                if measurement_time is None and self.adblue_level.last_updated is not None:
                    measurement_time = self.adblue_level.last_updated
                if measurement_time is None:
                    measurement_time = datetime.now(tz=timezone.utc)
                self.adblue_range_estimated_full._set_value(value=new_range_estimated_full, measured=measurement_time,  # pylint: disable=protected-access
                                                            unit=self.adblue_range.unit)

        # pylint: disable-next=too-many-boolean-expressions
        if self.adblue_range.enabled and self.adblue_level.enabled and self.adblue_range.value is not None and self.adblue_level.value is not None \
                and self.adblue_level.value > 0 \
                and self.adblue_tank.enabled and self.adblue_tank is not None and self.adblue_tank.available_capacity.enabled \
                and self.adblue_tank.available_capacity.value is not None and self.adblue_tank.available_capacity.value > 0:
            new_estimated_consuption: float = self.adblue_tank.available_capacity.value / (self.adblue_range.value / self.adblue_level.value * 100) * 100
            if self.adblue_consumption.value != new_estimated_consuption:
                measurement_time: Optional[datetime] = self.adblue_range.last_updated
                if measurement_time is None and self.adblue_level.last_updated is not None:
                    measurement_time = self.adblue_level.last_updated
                if measurement_time is None:
                    measurement_time = datetime.now(tz=timezone.utc)
                if self.adblue_range.unit == Length.KM:
                    unit: FuelConsumption = FuelConsumption.L100KM
                else:
                    unit = FuelConsumption.MPG
                self.adblue_consumption._set_value(value=new_estimated_consuption, measured=measurement_time, unit=unit)  # pylint: disable=protected-access
