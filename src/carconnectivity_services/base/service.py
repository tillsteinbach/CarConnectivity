"""Module containing the BaseService class that needs to be extended to implement a new service."""
from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute
from carconnectivity.errors import ConfigurationError
from carconnectivity.util import LogMemoryHandler

if TYPE_CHECKING:
    from typing import Dict, Any

    from carconnectivity.carconnectivity import CarConnectivity


class BaseService(GenericObject):  # pylint: disable=too-few-public-methods
    """BaseService is a base class for service in the CarConnectivity system.
    """
    def __init__(self, service_id: str, car_connectivity: CarConnectivity, config: Dict, log: logging.Logger) -> None:
        """
        Initializes the connector with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the service is running.
            config (Dict): A dictionary containing the configuration parameters for this service only.
        """
        super().__init__(object_id=service_id, parent=car_connectivity)
        self.car_connectivity: CarConnectivity = car_connectivity
        self.active_config: Dict[str, Any] = {}
        self.log_storage: LogMemoryHandler = LogMemoryHandler()
        self.log_level = StringAttribute(name="log_level", parent=self, tags={'carconnectivity'})
        self.version = StringAttribute(name="version", parent=self, value=self.get_version(), tags={'carconnectivity'})

        # pylint: disable=duplicate-code
        # Configure logging
        if 'log_level' in config and config['log_level'] is not None:
            self.active_config['log_level'] = config['log_level'].upper()
            if self.active_config['log_level'] in logging._nameToLevel:
                log.setLevel(self.active_config['log_level'])
                self.log_level._set_value(self.active_config['log_level'])  # pylint: disable=protected-access
            else:
                raise ConfigurationError(f'Invalid log level: "{self.active_config["log_level"]}" not in {list(logging._nameToLevel.keys())}')
        log.addHandler(self.log_storage)
        # pylint: enable=duplicate-code

    def startup(self) -> None:
        """
        Starts up the service.

        This method should be overridden by subclasses to implement any necessary
        startup procedures for the service. If threads are needed they should be started here.
        """

    def shutdown(self) -> None:
        """
        Shuts down the service.

        This method should be overridden by subclasses to implement any necessary
        cleanup or shutdown procedures for the service. If threads were started in startup() they should be stopped here.
        If data needs to be persisted, it should be done here.
        """

    def get_version(self) -> str:
        """
        Returns the version of the service.

        Returns:
            str: The version of the service.
        """
        raise NotImplementedError("Method get_version() must be implemented by service")

    def get_type(self) -> str:
        """
        Returns the type of the service.

        Returns:
            str: The type of the service.
        """
        raise NotImplementedError("Method get_type() must be implemented by service")

    def is_healthy(self) -> bool:
        """
        Returns whether the service is healthy.

        Returns:
            bool: True if the service is healthy, False otherwise.
        """
        return True
