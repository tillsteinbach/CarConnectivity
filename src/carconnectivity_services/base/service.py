"""Module containing the BaseService class that needs to be extended to implement a new service."""
# pylint: disable=duplicate-code
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

import logging

if TYPE_CHECKING:
    from carconnectivity.carconnectivity import CarConnectivity


class BaseService():  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Base class for all CarConnectivity services.
    This class provides the foundation for implementing services that interact with
    the CarConnectivity system. Services are components that provide specific
    functionality such as location or amenity lookup for data processing.
    Attributes:
        service_id (str): Unique identifier for the service instance.
        car_connectivity (CarConnectivity): Reference to the main CarConnectivity instance.
        log (logging.Logger): Logger instance for service-specific logging.
    Note:
        This is an abstract base class. Subclasses must implement the get_types() method
        to define the specific service types they provide.
    """
    def __init__(self, service_id: str, car_connectivity: CarConnectivity, log: logging.Logger) -> None:
        self.service_id: str = service_id
        self.car_connectivity: CarConnectivity = car_connectivity
        self.log: logging.Logger = log

    def get_types(self) -> list[ServiceType]:
        """
        Returns the type of the connector.

        Returns:
            list[ServiceTypes]: The types of the connector.
        """
        raise NotImplementedError("Method get_types() must be implemented by plugin")


class ServiceType(Enum):
    """
    Enumeration of available service types in CarConnectivity.
    This enum defines the different types of services that can be provided by the CarConnectivity system,
    primarily related to location-based services.
    Attributes:
        LOCATION_REVERSE: Service for reverse geocoding (converting coordinates to addresses).
        LOCATION_GAS_STATION: Service for locating nearby gas/fuel stations.
        LOCATION_CHARGING_STATION: Service for locating nearby electric vehicle charging stations.
    """
    LOCATION_REVERSE = "reverse_location"
    LOCATION_GAS_STATION = "gas_station"
    LOCATION_CHARGING_STATION = "charging_station"
