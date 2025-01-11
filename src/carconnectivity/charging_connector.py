"""
Module for connector.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute
if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity.charging import Charging


class ChargingConnector(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent the charging connector of a vehicle.
    """
    def __init__(self, charging: Optional[Charging] = None) -> None:
        if charging is None:
            raise ValueError('Cannot create connector without charging')
        super().__init__(object_id='connector', parent=charging)
        self.delay_notifications = True
        self.connection_state: EnumAttribute = EnumAttribute("connection_state", parent=self)
        self.lock_state: EnumAttribute = EnumAttribute("lock_state", parent=self)
        self.external_power: EnumAttribute = EnumAttribute("lock_state", parent=self)
        self.delay_notifications = False

    def __str__(self) -> str:
        return_string: str = 'Connector:\n'
        if self.connection_state.enabled and self.connection_state.value is not None:
            return_string += f'Connection State: {self.connection_state.value.value}\n'
        if self.lock_state.enabled and self.lock_state.value is not None:
            return_string += f'Lock State: {self.lock_state.value.value}\n'
        if self.external_power.enabled and self.external_power.value is not None:
            return_string += f'External Power: {self.external_power.value.value}\n'
        return return_string

    class ChargingConnectorConnectionState(Enum,):
        """
        Enum representing the connection state of the connector.

        Attributes:
            CONNECTED (str): The connector is connected.
            DISCONNECTED (str): The connector is disconnected.
            INVALID (str): The connector state is invalid.
            UNSUPPORTED (str): The connector state is unsupported.
            UNKNOWN (str): The connector state is unknown.
        """
        CONNECTED = 'connected'
        DISCONNECTED = 'disconnected'
        INVALID = 'invalid'
        UNSUPPORTED = 'unsupported'
        UNKNOWN = 'unknown unlock plug state'

    class ChargingConnectorLockState(Enum,):
        """
        Enum representing the lock state of a plug.

        Attributes:
            LOCKED (str): The plug is locked.
            UNLOCKED (str): The plug is unlocked.
            INVALID (str): The plug state is invalid.
            UNSUPPORTED (str): The plug state is unsupported.
            UNKNOWN (str): The plug state is unknown.
        """
        LOCKED = 'locked'
        UNLOCKED = 'unlocked'
        INVALID = 'invalid'
        UNSUPPORTED = 'unsupported'
        UNKNOWN = 'unknown unlock plug state'

    class ExternalPower(Enum,):
        """
        Enum representing the state of external power.

        Attributes:
            AVAILABLE (str): External power is available.
            ACTIVE (str): External power is used.
            UNAVAILABLE (str): External power is unavailable.
            INVALID (str): External power state is invalid.
            UNSUPPORTED (str): External power is unsupported.
            UNKNOWN (str): External power state is unknown.
        """
        AVAILABLE = 'available'
        ACTIVE = 'active'
        UNAVAILABLE = 'unavailable'
        INVALID = 'invalid'
        UNSUPPORTED = 'unsupported'
        UNKNOWN = 'unknown external power'
