"""This module defines the classes that represent attributes in the CarConnectivity system."""
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Optional

import logging
import json

from enum import Enum

from datetime import datetime, timezone, timedelta

from pytimeparse import parse

from carconnectivity.units import GenericUnit, Length, Level, Temperature, Speed, Power, Current, Energy
from carconnectivity.observable import Observable
from carconnectivity.json_util import ExtendedWithNullEncoder

# pylint: disable=duplicate-code
SUPPORT_IMAGES = False
try:
    from PIL import Image
    SUPPORT_IMAGES = True
except ImportError:
    pass

SUPPORT_ASCII_IMAGES = False
try:
    from carconnectivity.image_util import image_to_ASCII_art  # pylint: disable=ungrouped-imports
    SUPPORT_ASCII_IMAGES = True
except ImportError:
    pass
# pylint: enable=duplicate-code

if TYPE_CHECKING:
    from typing import Any, Union, List, Literal, Callable, Tuple, Set, Self, Type, Dict
    from carconnectivity.objects import GenericObject


T = TypeVar('T')
U = TypeVar('U', bound=Optional[GenericUnit])


LOG: logging.Logger = logging.getLogger("carconnectivity")


class GenericAttribute(Observable, Generic[T, U]):  # pylint: disable=too-many-instance-attributes, too-many-lines, too-many-public-methods
    """
    GenericAttribute represents a generic attribute with a name, value, unit, and parent object.

    Attributes:
        name (str): The name of the attribute.
        parent (GenericObject): The parent object to which this attribute belongs.
        value (Optional[Any]): The value of the attribute.
        unit (Optional[str]): The unit of the attribute value.
        enabled (bool): A flag indicating whether the attribute is enabled.
        last_changed (Optional[datetime]): The last time the attribute value was changed in the vehicle.
        last_changed_local (Optional[datetime]): The last time the attribute value was changed in carconnectivity.
        last_updated (Optional[datetime]): The last time the attribute value was updated in the vehicle.
        last_updated_local (Optional[datetime]): The last time the attribute value was updated in carconnectivity.
    """

    # pylint: disable-next=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: Optional[GenericObject], value: Optional[T] = None, value_type: Optional[Type[T]] = None, unit: Optional[U] = None,
                 tags: Optional[Set[str]] = None) -> None:
        """
        Initialize an attribute for a car connectivity object.

        Args:
            name (str): The name of the attribute.
            parent (GenericObject): The parent object to which this attribute belongs.
            value (Optional[Any], optional): The initial value of the attribute. Defaults to None.
            unit (Optional[str], optional): The unit of the attribute value. Defaults to None.
        """
        super().__init__()
        self.__name: str = name
        self.tags: Set[str] = tags if tags is not None else set()
        if parent is None:
            raise ValueError('Parent object is required')
        self.__parent: GenericObject = parent
        self.__parent.children.append(self)
        self.__value: Optional[T] = None
        self.__value_type: Optional[Type[T]] = value_type if value_type is not None else type(value) if value is not None else None
        self.__unit: Optional[U] = unit
        self.__unit_type: Optional[Type[U]] = type(unit) if unit is not None else None
        self._is_changeable: bool = False
        self._on_set_hooks: List[Tuple[Callable[[Self, Optional[T]], T], bool]] = []

        self.__enabled = False

        self.last_changed: Optional[datetime] = None
        self.last_changed_local: Optional[datetime] = None
        self.last_updated: Optional[datetime] = None
        self.last_updated_local: Optional[datetime] = None

        if value is not None:
            self._set_value(value)

    def has_tag(self, tag: str) -> bool:
        """
        Check if the attribute has a specific tag.

        Args:
            tag (str): The tag to check.

        Returns:
            bool: True if the attribute has the tag, False otherwise.
        """
        return tag in self.tags

    def tag(self, tag: str) -> None:
        """
        Add a tag to the attribute.

        Args:
            tag (str): The tag to add.

        Returns:
            None
        """
        self.tags.add(tag)

    def untag(self, tag: str) -> None:
        """
        Remove a tag from the attribute.

        Args:
            tag (str): The tag to remove.

        Returns:
            None
        """
        self.tags.remove(tag)

    def _add_on_set_hook(self, hook: Callable[[Self, T], T], early_hook=False) -> None:
        """
        Add a hook to be called when the value is set.

        Args:
            hook (Callable): The hook to be called when the value is set.

        Returns:
            None
        """
        if hook not in self._on_set_hooks:
            self._on_set_hooks.append((hook, early_hook))

    def _execute_on_set_hook(self, new_value: Optional[T], early_hook=False) -> Optional[T]:
        """
        Execute all hooks that are called when the value is set.

        Args:
            early_hook (bool): If True, only execute hooks that are called before the value is set.

        Returns:
            None
        """
        for hook, early in self._on_set_hooks:
            if early == early_hook:
                new_value = hook(self, new_value)
        return new_value

    def _remove_on_set_hook(self, hook: Callable[[Self, T], T]) -> None:
        """
        Remove a hook from the list of hooks to be called when the value is set.

        Args:
            hook (Callable): The hook to be removed.

        Returns:
            None
        """
        for ihook, _ in self._on_set_hooks:
            if ihook == hook:
                self._on_set_hooks.remove((ihook, _))

    def _has_on_set_hook(self, hook: Callable[[Self, T], T]) -> bool:
        """
        Check if a hook is present in the list of hooks to be called when the value is set.

        Args:
            hook (Callable): The hook to check.

        Returns:
            bool: True if the hook is present, False otherwise.
        """
        for ihook, _ in self._on_set_hooks:
            if ihook == hook:
                return True
        return False

    def get_on_set_hooks(self, early_hook=False) -> List[Callable[[Self, T], T]]:
        """
        Retrieve all hooks that are called when the value is set.

        Args:
            early_hook (bool): If True, only return hooks that are called before the value is set.

        Returns:
            List[Callable]: A list of hooks that are called when the value is set.
        """
        return [hook for hook, early in self._on_set_hooks if early == early_hook]

    def __del__(self) -> None:
        if self.enabled:
            self.enabled = False

    # pylint: disable=duplicate-code
    def get_observer_entries(self, flags: Observable.ObserverEvent, on_transaction_end: bool = False, entries_sorted=True) \
            -> List[Tuple[Callable, Observable.ObserverEvent, Observable.ObserverPriority, bool]]:
        """
        Retrieve a sorted list of observer entries based on the specified flags and transaction end condition.

        Args:
            flags (Observable.ObserverEvent): The event flags to filter observers.
            on_transaction_end (bool, optional): If True, only include observers that should be notified on transaction end. Defaults to False.
            entries_sorted (bool, optional): If True, the list of observers will be sorted by priority. Defaults to True.

        Returns:
            List[Any]: A sorted list of observer entries that match the specified criteria.
        """
        observers: Set[Tuple[Callable, Observable.ObserverEvent, Observable.ObserverPriority, bool]] \
            = set(super().get_observer_entries(flags, on_transaction_end, False))
        if self.__parent is not None:
            observers.update(self.__parent.get_observer_entries(flags=flags, on_transaction_end=on_transaction_end, entries_sorted=False))
        if entries_sorted:
            def get_priority(entry) -> int:
                return int(entry[2])
            return sorted(observers, key=get_priority)
        return list(observers)
    # pylint: enable=duplicate-code

    @property
    def name(self) -> str:
        """
        Returns the name attribute of the object.

        Returns:
            str: The name attribute.
        """
        return self.__name

    @property
    def id(self) -> str:
        """
        Returns the identifier of the object.

        Returns:
            str: The identifier of the object.
        """
        return self.__name

    @property
    def is_changeable(self) -> bool:
        """
        Check if the attribute is changeable.

        Returns:
            bool: True if the attribute is changeable, False otherwise.
        """
        return self._is_changeable

    @property
    def value(self) -> Optional[T]:
        """
        Retrieve the value of the attribute.

        Returns:
            Optional[Any]: The current value of the attribute, or None if not set.
        """
        return self.__value

    @property
    def value_type(self) -> Optional[Type[T]]:
        """
        Retrieve the value type of the attribute.

        Returns:
            Optional[Any]: The current value type of the attribute, or None if not set.
        """
        return self.__value_type

    @property
    def unit(self) -> Optional[U]:
        """
        Get the si-unit of the attribute.

        Returns:
            Optional[U]: The unit of the attribute if set, otherwise None.
        """
        return self.__unit

    @property
    def unit_type(self) -> Optional[Type[U]]:
        """
        Get the si-unit of the attribute.

        Returns:
            TypeVar: The unit type of the attribute.
        """
        return self.__unit_type

    def _set_unit(self, unit: Optional[U]) -> None:
        """
        Set the unit of the attribute.

        Args:
            unit (Optional[U]): The unit to set.

        Returns:
            None
        """
        self.__unit = unit

    def _set_value(self, value: Optional[T], measured: Optional[datetime] = None, unit: Optional[U] = None) -> None:
        """
        Set the value of the attribute.

        Will set last_updated_local to the current time and set the UPDATED flag for any notifications.
        Will set last_updated to the measured time if it is given, otherwise will set to now.
        Will set UPDATED_NEW_MEASUREMENT flag if the measured time is different than last_updated.
        Will set VALUE_CHANGED flag if the value or unit is different than the current value or unit.

        Args:
            value (Optional[Any]): The value to set.
            measured (Optional[datetime], optional): The time the value was measured. Defaults to None.
            unit (Optional[U], optional): The unit of the value. Defaults to None.

        Returns:
            None
        """
        flags: Observable.ObserverEvent = Observable.ObserverEvent.NONE
        now: datetime = datetime.now(tz=timezone.utc)

        if value is not None:
            value = self.type_conversion(value)

        # Value from the past
        if self.last_updated is not None and measured is not None and self.last_updated > measured:
            LOG.debug('Value from the past: %s: %s > %s', self.name, self.last_updated, measured)
            return

        # Value was updated
        if self.last_updated_local != now:
            flags |= Observable.ObserverEvent.UPDATED
            self.last_updated_local = now
        # Value was measured
        if measured and self.last_updated != measured:
            flags |= Observable.ObserverEvent.UPDATED_NEW_MEASUREMENT
            self.last_updated = measured or now
        else:
            self.last_updated = now
        # Value was changed
        if self.__value != value:
            flags |= Observable.ObserverEvent.VALUE_CHANGED
            self.__value = value
            self.last_changed_local = now
            self.last_changed = measured or now

            if value is not None:
                self.enabled = True
            else:
                self.enabled = False
        # Unit was changed
        if unit is not None and self.__unit != unit:
            flags |= Observable.ObserverEvent.VALUE_CHANGED
            self.__unit = unit
        self.notify(flags)

    def type_conversion(self, value: T) -> Any:  # pylint: disable=too-many-return-statements
        """
        Convert the value to the correct type.

        Args:
            value (T): The value to convert.

        Returns:
            bool: The converted value.
        """
        if self.__value_type is bool and value is not None and not isinstance(value, bool):
            LOG.debug('Implicitly converting value to bool: %s', value)
            if isinstance(value, str):
                if value.lower() in [x.lower() for x in ['true', 'yes', '1', 'on']]:
                    return True
                if value.lower() in [x.lower() for x in ['false', 'no', '0', 'off']]:
                    return False
                raise ValueError('Not a value that can be interpreted as valid boolean value (True/False)')
            if isinstance(value, (float, int)):
                if value == 0:
                    return False
                return True
            return bool(value)
        if self.__value_type is float and value is not None and not isinstance(value, float):
            LOG.debug('Implicitly converting value to float: %s', value)
            return float(value)
        if self.__value_type is timedelta and value is not None and not isinstance(value, timedelta):
            LOG.debug('Implicitly converting value to timedelta: %s', value)
            if isinstance(value, str):
                try:
                    try:
                        return timedelta(seconds=float(value))
                    except ValueError:
                        return timedelta(seconds=parse(value))
                except TypeError as err:
                    raise ValueError('Not a value that can be interpreted as valid timedelta value') from err
            elif isinstance(value, (int, float)):
                return timedelta(seconds=value)
            return timedelta(value)
        return value

    @staticmethod
    def convert(value, from_unit: U, to_unit: U) -> T:
        """
        Converts a value from one unit to another.

        Args:
            value: The value to be converted.
            from_unit (U): The unit of the input value.
            to_unit (U): The unit to convert the value to.

        Returns:
            T: The converted value.
        """
        del from_unit, to_unit
        return value

    def set_value(self, value: Optional[T], unit: Optional[U] = None) -> None:
        """
        Set the value of the attribute. Will convert the unit if needed.

        Args:
            value (Optional[Any]): The value to set.
            unit (Optional[U], optional): The unit of the value. Defaults to None.

        Returns:
            None
        """
        if unit is not None and self.__unit is not None:
            self.value = self.convert(value=value, from_unit=unit, to_unit=self.__unit)
        else:
            self.value = value

    def in_locale(self, locale: Optional[str]) -> Tuple[Optional[Any], Optional[U]]:
        """
        Returns the value and unit of the attribute, using the provided locale.
        This is used to change e.g. Temperature in Celsius to Farenheit for users in the US.

        Args:
            locale (str): The locale to be used.

        Returns:
            Tuple[Optional[float], U]: A tuple containing the converted value and unit of the attribute.
        """
        del locale
        return self.value, self.unit

    # pylint: disable=duplicate-code
    @value.setter
    def value(self, new_value: Optional[T]) -> None:
        """
        Setting the value directly is not allowed. GenericAttributes are not mutable by the user.
        """
        # then execute all early hooks
        new_value = self._execute_on_set_hook(new_value, early_hook=True)
        if self._is_changeable:
            # First bring the value to the correct type
            if new_value is not None:
                new_value = self.type_conversion(new_value)
            # then execute all late hooks
            new_value = self._execute_on_set_hook(new_value, early_hook=False)
            # finally set the value
            self._set_value(new_value)
        else:
            raise TypeError('You cannot set this attribute. Attribute is not mutable.')
    # pylint: enable=duplicate-code

    @property
    def enabled(self) -> bool:
        """
        Check if the feature is enabled.

        Returns:
            bool: True if the feature is enabled, False otherwise.
        """
        return self.__enabled

    # pylint: disable=duplicate-code
    @enabled.setter
    def enabled(self, set_enabled: bool) -> None:
        if set_enabled:
            # if the object is being enabled, we need to enable the parent first
            if self.__parent is not None:
                self.__parent.enabled = True
            # only notify if the object was not enabled before
            if not self.__enabled:
                self.__enabled = True
                self.notify(Observable.ObserverEvent.ENABLED)
        else:
            # only notify if the object was enabled before
            if self.__enabled:
                self.__enabled = False
                self.notify(Observable.ObserverEvent.DISABLED)

            # Disable parent only if all children are disabled
            if all(not child.enabled for child in self.__parent.children):
                self.__parent.enabled = False

    @property
    def parent(self) -> GenericObject:
        """
        Returns the parent object of the current attribute.

        Returns:
            GenericObject: The parent object.
        """
        if self.__parent is not None and self not in self.__parent.children:
            raise ValueError(f'Error in structure: Parent object {self.__parent.get_absolute_path()} does not have this attribute '
                             f'{self.get_absolute_path()} as a child')
        return self.__parent

    @parent.setter
    def parent(self, parent: GenericObject) -> None:
        """
        Sets the parent object of the current attribute.

        Args:
            parent (Optional[GenericObject]): The parent object to set.

        Returns:
            None
        """
        if self.__parent is not None and self in self.__parent.children:
            self.__parent.children.remove(self)
        self.__parent = parent
        parent.children.append(self)
    # pylint: enable=duplicate-code

    def __str__(self) -> str:
        unit_str = self.__unit.value if self.__unit else ""
        return f"{self.__value}{unit_str}"

    def get_by_path(self, address_string: str) -> Union[GenericObject, GenericAttribute, Literal[False]]:  # pylint: disable=too-many-return-statements
        """
        Retrieve an object or attribute by its path.

        Args:
            address_string (str): The path to the desired object or attribute.
                                  It can be an empty string (''), a parent reference ('..'),
                                  an absolute path starting with '/', or a relative path.

        Returns:
            Union[GenericObject, GenericAttribute, bool]: The object or attribute found at the specified path,
                                                          or False if no matching object or attribute is found.
        """
        # an empty string means we are looking for the current object
        if address_string == '':
            return self
        # '..' means we are looking for the parent object
        if address_string == '..':
            if self.__parent is None:
                return False
            return self.__parent
        # an absolute path starts with '/'
        if address_string.startswith('/'):
            return self.get_root().get_by_path(address_string[1:])
        # a relative path
        parts = address_string.split('/', 1)
        for child in self.__parent.children:
            # if the child has the same id as the first part of the address
            if child.id == parts[0]:
                # if there is no more parts, we found the object
                if len(parts) == 1:
                    return child
                # otherwise, we continue the search with the remaining parts
                return child.get_by_path(parts[1])
        # if we reach this point, we did not find the object
        return False

    def get_root(self) -> Union[GenericObject, GenericAttribute]:
        """
        Retrieve the root object in the hierarchy.

        This method traverses up the parent chain to find the root object.
        If the current object has no parent, it is considered the root.

        Returns:
            Union[GenericObject, GenericAttribute]: The root object in the hierarchy.
        """
        if self.__parent is None:
            return self
        return self.__parent.get_root()

    def get_absolute_path(self) -> str:
        """
        Constructs and returns the absolute path of the current object.

        The absolute path is built by recursively calling the `get_absolute_path`
        method on the parent object (if it exists) and appending the current object's
        `id` to it.

        Returns:
            str: The absolute path of the current object.
        """
        address: str = ''
        # if there is a parent, we get the parent's address
        if self.__parent is not None:
            address = f'{self.__parent.get_absolute_path()}/'
        # we append the current object's id
        address += f'{self.id}'
        return address

    def get_attributes(self, recursive=False) -> List[GenericAttribute]:
        """
        Retrieve a list of attributes from the object's children.
        Will return self as a List

        Args:
            recursive (bool): If True, the method will recursively retrieve attributes from all nested children.

        Returns:
            List[GenericAttribute]: A list of attributes found in the object's children.
        """
        del recursive
        return [self]

    def as_dict(self, filter_function: Optional[Callable[[Any], None]] = None) -> Optional[Any]:
        """
        Convert the attribute value to a dictionary representation if it passes the filter function.

        Args:
            filter_function (Optional[Callable[[Any], None]]): A function that takes the attribute value as input
                and returns a boolean indicating whether the value should be included in the dictionary.

        Returns:
            Optional[Any]: The attribute value if it passes the filter function, otherwise None.
        """
        if filter_function is None or not filter_function(self.value):
            return_dict: Dict[str, Any] = {"val": self.value}
            if self.last_updated is not None:
                return_dict["upd"] = self.last_updated.isoformat()
            if self.unit is not None:
                return_dict["uni"] = self.unit.value
            return return_dict
        return None

    def as_json(self) -> Optional[str]:
        """
        Convert the attribute value to a JSON string.

        If the attribute value is an image and image support is enabled,
        the method returns None. Otherwise, it serializes the value to a
        JSON string using the ExtendedWithNullEncoder class.

        Returns:
            Optional[str]: The JSON string representation of the attribute
            value, or None if the value is an image and image support is enabled.
        """
        if SUPPORT_IMAGES and isinstance(self.value, Image.Image):
            return None
        return json.dumps(self.value, cls=ExtendedWithNullEncoder, skipkeys=True, indent=4)


