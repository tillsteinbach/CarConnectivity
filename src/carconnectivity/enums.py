"""
This module defines general enums.
"""

from enum import Enum


class ConnectionState(Enum):
    """
    Enum for conenction state
    """
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    DISCONNECTING = 'disconnecting'
    ERROR = 'error'
    UNKNOWN = 'unknown connection state'
