""" Module defining the Location data class for geographical locations."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject
from carconnectivity.attributes import StringAttribute, FloatAttribute
from carconnectivity.units import LatitudeLongitude

if TYPE_CHECKING:
    from typing import Optional


class Location(GenericObject):  # pylint: disable=too-few-public-methods
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
    def __init__(self, name: str, parent: Optional[GenericObject]) -> None:
        super().__init__(object_id=name, parent=parent)

        self.source: StringAttribute = StringAttribute("source", parent=self, tags={'carconnectivity'})
        self.uid: StringAttribute = StringAttribute("uid", parent=self, tags={'carconnectivity'})
        self.latitude: FloatAttribute = FloatAttribute("latitude", parent=self, minimum=-90, maximum=90, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                       tags={'carconnectivity'})
        self.longitude: FloatAttribute = FloatAttribute("longitude", parent=self, minimum=-180, maximum=180, unit=LatitudeLongitude.DEGREE, precision=0.000001,
                                                        tags={'carconnectivity'})
        self.display_name: StringAttribute = StringAttribute("display_name", parent=self, tags={'carconnectivity'})
        self.name: StringAttribute = StringAttribute("name", parent=self, tags={'carconnectivity'})
        self.amenity: StringAttribute = StringAttribute("amenity", parent=self, tags={'carconnectivity'})
        self.house_number: StringAttribute = StringAttribute("house_number", parent=self, tags={'carconnectivity'})
        self.road: StringAttribute = StringAttribute("road", parent=self, tags={'carconnectivity'})
        self.neighbourhood: StringAttribute = StringAttribute("neighbourhood", parent=self, tags={'carconnectivity'})
        self.city: StringAttribute = StringAttribute("city", parent=self, tags={'carconnectivity'})
        self.postcode: StringAttribute = StringAttribute("postcode", parent=self, tags={'carconnectivity'})
        self.county: StringAttribute = StringAttribute("county", parent=self, tags={'carconnectivity'})
        self.country: StringAttribute = StringAttribute("country", parent=self, tags={'carconnectivity'})
        self.state: StringAttribute = StringAttribute("state", parent=self, tags={'carconnectivity'})
        self.state_district: StringAttribute = StringAttribute("state_district", parent=self, tags={'carconnectivity'})
        self.raw: StringAttribute = StringAttribute("raw", parent=self, tags={'carconnectivity'})

    def clear(self) -> None:
        """
        Clears all location data attributes.
        """

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
