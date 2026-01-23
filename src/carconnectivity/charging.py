"""
Module for charging.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import logging
from enum import Enum

from carconnectivity.interfaces import ICarConnectivity, IGenericVehicle
from carconnectivity.observable import Observable
from carconnectivity.objects import GenericObject
from carconnectivity.attributes import DateAttribute, EnumAttribute, SpeedAttribute, PowerAttribute, LevelAttribute, CurrentAttribute, BooleanAttribute
from carconnectivity.charging_connector import ChargingConnector
from carconnectivity.commands import Commands
from carconnectivity.charging_station import ChargingStation

from carconnectivity_services.base.service import BaseService, ServiceType
from carconnectivity_services.location.location_service import LocationService

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.vehicle import ElectricVehicle

LOG: logging.Logger = logging.getLogger("carconnectivity")


class Charging(GenericObject):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent the charging of a vehicle.
    """
    # pylint: disable=duplicate-code
    def __init__(self, vehicle: Optional[ElectricVehicle] = None,  origin: Optional[Charging] = None, initialization: Optional[Dict] = None) -> None:
        if origin is not None:
            super().__init__(parent=vehicle, origin=origin, initialization=initialization)
            self.delay_notifications = True
            self.commands: Commands = origin.commands
            self.commands.parent = self
            self.connector: ChargingConnector = origin.connector
            self.connector.parent = self
            self.state: EnumAttribute[Charging.ChargingState] = origin.state
            self.state.parent = self
            self.type: EnumAttribute[Charging.ChargingType] = origin.type
            self.type.parent = self
            self.rate: SpeedAttribute = origin.rate
            self.rate.parent = self
            self.power: PowerAttribute = origin.power
            self.power.parent = self
            self.estimated_date_reached: DateAttribute = origin.estimated_date_reached
            self.estimated_date_reached.parent = self
            self.settings: Charging.Settings = origin.settings
            self.settings.parent = self
            self.charging_station: ChargingStation = origin.charging_station
            self.charging_station.parent = self
        else:
            if vehicle is None:
                raise ValueError('Cannot create charging without vehicle')
            super().__init__(object_id='charging', parent=vehicle, initialization=initialization)
            self.delay_notifications = True
            self.commands: Commands = Commands(parent=self)
            self.connector: ChargingConnector = ChargingConnector(charging=self)
            self.state: EnumAttribute[Charging.ChargingState] = EnumAttribute("state", parent=self, value_type=Charging.ChargingState,
                                                                              tags={'carconnectivity'}, initialization=self.get_initialization('state'))
            self.type: EnumAttribute[Charging.ChargingType] = EnumAttribute("type", parent=self, value_type=Charging.ChargingType,
                                                                            tags={'carconnectivity'}, initialization=self.get_initialization('type'))
            self.rate: SpeedAttribute = SpeedAttribute("rate", parent=self, precision=0.1, tags={'carconnectivity'},
                                                       initialization=self.get_initialization('rate'))
            self.power: PowerAttribute = PowerAttribute("power", parent=self, precision=0.1, tags={'carconnectivity'},
                                                        initialization=self.get_initialization('power'))
            self.estimated_date_reached: DateAttribute = DateAttribute("estimated_date_reached", parent=self, tags={'carconnectivity'},
                                                                       initialization=self.get_initialization('estimated_date_reached'))
            self.settings: Charging.Settings = Charging.Settings(parent=self, initialization=self.get_initialization('settings'))
            self.charging_station: ChargingStation = ChargingStation(name="charging_station", parent=self,
                                                                     initialization=self.get_initialization('charging_station'))
        self.delay_notifications = False

    # pylint: enable=duplicate-code

        self.state.add_observer(self._on_state_changed, flag=(Observable.ObserverEvent.VALUE_CHANGED
                                                              | Observable.ObserverEvent.ENABLED
                                                              | Observable.ObserverEvent.DISABLED),
                                priority=Observable.ObserverPriority.INTERNAL_HIGH)

    def _on_state_changed(self, element: EnumAttribute[Charging.ChargingState], flags) -> None:
        """
        Callback when position attributes change.
        """
        del flags
        if element.enabled and element.value in [Charging.ChargingState.CHARGING,
                                                 Charging.ChargingState.READY_FOR_CHARGING,
                                                 Charging.ChargingState.CONSERVATION,
                                                 Charging.ChargingState.DISCHARGING]:
            # Get cars location
            # pylint: disable-next=too-many-boolean-expressions
            if self.parent is not None and isinstance(self.parent, IGenericVehicle) and self.parent.position is not None \
                    and self.parent.position.latitude.enabled and self.parent.position.latitude.value is not None \
                    and self.parent.position.longitude.enabled and self.parent.position.longitude.value is not None:
                latitude: float = self.parent.position.latitude.value
                longitude: float = self.parent.position.longitude.value

                if self.parent.parent is not None and isinstance(self.parent.parent.parent, ICarConnectivity):
                    location_service: Optional[BaseService] = self.parent.parent.parent.get_service_for(ServiceType.LOCATION_CHARGING_STATION)
                    if location_service is not None and isinstance(location_service, LocationService):
                        result: Optional[ChargingStation] = location_service.charging_station_from_lat_lon(
                            latitude=latitude,
                            longitude=longitude,
                            radius=100,
                            charging_station=self.charging_station
                        )
                        if result is not None:
                            LOG.debug('Resolved charging station from position (%s, %s)', latitude, longitude)
                    else:
                        LOG.warning('No LocationService available to resolve charging station from position')
                        self.charging_station.clear()
                else:
                    LOG.warning('Charging not in correct context of CarConnectivity, cannot resolve charging station')
                    self.charging_station.clear()
            else:
                LOG.debug('Cannot resolve charging station, position not available')
                self.charging_station.clear()
        else:
            self.charging_station.clear()

    class ChargingState(Enum,):
        """
        Enum representing the various states of charging.

        Attributes:
            OFF (str): The charging state is off.
            READY_FOR_CHARGING (str): The vehicle is ready for charging.
            CHARGING (str): The vehicle is currently charging.
            CONSERVATION (str): The vehicle is in conservation mode.
            ERROR (str): There is an error in the charging system.
            UNSUPPORTED (str): The charging state is unsupported.
            DISCHARGING (str): The vehicle is discharging.
            UNKNOWN (str): The charging state is unknown.
        """
        OFF = 'off'
        READY_FOR_CHARGING = 'ready_for_charging'
        CHARGING = 'charging'
        CONSERVATION = 'conservation'
        ERROR = 'error'
        UNSUPPORTED = 'unsupported'
        DISCHARGING = 'discharging'
        UNKNOWN = 'unknown charging state'

    class ChargingType(Enum,):
        """
        Enum representing different types of car charging.

        Attributes:
            INVALID (str): Represents an invalid charging type.
            OFF (str): Represents the state when charging is off.
            AC (str): Represents AC (Alternating Current) charging.
            DC (str): Represents DC (Direct Current) charging.
            UNSUPPORTED (str): Represents an unsupported charging type.
            UNKNOWN (str): Represents an unknown charging type.
        """
        INVALID = 'invalid'
        OFF = 'off'
        AC = 'ac'
        DC = 'dc'
        UNSUPPORTED = 'unsupported'
        UNKNOWN = 'unknown charge type'

    class Settings(GenericObject):
        """
        This class represents the settings for car  charging.
        """
        def __init__(self, parent: Optional[GenericObject] = None, origin: Optional[Charging.Settings] = None, initialization: Optional[Dict] = None) -> None:
            if origin is not None:
                super().__init__(parent=parent, origin=origin, initialization=initialization)
                self.target_level: LevelAttribute = origin.target_level
                self.target_level.parent = self
                self.maximum_current: CurrentAttribute = origin.maximum_current
                self.maximum_current.parent = self
                self.auto_unlock: BooleanAttribute = origin.auto_unlock
                self.auto_unlock.parent = self
            else:
                super().__init__(object_id="settings", parent=parent, initialization=initialization)
                self.target_level: LevelAttribute = LevelAttribute("target_level", parent=self, precision=0.1, tags={'carconnectivity'},
                                                                   initialization=self.get_initialization('target_level'))
                self.maximum_current: CurrentAttribute = CurrentAttribute("maximum_current", parent=self, precision=0.1, tags={'carconnectivity'},
                                                                          initialization=self.get_initialization('maximum_current'))
                self.auto_unlock: BooleanAttribute = BooleanAttribute("auto_unlock", parent=self, tags={'carconnectivity'},
                                                                      initialization=self.get_initialization('auto_unlock'))