class BooleanAttribute(GenericAttribute[bool, None]):
    """
    A class used to represent a Boolean Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Optional[bool] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, value_type=bool, unit=None, tags=tags)


class IntegerAttribute(GenericAttribute[int, None]):
    """
    A class used to represent a Integer Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Optional[int] = None,  # pylint: disable=too-many-arguments, too-many-positional-arguments
                 maximum: Optional[int] = None, minimum: Optional[int] = None, tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, value_type=int, unit=None, tags=tags)
        self.maximum: Optional[int] = maximum
        self.minimum: Optional[int] = minimum

    @GenericAttribute.value.setter
    def value(self, new_value: int) -> None:
        """
        Overwriting value setter to check for minimum/maximum limits
        """
        if self._is_changeable:
            # First bring the value to the correct type
            if new_value is not None:
                new_value = self.type_conversion(new_value)
            if self.minimum is not None and new_value is not None and new_value < self.minimum:
                raise ValueError(f'Value {new_value}{self.unit.value if self.unit is not None else ""} '
                                 f'is below minimum {self.minimum}{self.unit.value if self.unit is not None else ""}')
            if self.maximum is not None and new_value is not None and new_value > self.maximum:
                raise ValueError(f'Value {new_value}{self.unit.value if self.unit is not None else ""} '
                                 f'is above maximum {self.maximum}{self.unit.value if self.unit is not None else ""}')
        GenericAttribute.value.fset(self, new_value)


