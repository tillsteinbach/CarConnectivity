"""
This module defines the generic classes that represent objects in the CarConnectivity system.

The module provides a GenericObject class that can be used to create a hierarchical structure of objects,
each with a unique identifier, parent-child relationships, and attributes. The objects can be enabled or
disabled, and their attributes can be retrieved recursively.

Classes:
    GenericObject: A class to represent a generic object in a hierarchical structure.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, TypeVar

from carconnectivity.attributes import GenericAttribute


if TYPE_CHECKING:
    from typing import Optional, Union, Literal


class GenericObject:
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
    def __init__(self, object_id: str, parent: Optional[GenericObject] = None) -> None:
        if '/' in object_id:
            raise ValueError('ID cannot contain /')
        self.__id: str = object_id
        self.__parent: Optional[GenericObject] = parent
        self.__enabled: bool = False
        if parent is not None:
            parent.children.append(self)
        self.__children: List[Union[GenericObject, GenericAttribute]] = []

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
        return self.__parent

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
        address = ''
        if self.__parent is not None:
            address: str = f'{self.__parent.get_absolute_path()}/'
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

    @enabled.setter
    def enabled(self, set_enabled: bool) -> None:
        self.__enabled: bool = set_enabled
        if self.__parent is not None and self.__parent.enabled != set_enabled:
            self.__parent.enabled = set_enabled

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


L = TypeVar('L', bound=GenericObject)


class GenericList(GenericObject, List[L]):
    """
    A class that represents a generic list which extends both GenericObject and List.

    Methods
    -------
    __add__(item):
        Adds an item to the list and enables the list if it was previously disabled.

    __str__() -> str:
        Returns a string representation of the list, including only the enabled items.
    """
    def __add__(self, item) -> List[L]:
        ret_val: list[L] = super().__add__(item)
        # Enable the list if it was previously disabled after an object was added
        if not self.enabled:
            self.enabled = True
        return ret_val

    def __str__(self) -> str:
        return '[' + ', '.join([str(item) for item in self if item.enabled]) + ']'
