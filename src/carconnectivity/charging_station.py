""" Module defining the ChargingStation data class for charging station locations."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, FloatAttribute, IntegerAttribute
from carconnectivity.units import LatitudeLongitude, Power

if TYPE_CHECKING:
    from typing import Optional, Dict


class ChargingStation(GenericObject):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Represents a charging station with its properties and attributes.
    This class encapsulates all information about a charging station including its location,
    power capabilities, operator details, and other relevant metadata.
    Args:
        name (str): The name/identifier of the charging station.
        parent (Optional[GenericObject]): The parent object in the object hierarchy.
    Attributes:
        source (StringAttribute): The data source providing the charging station information.
        uid (StringAttribute): Unique identifier for the charging station.
        name (StringAttribute): Display name of the charging station.
        latitude (FloatAttribute): Geographical latitude of the station location (-90 to 90 degrees).
        longitude (FloatAttribute): Geographical longitude of the station location (-180 to 180 degrees).
        address (StringAttribute): Physical address of the charging station.
        max_power (FloatAttribute): Maximum power output capacity in kilowatts (kW).
        num_spots (IntegerAttribute): Number of charging spots/ports available.
        operator_id (StringAttribute): Identifier of the charging station operator.
        operator_name (StringAttribute): Name of the charging station operator.
        raw (StringAttribute): Raw data from the source system.
    """
    def __init__(self, name: str, parent: Optional[GenericObject], initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id=name, parent=parent, initialization=initialization)

        self.source: StringAttribute = StringAttribute("source", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('source'))
        self.uid: StringAttribute = StringAttribute("uid", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('uid'))
        self.name: StringAttribute = StringAttribute("name", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('name'))
        self.latitude: FloatAttribute = FloatAttribute("latitude", parent=self, minimum=-90, maximum=90, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                       tags={'carconnectivity'}, initialization=self.get_initialization('latitude'))
        self.longitude: FloatAttribute = FloatAttribute("longitude", parent=self, minimum=-180, maximum=180, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                        tags={'carconnectivity'}, initialization=self.get_initialization('longitude'))
        self.address: StringAttribute = StringAttribute("address", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('address'))
        self.max_power: FloatAttribute = FloatAttribute("max_power", parent=self, minimum=0, unit=Power.KW, precision=0.1,
                                                        tags={'carconnectivity'}, initialization=self.get_initialization('max_power'))
        self.num_spots: IntegerAttribute = IntegerAttribute("num_spots", parent=self, minimum=0, tags={'carconnectivity'},
                                                            initialization=self.get_initialization('num_spots'))
        self.operator_id: StringAttribute = StringAttribute("operator_id", parent=self, tags={'carconnectivity'},
                                                            initialization=self.get_initialization('operator_id'))
        self.operator_name: StringAttribute = StringAttribute("operator_name", parent=self, tags={'carconnectivity'},
                                                              initialization=self.get_initialization('operator_name'))
        self.raw: StringAttribute = StringAttribute("raw", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('raw'))

    def clear(self) -> None:
        """
        Clears all charging station data attributes.
        """
        self.source._set_value(None)  # pylint: disable=protected-access
        self.uid._set_value(None)  # pylint: disable=protected-access
        self.name._set_value(None)  # pylint: disable=protected-access
        self.latitude._set_value(None)  # pylint: disable=protected-access
        self.longitude._set_value(None)  # pylint: disable=protected-access
        self.address._set_value(None)  # pylint: disable=protected-access
        self.max_power._set_value(None)  # pylint: disable=protected-access
        self.num_spots._set_value(None)  # pylint: disable=protected-access
        self.operator_id._set_value(None)  # pylint: disable=protected-access
        self.operator_name._set_value(None)  # pylint: disable=protected-access
        self.raw._set_value(None)  # pylint: disable=protected-access
