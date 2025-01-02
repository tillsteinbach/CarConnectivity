"""Module containing custom exceptions for the carconnectivity package."""


class CarConnectivityError(Exception):
    """
    Base exception class for the carconnectivity package.
    """


class ConfigurationError(CarConnectivityError):
    """
    Exception raised for problems with the configuration.
    """


class RetrievalError(CarConnectivityError):
    """
    Exception raised for errors that occur during data retrieval.
    """


class TooManyRequestsError(RetrievalError):
    """
    Exception raised when too many requests are made to a service.

    This error is typically used to indicate that the client should
    slow down or wait before making further requests.
    """


class SetterError(CarConnectivityError):
    """
    Exception raised for errors in the setter methods.
    """


class ControlError(SetterError):
    """
    Exception raised for errors when controlling something.
    """


class AuthenticationError(CarConnectivityError):
    """
    Exception raised for errors in the authentication process.
    """


class TemporaryAuthenticationError(AuthenticationError):
    """
    Exception raised for temporary authentication errors.

    This exception is a subclass of `AuthenticationError` and is used to indicate
    that an authentication error occurred, but it is temporary and may be resolved
    by retrying the operation.
    """


class APICompatibilityError(CarConnectivityError):
    """
    Exception raised for errors in the API compatibility.

    This exception is used to indicate that there is an issue with the compatibility
    of the API, such as when an expected API version is not supported or when there
    are breaking changes in the API.
    """


class APIError(CarConnectivityError):
    """
    Exception raised for errors that occur during API calls.

    This is a generic exception that can be used to indicate any kind of error
    related to API operations.
    """
