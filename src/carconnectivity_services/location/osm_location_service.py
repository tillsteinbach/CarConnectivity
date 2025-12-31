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
from carconnectivity.units import LatitudeLongitude

if TYPE_CHECKING:
    from typing import Optional

    import logging

    from carconnectivity.carconnectivity import CarConnectivity

REQUEST_HEADERS: dict[str, str] = {
    'User-Agent': 'CarConnectivity'
}


class OSMLocationService(LocationService):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
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
        return self.amenity_from_lat_lon(latitude=latitude, longitude=longitude, radius=radius, amenity='fuel', location=location)

    def charging_station_from_lat_lon(self, latitude: float, longitude: float, radius: int, location: Optional[Location] = None) -> Optional[Location]:
        return self.amenity_from_lat_lon(latitude=latitude, longitude=longitude, radius=radius, amenity='charging_station', location=location)

    def amenity_from_lat_lon(self, latitude: float, longitude: float, radius: int, amenity: str, with_fallback: bool = False,
                             location: Optional[Location] = None) -> Optional[Location]:
        north_west: tuple[float, float] = inverse_haversine((latitude, longitude), radius, Direction.NORTHWEST, unit=Unit.METERS)
        south_east: tuple[float, float] = inverse_haversine((latitude, longitude), radius, Direction.SOUTHEAST, unit=Unit.METERS)
        query: dict[str, float | int | str] = {
            'q': f'[{amenity}]',
            'viewbox': f'{north_west[1]},{north_west[0]},{south_east[1]},{south_east[0]}',
            'bounded': 1,
            'namedetails': 1,
            'addressdetails': 1,
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
                        return self._response_to_location(json_dict=place, location=location)
            if with_fallback:
                return self.location_from_lat_lon(latitude, longitude, location)
        except requests.exceptions.RetryError as retry_error:
            self.log.error('Could not retrieve location: %s', retry_error)
        return None

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
                if 'display_name' in json_dict and json_dict['display_name'] is not None:
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
