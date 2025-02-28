"""Module containing custom json encoders for the carconnectivity package."""
from __future__ import annotations
from typing import TYPE_CHECKING


from enum import Enum
import json
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from typing import Any


class ExtendedEncoder(json.JSONEncoder):
    """Datetime object encode used for json serialization"""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def default(self, o: Any) -> str:
        """Serialize datetime object to isodate string

        Args:
            o (Any): object to encode

        Returns:
            str: object represented as isoformat string
        """
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, timedelta):
            return o.total_seconds()
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


class ExtendedWithNullEncoder(ExtendedEncoder):
    """Encoder allowing null used for json serialization"""

    def default(self, o: Any) -> str:
        try:
            return super().default(o)
        except TypeError:
            return None
