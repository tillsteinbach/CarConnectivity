"""Module containing the BaseConnector class that needs to be extended to implement a new connector."""
# pylint: disable=duplicate-code
from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, DateAttribute, BooleanAttribute
from carconnectivity.errors import ConfigurationError
from carconnectivity.util import LogMemoryHandler

if TYPE_CHECKING:
    from typing import Dict, Any, Optional

    from carconnectivity.carconnectivity import CarConnectivity


class BaseConnector(GenericObject):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """BaseConnector is a base class for connectors in the CarConnectivity system.

    Attributes:

    Methods:
        __init__(car_connectivity: CarConnectivity, config: Dict) -> None:
        shutdown() -> None:
            Placeholder method for shutting down the connector.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, connector_id: str, car_connectivity: CarConnectivity, config: Dict, log: logging.Logger, api_log: Optional[logging.Logger]) -> None:
        """
        Initializes the connector with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the connector is running.
            config (Dict): A dictionary containing the configuration parameters for this connector only.
        """
        super().__init__(object_id=connector_id, parent=car_connectivity.connectors)
        self.car_connectivity: CarConnectivity = car_connectivity
        self.active_config: Dict[str, Any] = {}
        self.log_storage: LogMemoryHandler = LogMemoryHandler()
        self.api_log_storage: LogMemoryHandler = LogMemoryHandler()
        self.log_level = StringAttribute(name="log_level", parent=self, tags={'carconnectivity'})
        self.version = StringAttribute(name="version", parent=self, value=self.get_version(), tags={'carconnectivity'})
        self.last_update: DateAttribute = DateAttribute(name="last_update", parent=self, tags={'carconnectivity'})
        self.healthy: BooleanAttribute = BooleanAttribute(name="healthy", parent=self, tags={'carconnectivity'})

        # Configure logging
        if 'log_level' in config and config['log_level'] is not None:
            self.active_config['log_level'] = config['log_level'].upper()
            if self.active_config['log_level'] in logging._nameToLevel:
                log.setLevel(self.active_config['log_level'])
                self.log_level._set_value(self.active_config['log_level'])  # pylint: disable=protected-access
                logging.getLogger('requests').setLevel(self.active_config['log_level'])
                logging.getLogger('urllib3').setLevel(self.active_config['log_level'])
                logging.getLogger('oauthlib').setLevel(self.active_config['log_level'])
            else:
                raise ConfigurationError(f'Invalid log level: "{self.active_config["log_level"]}" not in {list(logging._nameToLevel.keys())}')
        if api_log is not None and 'api_log_level' in config and config['api_log_level'] is not None:
            self.active_config['api_log_level'] = config['api_log_level'].upper()
            if self.active_config['api_log_level'] in logging._nameToLevel:
                api_log.setLevel(self.active_config['api_log_level'])
            else:
                raise ConfigurationError(f'Invalid log level: "{self.active_config["api_log_level"]}" not in {list(logging._nameToLevel.keys())}')
        log.addHandler(self.log_storage)
        api_log.addHandler(self.api_log_storage)

        if 'hide_vins' in config and config['hide_vins'] is not None:
            self.active_config['hide_vins'] = config['hide_vins']
        else:
            self.active_config['hide_vins'] = []

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

    def get_type(self) -> str:
        """
        Returns the type of the connector.

        Returns:
            str: The type of the connector.
        """
        raise NotImplementedError("Method get_type() must be implemented by plugin")

    def is_healthy(self) -> bool:
        """
        Returns whether the connector is healthy.

        Returns:
            bool: True if the connector is healthy, False otherwise.
        """
        if self.healthy.enabled and self.healthy.value is not None:
            return self.healthy.value
        return False

    def get_name(self) -> str:
        """
        Returns the user readable name of the connector.
        If not implemented by the connector, fallback is the ID of the connector.

        Returns:
            str: The name of the connector.
        """
        return self.id
