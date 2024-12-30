"""This module defines the classes that represent attributes in the CarConnectivity system."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum

from datetime import datetime

from carconnectivity.units import GenericUnit, Length, Level

if TYPE_CHECKING:
    from typing import Any, Optional, Union, List, Literal
    from carconnectivity.objects import GenericObject


class GenericAttribute:  # pylint: disable=too-many-instance-attributes
    """
    GenericAttribute represents a generic attribute with a name, value, unit, and parent object.

    Attributes:
        name (str): The name of the attribute.
        parent (GenericObject): The parent object to which this attribute belongs.
        value (Optional[Any]): The value of the attribute.
        unit (Optional[str]): The unit of the attribute value.
        enabled (bool): A flag indicating whether the attribute is enabled.
        last_changed (Optional[datetime]): The last time the attribute value was changed in the vechile.
        last_changed_local (Optional[datetime]): The last time the attribute value was changed in carconnectivity.
        last_updated (Optional[datetime]): The last time the attribute value was updated in the vehcile.
        last_updated_local (Optional[datetime]): The last time the attribute value was updated in carconnectivity.
    """

    def __init__(self, name: str, parent: GenericObject, value: Optional[Any] = None, unit: Optional[GenericUnit] = None) -> None:
        """
        Initialize an attribute for a car connectivity object.

        Args:
            name (str): The name of the attribute.
            parent (GenericObject): The parent object to which this attribute belongs.
            value (Optional[Any], optional): The initial value of the attribute. Defaults to None.
            unit (Optional[str], optional): The unit of the attribute value. Defaults to None.
        """
        self.__name: str = name
        self.__parent: GenericObject = parent
        self.__parent.children.append(self)
        self.__value: Optional[Any] = None
        self.__unit: Optional[GenericUnit] = unit

        self.__enabled = False

        self.last_changed: Optional[datetime] = None
        self.last_changed_local: Optional[datetime] = None
        self.last_updated: Optional[datetime] = None
        self.last_updated_local: Optional[datetime] = None

        if value is not None:
            self._set_value(value)

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
    def value(self) -> Optional[Any]:
        """
        Retrieve the value of the attribute.

        Returns:
            Optional[Any]: The current value of the attribute, or None if not set.
        """
        return self.__value

    @property
    def unit(self) -> Optional[str]:
        """
        Get the si-unit of the attribute.

        Returns:
            Optional[str]: The unit of the attribute if set, otherwise None.
        """
        return self.__unit

    def _set_value(self, value: Optional[Any], measured: Optional[datetime] = None, unit: Optional[GenericUnit] = None) -> None:
        now: datetime = datetime.now()
        self.last_updated_local = now
        self.last_updated = measured or now
        if self.__value != value:
            self.__value = value
            self.last_changed_local = now
            self.last_changed = measured or now

            self.enabled = True
        if self.__unit != unit:
            self.__unit = unit

    @value.setter
    def value(self, new_value) -> None:
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
        self.__enabled: bool = set_enabled
        # if there is a parent and it is not yet enabled, enable it
        if set_enabled and self.__parent is not None:
            self.__parent.enabled = set_enabled

    @property
    def parent(self) -> Optional[GenericObject]:
        """
        Returns the parent object of the current attribute.

        Returns:
            Optional[GenericObject]: The parent object if it exists, otherwise None.
        """
        return self.__parent

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
        address = ''
        # if there is a parent, we get the parent's address
        if self.__parent is not None:
            address: str = f'{self.__parent.get_absolute_path()}/'
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


class BooleanAttribute(GenericAttribute):
    """
    A class used to represent a Boolean Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: bool | None = None) -> None:
        super().__init__(name, parent, value, None)


class EnumAttribute(GenericAttribute):
    """
    A class used to represent a Enum Attribute.
    """
    def __init__(self, name: str, parent: GenericObject, value: Enum | None = None) -> None:
        super().__init__(name, parent, value, None)

    def __str__(self) -> str:
        return f"{self.name}: {self.value.value}"


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
