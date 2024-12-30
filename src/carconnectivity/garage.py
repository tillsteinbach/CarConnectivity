""" Module containing the Garage class. """
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
        self._vehicles: Dict[str, GenericVehicle] = {}
        self.enabled = True

    def add_vehicle(self, vehicle_id: str, vehicle: GenericVehicle) -> None:
        """
        Adds a vehicle to the garage.

        Args:
            vehicle_id (str): The unique identifier of the vehicle.
            vehicle (GenericVehicle): The vehicle object to be added.

        Returns:
            None
        """
        self._vehicles[vehicle_id] = vehicle

    def remove_vehicle(self, vehicle_id: str) -> None:
        """
        Remove a vehicle from the garage by its vehicle ID.

        Args:
            vehicle_id (str): The ID of the vehicle to be removed.

        Returns:
            None
        """
        if vehicle_id in self._vehicles:
            del self._vehicles[vehicle_id]

    def get_vehicle(self, vehicle_id: str) -> Optional[GenericVehicle]:
        """
        Retrieve a vehicle from the garage by its vehicle ID.

        Args:
            vehicle_id (str): The unique identifier of the vehicle to retrieve.

        Returns:
            GenericVehicle | None: The vehicle object if found, otherwise None.
        """
        return self._vehicles.get(vehicle_id)

    def list_vehicles(self) -> List[GenericVehicle]:
        """
        Returns a list of all vehicles in the garage.

        Returns:
            list[GenericVehicle]: A list containing all the vehicles.
        """
        return list(self._vehicles.values())

    def list_vehicle_vins(self) -> List[str]:
        """
        Returns a list of all vehicle vins of vehciles in the garage.

        Returns:
            list[GenericVehicle]: A list containing all the vehicle vins.
        """
        return list(self._vehicles.keys())

    def __str__(self) -> str:
        return 'Garage:\n' + '\n'.join(f'  {vehicle}' for vehicle in self._vehicles.values())
