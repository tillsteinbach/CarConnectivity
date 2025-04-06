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
        # Execute early hooks before parsing the value
        new_value = self._execute_on_set_hook(new_value, early_hook=True)
        if isinstance(new_value, ClimatizationStartStopCommand.Command):
            newvalue_dict = {}
            newvalue_dict['command'] = new_value
            new_value = newvalue_dict
        elif isinstance(new_value, str):
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
                args = parser.parse_args(new_value.strip().split(sep=' '))
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
            # Execute late hooks before setting the value
            new_value = self._execute_on_set_hook(new_value, early_hook=False)
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
        # Execute early hooks before parsing the value
        new_value = self._execute_on_set_hook(new_value, early_hook=True)
        if isinstance(new_value, ChargingStartStopCommand.Command):
            newvalue_dict = {}
            newvalue_dict['command'] = new_value
            new_value = newvalue_dict
        elif isinstance(new_value, str):
            parser = ThrowingArgumentParser(prog='', add_help=False, exit_on_error=False)
            parser.add_argument('command', help='Command to execute', type=ChargingStartStopCommand.Command,
                                choices=list(ChargingStartStopCommand.Command))
            try:
                args = parser.parse_args(new_value.strip().split(sep=' '))
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
            # Execute late hooks before setting the value
            new_value = self._execute_on_set_hook(new_value, early_hook=False)
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


class HonkAndFlashCommand(GenericCommand):
    """
    HonkAndFlashCommand is a command class for honking and flashing the lights.
    """
    def __init__(self, name: str = 'honk-flash', parent: Optional[GenericObject] = None, with_duration: bool = False) -> None:
        super().__init__(name=name, parent=parent)
        self.with_duration: bool = with_duration

    @property
    def value(self) -> Optional[Union[str, Dict]]:
        return super().value

    @value.setter
    def value(self, new_value: Optional[Union[str, Dict]]) -> None:
        # Execute early hooks before parsing the value
        new_value = self._execute_on_set_hook(new_value, early_hook=True)
        if isinstance(new_value, HonkAndFlashCommand.Command):
            newvalue_dict = {}
            newvalue_dict['command'] = new_value
            new_value = newvalue_dict
        elif isinstance(new_value, str):
            parser = ThrowingArgumentParser(prog='', add_help=False, exit_on_error=False)
            parser.add_argument('command', help='Command to execute', type=HonkAndFlashCommand.Command,
                                choices=list(HonkAndFlashCommand.Command))
            if self.with_duration:
                parser.add_argument('--duration', dest='duration', help='Duration for honking and flashing in seconds', type=int, required=False)
            try:
                args = parser.parse_args(new_value.strip().split(sep=' '))
            except argparse.ArgumentError as e:
                raise SetterError(f'Invalid format for HonkAndFlashCommand: {e.message} {parser.format_usage()}') from e

            newvalue_dict = {}
            newvalue_dict['command'] = args.command
            if self.with_duration:
                newvalue_dict['duration'] = args.duration
            new_value = newvalue_dict
        elif isinstance(new_value, dict):
            if 'command' in new_value and isinstance(new_value['command'], str):
                if new_value['command'] in HonkAndFlashCommand.Command:
                    new_value['command'] = HonkAndFlashCommand.Command(new_value['command'])
                else:
                    raise ValueError('Invalid value for HonkAndFlashCommand. '
                                     f'Command must be one of {HonkAndFlashCommand.Command}')
        if self._is_changeable:
            # Execute late hooks before setting the value
            new_value = self._execute_on_set_hook(new_value, early_hook=False)
            self._set_value(new_value)
        else:
            raise TypeError('You cannot set this attribute. Attribute is not mutable.')

    class Command(Enum):
        """
        Enum class representing different commands for honking and flashing the lights.

        Attributes:
            FLASH (str): Command to flash the lights.
            HONK_AND_FLASH (str): Command to honk and flash the lights.
        """
        FLASH = 'flash'
        HONK_AND_FLASH = 'honk-and-flash'

        def __str__(self) -> str:
            return self.value


class LockUnlockCommand(GenericCommand):
    """
    LockUnlockCommand is a command class for locking and unlocking the vehicle.

    Command (Enum): Enum class representing different commands for locking.

    """
    def __init__(self, name: str = 'lock-unlock', parent: Optional[GenericObject] = None) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def value(self) -> Optional[Union[str, Dict]]:
        return super().value

    @value.setter
    def value(self, new_value: Optional[Union[str, Dict]]) -> None:
        # Execute early hooks before parsing the value
        new_value = self._execute_on_set_hook(new_value, early_hook=True)
        if isinstance(new_value, LockUnlockCommand.Command):
            newvalue_dict = {}
            newvalue_dict['command'] = new_value
            new_value = newvalue_dict
        elif isinstance(new_value, str):
            parser = ThrowingArgumentParser(prog='', add_help=False, exit_on_error=False)
            parser.add_argument('command', help='Command to execute', type=LockUnlockCommand.Command,
                                choices=list(LockUnlockCommand.Command))
            try:
                args = parser.parse_args(new_value.strip().split(sep=' '))
            except argparse.ArgumentError as e:
                raise SetterError(f'Invalid format for LockUnlockCommand: {e.message} {parser.format_usage()}') from e

            newvalue_dict = {}
            newvalue_dict['command'] = args.command
            new_value = newvalue_dict
        elif isinstance(new_value, dict):
            if 'command' in new_value and isinstance(new_value['command'], str):
                if new_value['command'] in LockUnlockCommand.Command:
                    new_value['command'] = LockUnlockCommand.Command(new_value['command'])
                else:
                    raise ValueError('Invalid value for LockUnlockCommand. '
                                     f'Command must be one of {LockUnlockCommand.Command}')
        if self._is_changeable:
            # Execute late hooks before setting the value
            new_value = self._execute_on_set_hook(new_value, early_hook=False)
            self._set_value(new_value)
        else:
            raise TypeError('You cannot set this attribute. Attribute is not mutable.')

    class Command(Enum):
        """
        Enum class representing different commands for locking.

        Attributes:
            LOCK (str): Command to lock the vehicle.
            UNLOCK (str): Command to unlocking the vehicle.
        """
        LOCK = 'lock'
        UNLOCK = 'unlock'

        def __str__(self) -> str:
            return self.value


