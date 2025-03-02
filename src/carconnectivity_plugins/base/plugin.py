"""Module containing the BasePlugin class that needs to be extended to implement a new plugin."""
# pylint: disable=duplicate-code
from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, BooleanAttribute
from carconnectivity.errors import ConfigurationError
from carconnectivity.util import LogMemoryHandler

if TYPE_CHECKING:
    from typing import Dict, Any

    from carconnectivity.carconnectivity import CarConnectivity


class BasePlugin(GenericObject):  # pylint: disable=too-few-public-methods
    """BaseConnector is a base class for plugins in the CarConnectivity system.

    Attributes:

    Methods:
        __init__(car_connectivity: CarConnectivity, config: Dict) -> None:
        shutdown() -> None:
            Placeholder method for shutting down the plugin.
    """
    def __init__(self, plugin_id: str, car_connectivity: CarConnectivity, config: Dict, log: logging.Logger) -> None:
        """
        Initializes the connector with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the plugin is running.
            config (Dict): A dictionary containing the configuration parameters for this plugin only.
        """
        super().__init__(object_id=plugin_id, parent=car_connectivity.plugins)
        self.car_connectivity: CarConnectivity = car_connectivity
        self.active_config: Dict[str, Any] = {}
        self.log_storage: LogMemoryHandler = LogMemoryHandler()
        self.log_level = StringAttribute(name="log_level", parent=self, tags={'carconnectivity'})
        self.version = StringAttribute(name="version", parent=self, value=self.get_version(), tags={'carconnectivity'})
        self.healthy: BooleanAttribute = BooleanAttribute(name="healthy", parent=self, tags={'carconnectivity'})

        # Configure logging
        if 'log_level' in config and config['log_level'] is not None:
            self.active_config['log_level'] = config['log_level'].upper()
            if self.active_config['log_level'] in logging._nameToLevel:
                log.setLevel(self.active_config['log_level'])
                self.log_level._set_value(self.active_config['log_level'])  # pylint: disable=protected-access
            else:
                raise ConfigurationError(f'Invalid log level: "{self.active_config["log_level"]}" not in {list(logging._nameToLevel.keys())}')
        log.addHandler(self.log_storage)

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

    def get_type(self) -> str:
        """
        Returns the type of the plugin.

        Returns:
            str: The type of the plugin.
        """
        raise NotImplementedError("Method get_type() must be implemented by plugin")

    def is_healthy(self) -> bool:
        """
        Returns whether the plugin is healthy.

        Returns:
            bool: True if the plugin is healthy, False otherwise.
        """
        if self.healthy.enabled and self.healthy.value is not None:
            return self.healthy.value
        return False

    def get_name(self) -> str:
        """
        Returns the user readable name of the plugin.
        If not implemented by the plugin, fallback is the ID of the plugin.

        Returns:
            str: The name of the plugin.
        """
        return self.id
