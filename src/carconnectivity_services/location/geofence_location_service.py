"""Module containing the OpenStreetMap location service."""
# pylint: disable=duplicate-code
from __future__ import annotations
from typing import TYPE_CHECKING

import json

from haversine import haversine, Unit

from carconnectivity_services.base.service import ServiceType
from carconnectivity_services.location.location_service import LocationService
from carconnectivity.location import Location
from carconnectivity.charging_station import ChargingStation
from carconnectivity.errors import ConfigurationError

if TYPE_CHECKING:
    from typing import Optional

    import logging

    from carconnectivity.carconnectivity import CarConnectivity


class GeofenceLocationService(LocationService):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    A location service that uses geofences to provide location and charging station information.
    This service allows users to define geographic boundaries (geofences) in the configuration,
    and provides location and charging station data when coordinates fall within these boundaries.
    When multiple geofences match, the closest one is selected.
    Configuration:
        Geofences are configured in the 'carConnectivity.geofences' section of the configuration.
        Each geofence requires:
        - name: Identifier for the geofence
        - latitude: Center latitude coordinate
        - longitude: Center longitude coordinate
        - radius: (optional) Radius in meters, defaults to 50.0
        - location: (optional) Location details to return when within the geofence
        - charging_station: (optional) Charging station details to return when within the geofence
    Attributes:
        geofences (list[Geofence]): List of configured geofence objects
    Methods:
        get_types: Returns supported service types (location reverse lookup and charging station lookup)
        location_from_lat_lon: Returns location information if coordinates fall within a geofence
        charging_station_from_lat_lon: Returns charging station information if coordinates fall within a geofence
    Raises:
        ConfigurationError: If a geofence is missing required fields (name, latitude, or longitude)
    """
    # pylint: disable-next=too-many-branches, too-many-statements
    def __init__(self, service_id: str, car_connectivity: CarConnectivity, log: logging.Logger) -> None:
        super().__init__(service_id, car_connectivity, log)
        self.geofences: list[Geofence] = []
        if 'carConnectivity' in car_connectivity.config and 'geofences' in car_connectivity.config['carConnectivity']:
            for geofence in car_connectivity.config['carConnectivity']['geofences']:
                if 'name' in geofence and 'latitude' in geofence and 'longitude' in geofence:
                    name: str = geofence['name']
                    latitude: float = float(geofence['latitude'])
                    longitude: float = float(geofence['longitude'])
                    radius: float = 50.0
                    if 'radius' in geofence:
                        radius = float(geofence['radius'])
                    location: Optional[Location] = None
                    if 'location' in geofence:
                        location_data = geofence['location']
                        display_string: str = ''
                        if 'name' in location_data:
                            location = Location(name=location_data['name'], parent=None)
                            location.name._set_value(location_data['name'])  # pylint: disable=protected-access
                            display_string = location_data['name']
                        else:
                            location = Location(name=name, parent=None)
                            location.name._set_value(name)  # pylint: disable=protected-access
                            display_string = name
                        if 'source' in location_data:
                            location.source._set_value(location_data['source'])  # pylint: disable=protected-access
                        else:
                            location.source._set_value('geofence')  # pylint: disable=protected-access
                        if 'uid' in location_data:
                            location.uid._set_value(location_data['uid'])  # pylint: disable=protected-access
                        else:
                            location.uid._set_value(f'geofence-{name}')  # pylint: disable=protected-access
                        if 'latitude' in location_data:
                            location.latitude._set_value(float(location_data['latitude']))  # pylint: disable=protected-access
                        else:
                            location.latitude._set_value(latitude)  # pylint: disable=protected-access
                        if 'longitude' in location_data:
                            location.longitude._set_value(float(location_data['longitude']))  # pylint: disable=protected-access
                        else:
                            location.longitude._set_value(longitude)  # pylint: disable=protected-access
                        if 'amenity' in location_data:
                            location.amenity._set_value(location_data['amenity'])  # pylint: disable=protected-access
                            display_string += f", {location_data['amenity']}"
                        if 'house_number' in location_data:
                            location.house_number._set_value(location_data['house_number'])  # pylint: disable=protected-access
                            display_string += f", {location_data['house_number']}"
                        if 'road' in location_data:
                            location.road._set_value(location_data['road'])  # pylint: disable=protected-access
                            display_string += f", {location_data['road']}"
                        if 'neighbourhood' in location_data:
                            location.neighbourhood._set_value(location_data['neighbourhood'])  # pylint: disable=protected-access
                            display_string += f", {location_data['neighbourhood']}"
                        if 'city' in location_data:
                            location.city._set_value(location_data['city'])  # pylint: disable=protected-access
                            display_string += f", {location_data['city']}"
                        if 'postcode' in location_data:
                            location.postcode._set_value(location_data['postcode'])  # pylint: disable=protected-access
                            display_string += f", {location_data['postcode']}"
                        if 'county' in location_data:
                            location.county._set_value(location_data['county'])  # pylint: disable=protected-access
                            display_string += f", {location_data['county']}"
                        if 'country' in location_data:
                            location.country._set_value(location_data['country'])  # pylint: disable=protected-access
                        if 'state' in location_data:
                            location.state._set_value(location_data['state'])  # pylint: disable=protected-access
                        if 'state_district' in location_data:
                            location.state_district._set_value(location_data['state_district'])  # pylint: disable=protected-access
                        if 'display_name' in location_data:
                            location.display_name._set_value(location_data['display_name'])  # pylint: disable=protected-access
                        else:
                            location.display_name._set_value(display_string)  # pylint: disable=protected-access
                        location.raw._set_value(json.dumps(location_data))  # pylint: disable=protected-access
                    charging_station: Optional[ChargingStation] = None
                    if 'charging_station' in geofence:
                        cs_data = geofence['charging_station']
                        if 'name' in cs_data:
                            charging_station = ChargingStation(name=cs_data['name'], parent=None)
                            charging_station.name._set_value(cs_data['name'])  # pylint: disable=protected-access
                        else:
                            charging_station = ChargingStation(name=name, parent=None)
                            charging_station.name._set_value(name)  # pylint: disable=protected-access
                        if 'source' in cs_data:
                            charging_station.source._set_value(cs_data['source'])  # pylint: disable=protected-access
                        else:
                            charging_station.source._set_value('geofence')  # pylint: disable=protected-access
                        if 'uid' in cs_data:
                            charging_station.uid._set_value(cs_data['uid'])  # pylint: disable=protected-access
                        else:
                            charging_station.uid._set_value(f'geofence-cs-{name}')  # pylint: disable=protected-access
                        if 'latitude' in cs_data:
                            charging_station.latitude._set_value(float(cs_data['latitude']))  # pylint: disable=protected-access
                        else:
                            charging_station.latitude._set_value(latitude)  # pylint: disable=protected-access
                        if 'longitude' in cs_data:
                            charging_station.longitude._set_value(float(cs_data['longitude']))  # pylint: disable=protected-access
                        else:
                            charging_station.longitude._set_value(longitude)  # pylint: disable=protected-access
                        if 'address' in cs_data:
                            charging_station.address._set_value(cs_data['address'])  # pylint: disable=protected-access
                        if 'max_power' in cs_data:
                            charging_station.max_power._set_value(float(cs_data.get('max_power', 0.0)))  # pylint: disable=protected-access
                        if 'num_spots' in cs_data:
                            charging_station.num_spots._set_value(int(cs_data.get('num_spots', 0)))  # pylint: disable=protected-access
                        if 'operator_id' in cs_data:
                            charging_station.operator_id._set_value(cs_data.get('operator_id', ''))  # pylint: disable=protected-access
                        if 'operator_name' in cs_data:
                            charging_station.operator_name._set_value(cs_data.get('operator_name', ''))  # pylint: disable=protected-access
                    self.geofences.append(Geofence(name=name, latitude=latitude, longitude=longitude,
                                                   radius=radius, location=location,
                                                   charging_station=charging_station))
                else:
                    raise ConfigurationError("Geofence must have at least 'name', 'latitude', and 'longitude' fields")
        log.info(f"GeofenceLocationService initialized with {len(self.geofences)} geofences")

    def get_types(self) -> list[tuple[ServiceType, int]]:
        return [(ServiceType.LOCATION_REVERSE, 10), (ServiceType.LOCATION_CHARGING_STATION, 10)]

    def location_from_lat_lon(self, latitude: float, longitude: float, location: Optional[Location]) -> Optional[Location]:
        found_location: Optional[Location] = None
        distance: Optional[float] = None
        for geofence in self.geofences:
            if geofence.location is not None:
                distance_to_geofence = haversine((latitude, longitude), (geofence.latitude, geofence.longitude), unit=Unit.METERS)
                if distance_to_geofence <= geofence.radius:
                    self.log.debug(f"Geofence '{geofence.name}' matched for location ({latitude}, {longitude}) within radius {geofence.radius}m")
                    if distance is None or distance_to_geofence < distance:
                        distance = distance_to_geofence
                        found_location = geofence.location
        if location is None:
            return found_location
        if found_location is not None:
            location.source._set_value(found_location.source.value)  # pylint: disable=protected-access
            location.uid._set_value(found_location.uid.value)  # pylint: disable=protected-access
            location.latitude._set_value(found_location.latitude.value)  # pylint: disable=protected-access
            location.longitude._set_value(found_location.longitude.value)  # pylint: disable=protected-access
            location.display_name._set_value(found_location.display_name.value)  # pylint: disable=protected-access
            location.name._set_value(found_location.name.value)  # pylint: disable=protected-access
            location.amenity._set_value(found_location.amenity.value)  # pylint: disable=protected-access
            location.house_number._set_value(found_location.house_number.value)  # pylint: disable=protected-access
            location.road._set_value(found_location.road.value)  # pylint: disable=protected-access
            location.neighbourhood._set_value(found_location.neighbourhood.value)  # pylint: disable=protected-access
            location.city._set_value(found_location.city.value)  # pylint: disable=protected-access
            location.postcode._set_value(found_location.postcode.value)  # pylint: disable=protected-access
            location.county._set_value(found_location.county.value)  # pylint: disable=protected-access
            location.country._set_value(found_location.country.value)  # pylint: disable=protected-access
            location.state._set_value(found_location.state.value)  # pylint: disable=protected-access
            location.state_district._set_value(found_location.state_district.value)  # pylint: disable=protected-access
            location.raw._set_value(found_location.raw.value)  # pylint: disable=protected-access
            return location
        return None

    def charging_station_from_lat_lon(self, latitude: float, longitude: float, radius: int,  # pylint: disable=too-many-branches,too-many-statements
                                      charging_station: Optional[ChargingStation] = None) -> Optional[ChargingStation]:
        found_charging_station: Optional[ChargingStation] = None
        distance: Optional[float] = None
        for geofence in self.geofences:
            if geofence.charging_station is not None:
                distance_to_geofence = haversine((latitude, longitude), (geofence.latitude, geofence.longitude), unit=Unit.METERS)
                if distance_to_geofence <= geofence.radius:
                    self.log.debug(f"Geofence '{geofence.name}' matched for charging station at ({latitude}, {longitude}) within radius {geofence.radius}m")
                    if distance is None or distance_to_geofence < distance:
                        distance = distance_to_geofence
                        found_charging_station = geofence.charging_station
        if charging_station is None:
            return found_charging_station
        if found_charging_station is not None:
            charging_station.source._set_value(found_charging_station.source.value)  # pylint: disable=protected-access
            charging_station.uid._set_value(found_charging_station.uid.value)  # pylint: disable=protected-access
            charging_station.name._set_value(found_charging_station.name.value)  # pylint: disable=protected-access
            charging_station.latitude._set_value(found_charging_station.latitude.value)  # pylint: disable=protected-access
            charging_station.longitude._set_value(found_charging_station.longitude.value)  # pylint: disable=protected-access
            charging_station.address._set_value(found_charging_station.address.value)  # pylint: disable=protected-access
            charging_station.max_power._set_value(found_charging_station.max_power.value)  # pylint: disable=protected-access
            charging_station.num_spots._set_value(found_charging_station.num_spots.value)  # pylint: disable=protected-access
            charging_station.operator_id._set_value(found_charging_station.operator_id.value)  # pylint: disable=protected-access
            charging_station.operator_name._set_value(found_charging_station.operator_name.value)  # pylint: disable=protected-access
            charging_station.raw._set_value(found_charging_station.raw.value)  # pylint: disable=protected-access
            return charging_station
        return None

    def gas_station_from_lat_lon(self, latitude: float, longitude: float, radius: int, location: Optional[Location]) -> Optional[Location]:
        """
        Retrieve gas station information from latitude and longitude coordinates.
        Args:
            latitude (float): The latitude coordinate of the location.
            longitude (float): The longitude coordinate of the location.
            radius (int): The search radius in meters around the given coordinates.
            location (Optional[Location]): An optional Location object to populate with gas station data.
        Returns:
            Optional[Location]: A Location object containing gas station information if found, None otherwise.
        Raises:
            NotImplementedError: This method is not supported by the current service implementation.
        """
        raise NotImplementedError("Method gas_station_from_lat_lon() not supported by service")


# pylint: disable-next=too-few-public-methods
class Geofence:
    """Class representing a geofence with associated location and charging station data."""
    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(self, name: str, latitude: float, longitude: float, radius: float = 50, location: Optional[Location] = None,
                 charging_station: Optional[ChargingStation] = None) -> None:
        self.name: str = name
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.radius: float = radius
        self.location: Optional[Location] = location
        self.charging_station: Optional[ChargingStation] = charging_station
