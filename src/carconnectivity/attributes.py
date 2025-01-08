"""This module defines the classes that represent attributes in the CarConnectivity system."""
from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic

import logging

from enum import Enum

from datetime import datetime, timezone, timedelta

from carconnectivity.units import GenericUnit, Length, Level, Temperature
from carconnectivity.observable import Observable

if TYPE_CHECKING:
    from typing import Optional, Union, List, Literal, Callable, Tuple, Set
    from carconnectivity.objects import GenericObject


T = TypeVar('T')


LOG: logging.Logger = logging.getLogger("carconnectivity")


class GenericAttribute(Observable, Generic[T]):  # pylint: disable=too-many-instance-attributes
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

    def __init__(self, name: str, parent: GenericObject, value: Optional[T] = None, unit: Optional[GenericUnit] = None) -> None:
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
        self.__parent: GenericObject = parent
        self.__parent.children.append(self)
        self.__value: Optional[T] = None
        self.__unit: Optional[GenericUnit] = unit

        self.__enabled = False

        self.last_changed: Optional[datetime] = None
        self.last_changed_local: Optional[datetime] = None
        self.last_updated: Optional[datetime] = None
        self.last_updated_local: Optional[datetime] = None

        if value is not None:
            self._set_value(value)

    def __del__(self) -> None:
        if self.enabled:
            self.enabled = False

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
            observers.update(self.__parent.get_observer_entries(flags, on_transaction_end, False))
        if entries_sorted:
            def get_priority(entry) -> int:
                return int(entry[2])
            return sorted(observers, key=get_priority)
        return list(observers)

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
    def value(self) -> Optional[T]:
        """
        Retrieve the value of the attribute.

        Returns:
            Optional[Any]: The current value of the attribute, or None if not set.
        """
        return self.__value

    @property
    def unit(self) -> Optional[GenericUnit]:
        """
        Get the si-unit of the attribute.

        Returns:
            Optional[GenericUnit]: The unit of the attribute if set, otherwise None.
        """
        return self.__unit

    def _set_unit(self, unit: Optional[GenericUnit]) -> None:
        """
        Set the unit of the attribute.

        Args:
            unit (Optional[GenericUnit]): The unit to set.

        Returns:
            None
        """
        self.__unit = unit

    def _set_value(self, value: Optional[T], measured: Optional[datetime] = None, unit: Optional[GenericUnit] = None) -> None:
        """
        Set the value of the attribute.

        Will set last_updated_local to the current time and set the UPDATED flag for any notifications.
        Will set last_updated to the measured time if it is given, otherwise will set to now.
        Will set UPDATED_NEW_MEASUREMENT flag if the measured time is different than last_updated.
        Will set VALUE_CHANGED flag if the value or unit is different than the current value or unit.

        Args:
            value (Optional[Any]): The value to set.
            measured (Optional[datetime], optional): The time the value was measured. Defaults to None.
            unit (Optional[GenericUnit], optional): The unit of the value. Defaults to None.

        Returns:
            None
        """
        flags: Observable.ObserverEvent = Observable.ObserverEvent.NONE
        now: datetime = datetime.now(tz=timezone.utc)
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
        if self.__unit != unit:
            flags |= Observable.ObserverEvent.VALUE_CHANGED
            self.__unit = unit
        self.notify(flags)

    @value.setter
    def value(self, new_value: T) -> None:
        """
        Setting the value directly is not allowed. GenericAttributes are not mutable by the user.
        """
        raise NotImplementedError('You cannot set this attribute. Set is not implemented')

    @property
    def enabled(self) -> bool:
        """
        Check if the feature is enabled.

        Returns:
            bool: True if the feature is enabled, False otherwise.
        """
        return self.__enabled

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
        self.__parent = parent

    def __str__(self) -> str:
        unit_str = self.__unit.value if self.__unit else ""
        return f"{self.__name}: {self.__value}{unit_str}"

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


class ChangeableAttribute(GenericAttribute):
    """
    A class representing a changeable attribute in the car connectivity system.

    This class inherits from `GenericAttribute` and serves as a marker for attributes
    that can be changed.
    """
    @GenericAttribute.value.setter
    def value(self, new_value) -> None:
        """
        Setting the value directly.
        """
        self._set_value(new_value)


class BooleanAttribute(GenericAttribute):
    """
    A class used to represent a Boolean Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: bool | None = None) -> None:
        super().__init__(name, parent, value, None)


class FloatAttribute(GenericAttribute):
    """
    A class used to represent a attribute attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Optional[float] = None, unit: Optional[GenericUnit] = None) -> None:
        super().__init__(name, parent, value, unit)


class EnumAttribute(GenericAttribute):
    """
    A class used to represent a Enum Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Enum | None = None) -> None:
        super().__init__(name, parent, value, None)

    def __str__(self) -> str:
        return f"{self.name}: {self.value.value if self.value else None}"


class StringAttribute(GenericAttribute):
    """
    A class used to represent a String Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: str | None = None) -> None:
        super().__init__(name, parent, value, None)


class DateAttribute(GenericAttribute):
    """
    A class used to represent a Date Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: datetime | None = None) -> None:
        super().__init__(name, parent, value, None)


class DurationAttribute(GenericAttribute):
    """
    A class used to represent a Duration.
    """
    def __init__(self, name: str, parent: GenericObject, value: timedelta | None = None) -> None:
        super().__init__(name, parent, value, None)


class RangeAttribute(GenericAttribute):
    """
    A class used to represent a Range Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: float | None = None, unit: Length = Length.KM) -> None:
        super().__init__(name, parent, value, unit)


class LevelAttribute(GenericAttribute):
    """
    A class used to represent a Level Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: float | None = None) -> None:
        super().__init__(name, parent, value, unit=Level.PERCENTAGE)


class TemperatureAttribute(GenericAttribute):
    """
    A class used to represent a Temperature Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: float | None = None, unit: Temperature = Temperature.C) -> None:
        super().__init__(name, parent, value, unit=unit)

    def temperature_in(self, unit: Temperature) -> float:
        """
        Convert the temperature to a different unit.

        Args:
            unit (Temperature): The unit to convert the temperature to.

        Returns:
            float: The temperature in the specified unit.
        """
        if unit is None or self.unit is None:
            raise ValueError('No unit specified or value has no unit')
        elif unit == self.unit:
            return self.value
        elif unit == Temperature.C:
            if self.unit == Temperature.F:
                return ((self.value - 32.0) * (5.0 / 9.0))
            elif self.unit == Temperature.K:
                return self.value - 273.15
        elif unit == Temperature.F:
            if self.unit == Temperature.C:
                return ((self.value * (9.0 / 5.0)) + 32.0)
            elif self.unit == Temperature.K:
                return ((self.value - 273.15) * (9.0 / 5.0)) + 32.0
        elif unit == Temperature.K:
            if self.unit == Temperature.C:
                return self.value + 273.15
            elif self.unit == Temperature.F:
                return 273.5 + ((self.value - 32.0) * (5.0 / 9.0))
            return self.unit.convert_to_kelvin(self.value)
        return self.value
