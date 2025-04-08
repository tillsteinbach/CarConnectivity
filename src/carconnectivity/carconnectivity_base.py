"""Module containing the commandline interface for the carconnectivity package."""
from __future__ import annotations
from typing import TYPE_CHECKING

import sys
import os
import signal
import argparse
import logging
import tempfile
import json
import threading

from json_minify import json_minify

from carconnectivity import carconnectivity, errors, util
from carconnectivity._version import __version__ as __carconnectivity_version__

if TYPE_CHECKING:
    from typing import Optional

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "ERROR"

LOG: logging.Logger = logging.getLogger("carconnectivity")


class CLI():  # pylint: disable=too-few-public-methods
    """
    Class containing the commandline interface for the carconnectivity package.
    """

    def __init__(self, logger: logging.Logger, name: str, description: str, subversion: Optional[str] = None) -> None:
        self._stop_event = threading.Event()
        self.logger = logger

        self.parser = argparse.ArgumentParser(
            prog=name,
            description=description)
        if subversion is not None:
            version = f'%(prog)s {subversion} (using CarConnectivity {__carconnectivity_version__})'
        else:
            version = f'%(prog)s {__carconnectivity_version__}'
        self.parser.add_argument('--version', action='version', version=version)
        self.parser.add_argument('config', help='Path to the configuration file')

        default_temp = os.path.join(tempfile.gettempdir(), 'carconnectivity.token')
        self.parser.add_argument('--tokenfile', help=f'file to store token (default: {default_temp})', default=default_temp)
        default_cache_temp = os.path.join(tempfile.gettempdir(), 'carconnectivity.cache')
        self.parser.add_argument('--cachefile', help=f'file to store cache (default: {default_cache_temp})', default=default_cache_temp)
        self.parser.add_argument('--healthcheckfile', help='file to store healthcheck data', default=None)

        logging_group = self.parser.add_argument_group('Logging')
        logging_group.add_argument('-v', '--verbose', action="append_const", help='Logging level (verbosity)', const=-1,)
        logging_group.add_argument('--logging-format', dest='logging_format', help='Logging format configured for python logging '
                                   '(default: %%(asctime)s:%%(module)s:%%(message)s)', default='%(asctime)s:%(levelname)s:%(message)s')
        logging_group.add_argument('--logging-date-format', dest='logging_date_format', help='Logging format configured for python logging '
                                   '(default: %%Y-%%m-%%dT%%H:%%M:%%S%%z)', default='%Y-%m-%dT%H:%M:%S%z')
        logging_group.add_argument('--hide-repeated-log', dest='hide_repeated_log', help='Hide repeated log messages from the same module', action='store_true')

    def handler(self, signum, frame):
        """
        Signal handler for interrupt signals.

        This method is triggered when an interrupt signal (e.g., SIGINT) is received.
        It logs the interrupt event and sets the internal stop event to initiate a shutdown process.

        Args:
            signum (int): The signal number received.
            frame (FrameType): The current stack frame (unused).
        """
        del signum, frame  # unused
        self.logger.info('Interrupt received, shutting down...')
        self._stop_event.set()

    # pylint: disable-next=too-many-statements,too-many-branches,too-many-locals
    def main(self) -> None:  # noqa: C901
        """
        Entry point for the command-line interface.
        """
        args = self.parser.parse_args()
        log_level = LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
        for adjustment in args.verbose or ():
            log_level = min(len(LOG_LEVELS) - 1, max(log_level + adjustment, 0))

        logging.basicConfig(level=LOG_LEVELS[log_level], format=args.logging_format, datefmt=args.logging_date_format)
        if args.hide_repeated_log:
            for handler in logging.root.handlers:
                handler.addFilter(util.DuplicateFilter())

        try:  # pylint: disable=too-many-nested-blocks
            try:
                with open(file=args.config, mode='r', encoding='utf-8') as config_file:
                    try:
                        config_dict = json.loads(json_minify(config_file.read(), strip_space=False))
                        car_connectivity = carconnectivity.CarConnectivity(config=config_dict, tokenstore_file=args.tokenfile, cache_file=args.cachefile)
                        car_connectivity.startup()

                        signal.signal(signal.SIGINT, self.handler)
                        signal.signal(signal.SIGTERM, self.handler)
                        while not self._stop_event.is_set():
                            if args.healthcheckfile is not None:
                                with open(file=args.healthcheckfile, mode='w', encoding='utf-8') as healthcheck_file:
                                    if car_connectivity.is_healthy():
                                        healthcheck_file.write('healthy')
                                    else:
                                        healthcheck_file.write('unhealthy')
                            self._stop_event.wait(60)

                            car_connectivity.shutdown()
                    except json.JSONDecodeError as e:
                        self.logger.critical('Could not load configuration file %s (%s)', args.config, e)
                        sys.exit('Could not load configuration file')
            except FileNotFoundError as e:
                self.logger.critical('Could not find configuration file %s (%s)', args.config, e)
                sys.exit('Could not find configuration file')
        except errors.AuthenticationError as e:
            self.logger.critical('There was a problem when authenticating with one or multiple services: %s', e)
            sys.exit('There was a problem when authenticating with one or multiple services')
        except errors.APICompatibilityError as e:
            self.logger.critical('There was a problem when communicating with one or multiple services.'
                                 ' If this problem persists please open a bug report: %s', e)
            sys.exit('There was a problem when communicating with one or multiple services.')
        except errors.RetrievalError as e:
            self.logger.critical('There was a problem when communicating with one or multiple services: %s', e)
            sys.exit('There was a problem when communicating with one or multiple services.')
        except errors.ConfigurationError as e:
            self.logger.critical('There was a problem with the configuration: %s', e)
            sys.exit('There was a problem with the configuration')


def main() -> None:
    """
    Entry point for the car connectivity application.

    This function initializes and starts the command-line interface (CLI) for the
    car connectivity application using the specified logger and application name.
    """
    cli: CLI = CLI(logger=LOG, name='carconnectivity', description='Commandline Interface to interact with Car Services of various brands')
    cli.main()
