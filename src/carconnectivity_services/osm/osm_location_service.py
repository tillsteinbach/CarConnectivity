"""Module containing the OSM location service class that implements conenction to Open Street Map"""
from __future__ import annotations
from typing import TYPE_CHECKING

import logging
import requests
from requests.adapters import HTTPAdapter, Retry

from carconnectivity.errors import RetrievalError
from carconnectivity._version import __version__

from carconnectivity_services.base.location_service import BaseLocationService

if TYPE_CHECKING:
    from typing import Dict, Any, Union

    from carconnectivity.carconnectivity import CarConnectivity


class OSMLocationService(BaseLocationService):  # pylint: disable=too-few-public-methods
    """OSMLocationService is a class for retrieveing location data from Open Street Map.
    """
    def __init__(self, service_id: str, car_connectivity: CarConnectivity, config: Dict, log: logging.Logger) -> None:
        """
        Initializes the service with the given CarConnectivity instance and configuration.

        Args:
            car_connectivity (CarConnectivity): The instance in which the service is running.
            config (Dict): A dictionary containing the configuration parameters for this service only.
        """
        super().__init__(service_id=service_id, car_connectivity=car_connectivity, config=config, log=log)
        self.osm_session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500], raise_on_status=False)
        self.osm_session.mount('https://', HTTPAdapter(max_retries=retries))
        self.osm_session.headers = {
            'User-Agent': 'VWsFriend'
        }

    def get_location_at(self, latitude: float, longitude: float) -> Any:
        """
        Returns the location at the given latitude and longitude.

        Args:
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.

        Returns:
            str: The location at the given latitude and longitude.
        """
        query: Dict[str, Union[float, int, str]] = {
            'lat': latitude,
            'lon': longitude,
            'namedetails': 1,
            'format': 'json'
        }
        try:
            response = self.osm_session.get('https://nominatim.openstreetmap.org/reverse', params=query)
            if response.status_code == requests.codes['ok']:
                print(response.json())
        except requests.exceptions.RetryError as retry_error:
            raise RetrievalError(f"Error retrieving location data: {retry_error}") from retry_error
        return None

    def get_version(self) -> str:
        """
        Returns the version of the service.

        Returns:
            str: The version of the service.
        """
        return __version__

    def get_type(self) -> str:
        """
        Returns the type of the service.

        Returns:
            str: The type of the service.
        """
        return "osm-location"
