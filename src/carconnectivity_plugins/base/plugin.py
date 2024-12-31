"""Module containing the BasePlugin class that needs to be extended to implement a new plugin."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict

    from carconnectivity.carconnectivity import CarConnectivity


class BasePlugin:  # pylint: disable=too-few-public-methods
    """BaseConnector is a base class for plugins in the CarConnectivity system.

    Attributes:

    Methods:
        __init__(car_connectivity: CarConnectivity, config: Dict) -> None:
        shutdown() -> None:
            Placeholder method for shutting down the plugin.
    """
    def __init__(self, car_connectivity: CarConnectivity, config: Dict) -> None:
        """
        Initializes the connector with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the plugin is running.
            config (Dict): A dictionary containing the configuration parameters for this plugin only.
        """
        self.car_connectivity: CarConnectivity = car_connectivity
        self.config: Dict = config

    def startup(self) -> None:
        """
        Starts up the plugin.

        This method should be overridden by subclasses to implement any necessary
        startup procedures for the plugin. If threads are needed they should be started here.
        """

    def shutdown(self) -> None:
        """
        Shuts down the plugin.

        This method should be overridden by subclasses to implement any necessary
        cleanup or shutdown procedures for the plugin. If threads were started in startup() they should be stopped here.
        If data needs to be persisted, it should be done here.
        """

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            str: The version of the plugin.
        """
        raise NotImplementedError("Method get_version() must be implemented by plugin")
