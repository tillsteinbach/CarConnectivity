"""Module for position classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum
import logging

from carconnectivity.observable import Observable
from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute, FloatAttribute, RangeAttribute
from carconnectivity.units import LatitudeLongitude, Length, Heading
from carconnectivity.location import Location
from carconnectivity.interfaces import ICarConnectivity
from carconnectivity_services.base.service import BaseService
from carconnectivity_services.base.service import ServiceType
from carconnectivity_services.location.location_service import LocationService

if TYPE_CHECKING:
    from typing import Optional, Dict

LOG: logging.Logger = logging.getLogger("carconnectivity")


class Position(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a position.
    """
    def __init__(self, parent: Optional[GenericObject] = None, initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id='position', parent=parent, initialization=initialization)
        self.position_type: EnumAttribute[Position.PositionType] = EnumAttribute("position_type", parent=self, value_type=Position.PositionType,
                                                                                 tags={'carconnectivity'},
                                                                                 initialization=self.get_initialization('position_type'))
        self.latitude: FloatAttribute = FloatAttribute("latitude", parent=self, minimum=-90, maximum=90, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                       tags={'carconnectivity'}, initialization=self.get_initialization('latitude'))
        self.longitude: FloatAttribute = FloatAttribute("longitude", parent=self, minimum=-180, maximum=180, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                        tags={'carconnectivity'}, initialization=self.get_initialization('longitude'))
        self.altitude: RangeAttribute = RangeAttribute("altitude", parent=self, minimum=-1000, maximum=10000, unit=Length.M, precision=0.1,
                                                       tags={'carconnectivity'}, initialization=self.get_initialization('altitude'))
        self.heading: FloatAttribute = FloatAttribute("heading", parent=self, minimum=0, maximum=360, unit=Heading.DEGREE, precision=0.1,
                                                      tags={'carconnectivity'}, initialization=self.get_initialization('heading'))
        self.location: Location = Location(name="position_location", parent=self, initialization=self.get_initialization('position_location'))

        self.longitude.add_observer(self._on_position_changed, flag=(Observable.ObserverEvent.VALUE_CHANGED
                                                                     | Observable.ObserverEvent.ENABLED
                                                                     | Observable.ObserverEvent.DISABLED),
                                    priority=Observable.ObserverPriority.INTERNAL_HIGH)

    def _on_position_changed(self, element: FloatAttribute, flags) -> None:
        """
        Callback when position attributes change.
        """
        del flags
        del element
        if self.latitude.enabled and self.latitude.value is not None and self.longitude.enabled and self.longitude.value is not None:
            if self.parent is not None and self.parent.parent is not None \
                    and isinstance(self.parent.parent.parent, ICarConnectivity):
                location_service: Optional[BaseService] = self.parent.parent.parent.get_service_for(ServiceType.LOCATION_REVERSE)
                if location_service is not None and isinstance(location_service, LocationService):
                    result: Optional[Location] = location_service.location_from_lat_lon(
                        latitude=self.latitude.value,
                        longitude=self.longitude.value,
                        location=self.location
                    )
                    if result is not None:
                        LOG.debug('Resolved location from position (%s, %s)', self.latitude.value, self.longitude.value)
                else:
                    LOG.warning('No LocationService available to resolve location from position')
                    self.location.clear()
            else:
                LOG.warning('Position not in correct context of CarConnectivity, cannot resolve location')
                self.location.clear()
        else:
            self.location.clear()

    class PositionType(Enum):
        """
        Enum for position type.
        """
        PARKING = 'parking'
        DRIVING = 'driving'
        INVALID = 'invalid'
        UNKNOWN = 'unknown'
