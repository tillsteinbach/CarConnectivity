""" Module defining the Location data class for geographical locations."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, FloatAttribute
from carconnectivity.units import LatitudeLongitude

if TYPE_CHECKING:
    from typing import Optional, Dict


class Location(GenericObject):  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """
    Represents a geographical location with various address components.
    This class stores location data including coordinates, address details, and
    metadata. It serves as a data container for location information retrieved
    from various services.
    Args:
        uid (str): Unique identifier for the location.
    Attributes:
        source (LocationService): The service that provided the location data.
        uid (str): Unique identifier for the location.
        latitude (Optional[float]): Latitude coordinate of the location.
        longitude (Optional[float]): Longitude coordinate of the location.
        display_name (Optional[str]): Full formatted address string.
        name (Optional[str]): Name of the location or place.
        amenity (Optional[str]): Type of amenity (e.g., restaurant, parking).
        house_number (Optional[str]): Street number of the address.
        road (Optional[str]): Street or road name.
        neighbourhood (Optional[str]): Neighbourhood name.
        city (Optional[str]): City name.
        postcode (Optional[str]): Postal or ZIP code.
        county (Optional[str]): County name.
        country (Optional[str]): Country name.
        state (Optional[str]): State or province name.
        state_district (Optional[str]): State district name.
        raw (Optional[str]): Raw location data from the source service.
    """
    def __init__(self, name: str, parent: Optional[GenericObject], initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id=name, parent=parent, initialization=initialization)

        self.source: StringAttribute = StringAttribute("source", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('source'))
        self.uid: StringAttribute = StringAttribute("uid", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('uid'))
        self.latitude: FloatAttribute = FloatAttribute("latitude", parent=self, minimum=-90, maximum=90, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                       tags={'carconnectivity'}, initialization=self.get_initialization('latitude'))
        self.longitude: FloatAttribute = FloatAttribute("longitude", parent=self, minimum=-180, maximum=180, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                        tags={'carconnectivity'}, initialization=self.get_initialization('longitude'))
        self.display_name: StringAttribute = StringAttribute("display_name", parent=self, tags={'carconnectivity'},
                                                             initialization=self.get_initialization('display_name'))
        self.name: StringAttribute = StringAttribute("name", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('name'))
        self.amenity: StringAttribute = StringAttribute("amenity", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('amenity'))
        self.house_number: StringAttribute = StringAttribute("house_number", parent=self, tags={'carconnectivity'},
                                                             initialization=self.get_initialization('house_number'))
        self.road: StringAttribute = StringAttribute("road", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('road'))
        self.neighbourhood: StringAttribute = StringAttribute("neighbourhood", parent=self, tags={'carconnectivity'},
                                                              initialization=self.get_initialization('neighbourhood'))
        self.city: StringAttribute = StringAttribute("city", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('city'))
        self.postcode: StringAttribute = StringAttribute("postcode", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('postcode'))
        self.county: StringAttribute = StringAttribute("county", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('county'))
        self.country: StringAttribute = StringAttribute("country", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('country'))
        self.state: StringAttribute = StringAttribute("state", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('state'))
        self.state_district: StringAttribute = StringAttribute("state_district", parent=self, tags={'carconnectivity'},
                                                               initialization=self.get_initialization('state_district'))
        self.raw: StringAttribute = StringAttribute("raw", parent=self, tags={'carconnectivity'}, initialization=self.get_initialization('raw'))

    def clear(self) -> None:
        """
        Clears all location data attributes.
        """
        self.source._set_value(None)  # pylint: disable=protected-access
        self.uid._set_value(None)  # pylint: disable=protected-access
        self.latitude._set_value(None)  # pylint: disable=protected-access
        self.longitude._set_value(None)  # pylint: disable=protected-access
        self.display_name._set_value(None)  # pylint: disable=protected-access
        self.name._set_value(None)  # pylint: disable=protected-access
        self.amenity._set_value(None)  # pylint: disable=protected-access
        self.house_number._set_value(None)  # pylint: disable=protected-access
        self.road._set_value(None)  # pylint: disable=protected-access
        self.neighbourhood._set_value(None)  # pylint: disable=protected-access
        self.city._set_value(None)  # pylint: disable=protected-access
        self.postcode._set_value(None)  # pylint: disable=protected-access
        self.county._set_value(None)  # pylint: disable=protected-access
        self.country._set_value(None)  # pylint: disable=protected-access
        self.state._set_value(None)  # pylint: disable=protected-access
        self.state_district._set_value(None)  # pylint: disable=protected-access
        self.raw._set_value(None)  # pylint: disable=protected-access