class FloatAttribute(GenericAttribute[float, U]):
    """
    A class used to represent a float Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None, unit: Optional[U] = None,
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, value_type=float, unit=unit, tags=tags)
        self.precision: Optional[float] = precision
        self.maximum: Optional[float] = maximum
        self.minimum: Optional[float] = minimum

    @GenericAttribute.value.setter
    def value(self, new_value: float) -> None:
        """
        Overwriting value setter to check for minimum/maximum limits
        """
        if self._is_changeable:
            # First bring the value to the correct type
            if new_value is not None:
                new_value = self.type_conversion(new_value)
            if self.minimum is not None and new_value is not None and new_value < self.minimum:
                raise ValueError(f'Value {new_value}{self.unit.value if self.unit is not None else ""} '
                                 f'is below minimum {self.minimum}{self.unit.value if self.unit is not None else ""}')
            if self.maximum is not None and new_value is not None and new_value > self.maximum:
                raise ValueError(f'Value {new_value}{self.unit.value if self.unit is not None else ""} '
                                 f'is above maximum {self.maximum}{self.unit.value if self.unit is not None else ""}')
        GenericAttribute.value.fset(self, new_value)


class EnumAttribute(Generic[T], GenericAttribute[T, None]):
    """
    A class used to represent a Enum Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[Enum] = None, value_type: Type[Enum] = Enum,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, value_type=value_type, unit=None, tags=tags)

    def __str__(self) -> str:
        return f"{self.value.value if self.value else None}"


