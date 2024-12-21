"""
Module containing generic utility functions and classes.

This module provides utility functions and classes for logging and other purposes.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import re
from datetime import datetime

if TYPE_CHECKING:
    from typing import Dict, Tuple, Any
    from logging import LogRecord


def robust_time_parse(time_string: str) -> datetime:
    """
    This function replaces the 'Z' character with '+00:00' to handle UTC time and ensures that fractional
    seconds are padded to six digits if necessary.

    Args:
        def robust_time_parse(time_string: str) -> datetime:
 (str): The time string to be parsed. Expected format is 'YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM'
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


# pylint: disable=too-few-public-methods
class DuplicateFilter(logging.Filter):
    """
    A logging filter that suppresses duplicate log messages from the same module within a specified time frame.

    Attributes:
        do_not_filter_above (int): Log level above which messages should not be filtered.
        filter_reset_seconds (int): Time in seconds after which duplicate log messages are allowed again.

        __init__(do_not_filter_above=logging.ERROR, filter_reset_seconds: int = 0, name: str = ''):
            Initializes the DuplicateFilter with the specified parameters.

            Parameters:
                do_not_filter_above (int): Log level above which messages should not be filtered.
                filter_reset_seconds (int): Time in seconds after which duplicate log messages are allowed again.
                name (str): The name of the filter.
            Initializes the DuplicateFilter with the specified parameters.

        filter(record) -> bool:
            Determines if the log record should be logged or suppressed based on the duplicate filter criteria.
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

        now: datetime = datetime.now()

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
