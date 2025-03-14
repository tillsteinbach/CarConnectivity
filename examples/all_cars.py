"""
This script is an example showing how to retrieve all vehicles from the account using the CarConnectivity library.

Functions:
    main: The main function that sets up argument parsing, logging, and retrieves vehicle data.

Usage:
    python all_cars.py <config> [--tokenstorefile TOKENSTOREFILE] [-v] [--logging-format LOGGING_FORMAT] [--logging-date-format LOGGING_DATE_FORMAT]

Arguments:
    config: Path to the configuration file.
    --tokenstorefile: File to store tokenstore (default: /tmp/tokenstore).
    -v, --verbose: Logging level (verbosity).
    --logging-format: Logging format configured for python logging (default: %(asctime)s:%(levelname)s:%(message)s).
    --logging-date-format: Logging date format configured for python logging (default: %Y-%m-%dT%H:%M:%S%z).

Logging Levels:
    DEBUG, INFO, WARNING, ERROR, CRITICAL

Example:
    python all_cars.py config.json --tokenstorefile /path/to/tokenstore -v
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import argparse
import json
import os
import tempfile
import logging

from carconnectivity import carconnectivity

if TYPE_CHECKING:
    from typing import List, Optional

    from carconnectivity.garage import Garage


LOG_LEVELS: List[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL = "ERROR"
LOG: logging.Logger = logging.getLogger("carconnectivity-example")


#  pylint: disable=duplicate-code
def main() -> None:
    """ Simple example showing how to retrieve all vehicles from the account """
    parser = argparse.ArgumentParser(
        prog='allCars',
        description='Example retrieving all cars in all configured connectors'
    )
    parser.add_argument('config', help='Path to the configuration file')
    default_temp: str = os.path.join(tempfile.gettempdir(), 'tokenstore')
    parser.add_argument('--tokenstorefile', help=f'file to store tokenstore (default: {default_temp})', default=default_temp)

    logging_group = parser.add_argument_group('Logging')
    logging_group.add_argument('-v', '--verbose', action="append_const", help='Logging level (verbosity)', const=-1,)
    logging_group.add_argument('--logging-format', dest='logging_format', help='Logging format configured for python logging '
                               '(default: %%(asctime)s:%%(module)s:%%(message)s)', default='%(asctime)s:%(levelname)s:%(message)s')
    logging_group.add_argument('--logging-date-format', dest='logging_date_format', help='Logging format configured for python logging '
                               '(default: %%Y-%%m-%%dT%%H:%%M:%%S%%z)', default='%Y-%m-%dT%H:%M:%S%z')

    args = parser.parse_args()

    log_level: int = LOG_LEVELS.index(DEFAULT_LOG_LEVEL)
    for adjustment in args.verbose or ():
        log_level = min(len(LOG_LEVELS) - 1, max(log_level + adjustment, 0))

    logging.basicConfig(level=LOG_LEVELS[log_level], format=args.logging_format, datefmt=args.logging_date_format)

    print('#  read CarConnectivity configuration')
    with open(args.config, 'r', encoding='utf-8') as config_file:
        config_dict = json.load(config_file)
        print('#  Login')
        car_connectivity = carconnectivity.CarConnectivity(config=config_dict, tokenstore_file=args.tokenstorefile)
        print('#  fetch data')
        car_connectivity.fetch_all()
        print('#  getData')
        garage: Optional[Garage] = car_connectivity.get_garage()
        if garage is not None:
            print('#  list all vehicles')
            for vehicle in garage.list_vehicles():
                print(f'#  {vehicle}')
        print('#  Shutdown')
        car_connectivity.shutdown()

    print('#  done')


if __name__ == '__main__':
    main()