class StringAttribute(GenericAttribute[str, None]):
    """
    A class used to represent a String Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Optional[str] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, value_type=str, unit=None, tags=tags)


class DateAttribute(GenericAttribute[datetime, None]):
    """
    A class used to represent a Date Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Optional[datetime] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, value_type=datetime, unit=None, tags=tags)


class DurationAttribute(GenericAttribute[timedelta, None]):
    """
    A class used to represent a Duration.
    """
    def __init__(self, name: str, parent: GenericObject, value: Optional[timedelta] = None,  # pylint: disable=too-many-arguments, too-many-positional-arguments
                 maximum: Optional[timedelta] = None, minimum: Optional[timedelta] = None, tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, value_type=timedelta, unit=None, tags=tags)
        self.maximum: Optional[timedelta] = maximum
        self.minimum: Optional[timedelta] = minimum

    @GenericAttribute.value.setter
    def value(self, new_value: timedelta) -> None:
        """
        Overwriting value setter to check for minimum/maximum limits
        """
        if self._is_changeable:
            # First bring the value to the correct type
            if new_value is not None:
                new_value = self.type_conversion(new_value)
            if self.minimum is not None and new_value is not None and new_value < self.minimum:
                raise ValueError(f'Value {new_value}{self.unit.value if self.unit is not None else ""} '
                                 f'is below minimum {self.minimum}{self.unit.value if self.unit is not None else ""}')
            if self.maximum is not None and new_value is not None and new_value > self.maximum:
                raise ValueError(f'Value {new_value}{self.unit.value if self.unit is not None else ""} '
                                 f'is above maximum {self.maximum}{self.unit.value if self.unit is not None else ""}')
        GenericAttribute.value.fset(self, new_value)