class WakeSleepCommand(GenericCommand):
    """
    WakeCommand is a command class for waking up a vehicle.

    Command (Enum): Enum class representing different commands for wake/sleep.

    """
    def __init__(self, name: str = 'wake-sleep', parent: Optional[GenericObject] = None) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def value(self) -> Optional[Union[str, Dict]]:
        return super().value

    # pylint: disable=duplicate-code
    @value.setter
    def value(self, new_value: Optional[Union[str, Dict]]) -> None:
        # Execute early hooks before parsing the value
        new_value = self._execute_on_set_hook(new_value, early_hook=True)
        if isinstance(new_value, WakeSleepCommand.Command):
            newvalue_dict = {}
            newvalue_dict['command'] = new_value
            new_value = newvalue_dict
        elif isinstance(new_value, str):
            parser = ThrowingArgumentParser(prog='', add_help=False, exit_on_error=False)
            parser.add_argument('command', help='Command to execute', type=WakeSleepCommand.Command,
                                choices=list(WakeSleepCommand.Command))
            try:
                args = parser.parse_args(new_value.strip().split(sep=' '))
            except argparse.ArgumentError as e:
                raise SetterError(f'Invalid format for WakeSleepCommand: {e.message} {parser.format_usage()}') from e

            newvalue_dict = {}
            newvalue_dict['command'] = args.command
            new_value = newvalue_dict
        elif isinstance(new_value, dict):
            if 'command' in new_value and isinstance(new_value['command'], str):
                if new_value['command'] in WakeSleepCommand.Command:
                    new_value['command'] = WakeSleepCommand.Command(new_value['command'])
                else:
                    raise ValueError('Invalid value for WakeSleepCommand. '
                                     f'Command must be one of {WakeSleepCommand.Command}')
        if self._is_changeable:
            # Execute late hooks before setting the value
            new_value = self._execute_on_set_hook(new_value, early_hook=False)
            self._set_value(new_value)
        else:
            raise TypeError('You cannot use this command. Command is not implemented.')
    # pylint: enable=duplicate-code

    class Command(Enum):
        """
        Enum representing different commands for car connectivity.

        Attributes:
            WAKE (str): Command to wake up the vehicle.
            SLEEP (str): Command to put the vehicle to sleep.
        """
        WAKE = 'wake'
        SLEEP = 'sleep'

        def __str__(self) -> str:
            return self.value


class WindowHeatingStartStopCommand(GenericCommand):
    """
    WindowHeatingStartStopCommand is a command class for starting or stopping the window heating.

    Command (Enum): Enum class representing different commands for window heating.

    """
    def __init__(self, name: str = 'start-stop', parent: Optional[GenericObject] = None) -> None:
        super().__init__(name=name, parent=parent)

    @property
    def value(self) -> Optional[Union[str, Dict]]:
        return super().value

    # pylint: disable=duplicate-code
    @value.setter
    def value(self, new_value: Optional[Union[str, Dict]]) -> None:
        # Execute early hooks before parsing the value
        new_value = self._execute_on_set_hook(new_value, early_hook=True)
        if isinstance(new_value, WindowHeatingStartStopCommand.Command):
            newvalue_dict = {}
            newvalue_dict['command'] = new_value
            new_value = newvalue_dict
        elif isinstance(new_value, str):
            parser = ThrowingArgumentParser(prog='', add_help=False, exit_on_error=False)
            parser.add_argument('command', help='Command to execute', type=WindowHeatingStartStopCommand.Command,
                                choices=list(WindowHeatingStartStopCommand.Command))
            try:
                args = parser.parse_args(new_value.strip().split(sep=' '))
            except argparse.ArgumentError as e:
                raise SetterError(f'Invalid format for WindowHeatingStartStopCommand: {e.message} {parser.format_usage()}') from e

            newvalue_dict = {}
            newvalue_dict['command'] = args.command
            new_value = newvalue_dict
        elif isinstance(new_value, dict):
            if 'command' in new_value and isinstance(new_value['command'], str):
                if new_value['command'] in WindowHeatingStartStopCommand.Command:
                    new_value['command'] = WindowHeatingStartStopCommand.Command(new_value['command'])
                else:
                    raise ValueError('Invalid value for WindowHeatingStartStopCommand. '
                                     f'Command must be one of {WindowHeatingStartStopCommand.Command}')
        if self._is_changeable:
            # Execute late hooks before setting the value
            new_value = self._execute_on_set_hook(new_value, early_hook=False)
            self._set_value(new_value)
        else:
            raise TypeError('You cannot use this command. Command is not implemented.')
    # pylint: enable=duplicate-code

    class Command(Enum):
        """
        Enum class representing different commands for window heating.

        Attributes:
            START (str): Command to start the window heating.
            STOP (str): Command to stop the window heating.
        """
        START = 'start'
        STOP = 'stop'

        def __str__(self) -> str:
            return self.value
