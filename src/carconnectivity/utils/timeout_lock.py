
"""
A wrapper class around TimeoutLock that adds timeout functionality for context manager usage.

This class provides a thread-safe lock with an optional timeout when used as a context manager.
It wraps Python's RLock (reentrant lock) and ensures that lock acquisition attempts will fail
with a TimeoutError if the specified timeout is exceeded when entering a context.

The class acts as a semi-transparent wrapper, exposing the underlying RLock's acquire() and
release() methods while adding timeout enforcement for context manager operations.

Attributes:
    timeout (float): Maximum time in seconds to wait for acquiring the lock when used as a
        context manager. A negative value indicates no timeout limit.
    lock (RLock): The underlying reentrant lock object.

Example:
    >>> lock = TimeoutLock(timeout=5.0)
    >>> try:
    ...     with lock:
    ...         # Critical section code here
    ...         pass
    ... except TimeoutError:
    ...     print("Could not acquire lock within 5 seconds")

    >>> # Or use acquire/release directly
    >>> if lock.acquire(timeout=2.0):
    ...     try:
    ...         # Critical section
    ...         pass
    ...     finally:
    ...         lock.release()
"""
from __future__ import annotations
from typing import Literal

from threading import RLock


class TimeoutLock():
    """
    A wrapper class around RLock that provides timeout functionality for lock acquisition.
    This class extends the basic RLock functionality by adding a default timeout
    for lock acquisition when used as a context manager. It provides a convenient
    way to prevent deadlocks by ensuring that lock acquisition attempts will fail
    after a specified timeout period.
    Attributes:
        timeout (float): The maximum time in seconds to wait when acquiring the lock
            in a context manager. A negative value indicates no timeout limit.
        lock (RLock): The underlying reentrant lock object.
    Example:
        >>> lock = TimeoutLock(timeout=5.0)
        >>> try:
        ...     with lock:
        ...         # Critical section
        ...         pass
        ... except TimeoutError:
        ...     print("Could not acquire lock within 5 seconds")
    Note:
        When using the lock as a context manager (__enter__/__exit__), the configured
        timeout is applied automatically. When using acquire() and release() directly,
        you can specify different timeout values as needed.
    """
    timeout: float
    lock: RLock

    # Semi-transparent __init__ method
    def __init__(self, timeout: float = -1) -> None:
        """
        Initialize a TimeoutLock with a specified timeout value.
        Args:
            timeout (float, optional): Maximum time in seconds to wait for acquiring the lock.
                A negative value (default: -1) indicates no timeout limit.
            *args: Variable length argument list to pass to the underlying RLock.
            **kwargs: Arbitrary keyword arguments to pass to the underlying RLock.
        Returns:
            None
        """

        self.timeout = timeout
        self.lock = RLock()

    def __enter__(self, *args, **kwargs) -> Literal[True]:
        """
        Enter the runtime context related to this object.
        Acquires the underlying lock with the specified timeout.
        Args:
            *args: Variable length argument list (unused, for compatibility).
            **kwargs: Arbitrary keyword arguments (unused, for compatibility).
        Returns:
            Literal[True]: Always returns True if the lock is successfully acquired.
        Raises:
            TimeoutError: If the lock cannot be acquired within the specified timeout period.
        """

        rc: bool = self.lock.acquire(timeout=self.timeout)
        if rc is False:
            raise TimeoutError(f"Could not acquire lock within specified timeout of {self.timeout}s")
        return rc

    def __exit__(self, *args, **kwargs) -> None:
        return self.lock.release()

    # Transparent method calls for rest of Lock's public methods:
    def acquire(self, *args, **kwargs) -> bool:
        """
        Acquire the underlying lock.
        This method delegates the acquisition of the lock to the underlying lock object,
        passing through all arguments and keyword arguments.
        Args:
            *args: Variable length argument list to pass to the underlying lock's acquire method.
            **kwargs: Arbitrary keyword arguments to pass to the underlying lock's acquire method.
                Common keyword arguments include:
                - blocking (bool): Whether to block waiting for the lock (default: True)
                - timeout (float): Maximum time in seconds to wait for the lock (default: -1, meaning no timeout)
        Returns:
            bool: True if the lock was successfully acquired, False otherwise (when blocking=False or timeout expires).
        Raises:
            Any exceptions raised by the underlying lock's acquire method.
        """

        return self.lock.acquire(*args, **kwargs)

    def release(self, *args, **kwargs) -> None:
        """
        Release the lock.
        This method releases the underlying lock, allowing other threads to acquire it.
        All arguments are forwarded to the underlying lock's release method.
        Args:
            *args: Variable length argument list to pass to the underlying lock's release method.
            **kwargs: Arbitrary keyword arguments to pass to the underlying lock's release method.
        Returns:
            None
        Raises:
            RuntimeError: If the lock is not currently held (depending on the underlying lock implementation).
        """

        return self.lock.release(*args, **kwargs)