class RangeAttribute(FloatAttribute[Length]):
    """
    A class used to represent a Range Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None, unit: Length = Length.KM,
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, unit=unit, maximum=maximum, minimum=minimum, precision=precision, tags=tags)

    @staticmethod
    def convert(value, from_unit: U, to_unit: U) -> T:  # pylint: disable=too-many-return-statements
        """
        Convert a range value from one unit to another.

        Parameters:
        value (float): The range value to be converted.
        from_unit (Length): The unit of the input range value. Must be an instance of the Length enum.
        to_unit (Length): The unit to convert the range value to. Must be an instance of the Length enum.

        Returns:
        float: The converted range value in the desired unit. If any of the parameters are None or if the units are the same,
        the original value is returned.

        Supported conversions:
        - Kilometers to miles
        - Miles to kilometers
        """
        if from_unit is None or to_unit is None or value is None or from_unit == to_unit:
            return value
        if from_unit == Length.MI and to_unit == Length.KM:
            return value * 1.609344
        if from_unit == Length.KM and to_unit == Length.MI:
            return value / 1.609344
        if from_unit == Length.M and to_unit == Length.KM:
            return value / 1000
        if from_unit == Length.KM and to_unit == Length.M:
            return value * 1000
        if from_unit == Length.FT and to_unit == Length.M:
            return value / 3.2808
        if from_unit == Length.M and to_unit == Length.FT:
            return value * 3.2808
        if from_unit == Length.FT and to_unit == Length.MI:
            return value / 5280
        if from_unit == Length.MI and to_unit == Length.FT:
            return value * 5280
        return value

    def range_in(self, unit: Length) -> Optional[float]:
        """
        Convert the range to a different unit.

        Args:
            unit (Length): The unit to convert the range to.

        Returns:
            float: The range in the specified unit.
        """
        if unit is None or self.unit is None:
            raise ValueError('No unit specified or value has no unit')
        return self.convert(self.value, self.unit, unit)

    def in_locale(self, locale: Optional[str]) -> Tuple[Optional[float], Optional[U]]:
        """
        Get the range in the unit the user is used to

        Args:
            locale (str): The locale to get the range in.

        Returns:
            str: The range in the locale.

        Converts the range to miles if the locale is 'en_US', 'en_GB', 'en_LR', 'en_MM', otherwise converts to kilometers.
        """
        if locale is None:
            return self.value, self.unit
        miles_locales: list[str] = ['en_US', 'en_GB', 'en_LR', 'en_MM']
        if any(locale.startswith(loc) for loc in miles_locales):
            if self.unit == Length.KM:
                return self.range_in(Length.MI), Length.MI
            if self.unit == Length.M:
                return self.range_in(Length.FT), Length.FT
        return self.range_in(Length.KM), Length.KM


class SpeedAttribute(FloatAttribute[Speed]):
    """
    A class used to represent a Speed Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None, unit: Speed = Speed.KMH,
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, unit=unit, maximum=maximum, minimum=minimum, precision=precision, tags=tags)

    @staticmethod
    def convert(value, from_unit: U, to_unit: U) -> T:
        """
        Convert a speed value from one unit to another.

        Parameters:
        value (float): The speed value to be converted.
        from_unit (Speed): The unit of the input speed value. Must be an instance of the Speed enum.
        to_unit (Speed): The unit to convert the speed value to. Must be an instance of the Speed enum.

        Returns:
        float: The converted speed value in the desired unit. If any of the parameters are None or if the units are the same,
        the original value is returned.

        Supported conversions:
        - Kilometers per hour to miles per hour
        - Miles per hour to kilometers per hour
        """
        if from_unit is None or to_unit is None or value is None or to_unit == from_unit:
            return value
        if from_unit == Speed.MPH and to_unit == Speed.KMH:
            return value * 1.609344
        if from_unit == Speed.KMH and to_unit == Speed.MPH:
            return value / 1.609344
        return value

    def speed_in(self, unit: Speed) -> Optional[float]:
        """
        Convert the speed to a different unit.

        Args:
            unit (Speed): The unit to convert the speed to.

        Returns:
            float: The speed in the specified unit.
        """
        if unit is None or self.unit is None:
            raise ValueError('No unit specified or value has no unit')
        return self.convert(self.value, self.unit, unit)

    def in_locale(self, locale: Optional[str]) -> Tuple[Optional[float], Optional[U]]:
        """
        Get the speed in the unit the user is used to

        Args:
            locale (str): The locale to get the range in.

        Returns:
            str: The speed in the locale.

        Converts the speed to miles per hour if the locale is 'en_US', 'en_GB', 'en_LR', 'en_MM', otherwise converts to kilometers per hour.
        """
        if locale is None:
            return self.value, self.unit
        miles_locales: list[str] = ['en_US', 'en_GB', 'en_LR', 'en_MM']
        if any(locale.startswith(loc) for loc in miles_locales):
            return self.speed_in(Speed.MPH), Speed.MPH
        return self.speed_in(Speed.KMH), Speed.KMH


