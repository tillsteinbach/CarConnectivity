"""Contains the main class to interact with the carconnectivity library."""
from __future__ import annotations
from typing import TYPE_CHECKING

import importlib
import pkgutil

import re
import json
import logging
import os
from datetime import datetime, timezone
from cryptography.fernet import Fernet, InvalidToken

import carconnectivity_connectors
import carconnectivity_plugins

from carconnectivity.objects import GenericObject
from carconnectivity.garage import Garage
from carconnectivity.json_util import ExtendedEncoder
from carconnectivity.errors import ConfigurationError
from carconnectivity.connectors import Connectors
from carconnectivity.plugins import Plugins
from carconnectivity.attributes import StringAttribute
from carconnectivity._version import __version__
from carconnectivity.util import LogMemoryHandler
from carconnectivity.errors import RetrievalError, MultipleRetrievalError

if TYPE_CHECKING:
    from typing import Dict, Any, Optional, Iterator

    from types import ModuleType

    from carconnectivity_connectors.base.connector import BaseConnector
    from carconnectivity_plugins.base.plugin import BasePlugin

LOG: logging.Logger = logging.getLogger("carconnectivity")

TOKENSTORE_FORMAT_VERSION: str = '1.0'
CACHE_FORMAT_VERSION: str = '1.0'
TOKENSTORE_KEY: str = '5weee2AYwL08LfVsDzzzDL82ffN6lWgwjUHYPzdzZBk='
CACHE_KEY: str = '5weee2AYwL08LfVsDzzzDL82ffN6lWgwjUHYPzdzZBk='


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


