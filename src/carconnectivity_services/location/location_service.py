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
    from carconnectivity.charging_station import ChargingStation


class LocationService(BaseService):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    LocationService provides location-based services for car connectivity.
    This abstract base class defines the interface for location services that can:
    - Retrieve location information from coordinates
    - Find nearby gas stations
    - Find nearby charging stations
    Args:
        service_id (str): Unique identifier for the service instance.
        car_connectivity (CarConnectivity): The car connectivity instance.
        log (logging.Logger): Logger instance for this service.
    Raises:
        NotImplementedError: If any of the abstract methods are not implemented by subclass.
    """
    def __init__(self, service_id: str, car_connectivity: CarConnectivity, log: logging.Logger) -> None:  # pylint: disable=useless-parent-delegation
        super().__init__(service_id, car_connectivity, log)

    def get_types(self) -> list[ServiceType]:
        """
        Returns the type of the connector.

        Returns:
            str: The type of the connector.
        """
        raise NotImplementedError("Method get_types() must be implemented by plugin")

    def location_from_lat_lon(self, latitude, longitude, location: Optional[Location]) -> Optional[Location]:
        """
        Convert latitude and longitude coordinates to a Location object.
        Args:
            latitude: The latitude coordinate as a float
            longitude: The longitude coordinate as a float
            location: Optional existing Location object to update with the resolved location data
        Returns:
            Optional[Location]: A Location object containing the resolved location information,
                               or None if the location could not be determined
        Raises:
            NotImplementedError: This method must be implemented by the service subclass
        """

        raise NotImplementedError("Method location_from_lat_lon() must be implemented by service")

    def gas_station_from_lat_lon(self, latitude: float, longitude: float, radius: int, location: Optional[Location]) -> Optional[Location]:
        """
        Find the nearest gas station from given latitude and longitude coordinates.
        Args:
            latitude (float): The latitude coordinate to search from.
            longitude (float): The longitude coordinate to search from.
            radius (int): The search radius in meters.
            location (Optional[Location]): Optional location object to use as context or update.
        Returns:
            Optional[Location]: A Location object representing the nearest gas station if found, None otherwise.
        Raises:
            NotImplementedError: This method must be implemented by a concrete service class.
        """

        raise NotImplementedError("Method gas_station_from_lat_lon() must be implemented by service")

    def charging_station_from_lat_lon(self, latitude: float, longitude: float, radius: int,
                                      charging_station: Optional[ChargingStation]) -> Optional[ChargingStation]:
        """
        Find the nearest charging station based on latitude and longitude coordinates.
        Args:
            latitude (float): The latitude coordinate to search from.
            longitude (float): The longitude coordinate to search from.
            radius (int): The search radius in meters within which to find charging stations.
            charging_station (Optional[ChargingStation]): An optional ChargingStation object that may contain additional
                                                          context or be updated with the found charging station information.
        Returns:
            Optional[ChargingStation]: A ChargingStation object representing the found charging station, or None if no charging
                                       station is found within the specified radius.
        Raises:
            NotImplementedError: This method must be implemented by a subclass providing the actual service implementation.
        """

        raise NotImplementedError("Method charging_station_from_lat_lon() must be implemented by service")
