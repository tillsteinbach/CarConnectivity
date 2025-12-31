""" Module to define interfaces for CarConnectivity components."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from carconnectivity_services.base.service import BaseService, ServiceType


class ICarConnectivity:  # pylint: disable=too-few-public-methods
    """
    Interface for CarConnectivity implementation.

    This interface defines the contract that all CarConnectivity implementations must follow.
    """
    def get_service_for(self, service_type: ServiceType) -> Optional[BaseService]:
        """
        Retrieve a service instance for the specified service type.
        This method must be implemented by CarConnectivity to provide
        access to specific service implementations based on the requested service type.
        Args:
            service_type (ServiceType): The type of service to retrieve.
        Returns:
            Optional[BaseService]: The service instance if available, None otherwise.
        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """

        raise NotImplementedError("Method get_service_for() must be implemented by CarConnectivity")


class IGenericVehicle:  # pylint: disable=too-few-public-methods
    """
    Interface for Generic Vehicle implementation.

    This interface defines the contract that all Generic Vehicle implementations must follow.
    """
