"""Module for door classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import GenericVehicle


class Doors(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent all doors in the vehicle.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create doors without vehicle')
        super().__init__(object_id='doors', parent=vehicle)
        self.open_state = EnumAttribute("open_state", self)
        self.lock_state = EnumAttribute("lock_state", self)
        self.doors: Dict[str, Doors.Door] = {}

    def __str__(self) -> str:
        return_string: str = 'Doors:'
        if self.open_state.enabled and self.open_state.value is not None:
            return_string += f' {self.open_state.value.value}'
        if self.lock_state.enabled and self.lock_state.value is not None:
            return_string += f' {self.lock_state.value.value}'
        return_string += '\n'
        for door in self.doors.values():
            if door is not None and door.enabled:
                return_string += f'\t{door}'
        return return_string

    # pylint: disable=duplicate-code
    class OpenState(Enum):
        """
        Enum for door open state.
        """
        OPEN = 'open'
        CLOSED = 'closed'
        UNSUPPORTED = 'unsupported'
        INVALID = 'invalid'
        UNKNOWN = 'unknown open state'
    # pylint: enable=duplicate-code

    class LockState(Enum):
        """
        Enum for door lock state.
        """
        LOCKED = 'locked'
        UNLOCKED = 'unlocked'
        INVALID = 'invalid'
        UNKNOWN = 'unknown lock state'

    class Door(GenericObject):
        """
        A class to represent a door in the vehicle.
        """
        def __init__(self, door_id: str, doors: Doors) -> None:
            super().__init__(object_id=door_id, parent=doors)
            self.door_id: str = door_id
            self.open_state = EnumAttribute("open_state", self)
            self.lock_state = EnumAttribute("lock_state", self)

        def __str__(self) -> str:
            return_string: str = f'Door {self.door_id}:'
            if self.open_state.enabled and self.open_state.value is not None:
                return_string += f' {self.open_state.value.value}'
            if self.lock_state.enabled and self.lock_state.value is not None:
                return_string += f' {self.lock_state.value.value}'
            return_string += '\n'
            return return_string
