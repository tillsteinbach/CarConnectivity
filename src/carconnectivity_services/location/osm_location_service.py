"""Module containing the OpenStreetMap location service."""
# pylint: disable=duplicate-code
from __future__ import annotations
from typing import TYPE_CHECKING

import json
import time
from datetime import datetime, timezone, timedelta

import requests
from requests.adapters import HTTPAdapter, Retry

from haversine import haversine, Unit, inverse_haversine, Direction

from carconnectivity_services.base.service import ServiceType
from carconnectivity_services.location.location_service import LocationService
from carconnectivity.location import Location
from carconnectivity.charging_station import ChargingStation
from carconnectivity.units import LatitudeLongitude

if TYPE_CHECKING:
    from typing import Optional

    import logging

    from carconnectivity.carconnectivity import CarConnectivity

REQUEST_HEADERS: dict[str, str] = {
    'User-Agent': 'CarConnectivity'
}


class OSMLocationService(LocationService):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    OpenStreetMap (OSM) based location service implementation.
    This service provides location-related functionality using the OpenStreetMap Nominatim API,
    including reverse geocoding, gas station lookup, and charging station lookup.
    The service implements rate limiting to comply with Nominatim's usage policy of maximum
    1 request per second.
    Attributes:
        osm_session (requests.Session): HTTP session for making requests to OSM Nominatim API.
        _last_request (datetime): Timestamp of the last API request to enforce rate limiting.
    Methods:
        get_types: Returns list of service types provided by this service.
        location_from_lat_lon: Performs reverse geocoding to get location details from coordinates.
        gas_station_from_lat_lon: Finds the nearest gas station within specified radius.
        charging_station_from_lat_lon: Finds the nearest charging station within specified radius.
        amenity_from_lat_lon: Generic method to find nearest amenity of specified type.
        _response_to_location: Converts OSM Nominatim JSON response to Location object.
    Note:
        This service respects OpenStreetMap's Nominatim usage policy by enforcing a minimum
        1-second delay between consecutive requests.
    """

    def __init__(self, service_id: str, car_connectivity: CarConnectivity, log: logging.Logger) -> None:
        super().__init__(service_id, car_connectivity, log)

        self.osm_session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.1, status_forcelist=[500], raise_on_status=False)
        self.osm_session.mount('https://', HTTPAdapter(max_retries=retries))
        self.osm_session.headers.update(REQUEST_HEADERS)
        self._last_request: datetime = datetime.now(timezone.utc) - timedelta(seconds=1)

    def get_types(self) -> list[ServiceType]:
        return [ServiceType.LOCATION_REVERSE, ServiceType.LOCATION_GAS_STATION, ServiceType.LOCATION_CHARGING_STATION]

    def location_from_lat_lon(self, latitude: float, longitude: float, location: Optional[Location]) -> Optional[Location]:
        query: dict[str, float | int | str] = {
            'lat': latitude,
            'lon': longitude,
            'namedetails': 1,
            'format': 'json'
        }
        try:
            if (datetime.now(timezone.utc) - self._last_request).total_seconds() < 1:
                # Nominatim usage policy: at most 1 request per second
                wait_time: float = 1.0 - (datetime.now(timezone.utc) - self._last_request).total_seconds()
                self.log.debug('Waiting %.2f seconds to comply with Nominatim usage policy', wait_time)
                time.sleep(wait_time)
            response: requests.Response = self.osm_session.get('https://nominatim.openstreetmap.org/reverse', params=query)
            self._last_request: datetime = datetime.now(timezone.utc)
            if response.status_code == requests.codes['ok']:
                return self._response_to_location(json_dict=response.json(), location=location)
        except requests.exceptions.RetryError as retry_error:
            self.log.error('Could not retrieve location: %s', retry_error)
        return None

    def gas_station_from_lat_lon(self, latitude: float, longitude: float, radius: int, location: Optional[Location] = None) -> Optional[Location]:
        """
        Find the nearest gas station from given coordinates.
        Args:
            latitude (float): The latitude coordinate to search from.
            longitude (float): The longitude coordinate to search from.
            radius (int): The search radius in meters.
            location (Optional[Location], optional): An existing Location object to update. Defaults to None.
        Returns:
            Optional[Location]: A Location object containing gas station information if found, None otherwise.
        """

        return self.amenity_from_lat_lon(latitude=latitude, longitude=longitude, radius=radius, amenity='fuel', location=location)

    def charging_station_from_lat_lon(self, latitude: float, longitude: float, radius: int,  # pylint: disable=too-many-branches,too-many-statements
                                      charging_station: Optional[ChargingStation] = None) -> Optional[ChargingStation]:
        """
        Retrieve charging station information from OpenStreetMap based on coordinates.
        Args:
            latitude (float): The latitude coordinate of the location to search.
            longitude (float): The longitude coordinate of the location to search.
            radius (int): The search radius in meters around the specified coordinates.
            location (Optional[Location], optional): An existing Location object to populate with
                charging station data. If None, a new Location object will be created. Defaults to None.
        Returns:
            Optional[Location]: A Location object containing charging station information if found,
                None otherwise.
        """
        amenity_dict: Optional[dict] = self._amenity_json_from_lat_lon(latitude, longitude, radius, 'charging_station')
        if amenity_dict is not None:  # pylint: disable=too-many-nested-blocks
            if 'osm_id' in amenity_dict and amenity_dict['osm_id'] is not None:
                if charging_station is None:
                    charging_station = ChargingStation(name=str(amenity_dict['osm_id']), parent=None)
                charging_station.uid._set_value(value=str(amenity_dict['osm_id']))  # pylint: disable=protected-access
                charging_station.source._set_value(value='OpenStreetMap')  # pylint: disable=protected-access
                if 'osm_type' in amenity_dict and amenity_dict['osm_type'] is not None:
                    pass  # Currently not used, but could be stored if needed
                if 'name' in amenity_dict and amenity_dict['name'] is not None and amenity_dict['name'] != '':
                    charging_station.name._set_value(value=amenity_dict['name'])  # pylint: disable=protected-access
                elif 'display_name' in amenity_dict and amenity_dict['display_name'] is not None and amenity_dict['display_name'] != '':
                    charging_station.name._set_value(value=amenity_dict['display_name'])  # pylint: disable=protected-access
                else:
                    charging_station.name._set_value(None)  # pylint: disable=protected-access
                if 'lat' in amenity_dict and amenity_dict['lat'] is not None:
                    charging_station.latitude._set_value(value=amenity_dict['lat'], unit=LatitudeLongitude.DEGREE)  # pylint: disable=protected-access
                else:
                    charging_station.latitude._set_value(None)  # pylint: disable=protected-access
                if 'lon' in amenity_dict and amenity_dict['lon'] is not None:
                    charging_station.longitude._set_value(value=amenity_dict['lon'], unit=LatitudeLongitude.DEGREE)  # pylint: disable=protected-access
                else:
                    charging_station.longitude._set_value(None)  # pylint: disable=protected-access
                if 'display_name' in amenity_dict and amenity_dict['display_name'] is not None and amenity_dict['display_name'] != '':
                    charging_station.address._set_value(value=amenity_dict['display_name'])  # pylint: disable=protected-access
                else:
                    charging_station.address._set_value(None)  # pylint: disable=protected-access
                if 'extratags' in amenity_dict and amenity_dict['extratags'] is not None:
                    if 'capacity' in amenity_dict['extratags'] and amenity_dict['extratags']['capacity'] is not None:
                        try:
                            charging_station.num_spots._set_value(value=int(amenity_dict['extratags']['capacity']))  # pylint: disable=protected-access
                        except ValueError:
                            charging_station.num_spots._set_value(None)  # pylint: disable=protected-access
                    else:
                        charging_station.num_spots._set_value(None)  # pylint: disable=protected-access
                    maximum_power: float = 0
                    for key, value in amenity_dict['extratags'].items():
                        if key.startswith('socket:') and key.endswith(':output'):
                            for splitted_value in value.split(';'):
                                power: float = float(''.join(filter(str.isdigit, splitted_value)))
                                maximum_power = max(maximum_power, power)
                    if maximum_power == 0 and 'amperage' in amenity_dict['extratags'] and amenity_dict['extratags']['amperage'] is not None:
                        try:
                            amperage: float = float(amenity_dict['extratags']['amperage'])
                            voltage: float = 230.0  # Default voltage
                            maximum_power: float = (amperage * voltage * 3) / 1000.0
                            charging_station.max_power._set_value(value=maximum_power)  # pylint: disable=protected-access
                        except ValueError:
                            maximum_power = 0
                    if maximum_power != 0:
                        charging_station.max_power._set_value(value=maximum_power)  # pylint: disable=protected-access
                    else:
                        charging_station.max_power._set_value(None)  # pylint: disable=protected-access
                    if 'operator' in amenity_dict['extratags'] and amenity_dict['extratags']['operator'] is not None \
                            and amenity_dict['extratags']['operator'] != '':
                        charging_station.operator_name._set_value(value=amenity_dict['extratags']['operator'])  # pylint: disable=protected-access
                        charging_station.operator_id._set_value(value=amenity_dict['extratags']['operator'])  # pylint: disable=protected-access
                    else:
                        charging_station.operator_name._set_value(None)  # pylint: disable=protected-access
                        charging_station.operator_id._set_value(None)  # pylint: disable=protected-access
                else:
                    charging_station.num_spots._set_value(None)  # pylint: disable=protected-access
                    charging_station.max_power._set_value(None)  # pylint: disable=protected-access
                    charging_station.operator_name._set_value(None)  # pylint: disable=protected-access
                    charging_station.operator_id._set_value(None)  # pylint: disable=protected-access
                charging_station.raw._set_value(value=json.dumps(amenity_dict))  # pylint: disable=protected-access
                return charging_station
            if charging_station is not None:
                charging_station.clear()
        return None

    # pylint: disable-next=too-many-locals,too-many-arguments,too-many-positional-arguments
    def amenity_from_lat_lon(self, latitude: float, longitude: float, radius: int, amenity: str, with_fallback: bool = False,
                             location: Optional[Location] = None) -> Optional[Location]:
        """
        Find the nearest amenity of a specific type within a given radius from coordinates.
        This method searches for amenities (e.g., charging stations, parking, etc.) within a specified
        radius from the given latitude and longitude coordinates using OpenStreetMap's Nominatim API.
        It respects Nominatim's usage policy by ensuring at least 1 second between requests.
        Args:
            latitude (float): The latitude coordinate of the center point.
            longitude (float): The longitude coordinate of the center point.
            radius (int): The search radius in meters from the center point.
            amenity (str): The type of amenity to search for (e.g., 'charging_station', 'parking').
            with_fallback (bool, optional): If True, falls back to general location lookup when no
                amenity is found within the radius. Defaults to False.
            location (Optional[Location], optional): An existing Location object to update with the
                amenity information. Defaults to None.
        Returns:
            Optional[Location]: A Location object representing the nearest amenity within the radius,
                or None if no amenity is found. If with_fallback is True and no amenity is found,
                returns the general location information for the coordinates.
        Raises:
            requests.exceptions.RetryError: Logged as an error if the API request fails after retries.
        Note:
            This method automatically enforces a minimum 1-second delay between consecutive requests
            to comply with Nominatim's usage policy.
        """
        amenity_json: Optional[dict] = self._amenity_json_from_lat_lon(latitude, longitude, radius, amenity)
        if amenity_json is not None:
            return self._response_to_location(json_dict=amenity_json, location=location)
        if with_fallback:
            return self.location_from_lat_lon(latitude, longitude, location)
        return None

    def _amenity_json_from_lat_lon(self, latitude: float, longitude: float, radius: int, amenity: str) -> Optional[dict]:
        """
        Find the nearest amenity of a specific type within a given radius from coordinates.
        This method searches for amenities (e.g., charging stations, parking, etc.) within a specified
        radius from the given latitude and longitude coordinates using OpenStreetMap's Nominatim API.
        It respects Nominatim's usage policy by ensuring at least 1 second between requests.
        Args:
            latitude (float): The latitude coordinate of the center point.
            longitude (float): The longitude coordinate of the center point.
            radius (int): The search radius in meters from the center point.
            amenity (str): The type of amenity to search for (e.g., 'charging_station', 'parking').
            with_fallback (bool, optional): If True, falls back to general location lookup when no
                amenity is found within the radius. Defaults to False.
            location (Optional[Location], optional): An existing Location object to update with the
                amenity information. Defaults to None.
        Returns:
            Optional[Location]: A Location object representing the nearest amenity within the radius,
                or None if no amenity is found. If with_fallback is True and no amenity is found,
                returns the general location information for the coordinates.
        Raises:
            requests.exceptions.RetryError: Logged as an error if the API request fails after retries.
        Note:
            This method automatically enforces a minimum 1-second delay between consecutive requests
            to comply with Nominatim's usage policy.
        """
        north_west: tuple[float, float] = inverse_haversine((latitude, longitude), radius, Direction.NORTHWEST, unit=Unit.METERS)
        south_east: tuple[float, float] = inverse_haversine((latitude, longitude), radius, Direction.SOUTHEAST, unit=Unit.METERS)
        query: dict[str, float | int | str] = {
            'q': f'[{amenity}]',
            'viewbox': f'{north_west[1]},{north_west[0]},{south_east[1]},{south_east[0]}',
            'bounded': 1,
            'namedetails': 1,
            'addressdetails': 1,
            'extratags': 1,
            'format': 'json'
        }

        try:
            if (datetime.now(timezone.utc) - self._last_request).total_seconds() < 1:
                # Nominatim usage policy: at most 1 request per second
                wait_time: float = 1.0 - (datetime.now(timezone.utc) - self._last_request).total_seconds()
                self.log.debug('Waiting %.2f seconds to comply with Nominatim usage policy', wait_time)
                time.sleep(wait_time)
            response: requests.Response = self.osm_session.get('https://nominatim.openstreetmap.org/search', params=query)
            self._last_request: datetime = datetime.now(timezone.utc)
            if response.status_code == requests.codes['ok']:
                places: list[dict] = response.json()
                places_distance: list[tuple[float, dict]] = [(haversine((latitude, longitude), (float(place['lat']), float(place['lon'])),
                                                                        unit=Unit.METERS), place)
                                                             for place in places if 'lat' in place and 'lon' in place]
                places_distance = sorted(places_distance, key=lambda geofence: geofence[0])
                for distance, place in places_distance:
                    if distance < radius:
                        return place
        except requests.exceptions.RetryError as retry_error:
            self.log.error('Could not retrieve location: %s', retry_error)
        return None

    # pylint: disable-next=too-many-statements
    def _response_to_location(self, json_dict: dict, location: Optional[Location] = None) -> Optional[Location]:  # pylint: disable=too-many-branches
        """Convert a JSON response to a Location object."""
        if json_dict is not None:
            if 'osm_id' in json_dict and json_dict['osm_id'] is not None:
                if location is None:
                    location = Location(name=str(json_dict['osm_id']), parent=None)
                location.uid._set_value(value=str(json_dict['osm_id']))  # pylint: disable=protected-access
                location.source._set_value(value='OpenStreetMap')  # pylint: disable=protected-access
                if 'osm_type' in json_dict and json_dict['osm_type'] is not None:
                    pass  # Currently not used, but could be stored if needed
                if 'lat' in json_dict and json_dict['lat'] is not None:
                    location.latitude._set_value(value=json_dict['lat'], unit=LatitudeLongitude.DEGREE)  # pylint: disable=protected-access
                else:
                    location.latitude._set_value(None)  # pylint: disable=protected-access
                if 'lon' in json_dict and json_dict['lon'] is not None:
                    location.longitude._set_value(value=json_dict['lon'], unit=LatitudeLongitude.DEGREE)  # pylint: disable=protected-access
                else:
                    location.longitude._set_value(None)  # pylint: disable=protected-access
                if 'display_name' in json_dict and json_dict['display_name'] is not None and json_dict['display_name'] != '':
                    location.display_name._set_value(value=json_dict['display_name'])  # pylint: disable=protected-access
                else:
                    location.display_name._set_value(None)  # pylint: disable=protected-access
                if 'address' in json_dict and json_dict['address'] is not None:
                    address = json_dict['address']
                    if 'amenity' in address and address['amenity'] is not None:
                        location.amenity._set_value(value=address['amenity'])  # pylint: disable=protected-access
                    else:
                        location.amenity._set_value(None)  # pylint: disable=protected-access
                    value_found: bool = False
                    for attribute in ['house_number', 'street_number']:
                        if attribute in address and address[attribute] is not None:
                            location.house_number._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.house_number._set_value(None)  # pylint: disable=protected-access
                    value_found = False
                    for attribute in ['road', 'footway', 'street', 'street_name', 'residential', 'path', 'pedestrian', 'road_reference',
                                      'road_reference_intl', 'square', 'place']:
                        if attribute in address and address[attribute] is not None:
                            location.road._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.road._set_value(None)  # pylint: disable=protected-access
                    value_found = False
                    for attribute in ['neighbourhood', 'suburb', 'city_district', 'district', 'quarter', 'borough', 'city_block', 'residential',
                                      'commercial', 'industrial', 'houses', 'subdistrict', 'subdivision', 'ward']:
                        if attribute in address and address[attribute] is not None:
                            location.neighbourhood._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.neighbourhood._set_value(None)  # pylint: disable=protected-access
                    value_found = False
                    for attribute in ['city', 'town', 'township']:
                        if attribute in address and address[attribute] is not None:
                            location.city._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.city._set_value(None)  # pylint: disable=protected-access
                    value_found = False
                    for attribute in ['postcode', 'partial_postcode']:
                        if attribute in address and address[attribute] is not None:
                            location.postcode._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.postcode._set_value(None)  # pylint: disable=protected-access
                    value_found = False
                    for attribute in ['county', 'county_code', 'department']:
                        if attribute in address and address[attribute] is not None:
                            location.county._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.county._set_value(None)  # pylint: disable=protected-access
                    value_found = False
                    for attribute in ['country', 'country_name']:
                        if attribute in address and address[attribute] is not None:
                            location.country._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.country._set_value(None)  # pylint: disable=protected-access
                    value_found = False
                    for attribute in ['state', 'province', 'state_code']:
                        if attribute in address and address[attribute] is not None:
                            location.state._set_value(value=address[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                    if not value_found:
                        location.state._set_value(None)  # pylint: disable=protected-access
                else:
                    location.amenity._set_value(None)  # pylint: disable=protected-access
                    location.house_number._set_value(None)  # pylint: disable=protected-access
                    location.road._set_value(None)  # pylint: disable=protected-access
                    location.neighbourhood._set_value(None)  # pylint: disable=protected-access
                    location.city._set_value(None)  # pylint: disable=protected-access
                    location.postcode._set_value(None)  # pylint: disable=protected-access
                    location.county._set_value(None)  # pylint: disable=protected-access
                    location.country._set_value(None)  # pylint: disable=protected-access
                    location.state._set_value(None)  # pylint: disable=protected-access
                if 'state_district' in json_dict and json_dict['state_district'] is not None:
                    location.state_district._set_value(value=json_dict['state_district'])  # pylint: disable=protected-access
                else:
                    location.state_district._set_value(None)  # pylint: disable=protected-access
                value_found: bool = False
                if 'namedetails' in json_dict and json_dict['namedetails'] is not None:
                    namedetails = json_dict['namedetails']
                    for attribute in ['name', 'alt_name']:
                        if attribute in namedetails and namedetails[attribute] is not None:
                            location.name._set_value(value=namedetails[attribute])  # pylint: disable=protected-access
                            value_found = True
                            break
                if not value_found:
                    location.name._set_value(None)  # pylint: disable=protected-access
                location.raw._set_value(value=json.dumps(json_dict))  # pylint: disable=protected-access
                return location
        return None
