"""Module containing the BaseService class that needs to be extended to implement a new service."""
# pylint: disable=duplicate-code
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

import logging

if TYPE_CHECKING:
    from carconnectivity.carconnectivity import CarConnectivity


class BaseService():  # pylint: disable=too-few-public-methods, too-many-instance-attributes
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
    LOCATION_REVERSE = "reverse_location",
    LOCATION_GAS_STATION = "gas_station",
    LOCATION_CHARGING_STATION = "charging_station",