class PowerAttribute(FloatAttribute[Power]):
    """
    A class used to represent a power Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None, unit: Power = Power.KW,
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, unit=unit, maximum=maximum, minimum=minimum, precision=precision, tags=tags)

    @staticmethod
    def convert(value, from_unit: U, to_unit: U) -> T:
        """
        Convert a power value from one unit to another.

        Parameters:
        value (float): The power value to be converted.
        from_unit (Power): The unit of the input power value. Must be an instance of the Power enum.
        to_unit (Power): The unit to convert the power value to. Must be an instance of the Power enum.

        Returns:
        float: The converted power value in the desired unit. If any of the parameters are None or if the units are the same,
        the original value is returned.

        Supported conversions:
        - Watts to Kilowatts
        - Kilowatts to Watts
        """
        if from_unit is None or to_unit is None or value is None or to_unit == from_unit:
            return value
        if from_unit == Power.W and to_unit == Power.KW:
            return value / 1000
        if from_unit == Power.KW and to_unit == Power.W:
            return value * 1000
        return value

    def power_in(self, unit: Power) -> Optional[float]:
        """
        Convert the power to a different unit.

        Args:
            unit (Power): The unit to convert the power to.

        Returns:
            float: The power in the specified unit.
        """
        if unit is None or self.unit is None:
            raise ValueError('No unit specified or value has no unit')
        return self.convert(self.value, self.unit, unit)


class EnergyAttribute(FloatAttribute[Energy]):
    """
    A class used to represent a energy Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None, unit: Energy = Energy.KWH,
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, unit=unit, maximum=maximum, minimum=minimum, precision=precision, tags=tags)

    @staticmethod
    def convert(value, from_unit: U, to_unit: U) -> T:
        """
        Convert an energy value from one unit to another.

        Parameters:
        value (float): The power value to be converted.
        from_unit (Energy): The unit of the input energy value. Must be an instance of the Energy enum.
        to_unit (Energy): The unit to convert the energy value to. Must be an instance of the Energy enum.

        Returns:
        float: The converted energy value in the desired unit. If any of the parameters are None or if the units are the same,
        the original value is returned.

        Supported conversions:
        - Watthours to Kilowatthours
        - Kilowatthours to Watthours
        """
        if from_unit is None or to_unit is None or value is None or to_unit == from_unit:
            return value
        if from_unit == Energy.WH and to_unit == Energy.KWH:
            return value / 1000
        if from_unit == Energy.KWH and to_unit == Energy.WH:
            return value * 1000
        return value

    def energy_in(self, unit: Energy) -> Optional[float]:
        """
        Convert the energy to a different unit.

        Args:
            unit (Energy): The unit to convert the energy to.

        Returns:
            float: The energy in the specified unit.
        """
        if unit is None or self.unit is None:
            raise ValueError('No unit specified or value has no unit')
        return self.convert(self.value, self.unit, unit)


