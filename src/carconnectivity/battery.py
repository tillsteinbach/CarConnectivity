"""
This module defines classes related to batteries.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import TemperatureAttribute, EnergyAttribute
from carconnectivity.units import Temperature, Energy

if TYPE_CHECKING:
    from carconnectivity.drive import ElectricDrive


class Battery(GenericObject):
    """
    Represents the battery of a vehicle.
    """
    def __init__(self, drive: ElectricDrive) -> None:
        super().__init__(object_id='battery', parent=drive)
        self.total_capacity: EnergyAttribute = EnergyAttribute(name='total_capacity', parent=self, value=None, unit=Energy.KWH, minimum=0,
                                                               tags={'carconnectivity'})
        self.available_capacity: EnergyAttribute = EnergyAttribute(name='available_capacity', parent=self, value=None, unit=Energy.KWH,
                                                                   minimum=0, tags={'carconnectivity'})
        self.temperature: TemperatureAttribute = TemperatureAttribute(name="temperature", parent=self, value=None, unit=Temperature.C, tags={'carconnectivity'})
        self.temperature_min: TemperatureAttribute = TemperatureAttribute(name="temperature_min", parent=self, value=None, unit=Temperature.C,
                                                                          tags={'carconnectivity'})
        self.temperature_max: TemperatureAttribute = TemperatureAttribute(name="temperature_max", parent=self, value=None, unit=Temperature.C,
                                                                          tags={'carconnectivity'})
