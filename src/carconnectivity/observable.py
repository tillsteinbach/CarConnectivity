"""
This module provides the Observable class, which is a base class for objects that can be observed by other objects.

The Observable class allows objects to be observed by other objects, enabling a publish-subscribe pattern.
Observers can register to be notified of specific events, and the Observable class manages the notification process.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import IntEnum, Flag, auto

if TYPE_CHECKING:
    from typing import Optional, Set, Tuple, Callable, Any, List


class Observable:
    """
    A class to represent an observable object.
    """
    def __init__(self, origin: Optional[Observable] = None) -> None:
        if origin is not None:
            self.__observers: Set[Tuple[Callable[[Any, Observable.ObserverEvent], None],
                                        Observable.ObserverEvent, Observable.ObserverPriority, bool]] = origin.__observers  # pylint: disable=protected-access
            self.flags_to_notify_on_transaction_end: Observable.ObserverEvent = origin.flags_to_notify_on_transaction_end
            self.__delay_notifications: bool = origin.__delay_notifications  # pylint: disable=protected-access
            self.__delayed_flags: Observable.ObserverEvent = origin.__delayed_flags  # pylint: disable=protected-access
        else:
            self.__observers: Set[Tuple[Callable[[Any, Observable.ObserverEvent], None],
                                        Observable.ObserverEvent, Observable.ObserverPriority, bool]] = set()
            self.flags_to_notify_on_transaction_end: Observable.ObserverEvent = Observable.ObserverEvent.NONE
            self.__delay_notifications: bool = False
            self.__delayed_flags: Observable.ObserverEvent = Observable.ObserverEvent.NONE

    @property
    def delay_notifications(self) -> bool:
        """
        Delay notifications property is used to delay notifications to observers in certain phases of the object lifecycle,
        e.g. in the constructor when behaviour otherwise would be undefined.
        """
        return self.__delay_notifications

    @delay_notifications.setter
    def delay_notifications(self, value: bool) -> None:
        """
        Sets the delay notification flag and triggers notifications when the delaying is disabled.

        Args:
            value (bool): If True, delays notifications. If False, triggers any delayed notifications.
        """
        self.__delay_notifications = value
        if not value and self.__delayed_flags != Observable.ObserverEvent.NONE:
            self.notify(self.__delayed_flags)
            self.__delayed_flags = Observable.ObserverEvent.NONE

    def add_observer(self, observer: Callable[[Any, Observable.ObserverEvent], None], flag: Observable.ObserverEvent,
                     priority: Optional[Observable.ObserverPriority] = None, on_transaction_end: bool = False) -> None:
        """
        Adds an observer to the list of observers.

        Args:
            observer (Callable): The observer function to be added.
            flag (Observable.ObserverEvent): The event flag that the observer is interested in.
            priority (Optional[Observable.ObserverPriority], optional): The priority of the observer. Defaults to Observable.ObserverPriority.USER_MID.
            on_transaction_end (bool, optional): Whether the observer should be notified at the end of a transaction. Defaults to False.

        Returns:
            None
        """
        if priority is None:
            priority = Observable.ObserverPriority.USER_MID  # pyright: ignore[reportAssignmentType]
        self.__observers.add((observer, flag, priority, on_transaction_end))

    def remove_observer(self, observer: Callable[[Any, Observable.ObserverEvent], None], flag: Optional[Observable.ObserverEvent] = None) -> None:
        """
        Removes an observer from the list of observers.

        Args:
            observer (Callable): The observer to be removed.
            flag (Optional[Observable.ObserverEvent], optional): The specific event flag associated with the observer.
                If provided, only the observer with this flag will be removed. Defaults to None.

        Returns:
            None
        """
        self.__observers = set(filter(lambda observerEntry: observerEntry[0] == observer
                                      or (flag is not None and observerEntry[1] == flag), self.__observers))  # pyright: ignore [reportAttributeAccessIssue]

    def get_observers(self, flags, on_transaction_end: bool = False) -> List[Callable[[Any, Observable.ObserverEvent], None]]:
        """
        Retrieve a list of observers based on the specified flags.

        Args:
            flags: The criteria used to filter observers.
            on_transaction_end (bool, optional): If True, only return observers that should be notified at the end of a transaction. Defaults to False.

        Returns:
            List[Any]: A list of observers that match the specified criteria.
        """
        return [observerEntry[0] for observerEntry in self.get_observer_entries(flags, on_transaction_end)]

    # pylint: disable=duplicate-code
    def get_observer_entries(self, flags: Observable.ObserverEvent, on_transaction_end: bool = False, entries_sorted=True) -> \
            List[Callable[[Any, Observable.ObserverEvent], None]]:
        """
        Retrieve a sorted list of observer entries based on the specified flags and transaction end condition.

        Args:
            flags (Observable.ObserverEvent): The event flags to filter observers.
            on_transaction_end (bool, optional): If True, only include observers that should be notified on transaction end. Defaults to False.
            entries_sorted (bool, optional): If True, return the list of observers sorted by priority. Defaults to True.

        Returns:
            List[Any]: A sorted list of observer entries that match the specified criteria.
        """
        observers: Set[Tuple[Callable[[Any, Observable.ObserverEvent], None], Observable.ObserverEvent, Observable.ObserverPriority, bool]] = set()
        for observer_entry in self.__observers:
            observer, observerflags, priority, observer_on_transaction_complete = observer_entry
            del observer
            del priority
            if (flags & observerflags) and observer_on_transaction_complete == on_transaction_end:
                observers.add(observer_entry)
        if entries_sorted:
            def get_priority(entry) -> int:
                return int(entry[2])
            return sorted(observers, key=get_priority)
        return list(observers)
    # pylint: enable=duplicate-code

    def notify(self, flags: Observable.ObserverEvent) -> None:
        """
        Notify all observers of the current state.

        This method retrieves the list of observers based on the provided flags and
        notifies each observer by calling it with the current element and flags.

        If there are flags to notify on transaction end, it updates the flags to notify on transaction end.

        Args:
            flags (Observable.ObserverEvent): The flags indicating the current state to notify observers about.

        Returns:
            None
        """
        #  Notify observers if delay is not enabled
        if not self.delay_notifications:
            observers: List[Callable[[Any, Observable.ObserverEvent], None]] = self.get_observers(flags=flags, on_transaction_end=False)
            for observer in observers:
                observer(element=self, flags=flags)
        else:
            self.__delayed_flags |= flags
        # Remove disabled if was enabled and not yet notified, only last state to be reported
        if (flags & Observable.ObserverEvent.ENABLED) and (self.flags_to_notify_on_transaction_end & Observable.ObserverEvent.DISABLED):
            self.flags_to_notify_on_transaction_end &= ~Observable.ObserverEvent.DISABLED  # pylint: disable=invalid-unary-operand-type
        # Remove enabled if was enabled and not yet notified, only last state to be reported
        elif (flags & Observable.ObserverEvent.DISABLED) and (self.flags_to_notify_on_transaction_end & Observable.ObserverEvent.ENABLED):
            self.flags_to_notify_on_transaction_end &= ~Observable.ObserverEvent.ENABLED  # pylint: disable=invalid-unary-operand-type

        self.flags_to_notify_on_transaction_end |= flags

    def transaction_end(self) -> None:
        """
        Ends the current transaction and notifies the relevant observers.

        This method checks if there are any flags set to notify observers at the end of the transaction.
        If such flags exist, it retrieves the list of observers associated with these flags and calls
        each observer with the current element and the flags. After notifying the observers, it resets
        the flags to None.

        Returns:
            None
        """
        if self.flags_to_notify_on_transaction_end != Observable.ObserverEvent.NONE:
            observers: List[Callable[[Any, Observable.ObserverEvent], None]] = \
                self.get_observers(flags=self.flags_to_notify_on_transaction_end, on_transaction_end=True)
            for observer in observers:
                observer(element=self, flags=self.flags_to_notify_on_transaction_end)
            self.flags_to_notify_on_transaction_end = Observable.ObserverEvent.NONE

    class ObserverEvent(Flag):
        """
        ObserverEvent is an enumeration that represents different types of events
        that an observer can handle in the car connectivity context.
        Attributes:
            NONE: Represents no event.
            ENABLED: Represents the event when an object or attribute is enabled.
            DISABLED: Represents the event when an object or attribute is disabled.
            VALUE_CHANGED: Represents the event when the value observed by the observer changes.
            UPDATED: Represents the event when the value is updated (rewritten).
            UPDATED_MEASUREMENT: Represents the event when the value is updated (rewritten with a new measurement time).
            ALL: Represents a combination of all possible observer events.
        """
        NONE = 0
        ENABLED = auto()
        DISABLED = auto()
        VALUE_CHANGED = auto()
        UPDATED = auto()
        UPDATED_NEW_MEASUREMENT = auto()
        ALL = ENABLED | DISABLED | VALUE_CHANGED | UPDATED | UPDATED_NEW_MEASUREMENT  # pylint: disable=unsupported-binary-operation

    class ObserverPriority(IntEnum):
        """
        Enum representing the priority levels for observers.

        Attributes:
            INTERNAL_FIRST (int): Highest priority for internal observers.
            INTERNAL_HIGH (int): High priority for internal observers.
            USER_HIGH (int): High priority for user observers.
            INTERNAL_MID (int): Mid priority for internal observers.
            USER_MID (int): Mid priority for user observers.
            INTERNAL_LOW (int): Low priority for internal observers.
            USER_LOW (int): Low priority for user observers.
            INTERNAL_LAST (int): Lowest priority for internal observers.
        """
        INTERNAL_FIRST = 1
        INTERNAL_HIGH = 2
        USER_HIGH = 3
        INTERNAL_MID = 4
        USER_MID = 5
        INTERNAL_LOW = 6
        USER_LOW = 7
        INTERNAL_LAST = 8
