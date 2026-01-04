"""Module for door classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute
from carconnectivity.commands import Commands

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import GenericVehicle


class Doors(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent all doors in the vehicle.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None, initialization: Optional[Dict] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create doors without vehicle')
        super().__init__(object_id='doors', parent=vehicle, initialization=initialization)
        self.commands: Commands = Commands(parent=self)
        self.open_state: EnumAttribute[Doors.OpenState] = EnumAttribute("open_state", self, tags={'carconnectivity'},
                                                                        value_type=Doors.OpenState,
                                                                        initialization=self.get_initialization('open_state'))
        self.lock_state: EnumAttribute[Doors.LockState] = EnumAttribute("lock_state", self, tags={'carconnectivity'},
                                                                        value_type=Doors.LockState,
                                                                        initialization=self.get_initialization('lock_state'))
        self.doors: Dict[str, Doors.Door] = {}

    # pylint: disable=duplicate-code
    class OpenState(Enum):
        """
        Enum for door open state.
        """
        OPEN = 'open'
        CLOSED = 'closed'
        AJAR = 'ajar'
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
        def __init__(self, door_id: str, doors: Doors, initialization: Optional[Dict] = None) -> None:
            super().__init__(object_id=door_id, parent=doors, initialization=initialization)
            self.door_id: str = door_id
            self.open_state: EnumAttribute[Doors.OpenState] = EnumAttribute("open_state", self, tags={'carconnectivity'},
                                                                            value=Doors.OpenState,
                                                                            initialization=self.get_initialization('open_state'))
            self.lock_state: EnumAttribute[Doors.LockState] = EnumAttribute("lock_state", self, tags={'carconnectivity'},
                                                                            value=Doors.LockState,
                                                                            initialization=self.get_initialization('lock_state'))
