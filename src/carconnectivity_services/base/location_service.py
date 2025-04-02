"""Module containing the BaseService class that needs to be extended to implement a new service."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity_services.base.service import BaseService

if TYPE_CHECKING:
    from typing import Dict
    from logging import Logger
    from carconnectivity.carconnectivity import CarConnectivity


#  pylint: disable-next=abstract-method
class BaseLocationService(BaseService):
    """BaseLocationService is a base class for service in the CarConnectivity system that provides locations.
    """
    def __init__(self, service_id: str, car_connectivity: CarConnectivity, config: Dict, log: Logger) -> None:
        """
        Initializes the service with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the service is running.
            config (Dict): A dictionary containing the configuration parameters for this service only.
        """
        super().__init__(service_id=service_id, car_connectivity=car_connectivity, config=config, log=log)

    def get_location_at(self, latitude: float, longitude: float) -> str:
        raise NotImplementedError("Method get_type() must be implemented by service")