class CurrentAttribute(FloatAttribute[Current]):
    """
    A class used to represent a current Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None, unit: Current = Current.A,
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, unit=unit, maximum=maximum, minimum=minimum, precision=precision, tags=tags)


class LevelAttribute(FloatAttribute[Level]):
    """
    A class used to represent a Level Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None,  # pylint: disable=too-many-arguments, too-many-positional-arguments
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, unit=Level.PERCENTAGE, maximum=maximum, minimum=minimum, precision=precision, tags=tags)


class TemperatureAttribute(FloatAttribute[Temperature]):
    """
    A class used to represent a Temperature Attribute.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(self, name: str, parent: GenericObject, value: Optional[T] = None, unit: Temperature = Temperature.C,
                 maximum: Optional[float] = None, minimum: Optional[float] = None, precision: Optional[float] = None,
                 tags: Optional[Set[str]] = None) -> None:
        super().__init__(name=name, parent=parent, value=value, unit=unit, maximum=maximum, minimum=minimum, precision=precision, tags=tags)

    @staticmethod
    def convert(value, from_unit: U, to_unit: U) -> T:  # pylint: disable=too-many-return-statements
        """
        Convert a temperature value from one unit to another.

        Parameters:
        value (float): The temperature value to be converted.
        from_unit (Temperature): The unit of the input temperature value. Must be an instance of the Temperature enum.
        to_unit (Temperature): The unit to convert the temperature value to. Must be an instance of the Temperature enum.

        Returns:
        float: The converted temperature value in the desired unit. If any of the parameters are None or if the units are the same,
        the original value is returned.

        Supported conversions:
        - Celsius to Fahrenheit
        - Celsius to Kelvin
        - Fahrenheit to Celsius
        - Fahrenheit to Kelvin
        - Kelvin to Celsius
        - Kelvin to Fahrenheit
        """
        if from_unit is None or to_unit is None or value is None or to_unit == from_unit:
            return value
        if to_unit == Temperature.C:
            if from_unit == Temperature.F:
                return (value - 32.0) * (5.0 / 9.0)
            if from_unit == Temperature.K:
                return value - 273.15
        if to_unit == Temperature.F:
            if from_unit == Temperature.C:
                return ((value * (9.0 / 5.0)) + 32.0)
            if from_unit == Temperature.K:
                return ((value - 273.15) * (9.0 / 5.0)) + 32.0
        if to_unit == Temperature.K:
            if from_unit == Temperature.C:
                return value + 273.15
            if from_unit == Temperature.F:
                return 273.5 + ((value - 32.0) * (5.0 / 9.0))
        return value

    def temperature_in(self, unit: U) -> Optional[float]:
        """
        Convert the temperature to a different unit.

        Args:
            unit (Temperature): The unit to convert the temperature to.

        Returns:
            float: The temperature in the specified unit.
        """
        if unit is None:
            raise ValueError('No unit specified')
        if self.unit is None:
            target_unit = Temperature.C
            LOG.warning('No unit specified for temperature in Attribute %s, defaulting to Celsius', self.name)
        else:
            target_unit = self.unit
        return self.convert(self.value, target_unit, unit)

    def in_locale(self, locale: Optional[str]) -> Tuple[Optional[T], Optional[U]]:
        """
        Get the temperature in the unit the user is used to

        Args:
            locale (str): The locale to get the temperature in.

        Returns:
            str: The temperature in the locale.

        Converts the temperature to Fahrenheit if the locale is 'en_US', 'en_BS', 'en_KY', 'en_LR', 'en_PW', 'en_FM', 'en_MH', otherwise converts to Celsius.
        """
        if locale is None:
            return self.value, self.unit
        fahrenheit_locales: list[str] = ['en_US', 'en_BS', 'en_KY', 'en_LR', 'en_PW', 'en_FM', 'en_MH']
        if any(locale.startswith(loc) for loc in fahrenheit_locales):
            return self.temperature_in(Temperature.F), Temperature.F
        return self.temperature_in(Temperature.C), Temperature.C


if SUPPORT_IMAGES:
    class ImageAttribute(Generic[T], GenericAttribute[T, None]):
        """
        A class used to represent a Image Attribute.
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments
        def __init__(self, name: str, parent: GenericObject, value: Optional[Image] = None, value_type: Type[Image] = Image,
                     tags: Optional[Set[str]] = None) -> None:
            super().__init__(name=name, parent=parent, value=value, value_type=value_type, unit=None, tags=tags)

        def __str__(self) -> str:
            if SUPPORT_ASCII_IMAGES:
                return f"{image_to_ASCII_art(self.value) if self.value else None}"
            return f"{self.name}"
