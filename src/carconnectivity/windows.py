"""Module for windows classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import EnumAttribute

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import GenericVehicle


class Windows(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent all windows in the vehicle.
    """
    def __init__(self, vehicle: Optional[GenericVehicle] = None) -> None:
        if vehicle is None:
            raise ValueError('Cannot create windows without vehicle')
        super().__init__(object_id='windows', parent=vehicle)
        self.open_state = EnumAttribute("open_state", self)
        self.windows: Dict[str, Windows.Window] = {}

    def __str__(self) -> str:
        return_string: str = 'Windows:'
        if self.open_state.enabled and self.open_state.value is not None:
            return_string += f' {self.open_state.value.value}'
        return_string += '\n'
        for window in self.windows.values():
            if window is not None and window.enabled:
                return_string += f'\t{window}'
        return return_string

    class OpenState(Enum):
        """
        Enum for window open state.
        """
        OPEN = 'open'
        CLOSED = 'closed'
        UNSUPPORTED = 'unsupported'
        INVALID = 'invalid'
        UNKNOWN = 'unknown open state'

    class Window(GenericObject):
        """
        A class to represent a window in the vehicle.
        """
        def __init__(self, window_id: str, windows: Windows) -> None:
            super().__init__(object_id=window_id, parent=windows)
            self.window_id: str = window_id
            self.open_state = EnumAttribute("open_state", self)

        def __str__(self) -> str:
            return_string: str = f'Window {self.window_id}:'
            if self.open_state.enabled and self.open_state.value is not None:
                return_string += f' {self.open_state.value.value}'
            return_string += '\n'
            return return_string
