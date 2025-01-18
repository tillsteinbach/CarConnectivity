"""This module defines the classes that represent attributes in the CarConnectivity system."""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Union

import logging

from carconnectivity.attributes import GenericAttribute
from carconnectivity.objects import GenericObject

if TYPE_CHECKING:
    from carconnectivity.objects import Optional

LOG: logging.Logger = logging.getLogger("carconnectivity")


class Commands(GenericObject):
    """
    A class representing a collection of commands in the car connectivity system.

    Args:
        object_id (str): The object ID of the commands object.
        parent (GenericObject): The parent object of the commands object.
    """
    def __init__(self, object_id: str = "commands", parent: Optional[GenericObject] = None) -> None:
        super().__init__(object_id=object_id, parent=parent)
        self.commands: Dict[str, GenericCommand] = {}

    def add_command(self, command: GenericCommand) -> None:
        """
        Add a command to the commands object.

        Args:
            command (GenericCommand): The command to add.
        """
        if command.name not in self.commands:
            self.commands[command.name] = command

    def contains_command(self, command_name: str) -> bool:
        """
        Check if the commands object contains a command with the given name.

        Args:
            command_name (str): The name of the command to check.

        Returns:
            bool: True if the commands object contains the command, False otherwise.
        """
        return command_name in self.commands


class GenericCommand(GenericAttribute[Union[str, Dict], None]):
    """
    A class representing a generic command in the car connectivity system.

    Args:
        name (str): The name of the command.
        parent (GenericObject): The parent object of the command.
    """
    def __init__(self, name: str, parent: Optional[GenericObject]) -> None:
        super().__init__(name=name, parent=parent, value=None, unit=None)
        self._is_changeable: bool = True
