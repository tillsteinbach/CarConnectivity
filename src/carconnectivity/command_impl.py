"""This module defines the classes that represent attributes in the CarConnectivity system."""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Union

from enum import Enum
import argparse
import logging

from carconnectivity.commands import GenericCommand
from carconnectivity.objects import GenericObject
from carconnectivity.errors import SetterError
from carconnectivity.units import Temperature
from carconnectivity.climatization import Climatization
from carconnectivity.util import ThrowingArgumentParser

if TYPE_CHECKING:
    from carconnectivity.objects import Optional

LOG: logging.Logger = logging.getLogger("carconnectivity")


class ClimatizationStartStopCommand(GenericCommand):
    """
    ClimatizationStartStopCommand is a command class for starting or stopping the climatization system.

    Command (Enum): Enum class representing different commands for climatization.

    """
    def __init__(self, name: str = 'start-stop', parent: Optional[GenericObject] = None) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def value(self) -> Optional[Union[str, Dict]]:
        return super().value

    # pylint: disable=duplicate-code
    @value.setter
    def value(self, new_value: Optional[Union[str, Dict]]) -> None:
        if isinstance(new_value, str):
            parser = ThrowingArgumentParser(prog='', add_help=False, exit_on_error=False)
            parser.add_argument('command', help='Command to execute', type=ClimatizationStartStopCommand.Command,
                                choices=list(ClimatizationStartStopCommand.Command))
            if self.parent is not None and isinstance((climatization := self.parent.parent), Climatization) and climatization.settings is not None \
                    and (target_temperature_attribute := climatization.settings.target_temperature) is not None \
                    and target_temperature_attribute.value is not None:
                default_temperature = target_temperature_attribute.value
                default_temperature_unit = target_temperature_attribute.unit
            else:
                default_temperature = 25
                default_temperature_unit = Temperature.C
            parser.add_argument('--target-temperature', dest='target_temperature', help='Target temperature for climatization', type=float, required=False,
                                default=default_temperature)
            parser.add_argument('--target-temperature-unit', dest='target_temperature_unit', help='Target temperature for climatization', type=Temperature,
                                required=False, choices=list(Temperature), default=default_temperature_unit)
            try:
                args = parser.parse_args(new_value.split(sep=' '))
            except argparse.ArgumentError as e:
                raise SetterError(f'Invalid format for ClimatizationStartStopCommand: {e.message} {parser.format_usage()}') from e

            newvalue_dict = {}
            newvalue_dict['command'] = args.command
            newvalue_dict['target_temperature'] = args.target_temperature
            newvalue_dict['target_temperature_unit'] = args.target_temperature_unit
            new_value = newvalue_dict
        elif isinstance(new_value, dict):
            if 'command' in new_value and isinstance(new_value['command'], str):
                if new_value['command'] in ClimatizationStartStopCommand.Command:
                    new_value['command'] = ClimatizationStartStopCommand.Command(new_value['command'])
                else:
                    raise ValueError('Invalid value for ClimatizationStartStopCommand. '
                                     f'Command must be one of {ClimatizationStartStopCommand.Command}')
        if self._is_changeable:
            for hook in self._on_set_hooks:
                new_value = hook(self, new_value)
            self._set_value(new_value)
        else:
            raise TypeError('You cannot use this command. Command is not implemented.')
    # pylint: enable=duplicate-code

    class Command(Enum):
        """
        Enum class representing different commands for climatization.

        Attributes:
            START (str): Command to start the climatization.
            STOP (str): Command to stop the climatization.
        """
        START = 'start'
        STOP = 'stop'

        def __str__(self) -> str:
            return self.value


class ChargingStartStopCommand(GenericCommand):
    """
    ChargingStartStopCommand is a command class for starting or stopping the charging.

    Command (Enum): Enum class representing different commands for charging.

    """
    def __init__(self, name: str = 'start-stop', parent: Optional[GenericObject] = None) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def value(self) -> Optional[Union[str, Dict]]:
        return super().value

    @value.setter
    def value(self, new_value: Optional[Union[str, Dict]]) -> None:
        if isinstance(new_value, str):
            parser = ThrowingArgumentParser(prog='', add_help=False, exit_on_error=False)
            parser.add_argument('command', help='Command to execute', type=ChargingStartStopCommand.Command,
                                choices=list(ChargingStartStopCommand.Command))
            try:
                args = parser.parse_args(new_value.split(sep=' '))
            except argparse.ArgumentError as e:
                raise SetterError(f'Invalid format for ChargingStartStopCommand: {e.message} {parser.format_usage()}') from e

            newvalue_dict = {}
            newvalue_dict['command'] = args.command
            new_value = newvalue_dict
        elif isinstance(new_value, dict):
            if 'command' in new_value and isinstance(new_value['command'], str):
                if new_value['command'] in ChargingStartStopCommand.Command:
                    new_value['command'] = ChargingStartStopCommand.Command(new_value['command'])
                else:
                    raise ValueError('Invalid value for ChargingStartStopCommand. '
                                     f'Command must be one of {ChargingStartStopCommand.Command}')
        if self._is_changeable:
            for hook in self._on_set_hooks:
                new_value = hook(self, new_value)
            self._set_value(new_value)
        else:
            raise TypeError('You cannot set this attribute. Attribute is not mutable.')

    class Command(Enum):
        """
        Enum class representing different commands for charging.

        Attributes:
            START (str): Command to start the charging.
            STOP (str): Command to stop the charging.
        """
        START = 'start'
        STOP = 'stop'

        def __str__(self) -> str:
            return self.value
