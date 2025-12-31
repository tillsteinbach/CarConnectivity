"""Module containing the BaseService class that needs to be extended to implement a new service."""
# pylint: disable=duplicate-code
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity_services.base.service import BaseService

if TYPE_CHECKING:
    import logging
    from typing import Optional

    from carconnectivity.carconnectivity import CarConnectivity

    from carconnectivity_services.base.service import ServiceType
    from carconnectivity.location import Location


class LocationService(BaseService):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    def __init__(self, service_id: str, car_connectivity: CarConnectivity, log: logging.Logger) -> None:
        super().__init__(service_id, car_connectivity, log)

    def get_types(self) -> list[ServiceType]:
        """
        Returns the type of the connector.

        Returns:
            str: The type of the connector.
        """
        raise NotImplementedError("Method get_types() must be implemented by plugin")

    def location_from_lat_lon(self, latitude, longitude, location: Optional[Location]) -> Optional[Location]:
        raise NotImplementedError("Method location_from_lat_lon() must be implemented by service")
    
    def gas_station_from_lat_lon(self, latitude: float, longitude: float, radius: int, location: Optional[Location]) -> Optional[Location]:
        raise NotImplementedError("Method gas_station_from_lat_lon() must be implemented by service")

    def charging_station_from_lat_lon(self, latitude: float, longitude: float, radius: int, location: Optional[Location]) -> Optional[Location]:
        raise NotImplementedError("Method charging_station_from_lat_lon() must be implemented by service")
