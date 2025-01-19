"""Module containing the BaseConnector class that needs to be extended to implement a new connector."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject

from carconnectivity.attributes import StringAttribute, DateAttribute

if TYPE_CHECKING:
    from typing import Dict

    from carconnectivity.carconnectivity import CarConnectivity


class BaseConnector(GenericObject):  # pylint: disable=too-few-public-methods
    """BaseConnector is a base class for connectors in the CarConnectivity system.

    Attributes:

    Methods:
        __init__(car_connectivity: CarConnectivity, config: Dict) -> None:
        shutdown() -> None:
            Placeholder method for shutting down the connector.
    """
    def __init__(self, connector_id: str, car_connectivity: CarConnectivity, config: Dict) -> None:
        """
        Initializes the connector with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the connector is running.
            config (Dict): A dictionary containing the configuration parameters for this connector only.
        """
        super().__init__(object_id=connector_id, parent=car_connectivity.connectors)
        self.car_connectivity: CarConnectivity = car_connectivity
        self.config: Dict = config
        self.log_level = StringAttribute(name="log_level", parent=self)
        self.version = StringAttribute(name="version", parent=self, value=self.get_version())
        self.last_update: DateAttribute = DateAttribute(name="last_update", parent=self)

    def fetch_all(self) -> None:
        """
        Fetches all data from the connector and updates the CarConnectivity system.

        This method should be overridden by subclasses to implement the specific
        data fetching logic for the connector.
        """

    def startup(self) -> None:
        """
        Starts the connector.

        This method should be overridden by subclasses to implement any necessary
        startup procedures for the connector. If threads are used, they should be started here.
        """

    def shutdown(self) -> None:
        """
        Shuts down the connector.

        This method should be overridden by subclasses to implement any necessary
        cleanup or shutdown procedures for the connector. If threads are used, they should be stopped here.
        """

    def get_version(self) -> str:
        """
        Returns the version of the connector.

        Returns:
            str: The version of the connector.
        """
        raise NotImplementedError("Method get_version() must be implemented by connector")

    def is_healthy(self) -> bool:
        """
        Returns whether the connector is healthy.

        Returns:
            bool: True if the connector is healthy, False otherwise.
        """
        return True
