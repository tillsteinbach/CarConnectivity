"""
This module defines the collection of connectors.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject

if TYPE_CHECKING:
    from typing import Optional, Dict

    from carconnectivity.carconnectivity import CarConnectivity

    from carconnectivity_connectors.base.connector import BaseConnector


class Connectors(GenericObject):
    """
    Represents the collection of connectors.
    """
    def __init__(self, car_connectivity: CarConnectivity, initialization: Optional[Dict] = None) -> None:
        super().__init__(object_id='connectors', parent=car_connectivity, initialization=initialization)
        self.connectors: Dict[str, BaseConnector] = {}
