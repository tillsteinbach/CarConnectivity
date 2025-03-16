"""
This module defines the generic classes that represent objects in the CarConnectivity system.

The module provides a GenericObject class that can be used to create a hierarchical structure of objects,
each with a unique identifier, parent-child relationships, and attributes. The objects can be enabled or
disabled, and their attributes can be retrieved recursively.

Classes:
    GenericObject: A class to represent a generic object in a hierarchical structure.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import json

from carconnectivity.attributes import GenericAttribute
from carconnectivity.observable import Observable
from carconnectivity.json_util import ExtendedWithNullEncoder

SUPPORT_IMAGES = False
try:
    from PIL import Image
    SUPPORT_IMAGES = True
except ImportError:
    pass

if TYPE_CHECKING:
    from typing import Optional, Union, Literal, Callable, Tuple, Set, List, Any


class GenericObject(Observable):
    """
    A class to represent a generic object in a hierarchical structure.

    Attributes:
    ----------
    id : str
        The unique identifier for the object. It cannot contain '/'.
    parent : Optional[GenericObject]
        The parent object in the hierarchy. Default is None.
    children : List[Union[GenericObject, GenericAttribute]]
        The list of child objects or attributes.
    enabled : bool
        A flag indicating whether the object is enabled or not.
    """
    def __init__(self, object_id: Optional[str] = None, parent: Optional[GenericObject] = None, origin: Optional[GenericObject] = None) -> None:
        if origin is not None:
            super().__init__(origin=origin)
            self.__id: str = origin.id
            self.__children: List[Union[GenericObject, GenericAttribute]] = origin.children
            self.__parent: Optional[GenericObject] = origin.parent
            if parent is not None:
                self.parent = parent
            self.__enabled: bool = origin.enabled
            if self.enabled:
                self.notify(flags=Observable.ObserverEvent.UPDATED)
        else:
            super().__init__()
            if object_id is None:
                raise ValueError('ID cannot be None')
            if '/' in object_id:
                raise ValueError('ID cannot contain /')
            self.__id: str = object_id
            self.__parent: Optional[GenericObject] = parent
            self.__enabled: bool = False
            if parent is not None:
                parent.children.append(self)
            self.__children: List[Union[GenericObject, GenericAttribute]] = []

    def __str__(self) -> str:
        return_string: str = ''
        for element in sorted(self.__children, key=lambda x: x.id):
            if element.enabled:
                if isinstance(element, GenericAttribute):
                    return_string += f'{element.id}: {element}\n'
                else:
                    return_string += f'{element.id}:\n'
                    return_string += ''.join(['\t' + line for line in str(element).splitlines(True)])
        return return_string

    def get_observer_entries(self, flags: Observable.ObserverEvent, on_transaction_end: bool = False, entries_sorted=True) \
            -> List[Tuple[Callable, Observable.ObserverEvent, Observable.ObserverPriority, bool]]:
        """
        Retrieve a sorted list of observer entries based on the specified flags and transaction end condition.

        Args:
            flags (Observable.ObserverEvent): The event flags to filter observers.
            on_transaction_end (bool, optional): If True, only include observers that should be notified on transaction end. Defaults to False.
            entries_sorted (bool, optional): If True, the list of observer entries will be sorted by priority. Defaults to True.

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

    def transaction_end(self) -> None:
        """
        Ends the current transaction and notifies the relevant observers.

        This method override ensures that the transaction end notification is propagated down the hierarchy.

        Returns:
            None
        """
        for child in self.__children:
            child.transaction_end()
        super().transaction_end()

    @property
    def id(self) -> str:
        """
        Returns the identifier of the object.

        Returns:
            str: The identifier of the object.
        """
        return self.__id

    @property
    def parent(self) -> Optional[GenericObject]:
        """
        Returns the parent object of the current object.

        Returns:
            Optional[GenericObject]: The parent object if it exists, otherwise None.
        """
        if self.__parent is not None and self not in self.__parent.children:
            raise ValueError(f'Error in structure: Parent object {self.__parent.get_absolute_path()} does not have this attribute '
                             f'{self.get_absolute_path()} as a child')
        return self.__parent

    @parent.setter
    def parent(self, parent: Optional[GenericObject]) -> None:
        """
        Sets the parent object of the current object.

        Args:
            parent (Optional[GenericObject]): The parent object to set.

        Returns:
            None
        """
        if self.__parent is not None and self in self.__parent.children:
            self.__parent.children.remove(self)
        self.__parent = parent
        parent.children.append(self)

    @property
    def children(self) -> List[Union[GenericObject, GenericAttribute]]:
        """
        Returns the list of child objects.

        Returns:
            List[Union[GenericObject, GenericAttribute]]: A list containing child objects and attributes.
        """
        return self.__children

    def get_root(self) -> GenericObject:
        """
        Recursively finds and returns the root object in the hierarchy.

        This method traverses up the parent chain until it finds the top-most
        object (i.e., the object with no parent) and returns it.

        Returns:
            GenericObject: The root object in the hierarchy.
        """
        if self.parent is None:
            return self
        return self.parent.get_root()

    def get_absolute_path(self) -> str:
        """
        Returns the absolute path of the current object as a string.

        The absolute path is constructed by recursively calling the
        `get_absolute_path` method on the parent object (if it exists)
        and appending the current object's ID.

        Returns:
            str: The absolute path of the current object.
        """
        address: str = ''
        if self.__parent is not None:
            address = f'{self.__parent.get_absolute_path()}/'
        address += f'{self.__id}'
        return address

    def get_attributes(self, recursive=False) -> List[GenericAttribute]:
        """
        Retrieve a list of attributes from the object's children.

        Args:
            recursive (bool): If True, the method will recursively retrieve attributes from all nested children.

        Returns:
            List[GenericAttribute]: A list of attributes found in the object's children.
        """
        attributes = []
        for child in self.__children:
            if child.enabled:
                # If the child is an attribute, add it to the list
                if isinstance(child, GenericAttribute):
                    attributes.append(child)
                # If the child is an object and recursive is True, get its attributes as well
                elif recursive:
                    attributes.extend(child.get_attributes(recursive))
        return attributes

    @property
    def enabled(self) -> bool:
        """
        Check if the object is enabled.

        Returns:
            bool: True if the object is enabled, False otherwise.
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
            # Propagate the disabled state down to the children first to have right order of notifications
            for child in self.__children:
                if child.enabled:
                    child.enabled = False

            # only notify if the object was enabled before
            if self.__enabled:
                self.__enabled = False
                self.notify(Observable.ObserverEvent.DISABLED)

            # Disable parent only if all children are disabled
            if self.__parent is not None and \
                    all(not child.enabled for child in self.__parent.children):
                self.__parent.enabled = False
    # pylint: enable=duplicate-code

    def get_by_path(self, address_string: str) -> Union[GenericObject, GenericAttribute, Literal[False]]:
        """
        Retrieve an object or attribute by its path.

        Args:
            address_string (str): The path to the desired object or attribute.
                                  It can be an empty string (''), a parent reference ('..'),
                                  an absolute path starting with '/', or a relative path.

        Returns:
            Union[GenericObject, GenericAttribute, bool]: The object or attribute found at the specified path,
                                                          or False if no such object or attribute exists.
        """
        # An empty string means we are looking for the current object
        if address_string == '':
            return self
        # '..' means we are looking for the parent object
        if address_string == '..' and self.parent is not None:
            return self.parent

        # If the address starts with a /, we have an absolute path and start from the root
        if address_string.startswith('/'):
            # Normalize the address_string by removing leading slashes
            address_string = '/' + address_string.lstrip('/')
            return self.get_root().get_by_path(address_string[1:])
        # If the address is a relative path, we start from the current object
        child_id, _, rest_of_path = address_string.partition('/')
        for child in self.__children:
            # If the child has the same ID as the first part of the address
            if child.id == child_id:
                # recursively search for the rest of the path
                return child.get_by_path(rest_of_path)
        # If we reach this point, we did not find the object
        return False

    def as_dict(self, filter_function: Optional[Callable[[Any], None]] = None) -> dict[Any, Any]:
        """
        Convert the object and its enabled children to a dictionary.

        Args:
            filter_function (Optional[Callable[[Any], None]]): A function to filter the dictionary values. Defaults to None.

        Returns:
            dict[Any, Any]: A dictionary representation of the object and its enabled children.
        """
        as_dict = {}
        for child in self.children:
            if child.enabled:
                child_dict = child.as_dict(filter_function)
                if child_dict is not None:
                    as_dict[child.id] = child_dict
        return as_dict

    def as_json(self, pretty=False) -> str:
        """
        Convert the object to a JSON string representation.

        This method serializes the object to a JSON string using the `as_dict` method
        with a custom filter function to handle specific types of elements, such as images.
        The JSON string is formatted with an indentation of 4 spaces for readability.

        Returns:
            str: The JSON string representation of the object.
        """
        def filter_dict(element):
            if SUPPORT_IMAGES and isinstance(element, Image.Image):
                return True
            return False
        if pretty:
            indent: int = 4
        else:
            indent = 0
        return json.dumps(self.as_dict(filter_function=filter_dict), cls=ExtendedWithNullEncoder, skipkeys=True, indent=indent)
