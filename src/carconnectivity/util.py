"""
Module containing generic utility functions and classes.

This module provides utility functions and classes for logging and other purposes.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, NoReturn

import argparse
import logging
import re
from datetime import datetime, timezone

if TYPE_CHECKING:
    from typing import Dict, Tuple, Any
    from logging import LogRecord


def robust_time_parse(time_string: str) -> datetime:
    """
    This function replaces the 'Z' character with '+00:00' to handle UTC time and ensures that fractional
    seconds are padded to six digits if necessary.

    Args:
        time_string (str): The time string to be parsed. Expected format is 'YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM'
                          or 'YYYY-MM-DDTHH:MM:SS.ssssssZ'.

    Returns:
        datetime: A datetime object representing the parsed time string.

    Raises:
        ValueError: If the time string is not in a valid ISO 8601 format.
    """
    time_string = time_string.replace('Z', '+00:00')
    match: re.Match[str] | None = re.search(
        r'^(?P<start>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.)(?P<fractions>\d+)(?P<end>\+\d{2}:\d{2})$', time_string)
    if match:
        time_string = match.group('start') + match.group('fractions').ljust(6, "0") + match.group('end')
    return datetime.fromisoformat(time_string)


def log_extra_keys(log: logging.Logger, where: str, dictionary: Dict[str, Any], allowed_keys: set[str] = None) -> None:
    """
    Logs a warning if there are any keys in the dictionary that are not in the allowed_keys set.

    Args:
        log (logging.log): The logger instance to use for logging warnings.
        log (logging.Logger): The logger instance to use for logging warnings.
        dictionary (Dict[str, Any]): The dictionary to check for extra keys.
        allowed_keys (set[str]): The set of keys that are allowed in the dictionary.

    Returns:
        None
    """
    if allowed_keys is None:
        allowed_keys = set()
    extra_keys = set(dictionary.keys()) - allowed_keys
    if extra_keys:
        log.info(f"Unexpected keys found in {where}: {extra_keys} Dictionary is {dictionary}")


def config_remove_credentials(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Removes any credentials from the configuration dictionary.

    Args:
        config (Dict[str, Any]): The configuration dictionary to remove credentials from.

    Returns:
        Dict[str, Any]: The configuration dictionary with credentials removed.
    """
    def __recursive_remove_credentials(config: Dict[str, Any]) -> Dict[str, Any]:
        for key in config:
            if isinstance(config[key], dict):
                config[key] = __recursive_remove_credentials(config[key])
            if 'password' in key.lower() or 'token' in key.lower():
                config[key] = '***'
        return config
    config_copy: dict[str, Any] = config.copy()
    __recursive_remove_credentials(config_copy)
    return config_copy


# pylint: disable=too-few-public-methods
class DuplicateFilter(logging.Filter):
    """
    A logging filter that suppresses duplicate log messages from the same module within a specified time frame.
    """

    def __init__(self, do_not_filter_above=logging.ERROR, filter_reset_seconds: int = 0, name: str = '') -> None:
        super().__init__(name=name)
        self._last_log: Dict[str, Dict[int, Tuple[Tuple[str, Any], datetime]]] = {}
        self._first_time: bool = True
        self.do_not_filter_above: int = do_not_filter_above
        self.filter_reset_seconds: int = filter_reset_seconds

    def filter(self, record: LogRecord) -> bool:
        # don't filter messages above the specified level
        if record.levelno >= self.do_not_filter_above:
            return True

        now: datetime = datetime.now(tz=timezone.utc)

        # were messages from this module already logged?
        if record.module in self._last_log:
            time_since_last_log = (now - self._last_log[record.module][record.levelno][1]).total_seconds()
            if record.levelno in self._last_log[record.module]:
                # were the same message and arguments logged?
                if self._last_log[record.module][record.levelno][0] == (record.msg, record.args):
                    # was the message logged within the specified time frame?
                    if time_since_last_log < self.filter_reset_seconds:
                        # inform user about repeated messages being suppressed only the first time
                        if self._first_time:
                            self._first_time = False
                            logging.info('Repeated log messages from the same module are hidden (does not apply to errors or critical problems)')
                        # indicate that the message should be suppressed
                        return False
            # store the message and the time it was logged
            self._last_log[record.module][record.levelno] = ((record.msg, record.args), now)
        else:
            # store the message and the time it was logged
            self._last_log[record.module] = {record.levelno: ((record.msg, record.args), now)}
        return True


class ThrowingArgumentParser(argparse.ArgumentParser):
    """
    A custom argument parser that raises an exception instead of exiting on error.

    This class extends `argparse.ArgumentParser` and overrides the `error` method
    to raise an `argparse.ArgumentError` instead of printing an error message and
    exiting the program.

    Methods:
        error(message: str) -> NoReturn:
            Raises an `argparse.ArgumentError` with the provided error message.

    Args:
        message (str): The error message to be included in the raised exception.
    """
    def error(self, message) -> NoReturn:
        raise argparse.ArgumentError(argument=None, message=message)
