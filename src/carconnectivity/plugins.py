"""
This module defines the collection of plugins.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.objects import GenericObject

if TYPE_CHECKING:
    from typing import Dict

    from carconnectivity.carconnectivity import CarConnectivity

    from carconnectivity_plugins.base.plugin import BasePlugin


class Plugins(GenericObject):
    """
    Represents the collection of plugins.
    """
    def __init__(self, car_connectivity: CarConnectivity) -> None:
        super().__init__(object_id='plugins', parent=car_connectivity)
        self.plugins: Dict[str, BasePlugin] = {}
