"""
Module containing the Garage class.

This module defines the Garage class, which represents a garage that can hold multiple vehicles.
The Garage class provides methods to add, replace, remove, and retrieve vehicles, as well as list all vehicles and their VINs.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.vehicle import GenericVehicle

if TYPE_CHECKING:
    from typing import List, Dict, Optional


class Garage(GenericObject):
    """
    A class to represent a garage that can hold multiple vehicles.
    """
    def __init__(self, parent) -> None:
        super().__init__(object_id='garage', parent=parent)
        self.delay_notifications = True
        self._vehicles: Dict[str, GenericVehicle] = {}
        self.enabled = True
        self.delay_notifications = False

    def add_vehicle(self, vehicle_id: str, vehicle: GenericVehicle) -> None:
        """
        Adds a vehicle to the garage.

        Args:
            vehicle_id (str): The unique identifier of the vehicle.
            vehicle (GenericVehicle): The vehicle object to be added.

        Returns:
            None
        """
        if vehicle_id.upper() in self._vehicles:
            raise ValueError(f'Vehicle with ID {vehicle_id.upper()} already exists in the garage.')
        self._vehicles[vehicle_id.upper()] = vehicle

    def replace_vehicle(self, vehicle_id: str, vehicle: GenericVehicle) -> None:
        """
        Replaces a vehicle in the garage.

        Args:
            vehicle_id (str): The unique identifier of the vehicle.
            vehicle (GenericVehicle): The vehicle object to be added.

        Returns:
            None
        """
        self._vehicles[vehicle_id.upper()] = vehicle

    def remove_vehicle(self, vehicle_id: str) -> None:
        """
        Remove a vehicle from the garage by its vehicle ID.

        Args:
            vehicle_id (str): The ID of the vehicle to be removed.

        Returns:
            None
        """
        if vehicle_id.upper() in self._vehicles:
            del self._vehicles[vehicle_id.upper()]

    def get_vehicle(self, vehicle_id: str) -> Optional[GenericVehicle]:
        """
        Retrieve a vehicle from the garage by its vehicle ID.

        Args:
            vehicle_id (str): The unique identifier of the vehicle to retrieve.

        Returns:
            GenericVehicle | None: The vehicle object if found, otherwise None.
        """
        return self._vehicles.get(vehicle_id.upper())

    def list_vehicles(self) -> List[GenericVehicle]:
        """
        Returns a list of all vehicles in the garage.

        Returns:
            list[GenericVehicle]: A list containing all the vehicles.
        """
        return list(self._vehicles.values())

    def list_vehicle_vins(self) -> List[str]:
        """
        Returns a list of all vehicle vins of vehicles in the garage.

        Returns:
            list[str]: A list containing all the vehicle vins.
        """
        return list(self._vehicles.keys())
