"""Contains the main class to interact with the carconnectivity library."""
from __future__ import annotations
from typing import TYPE_CHECKING

import importlib
import pkgutil

import json
import logging
import os

import carconnectivity_connectors
import carconnectivity_plugins

from carconnectivity.objects import GenericObject
from carconnectivity.garage import Garage
from carconnectivity.util import ExtendedEncoder

if TYPE_CHECKING:
    from typing import Dict, List, Any, Optional, Iterator

    from types import ModuleType

    from carconnectivity_connectors.base.connector import BaseConnector
    from carconnectivity_plugins.base.plugin import BasePlugin

LOG: logging.Logger = logging.getLogger("carconnectivity")


def __iter_namespace(ns_pkg) -> Iterator[pkgutil.ModuleInfo]:
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


discovered_connectors: Dict[str, ModuleType] = {
    name: importlib.import_module('.connector', name)
    for finder, name, ispkg
    in __iter_namespace(carconnectivity_connectors)
}

discovered_plugins: Dict[str, ModuleType] = {
    name: importlib.import_module('.plugin', name)
    for finder, name, ispkg
    in __iter_namespace(carconnectivity_plugins)
}


class CarConnectivity(GenericObject):
    """
    CarConnectivity class is the main class to interact with the carconnectivity library.

    Attributes:
        config (Dict): Configuration dictionary for car connectivity.
        connectors (List[BaseConnector]): List of connector instances.
        garage (Garage): Instance of the Garage class.
    """
    def __init__(self, config: Dict, tokenstore_file: Optional[str] = None, cache_file: Optional[str] = None) -> None:
        """
        Initialize the CarConnectivity object.

        Args:
            config (Dict): Configuration dictionary for car connectivity.
            tokenstore_file (Optional[str]): Path to the token store file. Defaults to None.

        Raises:
            ValueError: If the configuration is invalid.
        """
        super().__init__('')
        self.delay_notifications = True
        self.__cache: Dict[str, Any] = {}
        self.__tokenstore: Dict[str, Any] = {}
        self.__tokenstore_file: Optional[str] = tokenstore_file
        self.__cache_file: Optional[str] = cache_file

        self.config: Dict[Any, Any] = config
        self.connectors: List[BaseConnector] = []
        self.plugins: List[BasePlugin] = []
        self.garage: Garage = Garage(self)

        if self.__tokenstore_file is not None:
            try:
                with open(file=self.__tokenstore_file, mode='r', encoding='utf8') as file:
                    self.__tokenstore = json.load(file)
            except json.JSONDecodeError as err:
                LOG.info('Could not use tokenstore from file %s (%s)', tokenstore_file, err.msg)
                self.__tokenstore = {}
            except FileNotFoundError as err:
                LOG.info('Could not use tokenstore from file %s (%s)', tokenstore_file, err)
                self.__tokenstore = {}
        else:
            self.__tokenstore = {}

        # Fill Cache
        if self.__cache_file is not None:
            LOG.info('Reading cachefile %s', cache_file)
            try:
                with open(self.__cache_file, 'r', encoding='utf8') as file:
                    self.__cache = json.load(file)
            except json.decoder.JSONDecodeError:
                LOG.error('Cachefile %s seems corrupted will delete it and try to create a new one. '
                          'If this problem persists please check if a problem with your disk exists.', self.__cache_file)
                os.remove(self.__cache_file)
                self.__cache = {}
            except FileNotFoundError:
                self.__cache = {}

        if 'carConnectivity' not in config:
            raise ValueError("Invalid configuration: 'carConnectivity' is missing")
        if 'connectors' in config['carConnectivity']:
            for connector_config in config['carConnectivity']['connectors']:
                if 'type' not in connector_config:
                    raise ValueError("Invalid configuration: 'type' is missing in connector")
                if f"carconnectivity_connectors.{connector_config['type']}" not in discovered_connectors:
                    raise ValueError(f"Invalid configuration: connector type '{connector_config['type']}' is not known")
                connector_class = getattr(discovered_connectors['carconnectivity_connectors.' + connector_config['type']], 'Connector')
                connector: BaseConnector = connector_class(car_connectivity=self, config=connector_config['config'])
                self.connectors.append(connector)
                connector.startup()
        if 'plugins' in config['carConnectivity']:
            for plugin_config in config['carConnectivity']['plugins']:
                if 'type' not in plugin_config:
                    raise ValueError("Invalid configuration: 'type' is missing in plugin")
                if f"carconnectivity_plugins.{plugin_config['type']}" not in discovered_plugins:
                    raise ValueError(f"Invalid configuration: plugin type '{plugin_config['type']}' is not known")
                plugin_class = getattr(discovered_plugins['carconnectivity_plugins.' + plugin_config['type']], 'Plugin')
                plugin: BasePlugin = plugin_class(car_connectivity=self, config=plugin_config['config'])
                self.plugins.append(plugin)
                plugin.startup()
        self.delay_notifications = False

    def fetch_all(self) -> None:
        """
        Fetch data from all connectors.

        This method iterates over all connectors in the `self.connectors` list
        and calls their `fetch_all` method to retrieve data.
        """
        for connector in self.connectors:
            connector.fetch_all()

    def persist(self) -> None:
        """
        Persist the token store to a file.

        This method writes the token store to a specified file in JSON format.
        If the token store or the file path is not set, the method does nothing.
        If an error occurs during writing, it logs an error message.
        """
        if self.__tokenstore and self.__tokenstore_file:
            try:
                with open(self.__tokenstore_file, 'w', encoding='utf8') as file:
                    json.dump(self.__tokenstore, file)
                LOG.info('Writing tokenstore to file %s', self.__tokenstore_file)
            except ValueError as err:  # pragma: no cover
                LOG.info('Could not write tokenstore to file %s (%s)', self.__tokenstore_file, err)

        # Persist cache
        if self.__cache and self.__cache_file:
            LOG.info('Writing cachefile %s', self.__cache_file)
            with open(self.__cache_file, 'w', encoding='utf8') as file:
                json.dump(self.__cache, file, cls=ExtendedEncoder)

    def shutdown(self) -> None:
        """
        Shuts down all connectors and persists the current state.

        This method iterates over all connectors in the `self.connectors` list and
        calls their `shutdown` method. After all connectors have been shut down,
        it calls the `persist` method to save the current state.
        """
        for connector in self.connectors:
            connector.shutdown()
        for plugin in self.plugins:
            plugin.shutdown()
        self.persist()

    def get_tokenstore(self) -> Dict[str, Any]:
        """
        Retrieve the token store.

        Returns:
            Dict[str, Any]: A dictionary containing the token store.
        """
        return self.__tokenstore

    def get_cache(self) -> Dict[str, Any]:
        """
        Retrieve the cache.

        Returns:
            Dict[str, Any]: The current cache stored in the object.
        """
        return self.__cache

    def get_garage(self) -> Garage | None:
        """
        Retrieve the garage associated with the car connectivity.

        Returns:
            Garage | None: The garage object if available, otherwise None.
        """
        return self.garage

    def __str__(self) -> str:
        return_string: str = ''
        return_string += str(self.get_garage())
        return return_string