class CarConnectivity(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    CarConnectivity class is the main class to interact with the carconnectivity library.

    Attributes:
        config (Dict): Configuration dictionary for car connectivity.
        connectors (List[BaseConnector]): List of connector instances.
        plugins (List[BasePlugin]): List of plugin instances.
        garage (Garage): Instance of the Garage class.
    """
    # pylint: disable=too-many-statements, too-many-branches, too-many-locals
    def __init__(self, config: Dict, tokenstore_file: Optional[str] = None, cache_file: Optional[str] = None) -> None:
        """
        Initialize the CarConnectivity object.

        Args:
            config (Dict): Configuration dictionary for car connectivity.
            tokenstore_file (Optional[str]): Path to the token store file. Defaults to None.

        Raises:
            ValueError: If the configuration is invalid.
        """
        super().__init__(object_id='', parent=None)
        self.delay_notifications = True
        self.__cache: Dict[str, Any] = {}
        self.__tokenstore: Dict[str, Any] = {}
        self.__tokenstore_file: Optional[str] = tokenstore_file
        self.__cache_file: Optional[str] = cache_file

        self.config: Dict[Any, Any] = config
        self.connectors: Connectors = Connectors(car_connectivity=self)
        self.plugins: Plugins = Plugins(car_connectivity=self)
        self.garage: Garage = Garage(self)
        self.log_storage: LogMemoryHandler = LogMemoryHandler()

        self.version: StringAttribute = StringAttribute(name="version", parent=self, value=__version__, tags={'carconnectivity'})

        if 'carConnectivity' not in config:
            raise ConfigurationError("Invalid configuration: 'carConnectivity' is missing")
        # Configure logging
        if 'log_level' in config['carConnectivity'] and config['carConnectivity']['log_level'] is not None:
            config['carConnectivity']['log_level'] = config['carConnectivity']['log_level'].upper()
            if config['carConnectivity']['log_level'] in logging._nameToLevel:
                LOG.setLevel(config['carConnectivity']['log_level'])
            else:
                raise ConfigurationError(f'Invalid log level: "{config["carConnectivity"]["log_level"]}" not in {list(logging._nameToLevel.keys())}')
        if 'log_format' in config['carConnectivity'] and config['carConnectivity']['log_format'] is not None:
            log_format: str = config['carConnectivity']['log_format']
        else:
            log_format: str = '%(asctime)s:%(name)s:%(levelname)s:%(module)s:%(message)s'
        formatter = logging.Formatter(log_format)
        if 'log_date_format' in config['carConnectivity'] and config['carConnectivity']['log_date_format'] is not None:
            formatter.datefmt = config['carConnectivity']['log_date_format']
        else:
            formatter.datefmt = '%Y-%m-%dT%H:%M:%S%z'
        for handler in logging.getLogger().handlers:
            handler.setFormatter(formatter)
        LOG.addHandler(self.log_storage)
        self.log_storage.setFormatter(formatter)

        # pylint: disable=too-few-public-methods
        class NoPluginsConnectorsAPIDebug(logging.Filter):
            """
            A logging filter that excludes connector and plugin messages from the logs.

            Methods:
                filter(record): Determines if the log record should be logged.
            """
            def filter(self, record):
                pattern = re.compile(r'carconnectivity\.(connectors|plugins)\..*-api-debug')
                return not pattern.match(record.name)

        #  Disable logging for plugins and connectors
        self.log_storage.addFilter(NoPluginsConnectorsAPIDebug())

        if self.__tokenstore_file is not None:
            try:
                with open(file=self.__tokenstore_file, mode='r', encoding='utf8') as file:
                    tokenstore_file_dict: Dict[str, Any] = json.load(file)
                    if 'format_version' not in tokenstore_file_dict or tokenstore_file_dict['format_version'] != TOKENSTORE_FORMAT_VERSION:
                        LOG.warning('Tokenstore file has wrong format version, ignoring it. Tokenstore will be regenerated when saving')
                        self.__tokenstore = {}
                    else:
                        if 'tokenstore' not in tokenstore_file_dict:
                            LOG.warning('Tokenstore file has no tokenstore content, ignoring it. Tokenstore will be regenerated when saving')
                            self.__tokenstore = {}
                        else:
                            if 'tokenstore_encrypted' in self.config['carConnectivity'] and not self.config['carConnectivity']['tokenstore_encrypted']:
                                self.__tokenstore = tokenstore_file_dict['tokenstore']
                            else:
                                try:
                                    fernet = Fernet(TOKENSTORE_KEY.encode('utf-8'))
                                    self.__tokenstore = json.loads(fernet.decrypt(tokenstore_file_dict['tokenstore'].encode('utf-8')).decode('utf-8'))
                                except InvalidToken:
                                    LOG.warning('Tokenstore file cannot be decrypted, ignoring it. Tokenstore will be regenerated when saving')
                                    self.__tokenstore = {}
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
                    cache_file_dict: Dict[str, Any] = json.load(file)
                    if 'format_version' not in cache_file_dict or cache_file_dict['format_version'] != CACHE_FORMAT_VERSION:
                        LOG.info('Cache file has wrong format version, ignoring it')
                        self.__cache = {}
                    else:
                        if 'cache_encrypted' in self.config['carConnectivity'] and not self.config['carConnectivity']['cache_encrypted']:
                            self.__cache = cache_file_dict['cache']
                        else:
                            fernet = Fernet(CACHE_KEY.encode('utf-8'))
                            self.__cache = json.loads(fernet.decrypt(cache_file_dict['cache'].encode('utf-8')).decode('utf-8'))
            except json.decoder.JSONDecodeError:
                LOG.error('Cachefile %s seems corrupted will delete it and try to create a new one. '
                          'If this problem persists please check if a problem with your disk exists.', self.__cache_file)
                os.remove(self.__cache_file)
                self.__cache = {}
            except FileNotFoundError:
                self.__cache = {}

        if 'connectors' in config['carConnectivity']:
            for connector_config in config['carConnectivity']['connectors']:
                if 'type' not in connector_config:
                    raise ConfigurationError("Invalid configuration: 'type' is missing in connector")
                if f"carconnectivity_connectors.{connector_config['type']}" not in discovered_connectors:
                    raise ConfigurationError(f"Invalid configuration: connector type '{connector_config['type']}' is not known")
                if 'disabled' in connector_config and connector_config['disabled']:
                    LOG.info('Skipping disabled connector %s', connector_config['type'])
                    continue
                connector_class = getattr(discovered_connectors['carconnectivity_connectors.' + connector_config['type']], 'Connector')
                if 'connector_id' in connector_config and connector_config['connector_id'] is not None:
                    connector_id = connector_config['connector_id']
                else:
                    connector_id = connector_config['type']
                if connector_id in self.connectors.connectors:
                    raise ConfigurationError(f"Invalid configuration: connector '{connector_id}' is not unique, set a 'connector_id' in configuration")
                connector: BaseConnector = connector_class(connector_id=connector_id, car_connectivity=self, config=connector_config['config'])
                self.connectors.connectors[connector_id] = connector
        if 'plugins' in config['carConnectivity']:
            for plugin_config in config['carConnectivity']['plugins']:
                if 'type' not in plugin_config:
                    raise ConfigurationError("Invalid configuration: 'type' is missing in plugin")
                if f"carconnectivity_plugins.{plugin_config['type']}" not in discovered_plugins:
                    raise ConfigurationError(f"Invalid configuration: plugin type '{plugin_config['type']}' is not known")
                if 'disabled' in plugin_config and plugin_config['disabled']:
                    LOG.info('Skipping disabled plugin %s', plugin_config['type'])
                    continue
                plugin_class = getattr(discovered_plugins['carconnectivity_plugins.' + plugin_config['type']], 'Plugin')
                if 'plugin_id' in plugin_config and plugin_config['plugin_id'] is not None:
                    plugin_id: str = plugin_config['plugin_id']
                else:
                    plugin_id: str = plugin_config['type']
                if plugin_id in self.plugins.plugins:
                    raise ConfigurationError(f"Invalid configuration: connector '{plugin_id}' is not unique, set a 'connector_id' in configuration")
                plugin: BasePlugin = plugin_class(plugin_id=plugin_id, car_connectivity=self, config=plugin_config['config'])
                self.plugins.plugins[plugin_id] = plugin
        self.delay_notifications = False

    def fetch_all(self) -> None:
        """
        Fetch data from all connectors.

        This method iterates over all connectors in the `self.connectors` list
        and calls their `fetch_all` method to retrieve data.

        Raises:
            RetrievalError: If any connector raises a RetrievalError during data fetching.
        If multiple connectors raise a RetrievalError, only the first one is raised.
        If no connector raises a RetrievalError, the method completes successfully.
        """
        retrieval_error: RetrievalError = None
        for connector in self.connectors.connectors.values():
            # This can be changed to GroupedException in the future when support for python 3.9 and 3.10 is dropped.
            try:
                connector.fetch_all()
            except RetrievalError as err:
                if retrieval_error is None:
                    retrieval_error = err
                elif isinstance(err, MultipleRetrievalError):
                    retrieval_error.errors.add(err.errors)
                else:
                    new_retrieval_error = MultipleRetrievalError(err)
                    new_retrieval_error.errors.add(retrieval_error.errors)
                    retrieval_error = new_retrieval_error
        if retrieval_error is not None:
            raise retrieval_error

    def persist(self) -> None:
        """
        Persist the token store to a file.

        This method writes the token store to a specified file in JSON format.
        If the token store or the file path is not set, the method does nothing.
        If an error occurs during writing, it logs an error message.
        """
        if self.__tokenstore and self.__tokenstore_file:
            try:
                with open(file=self.__tokenstore_file, mode='w', encoding='utf8') as file:
                    tokenstore_file_dict: Dict[str, Any] = {}
                    tokenstore_file_dict['format_version'] = TOKENSTORE_FORMAT_VERSION
                    tokenstore_file_dict['date'] = datetime.now(tz=timezone.utc).isoformat()
                    if 'tokenstore_encrypted' in self.config['carConnectivity'] and not self.config['carConnectivity']['tokenstore_encrypted']:
                        tokenstore_file_dict['tokenstore'] = self.__tokenstore
                    else:
                        fernet = Fernet(TOKENSTORE_KEY.encode('utf-8'))
                        tokenstore_file_dict['tokenstore'] = fernet.encrypt(json.dumps(self.__tokenstore, cls=ExtendedEncoder).encode('utf-8')).decode('utf-8')
                    json.dump(tokenstore_file_dict, file)
                LOG.info('Writing tokenstore to file %s', self.__tokenstore_file)
            except ValueError as err:  # pragma: no cover
                LOG.info('Could not write tokenstore to file %s (%s)', self.__tokenstore_file, err)

        # Persist cache
        if self.__cache and self.__cache_file:
            LOG.info('Writing cachefile %s', self.__cache_file)
            with open(file=self.__cache_file, mode='w', encoding='utf8') as file:
                cache_file_dict: Dict[str, Any] = {}
                cache_file_dict['format_version'] = CACHE_FORMAT_VERSION
                cache_file_dict['date'] = datetime.now(tz=timezone.utc).isoformat()
                if 'cache_encrypted' in self.config['carConnectivity'] and not self.config['carConnectivity']['cache_encrypted']:
                    cache_file_dict['cache'] = self.__cache
                else:
                    fernet = Fernet(CACHE_KEY.encode('utf-8'))
                    cache_file_dict['cache'] = fernet.encrypt(json.dumps(self.__cache).encode('utf-8')).decode('utf-8')
                json.dump(cache_file_dict, file, cls=ExtendedEncoder)

    def startup(self) -> None:
        """
        Start all connectors and plugins.

        This method iterates over all connectors in the `self.connectors` list and
        calls their `startup` method.
        """
        for connector in self.connectors.connectors.values():
            connector.startup()
        for plugin in self.plugins.plugins.values():
            plugin.startup()

    def shutdown(self) -> None:
        """
        Shuts down all connectors and persists the current state.

        This method iterates over all connectors in the `self.connectors` list and
        calls their `shutdown` method. After all connectors have been shut down,
        it calls the `persist` method to save the current state.
        """
        for connector in self.connectors.connectors.values():
            connector.shutdown()
        for plugin in self.plugins.plugins.values():
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

    def get_garage(self) -> Optional[Garage]:
        """
        Retrieve the garage associated with the car connectivity.

        Returns:
            Garage | None: The garage object if available, otherwise None.
        """
        return self.garage

    def is_healthy(self) -> bool:
        """
        Returns whether the carconnectivity instance and its connectors and plugins is healthy.

        Returns:
            bool: True if carconnectivity is healthy, False otherwise.
        """
        for connector in self.connectors.connectors.values():
            if not connector.is_healthy():
                return False
        for plugin in self.plugins.plugins.values():
            if not plugin.is_healthy():
                return False
        return True
