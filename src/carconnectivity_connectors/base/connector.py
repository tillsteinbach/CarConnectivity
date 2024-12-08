"""Module containing the BaseConnector class that needs to be extended to implement a new connector."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict

    from carconnectivity.carconnectivity import CarConnectivity


class BaseConnector:  # pylint: disable=too-few-public-methods
    """BaseConnector is a base class for connectors in the CarConnectivity system.

    Attributes:

    Methods:
        __init__(car_connectivity: CarConnectivity, config: Dict) -> None:
        shutdown() -> None:
            Placeholder method for shutting down the connector.
    """
    def __init__(self, car_connectivity: CarConnectivity, config: Dict) -> None:
        """
        Initializes the connector with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the connector is running.
            config (Dict): A dictionary containing the configuration parameters for this connector only.
        """
        self.car_connectivity: CarConnectivity = car_connectivity
        self.config: Dict = config

    def fetch_all(self) -> None:
        """
        Fetches all data from the connector and updates the CarConnectivity system.

        This method should be overridden by subclasses to implement the specific
        data fetching logic for the connector.
        """

    def shutdown(self) -> None:
        """
        Shuts down the connector.

        This method should be overridden by subclasses to implement any necessary
        cleanup or shutdown procedures for the connector.
        """
